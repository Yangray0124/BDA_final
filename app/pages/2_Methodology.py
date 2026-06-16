import streamlit as st
from utils.style import inject_global_style, inject_sidebar_footer

st.set_page_config(page_title="Methodology", page_icon="🔬", layout="wide")
inject_global_style()
inject_sidebar_footer()

st.title("🔬 Methodology & Trust")
st.markdown("Discover how Spatial BI uses data science and proprietary algorithms to find your next golden location.")

st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("What is the Void Score?")
    st.markdown("""
    The **Void Score** is our proprietary market evaluation metric (0-100). The higher the score, the greater the investment potential of the area.
    It comprehensively considers three key dimensions:

    1. **Supply Void - 40% Weight**
       - **Data Source:** Yelp Open Dataset.
       - **Logic:** We calculate the number of competitors of the same cuisine type in the area. The fewer competitors, the larger the supply void, leading to a higher probability of success for new entrants.
    
    2. **Cost Efficiency - 30% Weight**
       - **Data Source:** Zillow Observed Rent Index (ZORI).
       - **Logic:** Rent is the largest fixed cost for a cloud kitchen or physical storefront. We prioritize areas with reasonable or low rent to lower your operational threshold and risk.
    
    3. **Demand Strength - 30% Weight**
       - **Data Source:** Yelp Customer Review Data.
       - **Logic:** We use the total number of reviews in the area as a proxy metric for active consumer demand. A "ghost town" without demand is not worth investing in, regardless of how low the rent is.
    """)
    
    st.subheader("Why use Uber H3 Spatial Indexing?")
    st.markdown("""
    Traditional business analysis often relies on **Zip Codes**, but zip code shapes are highly irregular, and their boundaries are often based on administrative management rather than business logic.
    
    We introduced Uber's open-source **H3 Hexagonal Hierarchical Spatial Index** (Resolution 8, where each hexagon covers approximately 0.74 sq km):
    * **Equidistant Advantage:** The distance from the center of a hexagon to adjacent edges is equal, completely eliminating the edge distortion effects of traditional rectangular grids.
    * **Precise Clustering:** Accurately mapping hundreds of thousands of restaurants across the US into a honeycomb grid provides micro-analysis at the neighborhood level.
    """)

with col2:
    st.info("""
    **🛡️ Privacy and Data Robustness Guarantee**
    
    All data used on this platform is **De-identified** public commercial registration and regional aggregated data, fully compliant with CCPA and other relevant privacy regulations.
    
    Our PySpark backend pipeline automatically cleans and calibrates over 5GB of anomalous data daily, ensuring that every Void Score you see is precise and reliable.
    """)
    
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem; padding: 2rem; background: rgba(0,0,0,0.3); border-radius: 15px; border: 1px solid rgba(255,255,255,0.05);">
        <div style="font-size: 8rem; color: #00e676; text-shadow: 0 0 30px rgba(0,230,118,0.4); line-height: 1;">⬢</div>
        <div style="color: #94a3b8; font-size: 0.95rem; font-weight: 600; margin-top: 15px; letter-spacing: 1px;">Powered by Uber H3<br>Spatial Indexing</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

st.markdown("### Ready to find your Blue Ocean?")
st.button("Go to Dashboard", type="primary")
