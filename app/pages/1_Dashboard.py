import streamlit as st
import plotly.express as px
from utils.data_loader import load_void_scores
from utils.style import inject_global_style, inject_sidebar_footer

st.set_page_config(page_title="Executive Dashboard", page_icon="📊", layout="wide")
inject_global_style()
inject_sidebar_footer()

st.title("📊 Executive Dashboard")
st.markdown("探索不同料理類型與區域的競爭強度，識別最佳投資標的。")

# 載入快取資料
df = load_void_scores()

# --- Sidebar 過濾器 ---
st.sidebar.header("Filter Settings")

# 1. 料理類型篩選 (排除非食物的標籤)
blacklist = [
    "Nightlife", "Event Planning & Services", "Casinos", "Hotels", "Shopping", 
    "Arts & Entertainment", "Active Life", "Local Services", "Automotive", 
    "Health & Medical", "Beauty & Spas", "Home Services", "Financial Services", 
    "Education", "Real Estate", "Mass Media", "Pets", "Professional Services",
    "Grocery", "Convenience Stores", "Caterers", "Venues & Event Spaces"
]
valid_cuisines = df[~df["cuisine_type"].isin(blacklist)]["cuisine_type"].value_counts().head(40).index.tolist()
cuisine_options = ["All"] + sorted(valid_cuisines)
selected_cuisine = st.sidebar.selectbox("🍽️ Cuisine Type", cuisine_options)

min_reviews = st.sidebar.slider("最低總評論數 (需求門檻)", 0, int(df["total_reviews"].max() * 0.1), 100)

# 應用過濾器
filtered_df = df[df["total_reviews"] >= min_reviews]
if selected_cuisine != "All":
    filtered_df = filtered_df[filtered_df["cuisine_type"] == selected_cuisine]

st.divider()

# --- 圖表區塊 1 & 2 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚨 Saturated Market Alert")
    st.markdown("前 10 大最飽和料理類型 (依據競爭者總數)")
    
    # 聚合全美最飽和的料理
    sat_df = df.groupby("cuisine_type")["competitor_count"].sum().reset_index()
    sat_df = sat_df.sort_values(by="competitor_count", ascending=False).head(10)
    
    fig_bar = px.bar(
        sat_df, 
        x="competitor_count", 
        y="cuisine_type", 
        orientation='h',
        color="competitor_count",
        color_continuous_scale="Reds",
        labels={"competitor_count": "競爭者總數", "cuisine_type": "料理類型"}
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("🎯 Opportunity Matrix")
    st.markdown("X軸: 租金成本 | Y軸: 競爭者數量 | **左下角為最佳 Sweet Spot**")
    
    # 避免散佈圖點過多，取 Top 2000
    scatter_df = filtered_df.sort_values(by="void_score", ascending=False).head(2000)
    
    fig_scatter = px.scatter(
        scatter_df,
        x="rent_index",
        y="competitor_count",
        color="void_score",
        color_continuous_scale="Viridis",
        hover_data=["dominant_zip", "cuisine_type", "total_reviews"],
        labels={
            "rent_index": "區域租金指數 (Cost)", 
            "competitor_count": "競爭者數量 (Supply)",
            "void_score": "Void Score"
        }
    )
    # 加上 Sweet Spot 標註區塊
    fig_scatter.add_vrect(
        x0=scatter_df["rent_index"].min(), x1=scatter_df["rent_index"].median(),
        fillcolor="green", opacity=0.1, line_width=0
    )
    fig_scatter.add_hrect(
        y0=0, y1=scatter_df["competitor_count"].median(),
        fillcolor="green", opacity=0.1, line_width=0
    )
    fig_scatter.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# --- 資料表區塊 ---
st.subheader("🏆 Top 5 Investment Zones (最佳投資區域)")
st.markdown("基於您在左側選擇的條件，以下是全美 Void Score 最高的 5 個黃金社區。")

import requests

@st.cache_data(show_spinner=False)
def get_location_from_zip(zip_code):
    try:
        zip_str = str(int(zip_code)).zfill(5)
        res = requests.get(f"https://api.zippopotam.us/us/{zip_str}", timeout=2)
        if res.status_code == 200:
            data = res.json()
            city = data["places"][0]["place name"]
            state = data["places"][0]["state abbreviation"]
            return f"{city}, {state}"
    except:
        pass
    return "Unknown"

top5_df = filtered_df.sort_values(by="void_score", ascending=False).head(5).copy()

# 即時查詢 Zip Code 對應的城市與州
top5_df["Location"] = top5_df["dominant_zip"].apply(get_location_from_zip)

# 整理顯示欄位
display_df = top5_df[[
    "void_score", "Location", "dominant_zip", "cuisine_type", 
    "competitor_count", "rent_index", "total_reviews", "avg_rating"
]].reset_index(drop=True)

# 格式化
st.dataframe(
    display_df,
    column_config={
        "void_score": st.column_config.NumberColumn("Void Score", format="%.1f 分"),
        "rent_index": st.column_config.NumberColumn("Rent Index", format="$%d"),
        "total_reviews": st.column_config.NumberColumn("Total Reviews", format="%d"),
        "avg_rating": st.column_config.NumberColumn("Avg Rating", format="%.1f ⭐"),
        "Location": "City, State",
        "dominant_zip": "Zip Code",
        "cuisine_type": "Cuisine",
        "competitor_count": "Competitors"
    },
    use_container_width=True
)
