"""
Task 3.3: Void Score 計算

商業邏輯：
  Void Score 是本系統的核心指標，用於量化某區域對特定料理類型
  的投資價值。分數越高，代表該區域越適合新餐廳進入。

  Void Score 綜合考量三個維度：

  1. 供給空白度 (Supply Void) — 權重 40%：
     競爭者越少，市場空白越大，機會越高。
     使用 1 / (competitor_count + 1) 的反比關係。

  2. 成本效益 (Cost Efficiency) — 權重 30%：
     租金越低，營運成本越小，投資回收期越短。
     使用歸一化後的反向租金指數。

  3. 需求強度 (Demand Strength) — 權重 30%：
     以總評論數作為消費者需求的代理指標。
     評論越多代表該區域的餐飲消費活動越活躍。

  最終公式 (百分制)：
  void_score = (0.4 × norm_supply_void
              + 0.3 × norm_cost_efficiency
              + 0.3 × norm_demand) × 100
"""

import logging
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

logger = logging.getLogger(__name__)

# Void Score 權重配置
WEIGHT_SUPPLY_VOID = 0.4      # 供給空白度權重（最重要）
WEIGHT_COST_EFFICIENCY = 0.3  # 成本效益權重
WEIGHT_DEMAND = 0.3           # 需求強度權重


def calculate_void_score(df: DataFrame) -> DataFrame:
    """
    計算 Void Score，識別高價值的市場空白區域。

    步驟：
    1. 計算各維度的原始值
    2. Min-Max 歸一化至 [0, 1] 區間
    3. 加權平均 → 乘以 100 轉為百分制

    分數解讀：
    - 80-100: 極高機會（低競爭 + 低租金 + 高需求）
    - 60-80:  良好機會
    - 40-60:  中等
    - 20-40:  有限機會
    - 0-20:   不建議進入（高競爭 + 高租金 + 低需求）

    Args:
        df: Join 租金後的 H3 聚合 DataFrame

    Returns:
        新增 void_score 欄位的 DataFrame (0-100 分)
    """
    logger.info("正在計算 Void Score...")
    logger.info(
        f"權重配置: 供給空白={WEIGHT_SUPPLY_VOID}, "
        f"成本效益={WEIGHT_COST_EFFICIENCY}, "
        f"需求={WEIGHT_DEMAND}"
    )

    # ===== Step 1: 計算原始指標 =====

    # 供給空白度：競爭者越少 → 值越大
    df = df.withColumn(
        "supply_void_raw",
        1.0 / (F.col("competitor_count").cast("double") + 1.0)
    )

    # 需求強度：直接使用總評論數（已為正向指標）
    df = df.withColumn(
        "demand_raw",
        F.col("total_reviews").cast("double")
    )

    # ===== Step 2: Min-Max 歸一化 =====
    # 收集各維度的統計值（一次 collect 取得所有值）
    stats = df.agg(
        F.min("supply_void_raw").alias("min_sv"),
        F.max("supply_void_raw").alias("max_sv"),
        F.min("rent_index").alias("min_rent"),
        F.max("rent_index").alias("max_rent"),
        F.min("demand_raw").alias("min_demand"),
        F.max("demand_raw").alias("max_demand"),
    ).collect()[0]

    sv_range = (stats["max_sv"] or 0) - (stats["min_sv"] or 0)
    rent_range = (stats["max_rent"] or 0) - (stats["min_rent"] or 0)
    demand_range = (stats["max_demand"] or 0) - (stats["min_demand"] or 0)

    logger.info(
        f"歸一化範圍: supply_void=[{stats['min_sv']:.4f}, {stats['max_sv']:.4f}], "
        f"rent=[${stats['min_rent']:,.0f}, ${stats['max_rent']:,.0f}], "
        f"demand=[{stats['min_demand']:,.0f}, {stats['max_demand']:,.0f}]"
    )

    # 供給空白度歸一化（正向：越大越好）
    if sv_range > 0:
        df = df.withColumn(
            "norm_supply_void",
            (F.col("supply_void_raw") - F.lit(stats["min_sv"])) / F.lit(sv_range)
        )
    else:
        df = df.withColumn("norm_supply_void", F.lit(0.5))

    # 成本效益歸一化（反向：租金越低越好）
    if rent_range > 0:
        df = df.withColumn(
            "norm_cost_efficiency",
            1.0 - (F.col("rent_index") - F.lit(stats["min_rent"])) / F.lit(rent_range)
        )
    else:
        df = df.withColumn("norm_cost_efficiency", F.lit(0.5))

    # 需求強度歸一化（正向：越高越好）
    if demand_range > 0:
        df = df.withColumn(
            "norm_demand",
            (F.col("demand_raw") - F.lit(stats["min_demand"])) / F.lit(demand_range)
        )
    else:
        df = df.withColumn("norm_demand", F.lit(0.5))

    # ===== Step 3: 加權計算 Void Score =====
    df = df.withColumn(
        "void_score",
        F.round(
            (
                F.lit(WEIGHT_SUPPLY_VOID) * F.col("norm_supply_void")
                + F.lit(WEIGHT_COST_EFFICIENCY) * F.col("norm_cost_efficiency")
                + F.lit(WEIGHT_DEMAND) * F.col("norm_demand")
            ) * 100,  # 轉為百分制
            2
        )
    )

    # 清除中間計算欄位
    df_result = df.drop(
        "supply_void_raw", "demand_raw",
        "norm_supply_void", "norm_cost_efficiency", "norm_demand"
    )

    # 輸出統計摘要
    score_stats = df_result.agg(
        F.round(F.min("void_score"), 1).alias("min"),
        F.round(F.avg("void_score"), 1).alias("avg"),
        F.round(F.percentile_approx("void_score", 0.5), 1).alias("median"),
        F.round(F.max("void_score"), 1).alias("max"),
    ).collect()[0]

    logger.info(
        f"Void Score 統計: "
        f"最低={score_stats['min']}, "
        f"中位數={score_stats['median']}, "
        f"平均={score_stats['avg']}, "
        f"最高={score_stats['max']}"
    )

    return df_result
