"""计算赛博朋克指数。CPI = sqrt(T * L)。
流程: 取窗口内最新值 -> (取对数) -> 缩尾 5/95 -> 0-100 -> 子维度等权 -> T/L 等权 -> 几何平均。
并输出敏感性: 调和平均、min、各指标缩尾分位变化。
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C

def usable_years(long):
    """某年缺任何一个指标（该年当年没有任何国家有数据）则该年不可用。"""
    have = long.groupby("year").indicator.agg(lambda x: set(x))
    need = set(C.INDICATORS)
    return [int(y) for y, h in have.items() if need <= h and C.DOWNLOAD_FROM <= y <= C.DOWNLOAD_TO]

def snapshot(long, year):
    d = long[(long.year <= year) & (long.year > year - C.WINDOW)]
    d = d.sort_values("year").groupby(["iso3", "indicator"]).tail(1)
    vals = d.pivot(index="iso3", columns="indicator", values="value")
    raw = vals.copy()                           # 换算份额前的原始值，供明细页展示
    for k in C.SHARE_KEYS & set(vals):          # 总量 -> 占世界总量份额
        vals[k] = vals[k] / vals[k].sum()
    return vals, d.pivot(index="iso3", columns="indicator", values="year"), raw

def score(vals, lo_q=0.05, hi_q=0.95):
    s = pd.DataFrame(index=vals.index)
    for k, (side, sub, log, sign) in C.INDICATORS.items():
        if k not in vals: continue
        x = vals[k].astype(float)
        if log: x = np.log1p(x.clip(lower=0))
        lo, hi = x.quantile(lo_q), x.quantile(hi_q)
        x = x.clip(lo, hi)
        z = (x - lo) / (hi - lo) * 100 if hi > lo else x * 0
        s[k] = z if sign > 0 else 100 - z
    return s

def combine(s, vals):
    avail = [k for k in C.INDICATORS if k in s]
    cov = s[avail].notna().sum(axis=1) / len(avail)
    side = {}
    for sd in "TL":
        subs = {}
        for sub in sorted({v[1] for v in C.INDICATORS.values() if v[0] == sd}):
            ks = [k for k in avail if C.INDICATORS[k][:2] == (sd, sub)]
            if ks: subs[sub] = s[ks].mean(axis=1)
        side[sd] = pd.DataFrame(subs)
    T, L = side["T"].mean(axis=1), side["L"].mean(axis=1)
    # L 的 4 项是硬要求：缺任何一项的国家直接不入榜；T 至少 70% 指标有数据
    kl = [k for k in avail if C.INDICATORS[k][0] == "L"]
    kt = [k for k in avail if C.INDICATORS[k][0] == "T"]
    ok = (s[kl].notna().all(axis=1)) & (s[kt].notna().mean(axis=1) >= C.MIN_COVERAGE) & T.notna() & L.notna()
    out = pd.DataFrame({"T": T, "L": L, "coverage": cov})
    out["CPI"] = np.sqrt(out["T"] * out["L"])
    out["CPI_harmonic"] = 2 * out["T"] * out["L"] / (out["T"] + out["L"])
    out["CPI_min"] = out[["T", "L"]].min(axis=1)
    out = out.join(side["T"].add_prefix("T_")).join(side["L"].add_prefix("L_"))
    return out[ok]

def main():
    long = pd.read_csv(C.PROCESSED / "long.csv")
    names = pd.read_csv(C.PROCESSED / "countries.csv").set_index("iso3").country
    C.OUTPUT.mkdir(parents=True, exist_ok=True)
    allres, sens, detail = [], [], []
    years = C.SNAPSHOT_YEARS or usable_years(long)
    print("可用快照年份:", years)
    for y in years:
        vals, yrs, raw = snapshot(long, y)
        s = score(vals)
        res = combine(s, vals)
        # 指标明细：原始值、份额（仅总量指标）、实际数据年、0-100 得分；只保留入榜国家
        keep = res.index
        stk = lambda df, name: df.reindex(keep).stack().rename(name)
        det = pd.concat([stk(raw, "raw"), stk(vals[[k for k in C.SHARE_KEYS if k in vals]], "share"),
                         stk(yrs, "data_year"), stk(s, "score")], axis=1).reset_index()
        det.columns = ["iso3", "indicator", "raw", "share", "data_year", "score"]
        det["snapshot"] = y
        detail.append(det)
        res["rank"] = res.CPI.rank(ascending=False, method="min").astype(int)
        res["country"] = names.reindex(res.index)
        res["snapshot"] = y
        res["median_data_year"] = yrs.reindex(res.index).median(axis=1)
        allres.append(res.reset_index())
        # 敏感性：与替代融合公式 / 更宽缩尾的排名相关性(Spearman)
        wide = combine(score(vals, .01, .99), vals)
        j = res.join(wide.CPI.rename("cpi_wide"), how="inner")
        sens.append({"snapshot": y, "n_countries": len(res),
                     "spearman_vs_harmonic": res.CPI.corr(res.CPI_harmonic, method="spearman"),
                     "spearman_vs_min": res.CPI.corr(res.CPI_min, method="spearman"),
                     "spearman_vs_winsor_1_99": j.CPI.corr(j.cpi_wide, method="spearman"),
                     "spearman_T_vs_L": res["T"].corr(res["L"], method="spearman")})
        print(f"\n== {y}: {len(res)} 国 ==")
        print(res.sort_values("rank")[["country", "T", "L", "CPI", "rank"]].head(15).round(1).to_string())
    pd.concat(allres).to_csv(C.OUTPUT / "cyberpunk_index.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(sens).round(3).to_csv(C.OUTPUT / "sensitivity.csv", index=False)
    pd.concat(detail).to_csv(C.OUTPUT / "indicator_detail.csv", index=False, encoding="utf-8-sig")
    print("\n", pd.DataFrame(sens).round(3).to_string(index=False))

if __name__ == "__main__":
    main()
