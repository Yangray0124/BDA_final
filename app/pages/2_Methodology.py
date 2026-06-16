import streamlit as st
from utils.style import inject_global_style, inject_sidebar_footer

st.set_page_config(page_title="Methodology", page_icon="🔬", layout="wide")
inject_global_style()
inject_sidebar_footer()

st.title("🔬 Methodology & Trust")
st.markdown("了解 Spatial BI 如何透過資料科學與獨家演算法，為您找出下一個黃金店面。")

st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("什麼是 Void Score？")
    st.markdown("""
    **Void Score** 是我們專利的市場評估指標 (0-100分)，分數越高，代表該區域的投資潛力越大。
    它綜合考量了三個關鍵維度：

    1. **供給空白度 (Supply Void) - 40% 權重**
       - **資料來源：** Yelp 開放資料集。
       - **邏輯：** 我們計算該區域內同類型餐廳的競爭者數量。競爭者越少，市場的供給空白越大，新進入者的成功機率越高。
    
    2. **成本效益 (Cost Efficiency) - 30% 權重**
       - **資料來源：** Zillow 區域租金指數 (ZORI)。
       - **邏輯：** 租金是雲端廚房或實體店面最大的固定成本。我們優先推薦租金處於合理或低點的區域，以降低您的營運門檻與風險。
    
    3. **需求強度 (Demand Strength) - 30% 權重**
       - **資料來源：** Yelp 顧客評論數據。
       - **邏輯：** 我們使用該區域的總評論數作為活躍消費需求的代理指標。沒有需求的「死城」即便租金再低也不值得投資。
    """)
    
    st.subheader("為什麼使用 Uber H3 空間索引？")
    st.markdown("""
    傳統的商業分析往往依賴 **Zip Code (郵遞區號)**，但郵遞區號的形狀極不規則，且邊界劃分往往基於行政管理而非商業邏輯。
    
    我們導入了 Uber 開源的 **H3 六角形分層網格系統**（Resolution 8，每個六角形面積約 0.74 平方公里）：
    * **等距優勢：** 六角形中心到相鄰各邊的距離相等，徹底消除傳統矩形網格的邊緣扭曲效應。
    * **精確聚類：** 將全美數十萬家餐廳精準對應到蜂巢網格中，提供社區等級（Neighborhood-level）的微觀分析。
    """)

with col2:
    st.info("""
    **🛡️ 隱私與資料穩健性保證**
    
    本平台使用之資料皆為**去識別化 (De-identified)** 的公開商業登記與區域聚合數據，完全遵守 CCPA 等相關隱私法規。
    
    我們的 PySpark 後端管線每日自動化清洗、校正超過 5GB 的異常數據，確保您看到的每一個 Void Score 都精確可靠。
    """)
    
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem; padding: 2rem; background: rgba(0,0,0,0.3); border-radius: 15px; border: 1px solid rgba(255,255,255,0.05);">
        <div style="font-size: 8rem; color: #00e676; text-shadow: 0 0 30px rgba(0,230,118,0.4); line-height: 1;">⬢</div>
        <div style="color: #94a3b8; font-size: 0.95rem; font-weight: 600; margin-top: 15px; letter-spacing: 1px;">Powered by Uber H3<br>Spatial Indexing</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

st.markdown("### Ready to find your Blue Ocean?")
st.button("前往 Dashboard 開始分析", type="primary")
