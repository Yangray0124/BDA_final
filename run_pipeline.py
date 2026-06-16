"""
Spatial BI - Restaurant Void Analysis Platform
主管線執行腳本

串接所有階段的處理流程：
  Phase 1: Ingestion  (資料擷取 — 下載 Zillow CSV + 解壓 Yelp tar)
  Phase 2: Processing (PySpark 處理 + H3 空間映射)
  Phase 3: Aggregation(Void Score 計算)
  Phase 4: Visualization (Kepler.gl 3D 地圖生成)

使用方式：
  # 執行完整管線
  python run_pipeline.py

  # 從 Phase 2 開始（略過資料下載/解壓）
  python run_pipeline.py --start-phase 2

  # 只執行 Phase 3 和 Phase 4
  python run_pipeline.py --start-phase 3 --end-phase 4
"""

import os
import sys
import time
import logging
import argparse

# 設定專案根目錄
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# 配置 logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("pipeline")


def run_phase1():
    """
    Phase 1: 資料擷取
    - Task 1.1: 下載 Zillow ZORI CSV
    - Task 1.2: 從 tar 解壓 Yelp business JSON
    """
    logger.info("=" * 60)
    logger.info("Phase 1: Ingestion — 資料擷取")
    logger.info("=" * 60)

    from src.ingestion.download_zillow import download_zillow_rent_data
    from src.ingestion.extract_yelp import extract_yelp_business_json

    # Task 1.1: 下載 Zillow 租金資料
    zillow_path = download_zillow_rent_data(
        output_dir=os.path.join(PROJECT_ROOT, "data", "raw")
    )

    # Task 1.2: 解壓 Yelp business JSON
    yelp_path = extract_yelp_business_json(
        tar_path=os.path.join(
            PROJECT_ROOT, "data", "raw", "Yelp-JSON", "Yelp JSON", "yelp_dataset.tar"
        ),
        output_dir=os.path.join(PROJECT_ROOT, "data", "raw"),
    )

    return yelp_path, zillow_path


def run_phase2(yelp_path, zillow_path):
    """
    Phase 2: PySpark 處理 & H3 映射
    - Task 2.1: 初始化 PySpark + 載入/過濾 Yelp 餐廳
    - Task 2.2: 載入/標準化 Zillow 租金
    - Task 2.3: H3 空間索引映射
    """
    logger.info("=" * 60)
    logger.info("Phase 2: Processing — PySpark 處理 & H3 映射")
    logger.info("=" * 60)

    from src.processing.spark_session import get_spark_session
    from src.processing.load_yelp import load_yelp_restaurants
    from src.processing.load_zillow import load_zillow_rent_data
    from src.processing.h3_mapping import add_h3_index

    # Task 2.1: 初始化 PySpark & 載入 Yelp 餐廳
    spark = get_spark_session()
    df_restaurants = load_yelp_restaurants(spark, yelp_path)

    # Task 2.2: 載入 Zillow 租金
    df_rent = load_zillow_rent_data(spark, zillow_path)

    # Task 2.3: H3 空間索引映射
    df_h3 = add_h3_index(df_restaurants)

    return spark, df_h3, df_rent


def run_phase3(df_h3, df_rent):
    """
    Phase 3: Void Score 彙總計算
    - Task 3.1: 料理類型提取 + H3 聚合
    - Task 3.2: Join 租金資料
    - Task 3.3: 計算 Void Score
    - Task 3.4: 匯出 CSV
    """
    logger.info("=" * 60)
    logger.info("Phase 3: Aggregation — Void Score 計算")
    logger.info("=" * 60)

    from src.aggregation.aggregate_h3 import aggregate_by_h3, extract_primary_cuisine
    from src.aggregation.join_rent import join_with_rent
    from src.aggregation.void_score import calculate_void_score
    from src.aggregation.export import export_to_csv

    # Task 3.1: 提取料理類型 & H3 聚合
    df_cuisine = extract_primary_cuisine(df_h3)
    df_agg = aggregate_by_h3(df_cuisine)

    # Task 3.2: Join 租金資料
    df_joined = join_with_rent(df_agg, df_rent)

    # Task 3.3: 計算 Void Score
    df_scored = calculate_void_score(df_joined)

    # Task 3.4: 匯出 CSV
    output_path = export_to_csv(
        df_scored,
        output_path=os.path.join(
            PROJECT_ROOT, "data", "processed", "h3_void_scores.csv"
        ),
    )

    return output_path


def run_phase4(csv_path):
    """
    Phase 4: 3D 視覺化
    - Task 4.1 & 4.2: Kepler.gl 3D 六角形地圖
    """
    logger.info("=" * 60)
    logger.info("Phase 4: Visualization — 3D 地圖生成")
    logger.info("=" * 60)

    from src.visualization.kepler_map import generate_kepler_map

    html_path = generate_kepler_map(
        csv_path=csv_path,
        output_html=os.path.join(
            PROJECT_ROOT, "data", "processed", "void_analysis_map.html"
        ),
    )

    return html_path


def main():
    parser = argparse.ArgumentParser(
        description="Spatial BI - Restaurant Void Analysis Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  python run_pipeline.py                        # 執行完整管線 (Phase 1-4)
  python run_pipeline.py --start-phase 2        # 從 Phase 2 開始 (略過下載)
  python run_pipeline.py --start-phase 3 --end-phase 3  # 只執行 Phase 3
  python run_pipeline.py --start-phase 4        # 只執行視覺化
        """,
    )
    parser.add_argument(
        "--start-phase",
        type=int,
        default=1,
        choices=[1, 2, 3, 4],
        help="從指定階段開始執行 (預設: 1)",
    )
    parser.add_argument(
        "--end-phase",
        type=int,
        default=4,
        choices=[1, 2, 3, 4],
        help="執行到指定階段停止 (預設: 4)",
    )
    args = parser.parse_args()

    if args.start_phase > args.end_phase:
        logger.error("start-phase 不能大於 end-phase")
        sys.exit(1)

    start_time = time.time()
    logger.info("🚀 Spatial BI - Restaurant Void Analysis Pipeline 啟動")
    logger.info(f"   執行範圍: Phase {args.start_phase} → Phase {args.end_phase}")
    logger.info(f"   專案根目錄: {PROJECT_ROOT}")

    try:
        # 預設路徑（用於跳過前面階段時）
        yelp_path = os.path.join(
            PROJECT_ROOT, "data", "raw", "yelp_academic_dataset_business.json"
        )
        zillow_path = os.path.join(
            PROJECT_ROOT, "data", "raw", "zillow_zori.csv"
        )
        csv_path = os.path.join(
            PROJECT_ROOT, "data", "processed", "h3_void_scores.csv"
        )

        spark = None
        df_h3 = None
        df_rent = None

        # --- Phase 1 ---
        if args.start_phase <= 1 <= args.end_phase:
            phase_start = time.time()
            yelp_path, zillow_path = run_phase1()
            logger.info(f"Phase 1 完成，耗時: {time.time() - phase_start:.1f} 秒\n")

        # --- Phase 2 ---
        if args.start_phase <= 2 <= args.end_phase:
            phase_start = time.time()
            spark, df_h3, df_rent = run_phase2(yelp_path, zillow_path)
            logger.info(f"Phase 2 完成，耗時: {time.time() - phase_start:.1f} 秒\n")

        # --- Phase 3 ---
        if args.start_phase <= 3 <= args.end_phase:
            if df_h3 is None or df_rent is None:
                logger.error(
                    "Phase 3 需要 Phase 2 的輸出 (df_h3, df_rent)。"
                    "請從 Phase 2 開始執行，或確保已有處理結果。"
                )
                sys.exit(1)
            phase_start = time.time()
            csv_path = run_phase3(df_h3, df_rent)
            logger.info(f"Phase 3 完成，耗時: {time.time() - phase_start:.1f} 秒\n")

        # --- Phase 4 ---
        if args.start_phase <= 4 <= args.end_phase:
            if not os.path.exists(csv_path):
                logger.error(
                    f"找不到 Void Score CSV: {csv_path}。"
                    "請先執行 Phase 3 生成此檔案。"
                )
                sys.exit(1)
            phase_start = time.time()
            html_path = run_phase4(csv_path)
            logger.info(f"Phase 4 完成，耗時: {time.time() - phase_start:.1f} 秒\n")

        # --- 清理 ---
        if spark:
            spark.stop()
            logger.info("PySpark Session 已關閉")

        elapsed = time.time() - start_time
        logger.info("=" * 60)
        logger.info(f"✅ Pipeline 執行完成！總耗時: {elapsed:.1f} 秒")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Pipeline 執行失敗: {e}", exc_info=True)
        if spark:
            spark.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
