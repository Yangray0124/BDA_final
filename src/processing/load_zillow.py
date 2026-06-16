"""
Task 2.2: 載入 Zillow 租金指數資料

商業邏輯：
  Zillow ZORI (Zillow Observed Rent Index) 提供全美各 Zip code 的
  月租金中位數估計值。此資料代表「成本面」——在特定區域開設餐廳
  所需承擔的租金成本。低租金區域意味著較低的營運門檻。

  ZORI CSV 使用寬表格式：
  - 前幾欄為區域資訊 (RegionID, RegionName, StateName, ...)
  - 後續欄位為各月份的租金值 (如 "2024-01-31", "2024-02-29", ...)
  我們取最近一期的月份作為當前租金指數。
"""

import logging
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

logger = logging.getLogger(__name__)


def load_zillow_rent_data(
    spark: SparkSession,
    csv_path: str = "data/raw/zillow_zori.csv",
) -> DataFrame:
    """
    載入 Zillow ZORI CSV 並標準化 Zip code 格式。

    處理流程：
    1. 讀取 CSV（寬表格式）
    2. 識別最近期的日期欄位，取其租金值
    3. 標準化 Zip code 為 5 位字串（補前導零，如 01234）
    4. 過濾無效資料（null 或 <= 0 的租金）

    Args:
        spark: PySpark Session
        csv_path: Zillow ZORI CSV 路徑

    Returns:
        標準化後的租金 DataFrame，包含：
        - zip_code: 5 位 Zip code 字串
        - state_name: 州名
        - rent_index: 最近期的月租金指數 (美元)
    """
    logger.info(f"正在載入 Zillow ZORI 資料: {csv_path}")

    df_raw = spark.read.csv(csv_path, header=True, inferSchema=True)
    total_count = df_raw.count()
    logger.info(f"原始 Zip code 區域數: {total_count:,}")
    logger.info(f"欄位總數: {len(df_raw.columns)}")

    # --- 識別最近期的租金欄位 ---
    # ZORI CSV 的日期欄位格式為 "YYYY-MM-DD"
    date_columns = [
        col for col in df_raw.columns
        if len(col) == 10 and col[4:5] == "-" and col[7:8] == "-"
    ]

    if not date_columns:
        raise ValueError(
            "在 Zillow CSV 中找不到日期格式 (YYYY-MM-DD) 的欄位。\n"
            f"前 10 個欄位: {df_raw.columns[:10]}"
        )

    # 排序取最新日期
    date_columns.sort()
    latest_col = date_columns[-1]
    logger.info(f"日期欄位範圍: {date_columns[0]} ~ {latest_col}")
    logger.info(f"使用最近期租金資料: {latest_col}")

    # --- 標準化 Zip code ---
    # Zip code 應為 5 位字串。美國東北部 Zip code 以 0 開頭 (如 01234)，
    # 讀入 CSV 時可能被當作整數 1234，需要補前導零。
    df_rent = df_raw.select(
        F.lpad(F.col("RegionName").cast(StringType()), 5, "0").alias("zip_code"),
        F.col("StateName").alias("state_name"),
        F.col(f"`{latest_col}`").cast("double").alias("rent_index"),
    )

    # --- 過濾無效資料 ---
    df_valid = df_rent.filter(
        F.col("zip_code").isNotNull()
        & F.col("rent_index").isNotNull()
        & (F.col("rent_index") > 0)
    )
    valid_count = df_valid.count()
    dropped = total_count - valid_count
    if dropped > 0:
        logger.warning(f"過濾掉 {dropped:,} 筆無效租金記錄")
    logger.info(f"有效租金資料筆數: {valid_count:,}")

    # 顯示租金統計
    rent_stats = df_valid.agg(
        F.min("rent_index").alias("最低"),
        F.round(F.avg("rent_index"), 0).alias("平均"),
        F.max("rent_index").alias("最高"),
    ).collect()[0]
    logger.info(
        f"租金統計 (USD/月): 最低=${rent_stats['最低']:,.0f}, "
        f"平均=${rent_stats['平均']:,.0f}, 最高=${rent_stats['最高']:,.0f}"
    )

    return df_valid
