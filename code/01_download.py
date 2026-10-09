"""下载原始数据。仅用标准库。每个数据源写入 data/raw/ 下各自独立的子目录。
用法:  python code/01_download.py
"""
import json, sys, time, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C

def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "cyberpunk-index/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except Exception as e:
            print(f"  重试 {i+1}/{tries}: {e}")
            time.sleep(3 * (i + 1))
    raise RuntimeError(f"下载失败: {url}")

def main():
    wb = C.RAW / "worldbank"; wb.mkdir(parents=True, exist_ok=True)
    print("国家列表 ...")
    (wb / "_countries.json").write_bytes(get("https://api.worldbank.org/v2/country?format=json&per_page=400"))
    for key, code in C.WB.items():
        print("世界银行", code)
        url = (f"https://api.worldbank.org/v2/country/all/indicator/{code}"
               f"?format=json&per_page=20000&date={C.DOWNLOAD_FROM}:{C.DOWNLOAD_TO}")
        data = get(url)
        json.loads(data)  # 校验
        (wb / f"{key}.json").write_bytes(data)
    ow = C.RAW / "owid"; ow.mkdir(parents=True, exist_ok=True)
    for key, slug in C.OWID.items():
        print("OWID", slug)
        url = f"https://ourworldindata.org/grapher/{slug}.csv?v=1&csvType=full&useColumnShortNames=true"
        (ow / f"{key}.csv").write_bytes(get(url))
    print("完成。")

if __name__ == "__main__":
    main()
