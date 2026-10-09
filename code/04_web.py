"""生成网页数据 web/data/cpi.js（榜单页 index.html 与明细页 country.html 共用，file:// 下也能直接打开）。
输入: output/cyberpunk_index.csv、output/indicator_detail.csv
结构: window.CPI_DATA = {
  keys:  [指标 key...]            # 顺序同 config.INDICATORS
  subs:  [子维度列名...]          # 见 SUBS
  names: {iso3: 英文国名}
  data:  {快照年: {iso3: [T, L, CPI, 名次, [子维度得分...], [[原始值, 份额, 数据年, 得分] 或 null, ...]]}}
}
"""
import json, math, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C

SUBS = ["T_penetration", "T_innovation_input", "T_output_scale",
        "L_inequality", "L_environment", "L_safety", "L_food", "L_health", "L_hours", "L_longevity"]

def num(x, sig=5):
    """保留有效数字，缺失为 None。"""
    if x is None or (isinstance(x, float) and math.isnan(x)): return None
    return float(f"{x:.{sig}g}")

def main():
    idx = pd.read_csv(C.OUTPUT / "cyberpunk_index.csv")
    det = pd.read_csv(C.OUTPUT / "indicator_detail.csv")
    keys = list(C.INDICATORS)
    det = det.set_index(["snapshot", "iso3", "indicator"])
    data, names = {}, {}
    for r in idx.itertuples(index=False):
        y, iso = int(r.snapshot), r.iso3
        names[iso] = r.country
        v = []
        for k in keys:
            try: d = det.loc[(y, iso, k)]
            except KeyError: v.append(None); continue
            v.append([num(d.raw), num(d.share, 4), None if pd.isna(d.data_year) else int(d.data_year), num(d.score, 4)])
        data.setdefault(str(y), {})[iso] = [num(r.T, 4), num(r.L, 4), num(r.CPI, 4), int(r.rank),
                                            [num(getattr(r, s), 4) for s in SUBS], v]
    out = {"keys": keys, "subs": SUBS, "names": names, "data": data}
    dst = C.ROOT / "web" / "data" / "cpi.js"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("// 由 code/04_web.py 生成，勿手改\nwindow.CPI_DATA=" +
                   json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"已写入 {dst}（{dst.stat().st_size // 1024} KB，{len(idx)} 行）")

if __name__ == "__main__":
    main()
