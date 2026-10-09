"""集中配置：路径、年份、指标清单。只放配置，不放数据。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # 工作区根目录
RAW = ROOT / "data" / "raw"                            # 原始数据（只由下载脚本写入）
PROCESSED = ROOT / "data" / "processed"                # 清洗后的中间表
OUTPUT = ROOT / "output"                               # 指数结果

# 参考年份：每个快照取 [Y-WINDOW+1, Y] 内每个国家最新的一个值，并记录实际数据年
SNAPSHOT_YEARS = None   # None = 自动：凡是 13 个指标在该年当年都有数据的年份都算快照（不回避疫情年份）
WINDOW = 5
DOWNLOAD_FROM, DOWNLOAD_TO = 2005, 2025
MIN_COVERAGE = 0.70                                    # 至少 70% 指标有数据

# 世界银行指标：key -> (代码, 说明)
WB = {
    "patents":      "IP.PAT.RESD",         # 居民专利申请总数
    "sci_articles": "IP.JRN.ARTC.SC",      # 科技期刊论文篇数
    "hightech_usd": "TX.VAL.TECH.CD",      # 高技术出口总额（现价美元）
    "rd_gdp":       "GB.XPD.RSDV.GD.ZS",
    "researchers":  "SP.POP.SCIE.RD.P6",
    "internet":     "IT.NET.USER.ZS",      # 互联网使用率
    "broadband":    "IT.NET.BBND.P2",
    "oop_pc_ppp":   "SH.XPD.OOPC.PP.CD",   # 人均自付医疗支出（PPP 国际元）
    "gni_pc_ppp":   "NY.GNP.PCAP.PP.CD",   # 人均 GNI（PPP 国际元）
    "life_exp":     "SP.DYN.LE00.IN",      # 出生时预期寿命（年）
    "u5_mortality": "SH.DYN.MORT",         # 5 岁以下死亡率（每千名活产）
    "gini":         "SI.POV.GINI",         # 基尼系数
    "pm25":         "EN.ATM.PM25.MC.M3",   # PM2.5 年均浓度
    "homicide":     "VC.IHR.PSRC.P5",      # 凶杀率（每10万人）
}
OWID = {
    "unaff_diet": "share-healthy-diet-unaffordable",
    "work_hours": "annual-working-hours-per-worker",
}

# 指标定义：key -> (侧, 子维度, 是否取对数, 方向 +1 越高越"赛博"/-1 反向)
# 侧 T=高科技, L=低生活（L 侧已按"越高=生活越差"定向）
INDICATORS = {
    "internet":     ("T", "penetration",       False, +1),   # 渗透：人均/占比
    "broadband":    ("T", "penetration",       False, +1),
    "rd_gdp":       ("T", "innovation_input",  False, +1),   # 投入强度：与国家大小无关
    "researchers":  ("T", "innovation_input",  True,  +1),
    "patents":      ("T", "output_scale",      False,  +1),   # 产出规模：占世界总量份额，线性
    "sci_articles": ("T", "output_scale",      False,  +1),
    "hightech_usd": ("T", "output_scale",      False,  +1),
    "unaff_diet":   ("L", "food",              False, +1),   # 吃得起：买不起健康饮食的人口比例
    "oop_health":   ("L", "health",            False, +1),   # 看得起病：人均自付医疗支出 / 人均 GNI（%）
    "u5_mortality": ("L", "health",            True,  +1),   # 看得起病：基础医疗效果，与自付负担互相制衡（取对数）
    "life_exp":     ("L", "longevity",         False, -1),   # 活得久吗：预期寿命越短，分越高
    "work_hours":   ("L", "hours",             False, +1),   # 工时
    "gini":         ("L", "inequality",        False, +1),   # 不平等：基尼系数
    "pm25":         ("L", "environment",       True,  +1),   # 环境：PM2.5（取对数）
    "homicide":     ("L", "safety",            True,  +1),   # 安全：凶杀率（取对数）
}


# 取"占世界总量份额"的指标（每个快照内：国家值 / 所有入统计国家值之和），不取对数
SHARE_KEYS = {"patents", "sci_articles", "hightech_usd"}
