# app_rise.py（本日＆昨日の抽出、Tower API連携）
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# APIエンドポイント
TODAY_API = "https://app.kumagai-stock.com/api/highlow/batch"
CANDLE_API = "https://app.kumagai-stock.com/api/candle?code={code}"

def fetch_today_data():
    res = requests.get(TODAY_API)
    res.raise_for_status()
    return pd.DataFrame(res.json())

def is_yesterday_high(candle_data, high_value):
    if not candle_data:
        return False
    try:
        df = pd.DataFrame(candle_data)
        df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
        df = df.sort_values("date", ascending=False)
        if len(df) < 2:
            return False
        yesterday = df.iloc[1]
        return yesterday["high"] == high_value
    except:
        return False

def fetch_yesterday_high(df_today):
    results = []
    for _, row in df_today.iterrows():
        code = row["code"]
        try:
            res = requests.get(CANDLE_API.format(code=code))
            if res.status_code != 200:
                continue
            candle_data = res.json().get("data", [])
            if is_yesterday_high(candle_data, row["high"]):
                results.append(row)
        except:
            continue
    return pd.DataFrame(results)

# Streamlit UI
st.title("📈「ルール１」スクリーニング")

with st.spinner("データを取得中..."):
    try:
        df_today = fetch_today_data()

        st.subheader("📌 本日の抽出結果")
        if df_today.empty:
            st.info("該当はありません")
        else:
            df_today.index = range(1, len(df_today)+1)
            st.table(df_today[["code", "name", "low_date", "low", "high_date", "high", "倍率"]])

        st.subheader("📌 昨日の抽出結果")
        df_yesterday = fetch_yesterday_high(df_today)
        if df_yesterday.empty:
            st.info("該当はありません")
        else:
            df_yesterday.index = range(1, len(df_yesterday)+1)
            st.table(df_yesterday[["code", "name", "low_date", "low", "high_date", "high", "倍率"]])

    except Exception as e:
        st.error(f"エラーが発生しました：{e}")
