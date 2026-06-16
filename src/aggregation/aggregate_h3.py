"""
Task 3.1: H3 六角形聚合計算

商業邏輯：
  按 H3 六角形區域聚合餐廳資料，計算每個六角形內的競爭指標：

  - Competitor_Count (競爭者數量)：
    該區域內同類餐廳的數量。數量越多代表市場越飽和，
    新進入者面臨的競爭壓力越大。

  - Avg_Rating (平均評分)：
    區域內競爭者的平均星級評分。高評分意味著既有業者品質高，
    新進入者需要更高水準才能競爭。

  - Total_Reviews (總評論數)：
    作為該區域「需求」的代理指標。評論越多通常代表
    消費者流量越大，市場需求越旺盛。
"""

import logging
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

logger = logging.getLogger(__name__)


def extract_primary_cuisine(df: DataFrame) -> DataFrame:
    """
    從 categories 欄位提取主要料理類型。

    Yelp categories 格式: "Restaurants, Burgers, Fast Food"
    策略：取第一個非 "Restaurants" 且非 "Food" 的類別作為主要料理。
    若全為通用類別，標記為 "General"。

    Args:
        df: 包含 categories 欄位的 DataFrame

    Returns:
        新增 cuisine_type 欄位的 DataFrame
    """
    logger.info("正在提取主要料理類型...")

    # 分割 categories 字串，取第一個具體料理類別
    df_cuisine = df.withColumn(
        "categories_array",
        F.split(F.col("categories"), ", ")
    ).withColumn(
        "cuisine_type",
        F.expr("""
            CASE
                WHEN size(filter(categories_array,
                    x -> x != 'Restaurants' AND x != 'Food')) > 0
                THEN filter(categories_array,
                    x -> x != 'Restaurants' AND x != 'Food')[0]
                ELSE 'General'
            END
        """)
    ).drop("categories_array")

    # 顯示料理類型分布 (Top 10)
    logger.info("料理類型分布 (Top 10):")
    df_cuisine.groupBy("cuisine_type").count().orderBy(
        F.desc("count")
    ).show(10, truncate=False)

    return df_cuisine


def aggregate_by_h3(df: DataFrame) -> DataFrame:
    """
    按 H3 索引與料理類型進行空間聚合。

    每個 (H3 六角形, 料理類型) 組合計算以下指標：
    - competitor_count: 該區域內同類餐廳數量
    - avg_rating: 平均星級評分
    - total_reviews: 總評論數 (需求代理)
    - dominant_zip: 最常見的 Zip code (用於 Join 租金)
    - latitude/longitude: 六角形中心座標 (視覺化用)

    Args:
        df: 包含 h3_index 和 cuisine_type 的 DataFrame

    Returns:
        聚合後的 DataFrame
    """
    logger.info("正在按 H3 六角形進行空間聚合...")

    df_agg = df.groupBy("h3_index", "cuisine_type").agg(
        # 競爭者數量：該六角形內同類餐廳的總數
        F.count("business_id").alias("competitor_count"),

        # 平均評分：競爭者的服務品質指標
        F.round(F.avg("stars"), 2).alias("avg_rating"),

        # 總評論數：區域需求的代理指標
        F.sum("review_count").alias("total_reviews"),

        # 該六角形中最常見的 Zip code，用於後續與租金資料 Join
        F.first("postal_code").alias("dominant_zip"),

        # 保留代表性的經緯度（六角形內餐廳的平均位置）
        F.round(F.avg("latitude"), 6).alias("latitude"),
        F.round(F.avg("longitude"), 6).alias("longitude"),
    )

    agg_count = df_agg.count()
    logger.info(f"聚合完成，共 {agg_count:,} 個 (H3, cuisine) 組合")

    # 顯示聚合統計
    stats = df_agg.agg(
        F.round(F.avg("competitor_count"), 1).alias("avg_competitors"),
        F.max("competitor_count").alias("max_competitors"),
        F.round(F.avg("avg_rating"), 2).alias("overall_avg_rating"),
    ).collect()[0]
    logger.info(
        f"聚合統計: 平均競爭者={stats['avg_competitors']}, "
        f"最大競爭者={stats['max_competitors']}, "
        f"整體平均評分={stats['overall_avg_rating']}"
    )

    return df_agg
