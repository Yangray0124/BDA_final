import streamlit as st
from utils.style import inject_global_style, inject_sidebar_footer

st.set_page_config(page_title="Pricing & Subscription", page_icon="💳", layout="wide")
inject_global_style()
inject_sidebar_footer()

st.title("💳 Pricing & Subscription")
st.markdown("Choose a subscription plan that suits your needs and instantly unlock the data monetization potential of the US market.")

st.divider()

# 使用三欄式版面排列卡片
col1, col2, col3 = st.columns(3)

# --- Starter 方案 ---
with col1:
    st.container(border=True)
    st.subheader("🌱 Starter")
    st.markdown("#### Free / Forever")
    st.markdown("Ideal for small entrepreneurs for initial exploration and proof of concept.")
    st.markdown("""
    * ✅ Single test city (e.g., Philadelphia)
    * ✅ 2D static map preview
    * ✅ Top 5 saturated market rankings
    * ❌ No 3D Void Map access
    * ❌ No CSV exports
    """)
    st.button("Start for Free", key="btn_starter", use_container_width=True)

# --- Pro 方案 ---
with col2:
    st.container(border=True)
    st.subheader("🚀 Pro")
    st.markdown("#### $199 / month")
    st.markdown("Perfect for aggressively expanding cloud kitchen operators and chain brands.")
    st.markdown("""
    * ✅ All major US metropolitan areas
    * ✅ **Full 3D Void Map interactive access**
    * ✅ Complete Void Score dashboard analysis
    * ✅ **Export Top 50 zones via CSV**
    * ❌ No API integration
    """)
    st.button("Upgrade to Pro", key="btn_pro", type="primary", use_container_width=True)

# --- Enterprise 方案 ---
with col3:
    st.container(border=True)
    st.subheader("🏢 Enterprise")
    st.markdown("#### Custom Pricing")
    st.markdown("Tailored for large commercial real estate developers and investment firms.")
    st.markdown("""
    * ✅ Includes all Pro features
    * ✅ **REST API access**
    * ✅ Seamless integration with internal real estate systems
    * ✅ Daily real-time data stream updates
    * ✅ Dedicated data science consultant support
    """)
    st.button("Contact Sales", key="btn_ent", use_container_width=True)

st.divider()

st.markdown("""
**Have special requirements?** 
If you need a customized cuisine type model (e.g., subdividing into "Artisan Wood-Fired Pizza" instead of a generic "Pizza"), please contact us via the Enterprise plan.
""")
