"""
Task 1.2: Yelp Open Dataset 解壓腳本

商業邏輯：
  Yelp 開放資料集以 tar 壓縮檔形式提供，包含多個 JSON 檔案。
  本專案僅需 business JSON 檔案，其中包含餐廳的位置、評分、
  類別等關鍵資訊，作為「供給」維度的資料來源。
"""

import os
import tarfile
import logging

logger = logging.getLogger(__name__)

# 需要從 tar 中提取的檔案
TARGET_FILE = "yelp_academic_dataset_business.json"


def extract_yelp_business_json(
    tar_path: str = "data/raw/Yelp-JSON/Yelp JSON/yelp_dataset.tar",
    output_dir: str = "data/raw",
) -> str:
    """
    從 Yelp tar 壓縮檔中提取 business JSON 檔案。

    僅提取 yelp_academic_dataset_business.json 以節省時間和磁碟空間
    （完整 tar 包含約 4.3 GB 的資料，但 business JSON 約 120 MB）。

    Args:
        tar_path: tar 檔案路徑
        output_dir: 解壓輸出目錄

    Returns:
        解壓後的 JSON 檔案路徑

    Raises:
        FileNotFoundError: tar 檔案不存在
        tarfile.TarError: 解壓縮失敗
    """
    output_path = os.path.join(output_dir, TARGET_FILE)

    # 若已解壓過，跳過
    if os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(
            f"Yelp business JSON 已存在: {output_path} ({size_mb:.1f} MB)，跳過解壓。"
        )
        return output_path

    # 檢查 tar 檔案是否存在
    if not os.path.exists(tar_path):
        raise FileNotFoundError(
            f"找不到 Yelp tar 檔案: {tar_path}\n"
            f"請從 https://www.yelp.com/dataset 下載並放置於此路徑。"
        )

    os.makedirs(output_dir, exist_ok=True)
    tar_size_gb = os.path.getsize(tar_path) / (1024 ** 3)
    logger.info(f"正在從 tar ({tar_size_gb:.1f} GB) 中提取 {TARGET_FILE}...")

    try:
        with tarfile.open(tar_path, "r") as tar:
            # 搜尋目標檔案（tar 內可能有路徑前綴）
            members = tar.getmembers()
            target_member = None

            for member in members:
                basename = os.path.basename(member.name)
                if basename == TARGET_FILE:
                    target_member = member
                    break

            if target_member is None:
                available = [m.name for m in members if m.isfile()]
                raise FileNotFoundError(
                    f"在 tar 中找不到 {TARGET_FILE}。\n"
                    f"可用的檔案: {available}"
                )

            size_mb = target_member.size / (1024 * 1024)
            logger.info(f"找到目標檔案: {target_member.name} ({size_mb:.1f} MB)")

            # 以串流方式提取（避免一次載入整個檔案到記憶體）
            file_obj = tar.extractfile(target_member)
            if file_obj is None:
                raise tarfile.TarError(f"無法從 tar 中讀取 {target_member.name}")

            written = 0
            with open(output_path, "wb") as out_f:
                while True:
                    chunk = file_obj.read(1024 * 1024)  # 1 MB chunks
                    if not chunk:
                        break
                    out_f.write(chunk)
                    written += len(chunk)
                    pct = (written / target_member.size) * 100
                    if written % (10 * 1024 * 1024) == 0:  # 每 10 MB 報告一次
                        logger.info(f"解壓進度: {pct:.1f}%")

        final_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"解壓完成！儲存至: {output_path} ({final_size_mb:.1f} MB)")
        return output_path

    except tarfile.TarError as e:
        logger.error(f"解壓 Yelp tar 失敗: {e}")
        # 清理不完整的檔案
        if os.path.exists(output_path):
            os.remove(output_path)
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    extract_yelp_business_json()
