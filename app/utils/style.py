import streamlit as st

def inject_global_style():
    """注入全域共用的 CSS (玻璃側邊欄、深灰色按鈕、極暗背景材質)"""
    st.markdown("""
    <style>
    /* 啟用平滑滾動 */
    *, html, body, [data-testid="stAppViewContainer"], .main {
        scroll-behavior: smooth !important;
    }

    /* 全域背景：極暗的城市背景，為側邊欄提供高級的玻璃折射材質 */
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(to bottom, rgba(14,17,23,0.9), rgba(14,17,23,0.95)), url('https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=2000&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    [data-testid="stAppViewContainer"] > .main {
        background: transparent !important;
    }

    /* 側邊欄玻璃透視感 (Glassmorphism) */
    [data-testid="stSidebar"] {
        background: rgba(14, 17, 23, 0.2) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* 頂部橫槓透明化 */
    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* 側邊欄開關按鈕 (帶有灰色正方形框) */
    [data-testid="collapsedControl"] {
        background-color: rgba(128, 128, 128, 0.6) !important;
        border-radius: 4px !important;
        padding: 6px !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
        opacity: 1 !important;
        color: #ffffff !important;
        transition: all 0.3s ease;
    }
    /* 強制將按鈕內的圖示變成純白色 */
    [data-testid="collapsedControl"] svg {
        fill: #ffffff !important;
        color: #ffffff !important;
    }
    /* 滑鼠懸停時變成品牌綠色 */
    [data-testid="collapsedControl"]:hover {
        background-color: rgba(0, 230, 118, 0.8) !important;
        border-color: #00e676 !important;
    }

    /* 將側邊欄的連結文字首字母大寫 (解決 main -> Main 的問題) */
    [data-testid="stSidebarNav"] span {
        text-transform: capitalize;
    }

    /* 將 Streamlit 預設導覽列下方的空間撐開，把後面的元件推到最底下 */
    [data-testid="stSidebarNav"] {
        margin-bottom: auto !important;
    }
    </style>
    """, unsafe_allow_html=True)

def inject_home_style():
    """首頁專用的 CSS 覆寫 (明亮上方背景、Hero 排版)"""
    st.markdown("""
    <style>
    /* 覆寫全域背景，讓首頁上半部保持透亮 */
    [data-testid="stAppViewContainer"] {
        background-image: url('https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=2000&auto=format&fit=crop');
    }
    
    [data-testid="stAppViewContainer"] > .main {
        background: linear-gradient(to bottom, rgba(14, 17, 23, 0.3) 0vh, rgba(14, 17, 23, 0.85) 75vh, rgba(14, 17, 23, 1) 100vh, rgba(14, 17, 23, 1) 100%) !important;
    }

    .hero-wrapper {
        position: relative;
        width: 100vw;
        height: 70vh;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        margin-bottom: 2rem;
    }

    .hero-title {
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 3.8rem;
        font-weight: 900;
        letter-spacing: -1px;
        margin-bottom: 1rem;
        color: #ffffff;
        text-shadow: 0 4px 15px rgba(0,0,0,0.8);
    }

    .hero-subtitle {
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        max-width: 800px;
        line-height: 1.6;
        color: #ffffff;
        margin-bottom: 3rem;
        padding: 0 20px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.9);
    }

    .highlight-text {
        color: #00e676;
    }

    .scroll-btn {
        text-decoration: none;
        color: #00e676;
        font-size: 2.5rem;
        animation: bounce 2s infinite;
        transition: all 0.3s ease;
        opacity: 0.8;
        text-shadow: 0 2px 10px rgba(0,0,0,0.9);
    }
    .scroll-btn:hover {
        color: #ffffff;
        opacity: 1;
    }

    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
        40% {transform: translateY(-15px);}
        60% {transform: translateY(-7px);}
    }

    .intro-section {
        max-width: 900px;
        margin: 0 auto 3rem auto;
        text-align: center;
    }
    .intro-section h2 {
        color: #ffffff;
        text-shadow: 0 2px 8px rgba(0,0,0,0.8);
    }
    .intro-section p {
        color: #ffffff;
        font-weight: 500;
        text-shadow: 0 2px 8px rgba(0,0,0,0.8);
    }
    </style>
    """, unsafe_allow_html=True)

def inject_sidebar_footer():
    """在側邊欄最底部注入品牌標誌與版權"""
    st.sidebar.markdown("""
    <div style="text-align: left; padding: 10px 0; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 20px;">
        <h3 style="margin: 0; color: #ffffff; font-size: 1.2rem; text-shadow: 0 2px 5px rgba(0,0,0,0.5);">📍 Spatial BI</h3>
        <p style="color: #94a3b8; font-size: 0.8rem; margin: 5px 0 0 0;">© 2024 Spatial BI Analytics</p>
    </div>
    """, unsafe_allow_html=True)
