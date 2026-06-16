"""
Task 2.1: PySpark Session 初始化模組

配置本地 Spark 環境，用於分散式處理 GB 級的 Yelp JSON 資料集。
使用 local[2] 模式以避免 Windows 上的 worker 連線逾時問題。
"""

import os
import sys
import logging
from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)


def get_spark_session(
    app_name: str = "VoidAnalysis",
    driver_memory: str = "4g",
) -> SparkSession:
    """
    初始化並返回本地 PySpark Session。

    配置說明：
    - local[2]: 使用 2 個核心（避免 Windows 上 worker 過多導致連線逾時）
    - PYSPARK_PYTHON: 明確指定 Python 路徑，避免 worker 找不到 Python
    - python.worker.timeout: 延長至 300 秒，防止大資料集處理時逾時
    - python.worker.reuse: 啟用 worker 重用，減少反覆建立連線的開銷

    Args:
        app_name: Spark 應用程式名稱
        driver_memory: Driver 記憶體配置

    Returns:
        SparkSession 實例
    """
    logger.info(f"正在初始化 PySpark Session: {app_name}")

    # 明確設定 Python 路徑，解決 Windows 上 worker 無法連回的問題
    python_executable = sys.executable
    os.environ["PYSPARK_PYTHON"] = python_executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = python_executable
    logger.info(f"PYSPARK_PYTHON: {python_executable}")

    spark = (
        SparkSession.builder
        .appName(app_name)
        .master("local[2]")                            # 限制 2 核心，避免 Windows worker 逾時
        .config("spark.driver.memory", driver_memory)   # Driver 記憶體
        .config("spark.sql.shuffle.partitions", "4")    # 本地模式減少 partition 數
        .config("spark.ui.showConsoleProgress", "true")
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY")
        .config("spark.python.worker.timeout", "300")   # Worker 連線逾時延長至 300 秒
        .config("spark.python.worker.reuse", "true")    # 重用 Python worker
        .config("spark.driver.host", "127.0.0.1")       # 明確綁定 localhost
        .getOrCreate()
    )

    # 降低 Spark 內部日誌等級以減少噪音
    spark.sparkContext.setLogLevel("WARN")

    logger.info(f"PySpark Session 初始化完成 (version: {spark.version})")
    return spark
