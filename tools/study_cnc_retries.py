"""tools/study_cnc_retries.py - feasibility study (10 Nov 2026, entry 3.71). For each real TCP conversation in every
IoT-23 scenario, count failed tries (same src -> dst) in the hour before. Run: python tools/study_cnc_retries.py out.parquet"""
import glob, os, sys, numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq, pyarrow.compute as pc
FAILED = ["S0", "REJ", "RSTOS0", "SH", "RSTRH", "SHR", "OTH"]
COLS = ["ts", "id.orig_h", "id.resp_h", "proto", "conn_state", "resp_bytes", "class_name"]
out = []
for f in sorted(glob.glob("data/interim/*.parquet")):
    sc = os.path.basename(f)[:-8]; pf = pq.ParquetFile(f)
    conv = []
    for b in pf.iter_batches(columns=COLS, batch_size=2_000_000):
        rb = pc.fill_null(b.column("resp_bytes").cast(pa.float64()), 0.0)
        m = pc.and_(pc.equal(b.column("proto"), "tcp"), pc.and_(pc.invert(pc.is_in(b.column("conn_state"), pa.array(FAILED))), pc.greater(rb, 0)))
        if pc.any(m).as_py(): conv.append(b.filter(m).to_pandas())
    if not conv: continue
    conv = pd.concat(conv); dsts = pa.array(conv["id.resp_h"].unique())
    fails = []
    for b in pf.iter_batches(columns=["ts", "id.orig_h", "id.resp_h", "proto", "conn_state"], batch_size=2_000_000):
        m = pc.and_(pc.is_in(b.column("id.resp_h"), dsts), pc.and_(pc.equal(b.column("proto"), "tcp"), pc.is_in(b.column("conn_state"), pa.array(FAILED))))
        if pc.any(m).as_py(): fails.append(b.filter(m).to_pandas()[["ts", "id.orig_h", "id.resp_h"]])
    fails = pd.concat(fails) if fails else pd.DataFrame(columns=["ts", "id.orig_h", "id.resp_h"])
    ft = {k: np.sort(g.ts.values.astype(float)) for k, g in fails.groupby(["id.orig_h", "id.resp_h"])}
    cnt = []
    for s, d, t in zip(conv["id.orig_h"], conv["id.resp_h"], conv.ts.astype(float)):
        a = ft.get((s, d)); cnt.append(0 if a is None else int(np.searchsorted(a, t) - np.searchsorted(a, t - 3600)))
    conv["fails_1h"] = cnt; conv["scenario"] = sc; out.append(conv[["scenario", "class_name", "fails_1h"]])
    print(sc, len(conv), "conversations", flush=True)
r = pd.concat(out)
r.to_parquet(sys.argv[1])
def summ(x): return pd.Series({"n": len(x), "share_with_>=3_fails": (x.fails_1h >= 3).mean(), "median": x.fails_1h.median()})
print("\nBy class (all scenarios):"); print(r.groupby("class_name").apply(summ).round(3))
print("\nBy scenario and class:"); print(r.groupby(["scenario", "class_name"]).apply(summ).round(3).to_string())
