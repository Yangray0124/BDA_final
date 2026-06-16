import streamlit as st
from utils.style import inject_global_style, inject_sidebar_footer

st.set_page_config(page_title="Pricing & Subscription", page_icon="💳", layout="wide")
inject_global_style()
inject_sidebar_footer()

st.title("💳 定價方案 (Pricing & Subscription)")
st.markdown("選擇適合您的訂閱方案，立即解鎖全美市場的數據變現潛力。")

st.divider()

# 使用三欄式版面排列卡片
col1, col2, col3 = st.columns(3)

# --- Starter 方案 ---
with col1:
    st.container(border=True)
    st.subheader("🌱 Starter")
    st.markdown("#### Free / 永久免費")
    st.markdown("適合初步探索與概念驗證的小型創業者。")
    st.markdown("""
    * ✅ 單一測試城市 (如費城)
    * ✅ 2D 靜態地圖預覽
    * ✅ Top 5 飽和市場排行
    * ❌ 不支援 3D Void Map
    * ❌ 無法匯出 CSV
    """)
    st.button("Start for Free", key="btn_starter", use_container_width=True)

# --- Pro 方案 ---
with col2:
    st.container(border=True)
    st.subheader("🚀 Pro")
    st.markdown("#### $199 / 月")
    st.markdown("適合積極擴張的雲端廚房業者與連鎖品牌。")
    st.markdown("""
    * ✅ 全美所有大都會區
    * ✅ **完整 3D Void Map 互動操作**
    * ✅ 完整 Void Score 儀表板分析
    * ✅ **支援匯出 Top 50 區域 CSV**
    * ❌ 不支援 API 整合
    """)
    st.button("Upgrade to Pro", key="btn_pro", type="primary", use_container_width=True)

# --- Enterprise 方案 ---
with col3:
    st.container(border=True)
    st.subheader("🏢 Enterprise")
    st.markdown("#### Custom Pricing")
    st.markdown("專為大型商業地產開發商與投資機構打造。")
    st.markdown("""
    * ✅ 包含 Pro 所有功能
    * ✅ **REST API 存取權限**
    * ✅ 與內部不動產系統無縫整合
    * ✅ 每日即時資料流更新
    * ✅ 專屬資料科學顧問支援
    """)
    st.button("Contact Sales", key="btn_ent", use_container_width=True)

st.divider()

st.markdown("""
**有特殊需求？** 
如果您需要客製化的料理類型模型（例如細分至「手工窯烤披薩」而非泛用的「Pizza」），請透過 Enterprise 方案聯絡我們。
""")
