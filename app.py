import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="台股籌碼預警系統", layout="wide")
st.title("📈 台股籌碼與均線預警輔助系統")

st.sidebar.header("功能導覽")
page = st.sidebar.radio("請選擇模組", ["自選股追蹤 (Watchlist)", "全市場篩選 (Screener)", "預警設定 (Alerts)"])

def generate_mock_data():
    data = {
        "股票代號": ["2330", "2317", "2603", "1504", "3035", "3231"],
        "股票名稱": ["台積電", "鴻海", "長榮", "東元", "智原", "緯創"],
        "最新收盤價": [980, 210, 195, 52, 280, 115],
        "融資連減(日)": [1, 4, 0, 3, 5, 2],
        "借券連減(日)": [0, 3, 1, 4, 5, 0],
        "量縮比例(%)": [80, 45, 120, 30, 25, 90],
        "大戶持股增減(%)": [0.1, 1.2, -0.5, 0.8, 2.5, -1.0],
        "均線狀態": ["多頭排列", "糾結突破", "空頭排列", "空頭排列", "糾結突破", "多頭排列"]
    }
    return pd.DataFrame(data)

df = generate_mock_data()

if page == "自選股追蹤 (Watchlist)":
    st.header("🎯 自選股深度追蹤池")
    st.markdown("追蹤曾經熱門股的籌碼沉澱狀態。**綠燈 (✅) 代表符合打底特徵，紅燈 (❌) 代表未達標。**")
    
    def color_status(row):
        margin_ok = "✅" if row["融資連減(日)"] >= 3 else "❌"
        short_ok = "✅" if row["借券連減(日)"] >= 3 else "❌"
        vol_ok = "✅" if row["量縮比例(%)"] <= 50 else "❌"
        whale_ok = "✅" if row["大戶持股增減(%)"] > 0 else "❌"
        score = sum([row["融資連減(日)"] >= 3, row["借券連減(日)"] >= 3, row["量縮比例(%)"] <= 50, row["大戶持股增減(%)"] > 0])
        
        return pd.Series({
            "股票名稱": row["股票名稱"],
            "融資達標 (>3日)": margin_ok,
            "借券達標 (>3日)": short_ok,
            "極致量縮 (<50%)": vol_ok,
            "大戶增加": whale_ok,
            "沉澱達成率": f"{score}/4"
        })

    status_df = df.apply(color_status, axis=1)
    st.dataframe(status_df, use_container_width=True)

elif page == "全市場篩選 (Screener)":
    st.header("🔍 全市場動能與籌碼篩選")
    st.markdown("從全市場掃描同時符合「歷史熱門 + 籌碼沉澱」的標的。")
    
    if st.button("執行篩選 (模擬)"):
        with st.spinner('掃描全市場資料中...'):
            filtered_df = df[(df["融資連減(日)"] >= 3) & 
                             (df["量縮比例(%)"] <= 50) & 
                             (df["大戶持股增減(%)"] > 0) & 
                             (df["均線狀態"] == "糾結突破")]
            
            st.success(f"掃描完成！共篩選出 {len(filtered_df)} 檔潛力標的。")
            st.dataframe(filtered_df[["股票代號", "股票名稱", "最新收盤價", "大戶持股增減(%)", "均線狀態"]], use_container_width=True)

elif page == "預警設定 (Alerts)":
    st.header("🚨 多維度即時預警系統")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("新增價格預警")
        target_stock = st.selectbox("選擇追蹤標的", df["股票名稱"].tolist())
        target_price = st.number_input("設定觀察買入價", min_value=0.0, step=0.5)
        if st.button("加入價格監控"):
            st.toast(f"已將 {target_stock} ({target_price}元) 加入監控排程。")
            
    with col2:
        st.subheader("均線反轉監控")
        ma_type = st.radio("選擇觸發條件", ["短線糾結突破 (5MA穿20MA)", "長線正式翻多 (季線上揚)"])
        if st.button("開啟均線掃描"):
            st.toast(f"已啟動 {ma_type} 監控。")
