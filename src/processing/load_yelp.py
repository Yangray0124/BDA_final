"""
Task 2.1: 載入 Yelp 餐廳資料

商業邏輯：
  Yelp 開放資料集包含各類商家資訊。本模組負責：
  1. 載入完整的 business JSON 資料集
  2. 過濾出「餐廳」類別的商家（categories 中包含 "Restaurants"）
  3. 移除缺少經緯度座標的記錄（無法進行空間分析）

  這些餐廳資料代表「供給面」——即某區域內已有的競爭者數量與品質。
"""

import logging
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F

logger = logging.getLogger(__name__)


def load_yelp_restaurants(
    spark: SparkSession,
    json_path: str = "data/raw/yelp_academic_dataset_business.json",
) -> DataFrame:
    """
    載入 Yelp business JSON 並過濾出有效的餐廳資料。

    處理流程：
    1. 讀取 JSON（每行一筆記錄的 JSON Lines 格式）
    2. 過濾 categories 欄位包含 "Restaurants" 的記錄
    3. 移除 latitude 或 longitude 為 null / 0 的記錄
    4. 選取分析所需的關鍵欄位

    Args:
        spark: PySpark Session
        json_path: Yelp business JSON 檔案路徑

    Returns:
        過濾後的餐廳 DataFrame，包含以下欄位：
        - business_id, name, latitude, longitude
        - stars, review_count, categories, postal_code
        - city, state
    """
    logger.info(f"正在載入 Yelp 資料集: {json_path}")

    # Yelp JSON 使用每行一筆記錄的格式 (JSON Lines)
    df_raw = spark.read.json(json_path)
    total_count = df_raw.count()
    logger.info(f"原始商家資料筆數: {total_count:,}")

    # --- 過濾餐廳類別 ---
    # categories 欄位格式為逗號分隔字串，例如: "Restaurants, Burgers, Fast Food"
    # 使用 contains 篩選包含 "Restaurants" 關鍵字的商家
    df_restaurants = df_raw.filter(
        F.col("categories").isNotNull()
        & F.col("categories").contains("Restaurants")
    )
    restaurant_count = df_restaurants.count()
    logger.info(
        f"過濾後餐廳筆數: {restaurant_count:,} "
        f"(佔全部 {restaurant_count / total_count * 100:.1f}%)"
    )

    # --- 移除缺失座標 ---
    # 沒有經緯度的記錄無法進行 H3 空間索引，必須剔除
    df_valid = df_restaurants.filter(
        F.col("latitude").isNotNull()
        & F.col("longitude").isNotNull()
        & (F.col("latitude") != 0)
        & (F.col("longitude") != 0)
    )
    valid_count = df_valid.count()
    dropped = restaurant_count - valid_count
    if dropped > 0:
        logger.warning(f"移除 {dropped:,} 筆缺失/無效座標的記錄")
    logger.info(f"有效餐廳筆數: {valid_count:,}")

    # --- 選取關鍵欄位 ---
    df_selected = df_valid.select(
        "business_id",
        "name",
        "latitude",
        "longitude",
        "stars",
        "review_count",
        "categories",
        "postal_code",
        "city",
        "state",
    )

    # 顯示範例資料
    logger.info("前 3 筆範例資料:")
    df_selected.show(3, truncate=50)

    return df_selected
