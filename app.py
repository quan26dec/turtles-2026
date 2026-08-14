import streamlit as st
import requests
import pandas as pd

JQUANTS_API_KEY = st.secrets["JQUANTS_API_KEY"]

st.set_page_config(
    page_title="Turtles 2026",
    page_icon="🐢",
    layout="wide",
)

st.title("🐢 Turtles 2026")
st.subheader("日本株モメンタム・ブレイクアウト分析")

st.info("Turtles 2026 起動準備OK！")

st.divider()

st.subheader("🐢 銘柄チェック")

stock_code = st.text_input(
    "銘柄コードを入力してください",
    placeholder="例：8591"
)

st.caption("まずは1銘柄ずつ、タートルズ条件を判定します。")

if stock_code:
    url = "https://api.jquants.com/v2/equities/bars/daily"

    headers = {
        "x-api-key": JQUANTS_API_KEY
    }

    params = {
        "code": stock_code
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30
    )

    if response.status_code == 200:
        data = response.json().get("data", [])
        st.success(f"J-Quants接続成功：{len(data)}件取得")

        df = pd.DataFrame(data)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")
        df = df.dropna(subset=["AdjH", "AdjC"])

        if len(df) >= 21:
            latest = df.iloc[-1]
            prior_20 = df.iloc[-21:-1]

            latest_close = latest["AdjC"]
            high_20 = prior_20["AdjH"].max()
            breakout_20 = latest_close > high_20

            st.write(f"最新日：{latest['Date'].date()}")
            st.write(f"最新終値：{latest_close:,.1f}円")
            st.write(f"過去20日高値：{high_20:,.1f}円")

            if breakout_20:
                st.success("🐢 20日高値ブレイク！")
            else:
                st.info("20日高値はまだブレイクしていません。")    
    
    else:
        st.error(f"J-Quants接続エラー：{response.status_code}")
