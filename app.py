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

print("DEBUG_SINGLE_SECTION_END", flush=True)

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
    print("DEBUG_SCREEN_LOOP_START", len(codes), flush=True)
    
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

master_url = "https://api.jquants.com/v2/equities/master"

master_response = requests.get(master_url, headers={"x-api-key": JQUANTS_API_KEY})

if master_response.status_code == 200:
    master_data = master_response.json().get("data", [])
    master_df = pd.DataFrame(master_data)
    name_map_df = master_df[["Code", "CoName"]].copy()   
     
    auto_codes = master_df.loc[master_df["ProdCat"] == "011", "Code"].astype(str).tolist()

    auto_codes_4digit = [code[:4] for code in auto_codes]

st.divider()

bulk_list_url = "https://api.jquants.com/v2/bulk/list"

bulk_response = requests.get(
    bulk_list_url,
    headers={"x-api-key": JQUANTS_API_KEY},
    params={"endpoint": "/equities/bars/daily"}
)

bulk_data = bulk_response.json()

bulk_files = bulk_data.get("data", [])

latest_bulk_key = bulk_files[-1]["Key"]

bulk_get_url = "https://api.jquants.com/v2/bulk/get"

bulk_get_response = requests.get(
    bulk_get_url,
    headers={"x-api-key": JQUANTS_API_KEY},
    params={"key": latest_bulk_key}
)

bulk_get_data = bulk_get_response.json()

bulk_download_url = bulk_get_data["url"]

bulk_file_response = requests.get(bulk_download_url)

import io

bulk_df = pd.read_csv(io.BytesIO(bulk_file_response.content), compression="gzip")
live_bulk_files = [item for item in bulk_files if "/live/" in item.get("Key", "")]
bulk_55_files = live_bulk_files[-10:]

historical_bulk_files = [item for item in bulk_files if "/historical/" in item.get("Key", "")]
recent_historical_files = historical_bulk_files[-3:]
bulk_55_files = recent_historical_files + live_bulk_files

bulk_dfs = []

for bulk_item in bulk_55_files:
    item_key = bulk_item["Key"]
    item_get_response = requests.get(
        bulk_get_url,
        headers={"x-api-key": JQUANTS_API_KEY},
        params={"key": item_key}
    )
    item_get_data = item_get_response.json()

    item_download_url = item_get_data["url"]

    item_file_response = requests.get(item_download_url)

    item_df = pd.read_csv(
    io.BytesIO(item_file_response.content),
    compression="gzip",
    usecols=["Date", "Code", "H", "C", "Vo"],
    dtype={"Code": str}
)

    bulk_dfs.append(item_df)

bulk_all_df = pd.concat(bulk_dfs, ignore_index=True)
bulk_all_df = bulk_all_df[bulk_all_df["Code"].astype(str).isin(set(auto_codes))].copy()

bulk_all_df["Date"] = pd.to_datetime(bulk_all_df["Date"])

bulk_all_df = bulk_all_df.sort_values(["Code", "Date"])

bulk_all_df["C"] = pd.to_numeric(bulk_all_df["C"], errors="coerce")

bulk_all_df["H"] = pd.to_numeric(bulk_all_df["H"], errors="coerce")

bulk_all_df["Vo"] = pd.to_numeric(bulk_all_df["Vo"], errors="coerce")

bulk_all_df = bulk_all_df.dropna(subset=["Code", "Date", "C", "H", "Vo"])

bulk_all_df["High20"] = bulk_all_df.groupby("Code")["H"].transform(lambda x: x.shift(1).rolling(20).max())

bulk_all_df["High55"] = bulk_all_df.groupby("Code")["H"].transform(lambda x: x.shift(1).rolling(55).max())

bulk_all_df["Vol20"] = bulk_all_df.groupby("Code")["Vo"].transform(lambda x: x.shift(1).rolling(20).mean())

bulk_all_df["VolRatio"] = bulk_all_df["Vo"] / bulk_all_df["Vol20"]

bulk_all_df["Break55Pct"] = (bulk_all_df["C"] / bulk_all_df["High55"] - 1) * 100
bulk_all_df["Break20Pct"] = (bulk_all_df["C"] / bulk_all_df["High20"] - 1) * 100

bulk_all_df["Break20"] = bulk_all_df["C"] > bulk_all_df["High20"]

bulk_all_df["Break55"] = bulk_all_df["C"] > bulk_all_df["High55"]

latest_date = bulk_all_df["Date"].max()

latest_df = bulk_all_df[bulk_all_df["Date"] == latest_date].copy()

break20_df = latest_df[latest_df["Break20"] == True].copy()

break55_df = latest_df[latest_df["Break55"] == True].copy()

break20_vol_df = break20_df[break20_df["VolRatio"] >= 1.5].copy()
break55_vol_df = break55_df[break55_df["VolRatio"] >= 1.5].copy()

break20_display_df = break20_vol_df[["Code", "C", "High20", "Break20Pct", "Vo", "Vol20", "VolRatio"]].copy()
break20_display_df = break20_display_df.sort_values("VolRatio", ascending=False)
break20_display_df = break20_display_df.reset_index(drop=True)
break20_display_df.index = break20_display_df.index + 1
break20_display_df = break20_display_df.rename(columns={
    "Code": "銘柄コード",
    "C": "終値",
    "High20": "20日高値",
    "Break20Pct": "20日高値上抜け率(%)",
    "Vo": "最新出来高",
    "Vol20": "20日平均出来高",
    "VolRatio": "出来高倍率",
})
break55_display_df = break55_vol_df[["Code", "C", "High55", "Break55Pct", "Vo", "Vol20", "VolRatio"]].copy()
break55_display_df = break55_display_df.sort_values("VolRatio", ascending=False)
break55_display_df = break55_display_df.rename(columns={
    "Code": "銘柄コード",
    "C": "終値",
    "High55": "55日高値",
    "Break55Pct": "55日高値上抜け率(%)",
    "Vo": "最新出来高",
    "Vol20": "20日平均出来高",
    "VolRatio": "出来高倍率",
})

early_break20_df = break20_vol_df[(break20_vol_df["Break20Pct"] >= 0) & (break20_vol_df["Break20Pct"] <= 3)].copy()
early_break20_df["AvgTradingValue20"] = early_break20_df["C"] * early_break20_df["Vol20"]
early_break20_df = early_break20_df[early_break20_df["AvgTradingValue20"] >= 100_000_000].copy()
early_break20_df["ToHigh55Pct"] = (early_break20_df["High55"] / early_break20_df["C"] - 1) * 100
evolution55_df = early_break20_df[(early_break20_df["ToHigh55Pct"] > 0) & (early_break20_df["ToHigh55Pct"] <= 5)].copy()
evolution55_df = evolution55_df.sort_values("ToHigh55Pct", ascending=True)
evolution55_df = evolution55_df.reset_index(drop=True)
evolution55_df.index = evolution55_df.index + 1
evolution55_df = evolution55_df.merge(name_map_df, on="Code", how="left")
evolution55_df = evolution55_df.reset_index(drop=True)
evolution55_df.index = evolution55_df.index + 1
evolution55_display_df = evolution55_df[["Code", "CoName", "C", "Break20Pct", "ToHigh55Pct", "VolRatio", "AvgTradingValue20"]].copy()
evolution55_display_df = evolution55_display_df.rename(columns={"Code": "銘柄コード", "CoName": "銘柄名", "C": "終値", "Break20Pct": "20日高値上抜け率(%)", "ToHigh55Pct": "55日高値まであと(%)", "VolRatio": "出来高倍率", "AvgTradingValue20": "20日平均売買代金"})
evolution55_display_df = evolution55_display_df.round(2)
evolution55_display_df["予兆Score"] = evolution55_display_df["出来高倍率"] / (1 + evolution55_display_df["55日高値まであと(%)"])
evolution55_display_df = evolution55_display_df.sort_values("予兆Score", ascending=False)
evolution55_display_df = evolution55_display_df.reset_index(drop=True)
evolution55_display_df.index = evolution55_display_df.index + 1
evolution55_display_df["予兆Score"] = evolution55_display_df["予兆Score"].round(2)

early_break20_display_df = early_break20_df[["Code", "C", "High20", "Break20Pct", "Vo", "Vol20", "AvgTradingValue20", "VolRatio"]].copy()
early_break20_display_df = early_break20_display_df.sort_values("VolRatio", ascending=False)
early_break20_display_df = early_break20_display_df.reset_index(drop=True)
early_break20_display_df.index = early_break20_display_df.index + 1
early_break20_display_df = early_break20_display_df.merge(name_map_df, on="Code", how="left")
early_break20_display_df.index = early_break20_display_df.index + 1
early_break20_display_df = early_break20_display_df.rename(columns={"CoName": "銘柄名"})
early_break20_display_df = early_break20_display_df[["Code", "銘柄名", "C", "High20", "Break20Pct", "Vo", "Vol20", "AvgTradingValue20", "VolRatio"]]
early_break20_display_df["AvgTradingValue20"] = early_break20_display_df["AvgTradingValue20"] / 100_000_000
early_break20_display_df = early_break20_display_df.rename(columns={"AvgTradingValue20": "20日平均売買代金(億円)"})
early_break20_display_df = early_break20_display_df.rename(columns={
        "Code": "銘柄コード",
        "C": "終値",
        "High20": "20日高値",
        "Break20Pct": "20日高値上抜け率(%)",
        "Vo": "最新出来高",
        "Vol20": "20日平均出来高",
        "VolRatio": "出来高倍率",
})
early_break20_display_df["TurtleScore"] = early_break20_display_df["出来高倍率"] / (1 + early_break20_display_df["20日高値上抜け率(%)"])
early_break20_score_df = early_break20_display_df.sort_values("TurtleScore", ascending=False).copy()
early_break20_score_df = early_break20_score_df.reset_index(drop=True)
early_break20_score_df.index = early_break20_score_df.index + 1

early_break55_df = break55_vol_df[(break55_vol_df["Break55Pct"] >= 0) & (break55_vol_df["Break55Pct"] <= 3)].copy()

early_break55_display_df = early_break55_df[["Code", "C", "High55", "Break55Pct", "Vo", "Vol20", "VolRatio"]].copy()
early_break55_display_df["AvgTradingValue20"] = early_break55_display_df["C"] * early_break55_display_df["Vol20"]
early_break55_display_df = early_break55_display_df[early_break55_display_df["AvgTradingValue20"] >= 100_000_000].copy()
early_break55_display_df = early_break55_display_df.sort_values("VolRatio", ascending=False)
early_break55_display_df = early_break55_display_df.reset_index(drop=True)
early_break55_display_df.index = early_break55_display_df.index + 1
early_break55_price_df = early_break55_display_df.sort_values("Break55Pct", ascending=True).copy()
early_break55_price_df = early_break55_price_df.reset_index(drop=True)
early_break55_price_df.index = early_break55_price_df.index + 1
early_break55_display_df["TurtleScore"] = early_break55_display_df["VolRatio"] / (1 + early_break55_display_df["Break55Pct"])
early_break55_score_df = early_break55_display_df.sort_values("TurtleScore", ascending=False).copy()
early_break55_score_df = early_break55_score_df.merge(name_map_df, on="Code", how="left")
early_break55_score_df = early_break55_score_df.rename(columns={"CoName": "銘柄名"})
early_break55_score_df = early_break55_score_df.reset_index(drop=True)
early_break55_score_df.index = early_break55_score_df.index + 1
early_break55_score_df = early_break55_score_df[["Code", "銘柄名", "C", "High55", "Break55Pct", "Vo", "Vol20", "AvgTradingValue20", "VolRatio", "TurtleScore"]]
early_break55_score_df["AvgTradingValue20"] = early_break55_score_df["AvgTradingValue20"] / 100_000_000
early_break55_score_df = early_break55_score_df.rename(columns={
    "Code": "銘柄コード",
    "C": "終値",
    "High55": "55日高値",
    "Break55Pct": "55日高値上抜け率(%)",
    "Vo": "最新出来高",
    "Vol20": "20日平均出来高",
    "AvgTradingValue20": "20日平均売買代金(億円)",
    "VolRatio": "出来高倍率",
})

early_break55_display_df = early_break55_display_df.rename(columns={
    "Code": "銘柄コード",
    "C": "終値",
    "High55": "55日高値",
    "Break55Pct": "55日高値上抜け率(%)",
    "Vo": "最新出来高",
    "Vol20": "20日平均出来高",
    "VolRatio": "出来高倍率",
})

common_codes = set(early_break20_score_df["銘柄コード"]) & set(early_break55_score_df["銘柄コード"])
common_df = early_break55_score_df[early_break55_score_df["銘柄コード"].isin(common_codes)].copy()
common20_info = early_break20_score_df[["銘柄コード", "20日高値上抜け率(%)", "TurtleScore"]].copy()
common20_info = common20_info.rename(columns={"TurtleScore": "20日TurtleScore"})
common_df = common_df.merge(common20_info, on="銘柄コード", how="left")
common_df = common_df.rename(columns={"TurtleScore": "55日TurtleScore"})
common_df["総合TurtleScore"] = (common_df["20日TurtleScore"] + common_df["55日TurtleScore"]) / 2
common_df["進化差"] = common_df["20日高値上抜け率(%)"] - common_df["55日高値上抜け率(%)"]
common_df = common_df.sort_values("総合TurtleScore", ascending=False)
evolution_df = common_df[common_df["進化差"] > 0].copy()
evolution_df = evolution_df.sort_values("進化差", ascending=False)
evolution_df = evolution_df.reset_index(drop=True)
evolution_df.index = evolution_df.index + 1
common_df = common_df.reset_index(drop=True)
common_df.index = common_df.index + 1
evolution_df = evolution_df.rename(columns={"55日TurtleScore": "55日Score", "20日TurtleScore": "20日Score"})
evolution_df = evolution_df[["銘柄コード", "銘柄名", "終値", "20日高値上抜け率(%)", "55日高値上抜け率(%)", "進化差", "出来高倍率", "20日Score", "55日Score", "総合TurtleScore"]]
evolution_df = evolution_df.round(2)
common_df = common_df.rename(columns={"55日TurtleScore": "55日Score", "20日TurtleScore": "20日Score"})
common_df = common_df[["銘柄コード", "銘柄名", "終値", "20日高値上抜け率(%)", "55日高値上抜け率(%)", "出来高倍率", "20日平均売買代金(億円)", "20日Score", "55日Score", "進化差","総合TurtleScore"]]

common_df = common_df.round({"20日高値上抜け率(%)": 2, "55日高値上抜け率(%)": 2, "出来高倍率": 2, "20日平均売買代金(億円)": 2, "20日Score": 2, "55日Score": 2, "進化差": 2, "総合TurtleScore": 2})

st.header("🐢 Turtle メインスクリーナー")
st.subheader("🚀 20日突破 → 55日ブレイク直前候補")
st.write("🎯 55日ブレイク直前候補数：", len(evolution55_display_df))
st.dataframe(evolution55_display_df, use_container_width=True)
st.subheader("🏆 20日TurtleScoreランキング")
st.dataframe(early_break20_score_df, use_container_width=True)
st.subheader("🏆 55日TurtleScoreランキング")
st.dataframe(early_break55_score_df, use_container_width=True)
st.subheader("🐢 20日＋55日 共通モメンタム候補")
st.write("🎯 共通モメンタム候補数：", len(common_df))
st.dataframe(common_df, use_container_width=True)
