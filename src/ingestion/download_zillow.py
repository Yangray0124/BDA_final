"""
Task 1.1: Zillow Observed Rent Index (ZORI) 自動下載腳本

商業邏輯：
  ZORI 提供每個 Zip code 的月租金中位數估計值，
  作為 Void Score 中「成本」維度的核心資料來源。
  較低的租金成本意味著進入門檻較低，有利於新餐廳開設。
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)

# Zillow Research 公開 CSV 下載連結
ZILLOW_ZORI_URL = (
    "https://files.zillowstatic.com/research/public_csvs/"
    "zori/Zip_zori_uc_sfrcondomfr_sm_month.csv"
)


def download_zillow_rent_data(
    output_dir: str = "data/raw",
    filename: str = "zillow_zori.csv",
    url: str = ZILLOW_ZORI_URL,
) -> str:
    """
    從 Zillow Research 下載 ZORI 租金指數 CSV。

    Args:
        output_dir: 輸出目錄路徑
        filename: 儲存的檔名
        url: 下載 URL

    Returns:
        儲存的完整檔案路徑

    Raises:
        requests.HTTPError: 下載失敗時
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    # 若檔案已存在，跳過下載
    if os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"Zillow ZORI 檔案已存在: {output_path} ({size_mb:.1f} MB)，跳過下載。")
        return output_path

    logger.info("正在從 Zillow Research 下載 ZORI 資料...")
    logger.info(f"URL: {url}")

    try:
        response = requests.get(url, stream=True, timeout=120)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0 and downloaded % (1024 * 1024) == 0:
                    pct = (downloaded / total_size) * 100
                    logger.info(f"下載進度: {pct:.1f}%")

        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"下載完成！儲存至: {output_path} ({file_size_mb:.1f} MB)")
        return output_path

    except requests.exceptions.RequestException as e:
        logger.error(f"下載 Zillow ZORI 失敗: {e}")
        # 清理不完整的檔案
        if os.path.exists(output_path):
            os.remove(output_path)
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    download_zillow_rent_data()
