"""
Task 3.4: 匯出最終結果

將計算完成的 H3 Void Score 資料匯出為 CSV 檔案，
供後續 Kepler.gl 視覺化使用。

使用 Pandas 匯出單一 CSV 檔案（而非 PySpark 預設的多個 part 檔案），
方便後續工具直接讀取。
"""

import os
import logging
from pyspark.sql import DataFrame

logger = logging.getLogger(__name__)


def export_to_csv(
    df: DataFrame,
    output_path: str = "data/processed/h3_void_scores.csv",
) -> str:
    """
    將 DataFrame 匯出為單一 CSV 檔案。

    匯出欄位（按 void_score 降序排列）：
    - h3_index, cuisine_type
    - competitor_count, avg_rating, total_reviews
    - rent_index, void_score
    - latitude, longitude, dominant_zip

    Args:
        df: 最終的 Void Score DataFrame
        output_path: CSV 輸出路徑

    Returns:
        最終 CSV 檔案路徑
    """
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    # 選取最終需要的欄位並排序
    df_export = df.select(
        "h3_index",
        "cuisine_type",
        "competitor_count",
        "avg_rating",
        "total_reviews",
        "rent_index",
        "void_score",
        "latitude",
        "longitude",
        "dominant_zip",
    ).orderBy("void_score", ascending=False)

    total_rows = df_export.count()
    logger.info(f"準備匯出 {total_rows:,} 筆資料至: {output_path}")

    # 使用 Pandas 匯出為單一 CSV
    # 聚合後的資料量通常可容納於記憶體（數萬~數十萬行）
    df_pandas = df_export.toPandas()
    df_pandas.to_csv(output_path, index=False, encoding="utf-8")

    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    logger.info(f"匯出完成！檔案大小: {file_size_mb:.2f} MB")

    # 顯示 Top 5 高 Void Score 區域
    logger.info("Top 5 高 Void Score 區域 (最佳投資機會):")
    logger.info(f"\n{df_pandas.head(5).to_string()}")

    return output_path
