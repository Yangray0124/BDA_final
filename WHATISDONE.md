# WHATISDONE — 已完成事項

## 專案概述
**Spatial BI - Restaurant Void Analysis Platform**
一個 Big Data 變現系統，透過 PySpark + Uber H3 空間索引分析全美餐廳競爭態勢，計算 Void Score 識別最佳投資區域，並以 3D 互動式六角形地圖呈現結果。

---

## ✅ Phase 0: 專案基礎建設
- 建立完整目錄結構：`src/`, `data/processed/`, `notebooks/`
- 建立 `requirements.txt`（pyspark, h3, pydeck, pandas, numpy, requests, keplergl）
- 建立所有 Python 套件的 `__init__.py`
- 安裝所有 Python 依賴套件
- 安裝 Microsoft OpenJDK 17（PySpark 必要的 Java 環境）

## ✅ Phase 1: Ingestion — 資料擷取
- **`src/ingestion/download_zillow.py`**：自動從 Zillow Research 下載 ZORI 租金指數 CSV，含串流下載、進度回報、已存在跳過邏輯
- **`src/ingestion/extract_yelp.py`**：從 4.0 GB 的 Yelp tar 壓縮檔中僅解壓 `yelp_academic_dataset_business.json`（113.4 MB），節省時間與磁碟空間

## ✅ Phase 2: Processing — PySpark 處理 & H3 映射
- **`src/processing/spark_session.py`**：初始化本地 PySpark Session
  - 使用 `local[2]` 避免 Windows worker 連線逾時
  - 明確設定 `PYSPARK_PYTHON` 解決 Windows 相容性問題
  - 延長 worker timeout 至 300 秒
- **`src/processing/load_yelp.py`**：載入 Yelp JSON，過濾 "Restaurants" 類別，移除缺失/無效座標
- **`src/processing/load_zillow.py`**：載入 Zillow CSV，自動偵測最新日期欄位，標準化 5 位 Zip code（補前導零）
- **`src/processing/h3_mapping.py`**：PySpark UDF 將經緯度轉為 H3 索引（resolution=8, ~0.74 km²），支援 h3-py v3/v4 API

## ✅ Phase 3: Aggregation — Void Score 計算
- **`src/aggregation/aggregate_h3.py`**：
  - 從 categories 提取主要料理類型（Pizza, Sandwiches, Mexican 等）
  - 按 (H3 Index, cuisine_type) 分組計算：competitor_count, avg_rating, total_reviews
- **`src/aggregation/join_rent.py`**：H3 聚合資料與 Zillow 租金 Left Join（匹配率 87.8%），未匹配記錄以中位數租金（$1,787/月）填充
- **`src/aggregation/void_score.py`**：Void Score 公式（百分制）：
  - 供給空白度 × 40%（競爭者越少 → 分數越高）
  - 成本效益 × 30%（租金越低 → 分數越高）
  - 需求強度 × 30%（評論越多 → 分數越高）
- **`src/aggregation/export.py`**：匯出至 `data/processed/h3_void_scores.csv`（3.41 MB, 40,529 筆）

## ✅ Phase 4: Visualization — 3D 地圖生成
- **`src/visualization/kepler_map.py`**：使用 pydeck (Deck.gl) 產生 3D 互動式六角形地圖
  - CARTO 免費暗色底圖（不需要 Mapbox API key）
  - 高度 = 租金成本（越高越貴）
  - 顏色 = Void Score（🟢 綠色=好機會, 🟡 黃色=中等, 🔴 紅色=高競爭）
  - 懸停 Tooltip 顯示料理類型、競爭者數、評分、租金、Void Score
- 輸出：`data/processed/void_analysis_map.html`（20.6 MB）

## ✅ Pipeline 串接
- **`run_pipeline.py`**：主管線腳本，串接 Phase 1-4，支援 CLI 參數選擇執行階段
  - `python run_pipeline.py` — 執行完整管線
  - `python run_pipeline.py --start-phase 2` — 從 Phase 2 開始
  - `python run_pipeline.py --start-phase 4` — 只重新產生地圖

---

## 📊 執行結果摘要

| 指標 | 數值 |
|------|------|
| Pipeline 總耗時 | 84.3 秒 |
| H3/cuisine 組合數 | 40,529 |
| 租金匹配率 | 87.8% |
| Void Score 範圍 | 19.5 ~ 77.2 |
| 輸出 CSV | 3.41 MB |
| 輸出地圖 HTML | 20.6 MB |

### Top 5 最佳投資機會區域

| 地區 | 料理類型 | 競爭者 | 評分 | 租金 | Void Score |
|------|---------|--------|------|------|-----------|
| New Orleans (70130) | Live/Raw Food | 1 | 4.0 | $1,748 | 77.2 |
| Philadelphia (19107) | Candy Stores | 1 | 4.5 | $2,018 | 74.4 |
| New Orleans (70130) | German | 1 | 4.0 | $1,748 | 73.6 |
| St. Louis (63103) | Caterers | 1 | 4.5 | $1,503 | 73.4 |
| New Orleans (70130) | Shopping | 1 | 4.5 | $1,748 | 72.7 |

### 料理類型分布 (Top 10)

| 料理類型 | 餐廳數量 |
|---------|---------|
| Pizza | 3,605 |
| Sandwiches | 2,597 |
| Mexican | 2,442 |
| American (Traditional) | 2,391 |
| Fast Food | 2,207 |
| Chinese | 2,022 |
| American (New) | 1,885 |
| Italian | 1,807 |
| Burgers | 1,773 |
| Breakfast & Brunch | 1,701 |
