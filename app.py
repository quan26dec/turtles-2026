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
        df = df.dropna(subset=["AdjH", "AdjL", "AdjC", "AdjVo"])

        if len(df) >= 56:
            latest = df.iloc[-1]
            prior_20 = df.iloc[-21:-1]
            prior_10 = df.iloc[-11:-1]
            prior_55 = df.iloc[-56:-1]
            
            latest_close = latest["AdjC"]

            latest_volume = latest["AdjVo"]
            avg_volume_20 = prior_20["AdjVo"].mean()
            volume_ratio = latest_volume / avg_volume_20
            
            high_20 = prior_20["AdjH"].max()
            high_55 = prior_55["AdjH"].max()
            low_10 = prior_10["AdjL"].min()
            breakout_20 = latest_close > high_20
            breakout_55 = latest_close > high_55
            exit_10 = latest_close < low_10
            
            st.write(f"最新日：{latest['Date'].date()}")
            st.write(f"最新終値：{latest_close:,.1f}円")
            st.write(f"過去20日高値：{high_20:,.1f}円")
            st.write(f"過去55日高値：{high_55:,.1f}円")
            st.write(f"過去10日安値：{low_10:,.1f}円")

            st.write(f"最新出来高：{latest_volume:,.0f}株")
            st.write(f"20日平均出来高：{avg_volume_20:,.0f}株")
            st.write(f"出来高倍率：{volume_ratio:.2f}倍")

            if volume_ratio >= 2.0:
                st.success("🔥 出来高急増：20日平均の2倍以上")
            elif volume_ratio >= 1.5:
                st.warning("📈 出来高増加：20日平均の1.5倍以上")
            else:
                st.info("出来高は通常範囲です。")
            
            if breakout_20:
                st.success("🐢 20日高値ブレイク！")
            else:
                st.info("20日高値はまだブレイクしていません。")    
            if breakout_55:
                st.success("🐢🐢 55日高値ブレイク！")
            else:
                    st.info("55日高値はまだブレイクしていません。")
            if exit_10:
                st.error("🐢 EXIT：10日安値を割りました。")
            else:
                st.success("10日安値は維持しています。")

            st.divider()
            st.subheader("🐢 総合判定")
    
            if exit_10:
                st.error("🔴 EXIT候補：10日安値を割っています")
            elif breakout_55 and volume_ratio >= 1.5:
                st.success("🐢🐢 強い買い候補：55日高値突破 ＋ 出来高増加")
            elif breakout_20 and volume_ratio >= 1.5:
                st.success("🐢 買い候補：20日高値突破 ＋ 出来高増加")
            elif breakout_55:
                st.warning("🐢 55日高値突破：出来高を確認")
            elif breakout_20:
                st.warning("🐢 20日高値突破：出来高を確認")
            else:
                st.info("👀 監視：現在は新規エントリー条件なし")
    
    else:
        st.error(f"J-Quants接続エラー：{response.status_code}")
    
st.divider()
        
st.subheader("🐢 タートルズ・スクリーナー")
        
st.caption("複数銘柄からタートルズ条件に合う銘柄を探します。")

screen_codes = st.text_area(
    "スクリーニングする銘柄コードを入力してください",
    placeholder="例：8591, 4208, 6525"
)

if screen_codes:
    codes = [
        code.strip()
        for code in screen_codes.replace("\n", ",").split(",")
        if code.strip()
    ]

    st.write("入力された銘柄コード：", codes)

    if len(codes) > 20:
        st.warning("⚠️ 現在は最大20銘柄までです。最初の20銘柄を判定します。")
        codes = codes[:20]

    st.write(f"🐢 スクリーニング対象：{len(codes)}銘柄")
    
    turtle_candidates = []
    
    for code in codes:
        st.write("🐢 判定対象：", code)

        url = "https://api.jquants.com/v2/equities/bars/daily"

        headers = {
            "x-api-key": JQUANTS_API_KEY
        }

        params = {
            "code": code
        }
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json().get("data", [])
            st.success(f"🐢 {code}：J-Quants取得成功 {len(data)}件")

            df_screen = pd.DataFrame(data)
            df_screen["Date"] = pd.to_datetime(df_screen["Date"])
            df_screen = df_screen.sort_values("Date")
            df_screen = df_screen.dropna(
                subset=["AdjH", "AdjL", "AdjC", "AdjVo"]
            )

            if len(df_screen) >= 56:
                st.write(f"🐢 {code}：判定用データOK")

                latest_screen = df_screen.iloc[-1]
                prior_20_screen = df_screen.iloc[-21:-1]
                prior_10_screen = df_screen.iloc[-11:-1]
                prior_55_screen = df_screen.iloc[-56:-1]

                latest_close_screen = latest_screen["AdjC"]
                high_20_screen = prior_20_screen["AdjH"].max()
                high_55_screen = prior_55_screen["AdjH"].max()
                low_10_screen = prior_10_screen["AdjL"].min()
                volume_ratio_screen = latest_screen["AdjVo"] / prior_20_screen["AdjVo"].mean()

                breakout_20_screen = latest_close_screen > high_20_screen
                breakout_55_screen = latest_close_screen > high_55_screen
                exit_10_screen = latest_close_screen < low_10_screen

                st.write(f"終値：{latest_close_screen:,.1f}円")
                st.write(f"20日高値：{high_20_screen:,.1f}円 / 55日高値：{high_55_screen:,.1f}円")
                st.write(f"出来高倍率：{volume_ratio_screen:.2f}倍")

                if breakout_55_screen and volume_ratio_screen >= 1.5:
                    st.success(f"🐢🐢 {code}：タートルズ強い候補")
                    turtle_candidates.append({
                        "code": code,
                        "signal": "🐢🐢 強い候補",
                        "close": latest_close_screen,
                        "high20": high_20_screen,
                        "high55": high_55_screen,
                        "volume_ratio": volume_ratio_screen,
                    })
                
                elif breakout_20_screen and volume_ratio_screen >= 1.5:
                    st.success(f"🐢 {code}：タートルズ候補")
                    turtle_candidates.append({
                        "code": code,
                        "signal": "🐢 候補",
                        "close": latest_close_screen,
                        "high20": high_20_screen,
                        "high55": high_55_screen,
                        "volume_ratio": volume_ratio_screen,
                    })

                else:
                    st.info(f"👀 {code}：監視")
            
            else:
                st.warning(f"🐢 {code}：判定用データ不足")
        
        else:
            st.error(f"🐢 {code}：取得エラー {response.status_code}")  
                    
    st.divider()
    st.subheader("🐢 スクリーニング結果")

    if turtle_candidates:
        result_df = pd.DataFrame(turtle_candidates)
    
        result_df = result_df.rename(columns={
            "code": "銘柄コード",
            "signal": "判定",
            "close": "終値",
            "high20": "20日高値",
            "high55": "55日高値",
            "volume_ratio": "出来高倍率",
        })
    
        st.dataframe(result_df, use_container_width=True)
    else:
        st.info("👀 今回はタートルズ候補なし")

st.divider()
st.subheader("📡 自動銘柄一覧")

master_url = "https://api.jquants.com/v2/equities/master"

master_response = requests.get(master_url, headers={"x-api-key": JQUANTS_API_KEY})
st.write("📡 銘柄一覧API:", master_response.status_code)

if master_response.status_code == 200:
    master_data = master_response.json().get("data", [])
    master_df = pd.DataFrame(master_data)
    st.success(f"📡 自動取得した銘柄数：{len(master_df)}件")

    auto_codes = master_df["Code"].astype(str).tolist()
    st.write("🐢 自動巡回用コード（先頭10件）:", auto_codes[:10])

    auto_codes_4digit = [code[:4] for code in auto_codes]
    st.write("🐢 4桁変換（先頭10件）:", auto_codes_4digit[:10])

    test_code = auto_codes[0]
    
    test_url = "https://api.jquants.com/v2/equities/bars/daily"
    test_response = requests.get(
        test_url,
        headers={"x-api-key": JQUANTS_API_KEY},
        params={"code": test_code}
    )
    
    st.write("🐢 5桁コードテスト :", test_code)
    st.write("🐢 日足APIテスト :", test_response.status_code)

    st.write("🐢 5銘柄自動巡回テスト")
    
    test_codes = auto_codes[:5]
    auto_candidates = []
    auto_candidates_20 = []
    
    for test_code in test_codes:
        test_response = requests.get(
            test_url,
            headers={"x-api-key": JQUANTS_API_KEY},
            params={"code": test_code}
        )
        
        if test_response.status_code == 200:
            test_data = test_response.json().get("data", [])
            test_df = pd.DataFrame(test_data)
            test_df["AdjC"] = pd.to_numeric(test_df["AdjC"], errors="coerce")
            test_df["AdjH"] = pd.to_numeric(test_df["AdjH"], errors="coerce")
            test_df["AdjVo"] = pd.to_numeric(test_df["AdjVo"], errors="coerce")
            test_df = test_df.dropna(subset=["AdjC", "AdjH", "AdjVo"])

            if len(test_df) < 56:
                st.warning(f"⚠️ {test_code}：有効な日足データが56件未満のためスキップ")
                continue
                
            test_df["Date"] = pd.to_datetime(test_df["Date"])
            test_df = test_df.sort_values("Date")
            latest_test = test_df.iloc[-1]

            past_20_test = test_df.iloc[:-1].tail(20)
            high_20_test = past_20_test["AdjH"].max()
            
            past_55_test = test_df.iloc[:-1].tail(55)
            high_55_test = past_55_test["AdjH"].max()

            past_volume_test = test_df.iloc[:-1].tail(20)["AdjVo"].mean()
            latest_volume_test = latest_test["AdjVo"]

            volume_ratio_test = latest_volume_test / past_volume_test

            breakout_20_test = latest_test["AdjC"] > high_20_test

            if breakout_20_test and volume_ratio_test >= 1.5:
                auto_candidates_20.append(test_code)
            
            breakout_55_test = latest_test["AdjC"] > high_55_test

            if breakout_55_test and volume_ratio_test >= 1.5:
                auto_candidates.append(test_code)

            st.write("🐢 自動巡回候補数：", len(auto_candidates))
            st.write("🐢 自動巡回候補：", auto_candidates)
            st.write("🐢 20日候補数：", len(auto_candidates_20))
            st.write("🐢 20日候補：", auto_candidates_20)

st.divider()
st.subheader("⚡ Bulk高速化テスト")

bulk_list_url = "https://api.jquants.com/v2/bulk/list"

bulk_response = requests.get(
    bulk_list_url,
    headers={"x-api-key": JQUANTS_API_KEY},
    params={"endpoint": "/equities/bars/daily"}
)

st.write("⚡ Bulk APIテスト：", bulk_response.status_code)

bulk_data = bulk_response.json()

st.write("⚡ Bulkデータ項目：", bulk_data.keys())

bulk_files = bulk_data.get("data", [])
st.write("⚡ Bulkファイル件数：", len(bulk_files))

st.write("⚡ Bulk最終ファイル：", bulk_files[-1])
