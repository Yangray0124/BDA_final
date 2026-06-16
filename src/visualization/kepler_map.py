"""
Phase 4: 3D 六角形視覺化 (Deck.gl / pydeck)

商業邏輯：
  使用 pydeck (Deck.gl Python 綁定) 將 Void Score 分析結果
  以 3D 六角形地圖呈現，搭配免費 CARTO 底圖（無需 API key）。

  視覺映射：
  - 高度 (Elevation) = 租金成本
    → 越高的柱體代表該區域租金越貴
  - 顏色 (Color) = Void Score
    → 綠色 = 高 Void Score（最佳投資機會）
    → 紅色 = 低 Void Score（競爭激烈、不建議進入）
"""

import os
import logging
import numpy as np
import pandas as pd
import pydeck as pdk

logger = logging.getLogger(__name__)


def _compute_colors(df: pd.DataFrame) -> pd.DataFrame:
    """
    根據 void_score 計算每筆資料的 RGBA 顏色值。
    """
    score_min = df["void_score"].min()
    score_max = df["void_score"].max()
    score_range = score_max - score_min if score_max > score_min else 1
    normalized = (df["void_score"] - score_min) / score_range

    r = np.where(normalized < 0.5,
                 220 + (255 - 220) * (normalized / 0.5),
                 255 * (1 - (normalized - 0.5) / 0.5))
    g = np.where(normalized < 0.5,
                 50 + (200 - 50) * (normalized / 0.5),
                 200)
    b = np.where(normalized < 0.5,
                 50,
                 50 + (100 - 50) * ((normalized - 0.5) / 0.5))

    df = df.copy()
    df["color_r"] = r.astype(int).clip(0, 255)
    df["color_g"] = g.astype(int).clip(0, 255)
    df["color_b"] = b.astype(int).clip(0, 255)
    df["color_a"] = 200

    return df


def generate_kepler_map(
    csv_path: str = "data/processed/h3_void_scores.csv",
    output_html: str = "data/processed/void_analysis_map.html",
) -> str:
    """
    使用 pydeck (Deck.gl) 生成 3D 六角形視覺化地圖。
    """
    logger.info(f"正在載入資料: {csv_path}")
    df = pd.read_csv(csv_path)
    logger.info(f"載入 {len(df):,} 筆資料")

    # 計算顏色
    df = _compute_colors(df)

    # 【關鍵修正】：為了讓放大時能看到細節，縮小時能「視覺上合併」，
    # 我們不實際合併資料，而是將高度 (Elevation) 大幅拉高，並將覆蓋率 (coverage) 設為 1.0。
    # 這樣在全美視角下，相鄰的柱子會高聳且互相貼合，看起來像是一大根；
    # 放大到城市視角時，又能清楚看見一根根獨立的六角形。
    rent_max = df["rent_index"].max()
    # 將基礎高度拉高至 100,000 公尺 (100km)，確保在國家級別視角可見
    df["elevation"] = (df["rent_index"] / rent_max * 100000).fillna(0)

    # --- H3HexagonLayer ---
    h3_layer = pdk.Layer(
        "H3HexagonLayer",
        data=df,
        pickable=True,
        auto_highlight=True,                 # 滑鼠懸停時自動高亮
        highlight_color=[255, 255, 255, 255], # 高亮顏色設為純白色
        stroked=False,         # 取消邊線，讓柱子更容易視覺融合
        filled=True,
        extruded=True,
        get_hexagon="h3_index",
        get_fill_color="[color_r, color_g, color_b, color_a]",
        get_elevation="elevation",
        elevation_scale=1.5,   # 高度再放大
        coverage=1.0,          # 1.0 代表六角形之間無縫接合，縮小時容易黏在一起
        opacity=0.9,
    )

    # --- 初始視角：美國全境鳥瞰 ---
    view_state = pdk.ViewState(
        latitude=39.0,
        longitude=-95.0,
        zoom=4,
        bearing=15,
        pitch=45,
        min_zoom=2,
        max_zoom=15,
    )

    # --- Tooltip ---
    tooltip = {
        "html": """
        <div style="font-family: 'Segoe UI', sans-serif; padding: 8px; max-width: 280px;">
            <div style="font-size: 16px; font-weight: bold; margin-bottom: 6px; color: #00e676;">
                Void Score: {void_score}
            </div>
            <hr style="border-color: #444; margin: 4px 0;">
            <div style="font-size: 13px; line-height: 1.6;">
                <b>🍽️ Cuisine:</b> {cuisine_type}<br>
                <b>📍 Zip Code:</b> {dominant_zip}<br>
                <b>👥 Competitors:</b> {competitor_count}<br>
                <b>⭐ Avg Rating:</b> {avg_rating}<br>
                <b>💬 Reviews:</b> {total_reviews}<br>
                <b>💰 Rent Index:</b> ${rent_index}
            </div>
        </div>
        """,
        "style": {
            "backgroundColor": "#1a1a2e",
            "color": "#ffffff",
            "border": "1px solid #333",
            "border-radius": "8px",
        },
    }

    # --- 建立地圖 ---
    logger.info("正在建立 pydeck 3D 地圖（CARTO 免費底圖）...")
    deck = pdk.Deck(
        layers=[h3_layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_provider="carto",
        map_style=pdk.map_styles.DARK,
    )

    # --- 匯出 HTML ---
    output_dir = os.path.dirname(output_html)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    deck.to_html(output_html, open_browser=False)

    file_size_mb = os.path.getsize(output_html) / (1024 * 1024)
    logger.info(f"3D 地圖已儲存至: {output_html} ({file_size_mb:.1f} MB)")
    return output_html


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_kepler_map()
