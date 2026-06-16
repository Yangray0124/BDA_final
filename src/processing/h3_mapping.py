"""
Task 2.3: H3 地理空間索引映射 (Geospatial Core)

商業邏輯：
  Uber H3 是一種六角形階層空間索引系統，將地球表面劃分為
  均勻的六角形網格。Resolution 8 的六角形邊長約 460 公尺，
  面積約 0.74 km²，適合用於社區等級的餐廳競爭分析。

  透過 H3 索引，我們可以將任意經緯度座標歸入特定的六角形區域，
  實現精確的空間聚合與視覺化。

  相較於傳統的矩形網格，六角形具有以下優勢：
  - 每個六角形到所有鄰居的距離相等（減少邊緣效應）
  - 更接近圓形的覆蓋效率
  - 天然的多解析度層級結構
"""

import logging
import h3
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

logger = logging.getLogger(__name__)

# H3 Resolution 8: 邊長 ~461m, 面積 ~0.737 km²
# 適合社區等級分析，一個六角形大約覆蓋幾個街區
H3_RESOLUTION = 8


def _lat_lng_to_h3(lat: float, lng: float) -> str:
    """
    將經緯度轉換為 H3 六角形索引。

    支援 h3-py v4 (latlng_to_cell) 與 v3 (geo_to_h3) API，
    以相容不同版本的套件安裝環境。

    Args:
        lat: 緯度
        lng: 經度

    Returns:
        H3 索引字串，例如 "882a100d63fffff"
    """
    if lat is None or lng is None:
        return None
    try:
        # h3-py v4 API
        return h3.latlng_to_cell(lat, lng, H3_RESOLUTION)
    except AttributeError:
        # h3-py v3 fallback
        return h3.geo_to_h3(lat, lng, H3_RESOLUTION)


def add_h3_index(df: DataFrame) -> DataFrame:
    """
    為 DataFrame 中的每筆記錄新增 H3 六角形索引欄位。

    使用 PySpark UDF 將 latitude/longitude 轉換為 H3 index，
    以便後續按六角形區域進行空間聚合分析。

    Args:
        df: 包含 latitude 和 longitude 欄位的 DataFrame

    Returns:
        新增 h3_index 欄位的 DataFrame
    """
    row_count = df.count()
    logger.info(f"正在為 {row_count:,} 筆記錄建立 H3 索引 (resolution={H3_RESOLUTION})...")

    # 註冊為 PySpark UDF
    h3_udf = F.udf(_lat_lng_to_h3, StringType())

    df_with_h3 = df.withColumn(
        "h3_index",
        h3_udf(F.col("latitude"), F.col("longitude"))
    )

    # 過濾 H3 轉換失敗的記錄（例如非法座標）
    df_valid = df_with_h3.filter(F.col("h3_index").isNotNull())
    valid_count = df_valid.count()
    failed = row_count - valid_count
    if failed > 0:
        logger.warning(f"H3 轉換失敗: {failed:,} 筆記錄")
    logger.info(f"H3 映射完成，有效記錄: {valid_count:,}")

    # 統計涵蓋的唯一 H3 六角形數量
    hex_count = df_valid.select("h3_index").distinct().count()
    logger.info(f"涵蓋唯一 H3 六角形數量: {hex_count:,}")

    return df_valid
