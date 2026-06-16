import os
import numpy as np
import pandas as pd
import streamlit as st

# 專案根目錄
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "h3_void_scores.csv")

@st.cache_data
def load_void_scores():
    """
    使用 st.cache_data 載入 Void Score CSV 資料，並預先計算地圖渲染所需的顏色與高度。
    """
    if not os.path.exists(CSV_PATH):
        st.error(f"找不到資料檔案：{CSV_PATH}。請先執行後端管線 (Phase 3)。")
        st.stop()
    
    df = pd.read_csv(CSV_PATH)
    # 確保資料格式正確
    df["competitor_count"] = df["competitor_count"].fillna(0).astype(int)
    df["rent_index"] = df["rent_index"].fillna(0)
    
    # 計算顏色 (Void Score 紅 -> 黃 -> 綠)
    score_min, score_max = df["void_score"].min(), df["void_score"].max()
    score_range = score_max - score_min if score_max > score_min else 1
    norm = (df["void_score"] - score_min) / score_range
    
    df["color_r"] = np.where(norm < 0.5, 220 + (255 - 220) * (norm / 0.5), 255 * (1 - (norm - 0.5) / 0.5)).astype(int)
    df["color_g"] = np.where(norm < 0.5, 50 + (200 - 50) * (norm / 0.5), 200).astype(int)
    df["color_b"] = np.where(norm < 0.5, 50, 50 + (100 - 50) * ((norm - 0.5) / 0.5)).astype(int)
    df["color_a"] = 200
    
    # 計算高度 (Rent Index)
    rent_max = df["rent_index"].max()
    df["elevation"] = (df["rent_index"] / rent_max * 100000).fillna(0)
    
    return df

