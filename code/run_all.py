"""一键运行: 下载 -> 清洗 -> 计算。用法: python code/run_all.py"""
import runpy, sys
from pathlib import Path
d = Path(__file__).resolve().parent
for s in ["01_download.py", "02_clean.py", "03_index.py", "04_web.py"]:
    print(f"\n######## {s}")
    runpy.run_path(str(d / s), run_name="__main__")
