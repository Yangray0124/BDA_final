"""
Task 3.2: H3 聚合資料與租金資料 Join

商業邏輯：
  將空間聚合後的餐廳競爭指標與 Zillow 租金指數結合。

  映射邏輯：每個 H3 六角形包含的餐廳通常位於同一個或相鄰的
  Zip code 區域。我們使用該六角形中最常見的 Zip code (dominant_zip)
  作為代表，與 Zillow 租金資料進行 Left Join。

  注意：此為近似映射。H3 六角形與 Zip code 邊界不完全對齊，
  但在社區等級的分析中，此近似已足夠準確。未匹配的記錄將以
  中位數租金填充，避免下游計算出錯。
"""

import logging
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

logger = logging.getLogger(__name__)


def join_with_rent(
    df_h3: DataFrame,
    df_rent: DataFrame,
) -> DataFrame:
    """
    將 H3 聚合資料與 Zillow 租金指數 Join。

    使用 dominant_zip (六角形中最常見的 Zip code) 作為 Join key。
    採用 Left Join 保留所有 H3 記錄，未匹配的租金以中位數填充。

    Args:
        df_h3: H3 聚合後的 DataFrame (包含 dominant_zip 欄位)
        df_rent: Zillow 租金 DataFrame (包含 zip_code 欄位)

    Returns:
        Join 後的 DataFrame，新增 rent_index 欄位
    """
    logger.info("正在將 H3 聚合資料與租金資料 Join...")

    # 標準化 Zip code 格式以確保匹配
    # Yelp postal_code 可能包含非標準格式（如加拿大郵遞區號）
    df_h3_std = df_h3.withColumn(
        "zip_for_join",
        F.lpad(F.col("dominant_zip").cast(StringType()), 5, "0")
    )

    # Left Join：保留所有 H3 記錄，即使沒有對應的租金資料
    df_joined = df_h3_std.join(
        df_rent,
        df_h3_std["zip_for_join"] == df_rent["zip_code"],
        "left"
    ).drop("zip_for_join", "zip_code", "state_name")

    # 統計匹配率
    total = df_joined.count()
    matched = df_joined.filter(F.col("rent_index").isNotNull()).count()
    match_rate = (matched / total * 100) if total > 0 else 0
    logger.info(f"租金資料匹配率: {matched:,}/{total:,} ({match_rate:.1f}%)")

    if match_rate < 50:
        logger.warning(
            f"租金匹配率偏低 ({match_rate:.1f}%)。"
            "可能原因：Zip code 格式不一致、Zillow 未覆蓋該地區、"
            "或 Yelp 資料含有非美國商家。"
        )

    # 對未匹配的記錄填入中位數租金（避免 Void Score 計算出錯）
    median_rent = df_joined.filter(
        F.col("rent_index").isNotNull()
    ).approxQuantile("rent_index", [0.5], 0.01)

    if median_rent:
        fill_value = median_rent[0]
        df_filled = df_joined.fillna({"rent_index": fill_value})
        logger.info(f"未匹配記錄以中位數租金填入: ${fill_value:,.0f}/月")
    else:
        df_filled = df_joined
        logger.warning("無法計算中位數租金，未匹配記錄保留 null。")

    return df_filled
