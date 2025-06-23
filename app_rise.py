# app_rise.py（Render向けAPI版）
import streamlit as st
import pandas as pd
import requests

# -----------------------
REALDATA_API = "https://app.kumagai-stock.com/api/real"
PASTDATA_API = "https://app.kumagai-stock.com/api/past"
# -----------------------

TARGET_EXCHANGES = {1, 2, 256}
MULTIPLE_THRESHOLD = 1.5
LOOKBACK_DAYS = 14

def load_realdata():
    res = requests.get(REALDATA_API)
    res.raise_for_status()
    df = pd.DataFrame(res.json())
    df['date'] = pd.to_datetime(df['date'])
    return df[df['market'].isin(TARGET_EXCHANGES)][['code', 'market', 'high', 'low', 'date']]

def load_past_data():
    res = requests.get(PASTDATA_API)
    res.raise_for_status()
    df = pd.DataFrame(res.json())
    df['date'] = pd.to_datetime(df['date'])
    return df[df['market'].isin(TARGET_EXCHANGES)][['code', 'market', 'high', 'low', 'date']]

def extract_rising_stocks(real_df, past_df):
    combined = pd.concat([real_df, past_df], ignore_index=True)
    results = []

    for (code, market), group in combined.groupby(['code', 'market']):
        if group['low'].min() <= 0:
            continue
        min_row = group.loc[group['low'].idxmin()]
        max_row = group.loc[group['high'].idxmax()]
        ratio = max_row['high'] / min_row['low']
        if 1.3 <= ratio <= 2.0 and max_row['date'] in real_df['date'].values:
            results.append({
                '銘柄コード': code,
                '最安値日': min_row['date'].date(),
                '最安値': f"{min_row['low']:.2f}",
                '最高値日': max_row['date'].date(),
                '最高値': f"{max_row['high']:.2f}",
                '倍率': f"{ratio:.2f}"
            })
    return pd.DataFrame(results)

def extract_yesterday_high_rise_stocks(real_df, past_df):
    combined = pd.concat([real_df, past_df], ignore_index=True)
    results = []

    available_dates = sorted(combined['date'].dropna().unique(), reverse=True)
    if len(available_dates) < 2:
        return pd.DataFrame()

    yesterday = available_dates[1]
    yesterday_data = combined[combined['date'] == yesterday]

    for (code, market), group in combined.groupby(['code', 'market']):
        if group['low'].min() <= 0:
            continue

        min_row = group.loc[group['low'].idxmin()]
        y_rows = yesterday_data[(yesterday_data['code'] == code) & (yesterday_data['market'] == market)]
        if y_rows.empty:
            continue

        y_high = y_rows['high'].values[0]
        max_high = group['high'].max()

        if y_high < max_high:
            continue

        ratio = y_high / min_row['low']
        if 1.3 <= ratio <= 2.0:
            results.append({
                '銘柄コード': code,
                '最安値日': min_row['date'].date(),
                '最安値': f"{min_row['low']:.2f}",
                '昨日（最高値）日': pd.to_datetime(yesterday).date(),
                '昨日の高値': f"{y_high:.2f}",
                '倍率': f"{ratio:.2f}"
            })

    df = pd.DataFrame(results)
    if not df.empty:
        df = df.sort_values(by="倍率", ascending=False)
    return df

# ---------------- Streamlit ----------------
st.title("📈「ルール１」スクリーニング")

with st.spinner("データ取得中..."):
    try:
        real_df = load_realdata()
        past_df = load_past_data()

        st.subheader("📌 本日の抽出結果")
        rise_today_df = extract_rising_stocks(real_df, past_df)
        if rise_today_df.empty:
            st.info("該当はありません")
        else:
            rise_today_df.index = range(1, len(rise_today_df)+1)
            st.table(rise_today_df)

        st.subheader("📌 昨日の抽出結果")
        rise_yesterday_df = extract_yesterday_high_rise_stocks(real_df, past_df)
        if rise_yesterday_df.empty:
            st.info("該当はありません")
        else:
            rise_yesterday_df.index = range(1, len(rise_yesterday_df)+1)
            st.table(rise_yesterday_df)
    except Exception as e:
        st.error(f"データ取得中にエラーが発生しました：{e}")
