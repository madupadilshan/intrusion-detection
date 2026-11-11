"""tools/explore_window_features.py - Feasibility experiment (exploration only, NOT a project result).

Run:  .venv\Scripts\python.exe tools\explore_window_features.py "D:\intrusion detection"   (about 5 minutes)

Question: do "window" features (what the same source did in the last 60 s, and how regularly it
contacts the same destination) improve grouped-CV macro-F1, especially for CnC and DDoS?

Rules: training scenarios only (34-1 is never read). Window features are computed on the FULL
scenario stream (before sampling) and are causal (only past and current flows are used), so the
same values can be computed live in the Zeek adapter. The 4 largest scenarios (17-1, 33-1, 39-1,
43-1) are skipped to fit in memory on this PC.
"""
import gc
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.compute as pc
import pyarrow.parquet as pq
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, classification_report
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

ROOT = Path(sys.argv[1])
sys.path.insert(0, str(ROOT))
from ml_engine.features import make_features, CATEGORICAL_FEATURES, NUMERICAL_FEATURES  # noqa: E402

SKIP = {"17-1", "33-1", "39-1", "43-1", "34-1"}
CAP = 20000
RAW = ["proto", "service", "conn_state", "history", "id.orig_p", "id.resp_p", "duration", "orig_bytes",
       "resp_bytes", "missed_bytes", "orig_pkts", "orig_ip_bytes", "resp_pkts", "resp_ip_bytes"]
WIN = ["src_conn_60s", "src_udst_60s", "src_uport_60s", "src_udst_ratio", "pair_conn_60s",
       "pair_iat", "pair_iat_jitter"]
CLASSES = ["Benign", "DDoS_DoS", "PortScan", "CnC", "Malware_Download"]


def codes(col):
    return pc.dictionary_encode(col).combine_chunks().indices.to_numpy(zero_copy_only=False)


def window_features(path):
    t = pq.read_table(path, columns=["ts", "id.orig_h", "id.resp_h", "id.resp_p", "class_name", "conn_state", "orig_bytes"])
    d = pd.DataFrame({
        "ts": t["ts"].to_numpy(), "src": codes(t["id.orig_h"]), "dst": codes(t["id.resp_h"]),
        "port": t["id.resp_p"].to_numpy(zero_copy_only=False),
        "cls": t["class_name"].to_numpy(zero_copy_only=False),
        "s0": (pc.equal(t["conn_state"], "S0")).to_numpy(zero_copy_only=False),
        "local": pc.starts_with(t["id.orig_h"], "192.168.").to_numpy(zero_copy_only=False),
        "zero": pc.equal(pc.fill_null(t["orig_bytes"], 0), 0).to_numpy(zero_copy_only=False),
    })
    del t
    d["row"] = np.arange(len(d))
    d = d.sort_values(["ts", "row"], kind="stable").reset_index(drop=True)
    d["b"] = np.floor(d.ts / 60).astype(np.int64)
    g = d.groupby(["src", "b"], sort=False)
    d["src_conn_60s"] = g.cumcount() + 1
    d["src_udst_60s"] = (~d.duplicated(["src", "b", "dst"])).groupby([d.src, d.b]).cumsum()
    d["src_uport_60s"] = (~d.duplicated(["src", "b", "port"])).groupby([d.src, d.b]).cumsum()
    d["src_udst_ratio"] = d.src_udst_60s / d.src_conn_60s
    d["pair_conn_60s"] = d.groupby(["src", "dst", "b"], sort=False).cumcount() + 1
    d["pair_iat"] = d.groupby(["src", "dst"], sort=False).ts.diff()
    d["pair_iat_jitter"] = (d.pair_iat - d.groupby(["src", "dst"], sort=False).pair_iat.shift()).abs()
    d[["pair_iat", "pair_iat_jitter"]] = d[["pair_iat", "pair_iat_jitter"]].fillna(-1.0)
    return d


def raw_rows(path, rows):
    rows = np.sort(rows)
    out, off = [], 0
    for batch in pq.ParquetFile(path).iter_batches(batch_size=1_000_000, columns=RAW):
        n = batch.num_rows
        sel = rows[(rows >= off) & (rows < off + n)] - off
        if len(sel):
            out.append(batch.take(sel).to_pandas())
        off += n
    return pd.concat(out, ignore_index=True), rows


parts = []
for f in sorted((ROOT / "data" / "interim").glob("*.parquet")):
    sid = f.stem.split("-Capture-")[-1]
    if sid in SKIP:
        continue
    t0 = time.time()
    d = window_features(f)
    d = d[d.cls.isin(CLASSES)]
    pick = (d.groupby("cls", group_keys=False)
             .apply(lambda x: x.sample(min(len(x), CAP), random_state=42)))
    raw, rows = raw_rows(f, pick.row.to_numpy())
    pick = pick.set_index("row").loc[rows]
    X = make_features(raw).reset_index(drop=True)
    for c in WIN:
        X[c] = pick[c].to_numpy()
    X["y"] = pick.cls.to_numpy()
    X["noisy_benign"] = (pick.cls.eq("Benign") & pick.s0 & pick.local & pick.zero).to_numpy()
    X["scenario"] = sid
    parts.append(X)
    print(f"{sid:6s} rows={len(d):>11,d} sampled={len(X):>7,d} {time.time()-t0:5.1f}s", flush=True)
    del d, pick, raw
    gc.collect()

data = pd.concat(parts, ignore_index=True)
print("\nclass counts:\n", data.y.value_counts().to_string())


def cv(feats, df, name):
    cat = [c for c in feats if c in CATEGORICAL_FEATURES]
    pre = ColumnTransformer([("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1,
                                                    min_frequency=50), cat)], remainder="passthrough")
    model = Pipeline([("pre", pre), ("rf", RandomForestClassifier(
        n_estimators=100, max_depth=18, min_samples_leaf=4, min_samples_split=5, max_features="sqrt",
        class_weight="balanced", n_jobs=-1, random_state=42))])
    pred = np.empty(len(df), dtype=object)
    for tr, te in StratifiedGroupKFold(5, shuffle=True, random_state=42).split(df, df.y, df.scenario):
        model.fit(df.iloc[tr][feats], df.y.iloc[tr])
        pred[te] = model.predict(df.iloc[te][feats])
    f1 = f1_score(df.y, pred, labels=CLASSES, average=None, zero_division=0)
    print(f"\n=== {name}: out-of-fold macro-F1 = {f1.mean():.4f}")
    print("   " + "  ".join(f"{c}={v:.3f}" for c, v in zip(CLASSES, f1)))
    return f1


base = CATEGORICAL_FEATURES + NUMERICAL_FEATURES
cv(base, data, "A. current 19 features")
cv(base + WIN, data, "B. 19 + 7 window features")
clean = data[~data.noisy_benign].reset_index(drop=True)
print(f"\n(removed {data.noisy_benign.sum():,d} 'Benign' rows that are outbound unanswered SYNs with no data)")
cv(base, clean, "C. 19 features, Benign noise removed")
cv(base + WIN, clean, "D. 19 + window features, Benign noise removed")
