import streamlit as st
import pydeck as pdk
from utils.data_loader import load_void_scores

# 設定頁面資訊
st.set_page_config(
    page_title="Spatial BI - Void Analysis",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded" # 預設展開側邊欄，確保使用者能看到導航
)

from utils.style import inject_global_style, inject_home_style, inject_sidebar_footer

# 注入樣式與底部版權
inject_global_style()
inject_home_style()
inject_sidebar_footer()

st.markdown("""
<div class="hero-wrapper">
    <div class="hero-title">Find Your <span class="highlight-text">Blue Ocean</span>.</div>
    <div class="hero-subtitle">
        Stop burning money on the wrong locations. Spatial BI combines Yelp competitor data and Zillow rent indices with <b>Uber H3 Spatial Indexing</b> to pinpoint high-demand, low-competition, and low-cost commercial real estate.
    </div>
    <a href="#explore-the-map" class="scroll-btn">
        <div style="transform: rotate(90deg); display: inline-block; font-weight: 400; letter-spacing: -2px;">❯❯</div>
    </a>
</div>

<div id="explore-the-map" style="position: absolute; margin-top: -100px;"></div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="intro-section">
    <h2 style="font-weight: 700; margin-bottom: 1rem; color: #ffffff; text-shadow: 0 2px 8px rgba(0,0,0,0.8);">Interactive Void Map</h2>
    <p style="color: #ffffff; font-size: 1.2rem; font-weight: 600; text-shadow: 0 2px 8px rgba(0,0,0,0.9);">
        Explore the restaurant market saturation across the US. <br>
        <b>Height</b> represents the rent index, and <b>Color</b> represents our proprietary Void Score.
    </p>
    
<!-- 顏色光譜圖例 -->
<div style="display: inline-flex; align-items: center; justify-content: center; margin-top: 1rem; gap: 15px; background: rgba(0,0,0,0.5); padding: 10px 25px; border-radius: 50px; border: 1px solid rgba(255,255,255,0.15); box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
<span style="color: #ef4444; font-weight: 700; text-shadow: 0 1px 5px rgba(0,0,0,0.8); font-size: 0.95rem;">Bad (Saturated)</span>
<div style="width: 250px; height: 12px; border-radius: 6px; background: linear-gradient(to right, rgb(220,50,50), rgb(255,200,50), rgb(0,200,100)); box-shadow: inset 0 1px 4px rgba(0,0,0,0.6);"></div>
<span style="color: #10b981; font-weight: 700; text-shadow: 0 1px 5px rgba(0,0,0,0.8); font-size: 0.95rem;">Good (Blue Ocean)</span>
</div>
</div>
""", unsafe_allow_html=True)

# 載入快取資料
df = load_void_scores()

# 互動式篩選器
col1, col2 = st.columns(2)
with col1:
    # 過濾掉非菜餚的無效分類
    blacklist = [
        "Nightlife", "Event Planning & Services", "Casinos", "Hotels", "Shopping", 
        "Arts & Entertainment", "Active Life", "Local Services", "Automotive", 
        "Health & Medical", "Beauty & Spas", "Home Services", "Financial Services", 
        "Education", "Real Estate", "Mass Media", "Pets", "Professional Services",
        "Grocery", "Convenience Stores", "Caterers", "Venues & Event Spaces"
    ]
    valid_cuisines = df[~df["cuisine_type"].isin(blacklist)]["cuisine_type"].value_counts().head(40).index.tolist()
    cuisine_options = ["All"] + sorted(valid_cuisines)
    selected_cuisine = st.selectbox("🍽️ 篩選料理類型", cuisine_options)
with col2:
    view_mode = st.radio("👀 顯示模式", ["3D 柱狀立體 (高度=租金)", "2D 扁平色塊"], horizontal=True)

# 依據選擇過濾資料
if selected_cuisine != "All":
    filtered_df = df[df["cuisine_type"] == selected_cuisine]
else:
    filtered_df = df

is_extruded = view_mode.startswith("3D")

with st.spinner("🌍 正在載入並渲染全美 H3 空間網格地圖..."):
    # 動態建立 PyDeck 圖層
    h3_layer = pdk.Layer(
        "H3HexagonLayer",
        data=filtered_df,
        pickable=True,
        auto_highlight=True,
        highlight_color=[255, 255, 255, 255],
        stroked=False,
        filled=True,
        extruded=is_extruded,
        get_hexagon="h3_index",
        get_fill_color="[color_r, color_g, color_b, color_a]",
        get_elevation="elevation",
        elevation_scale=1.5 if is_extruded else 0,
        coverage=1.0,
        opacity=0.65 if is_extruded else 0.45,
    )

    # 視角設定 (若是 2D 則將視角壓平)
    view_state = pdk.ViewState(
        latitude=39.0,
        longitude=-95.0,
        zoom=3.5,
        bearing=15 if is_extruded else 0,
        pitch=45 if is_extruded else 0,
    )

    # Tooltip 設定
    tooltip = {
        "html": """
        <b>Void Score:</b> {void_score}<br>
        <b>Cuisine:</b> {cuisine_type}<br>
        <b>Rent:</b> ${rent_index}<br>
        <b>Competitors:</b> {competitor_count}
        """,
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }

    # 渲染互動式地圖
    st.pydeck_chart(pdk.Deck(
        layers=[h3_layer],
        initial_view_state=view_state,
        map_style=pdk.map_styles.DARK,
        tooltip=tooltip
    ), height=700)

st.divider()

# Footer
st.markdown("""
<div style='text-align: center; color: #6b7280; font-size: 0.9em;'>
    © 2024 Spatial BI Analytics. MVP Proof of Concept.<br>
    Powered by PySpark, Uber H3, Deck.gl, and Streamlit.
</div>
""", unsafe_allow_html=True)
