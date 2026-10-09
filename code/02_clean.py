"""把原始数据清洗成统一长表: data/processed/long.csv (iso3, indicator, year, value)。
只保留真实国家（剔除世界银行的地区/收入组聚合）。
"""
import json, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C

def load_wb():
    countries = json.loads((C.RAW / "worldbank" / "_countries.json").read_text(encoding="utf-8"))[1]
    real = {c["id"]: c["name"] for c in countries if c["region"]["value"] != "Aggregates"}
    frames = {}
    for key in C.WB:
        rows = json.loads((C.RAW / "worldbank" / f"{key}.json").read_text(encoding="utf-8"))[1] or []
        df = pd.DataFrame([{"iso3": r["countryiso3code"], "year": int(r["date"]), "value": r["value"]}
                           for r in rows if r["value"] is not None])
        frames[key] = df[df.iso3.isin(real)]
    # 看得起病 = 人均自付医疗支出 / 人均 GNI（均为 PPP 国际元）
    o = frames.pop("oop_pc_ppp").merge(frames.pop("gni_pc_ppp"), on=["iso3", "year"], suffixes=("_o", "_g"))
    o["value"] = o.value_o / o.value_g * 100
    frames["oop_health"] = o[["iso3", "year", "value"]]
    return frames, real

def load_owid(real):
    out = {}
    for key in C.OWID:
        df = pd.read_csv(C.RAW / "owid" / f"{key}.csv")
        df.columns = [c.lower() for c in df.columns]
        valcol = [c for c in df.columns if c not in ("entity", "code", "year", "owid_region")][0]
        df = df.rename(columns={"code": "iso3", valcol: "value"})[["iso3", "year", "value"]].dropna()
        out[key] = df[df.iso3.isin(real)]
    return out

def main():
    C.PROCESSED.mkdir(parents=True, exist_ok=True)
    frames, real = load_wb()
    frames.update(load_owid(real))
    long = pd.concat([d.assign(indicator=k) for k, d in frames.items() if k in C.INDICATORS])
    long.to_csv(C.PROCESSED / "long.csv", index=False)
    pd.Series(real, name="country").rename_axis("iso3").to_csv(C.PROCESSED / "countries.csv")
    print(long.groupby("indicator").iso3.nunique().to_string())

if __name__ == "__main__":
    main()
