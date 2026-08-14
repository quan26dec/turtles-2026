import streamlit as st
import requests
import pandas as pd

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
