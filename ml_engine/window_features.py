#!/usr/bin/env python3
"""
ml_engine/window_features.py - "Window" features: what the same source did in the last 60 seconds.

Decision D-051 (proposal Table 6: "rate over a time window if we use it"); D-052 added `pair_fail_1h`.

Why: one flow alone looks the same in most classes (one unanswered SYN, 0 bytes, 1 packet).
What separates the classes is the pattern over a short time:
  - a port scan contacts many different hosts;
  - C&C contacts the same 1-3 hosts again and again, at regular times;
  - DDoS sends very many connections to one host;
  - a C&C conversation usually comes after many failed tries to the same server (D-052).

Same code in training and live (golden rule, proposal 3.5):
  - `WindowState` reads flows one by one, in the order Zeek writes them, and uses only flows
    it has already seen. The IoT-23 files keep Zeek's write order, and the live Zeek adapter
    gets lines in the same order, so training and live values are made the same way.
  - Training (`ml_engine/sample_dataset.py`) runs `WindowState` over the FULL scenario stream
    before sampling. Live (`core_engine/zeek_adapter.py`) keeps one `WindowState` for the sensor.

IP addresses are only used to group flows. They are never model inputs (proposal Table 6).
"""

from __future__ import annotations

import math
from collections import deque
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

# The 7 window features, in fixed order (D-051).
WINDOW_FEATURES: List[str] = [
    "src_conn_60s",     # flows from the same source in the same 60 s period (this one included)
    "src_udst_60s",     # distinct destination IPs of that source in that period
    "src_uport_60s",    # distinct destination ports of that source in that period
    "src_udst_ratio",   # src_udst_60s / src_conn_60s
    "pair_conn_60s",    # flows from the same source to the same destination in that period
    "pair_gap",         # seconds since the previous flow of the same pair (-1: none or > PAIR_GAP_MAX)
    "pair_gap_change",  # |pair_gap - previous pair_gap| (-1: unknown); small = regular contact
    "pair_fail_1h",     # earlier failed TCP tries, same source -> same destination, last 50-60 min (D-052)
]

PERIOD_SECONDS = 60          # length of one period
PERIODS_KEPT = 3             # periods more than 3 periods behind the newest are forgotten
PAIR_GAP_MAX = 600.0         # a gap longer than 10 minutes counts as "no previous flow"
PAIR_KEEP_SECONDS = 600.0    # pairs not seen for 10 minutes are forgotten

# Size limits, so memory stays bounded under a very heavy scan or flood (IoT-23 scenario 43-1 has
# about 17,000 flows per second from one scanner). The same limits apply in training and live,
# so both give the same values. In a small camera lab they are not reached.
MAX_DSTS_PER_PERIOD = 10_000  # destinations remembered per source per period; above this, every
                              # destination not remembered is counted as a new one
MAX_PAIRS = 300_000           # source -> destination pairs remembered; the oldest are forgotten first
MAX_PAIR_LOG = 600_000        # bookkeeping entries kept for forgetting old pairs

# Failed tries (D-052). A TCP flow in one of these states is a failed try (no conversation).
FAILED_STATES = frozenset({"S0", "REJ", "RSTOS0", "SH", "RSTRH", "SHR", "OTH"})
FAIL_BUCKET_SECONDS = 600     # failed tries are counted per 10-minute period ...
FAIL_BUCKETS = 6              # ... over the current and the 5 previous periods (50-60 minutes)
FAIL_KEEP_SECONDS = 3600.0    # a pair with no failed try for 60 minutes is forgotten
MAX_FAIL_PAIRS = 300_000      # pairs with failed tries remembered; least recently updated forgotten first
MAX_FAIL_LOG = 600_000        # bookkeeping entries kept for forgetting old failed-try pairs

# Values used when a flow has no usable time or source (it is then not counted).
DEFAULT_VALUES: Tuple[float, ...] = (1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, 0.0)


def _num(x: Any) -> Optional[float]:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


class WindowState:
    """Remembers recent flows per source and per source-destination pair.

    Call `update()` once per flow, in the order the flows are written by Zeek.
    Memory is bounded: old periods and old pairs are forgotten (constants above).
    """

    __slots__ = ("_periods", "_period_keys", "_max_period", "_pairs", "_pair_log", "_max_ts", "_seq",
                 "_fails", "_fail_log")

    def __init__(self) -> None:
        # (src, period) -> [flow count, {dst: count}, {ports}, destinations not remembered]
        self._periods: Dict[Tuple[str, int], list] = {}
        # period -> list of (src, period) keys, used to forget old periods
        self._period_keys: Dict[int, List[Tuple[str, int]]] = {}
        self._max_period: Optional[int] = None
        # (src, dst) -> [last ts, last gap, update number]
        self._pairs: Dict[Tuple[str, str], list] = {}
        self._pair_log: deque = deque()   # (ts, (src, dst), update number)
        self._max_ts = -math.inf
        self._seq = 0
        # (src, dst) -> [{10-minute period: failed tries}, update number]   (D-052)
        self._fails: Dict[Tuple[str, str], list] = {}
        self._fail_log: deque = deque()   # (ts, (src, dst), update number)

    def reset(self) -> None:
        self.__init__()

    def __len__(self) -> int:
        return len(self._pairs)

    def update(self, src: Any, dst: Any, port: Any, ts: Any,
               proto: Any = None, conn_state: Any = None) -> Tuple[float, ...]:
        """Add one flow and return its 8 window feature values (order of WINDOW_FEATURES).

        `proto` and `conn_state` are needed for `pair_fail_1h`; without them a flow is never
        counted as a failed try."""
        t = _num(ts)
        if t is None or src is None or src == "" or (isinstance(src, float) and math.isnan(src)):
            return DEFAULT_VALUES
        src = str(src)
        dst = "" if dst is None or (isinstance(dst, float) and math.isnan(dst)) else str(dst)
        p = _num(port)
        port_key = int(p) if p is not None else -1

        # --- per source, per 60 s period ---
        period = int(t // PERIOD_SECONDS)
        if self._max_period is None or period > self._max_period:
            self._max_period = period
            oldest = period - PERIODS_KEPT
            for old in [b for b in self._period_keys if b < oldest]:
                for key in self._period_keys.pop(old):
                    self._periods.pop(key, None)
        key = (src, period)
        rec = self._periods.get(key)
        if rec is None:
            rec = [0, {}, set(), 0]
            self._periods[key] = rec
            self._period_keys.setdefault(period, []).append(key)
        rec[0] += 1
        dsts = rec[1]
        n = dsts.get(dst)
        if n is not None:
            dsts[dst] = n + 1
            pair_conn = n + 1
        elif len(dsts) < MAX_DSTS_PER_PERIOD:
            dsts[dst] = 1
            pair_conn = 1
        else:
            rec[3] += 1  # limit reached: counted as a new destination, not remembered
            pair_conn = 1
        rec[2].add(port_key)
        conn = rec[0]
        udst = len(dsts) + rec[3]
        uport = len(rec[2])

        # --- per source -> destination pair ---
        self._seq += 1
        pkey = (src, dst)
        prev = self._pairs.get(pkey)
        gap = -1.0
        change = -1.0
        if prev is not None:
            g = abs(t - prev[0])
            if g <= PAIR_GAP_MAX:
                gap = g
                if prev[1] >= 0.0:
                    change = abs(g - prev[1])
        self._pairs[pkey] = [t, gap, self._seq]
        self._pair_log.append((t, pkey, self._seq))
        if t > self._max_ts:
            self._max_ts = t
        limit = self._max_ts - PAIR_KEEP_SECONDS
        log = self._pair_log
        pairs = self._pairs
        while log and (log[0][0] < limit or len(pairs) > MAX_PAIRS or len(log) > MAX_PAIR_LOG):
            _, k, seq = log.popleft()
            cur = pairs.get(k)
            if cur is not None and cur[2] == seq:
                del pairs[k]

        # --- failed tries of the same pair in the last 50-60 minutes (D-052) ---
        bucket = int(t // FAIL_BUCKET_SECONDS)
        oldest_bucket = bucket - (FAIL_BUCKETS - 1)
        frec = self._fails.get(pkey)
        fails = 0
        if frec is not None:
            # Every flow already seen counts, also one with a later start time (Zeek writes a
            # flow when it ends, so the write order is not exactly the start-time order).
            fails = sum(c for b, c in frec[0].items() if b >= oldest_bucket)
        if (str(proto).lower() == "tcp") and (str(conn_state) in FAILED_STATES):
            if frec is None:
                frec = [{}, 0]
                self._fails[pkey] = frec
            counts = frec[0]
            counts[bucket] = counts.get(bucket, 0) + 1
            for b in [b for b in counts if b < oldest_bucket]:
                del counts[b]
            frec[1] = self._seq
            self._fail_log.append((t, pkey, self._seq))
            flog = self._fail_log
            fpairs = self._fails
            flimit = self._max_ts - FAIL_KEEP_SECONDS
            while flog and (flog[0][0] < flimit or len(fpairs) > MAX_FAIL_PAIRS or len(flog) > MAX_FAIL_LOG):
                _, k, seq = flog.popleft()
                cur = fpairs.get(k)
                if cur is not None and cur[1] == seq:
                    del fpairs[k]

        return (float(conn), float(udst), float(uport), udst / conn, float(pair_conn), gap, change,
                float(fails))

    def update_many(self, srcs: Iterable, dsts: Iterable, ports: Iterable, tss: Iterable,
                    protos: Optional[Iterable] = None, states: Optional[Iterable] = None) -> np.ndarray:
        """Run `update()` over many flows in order. Returns an array of shape (n, 8)."""
        up = self.update
        srcs, dsts, ports, tss = list(srcs), list(dsts), list(ports), list(tss)
        protos = list(protos) if protos is not None else [None] * len(srcs)
        states = list(states) if states is not None else [None] * len(srcs)
        rows = [up(s, d, p, t, pr, st) for s, d, p, t, pr, st in zip(srcs, dsts, ports, tss, protos, states)]
        if not rows:
            return np.empty((0, len(WINDOW_FEATURES)), dtype=np.float32)
        return np.asarray(rows, dtype=np.float32)


def _column(df: pd.DataFrame, names: Sequence[str]) -> List[Any]:
    for n in names:
        if n in df.columns:
            return df[n].tolist()
    return [None] * len(df)


def compute_window_features(df: pd.DataFrame, state: Optional[WindowState] = None) -> pd.DataFrame:
    """Window features for every row of `df`, in row order (the order Zeek wrote the flows).

    Pass a `state` to continue from earlier rows (for example the previous chunk of a file).
    """
    st = state if state is not None else WindowState()
    values = st.update_many(
        _column(df, ("id.orig_h", "id_orig_h", "src_ip")),
        _column(df, ("id.resp_h", "id_resp_h", "dst_ip")),
        _column(df, ("id.resp_p", "id_resp_p", "dst_port")),
        _column(df, ("ts",)),
        _column(df, ("proto",)),
        _column(df, ("conn_state",)),
    )
    return pd.DataFrame(values, columns=WINDOW_FEATURES, index=df.index)
