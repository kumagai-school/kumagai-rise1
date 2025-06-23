
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="上昇銘柄リスト", layout="wide")

def load_data(source):
    try:
        url = "https://app.kumagai-stock.com/api/highlow/today" if source == "today" else "https://app.kumagai-stock.com/api/highlow/yesterday"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        st.subheader("📦 デバッグ：JSONレスポンス")
        st.json(data)

        df = pd.DataFrame(data)
        st.subheader("📋 デバッグ：DataFrame表示")
        st.write(df)
        st.write("📑 カラム一覧:", df.columns.tolist())
        return df
    except Exception as e:
        st.error(f"データ取得エラー: {e}")
        return pd.DataFrame()

st.title("📈 上昇銘柄 抽出リスト")
option = st.radio("表示対象を選んでください", ["本日の抽出", "昨日の抽出"], horizontal=True)

data_source = "today" if option == "本日の抽出" else "yesterday"
df = load_data(data_source)

if df.empty:
    st.info("データがありません。")
else:
    try:
        df = df[["code", "low", "low_date", "high", "high_date", "倍率"]]
        df.columns = ["銘柄コード", "最安値", "最安値日", "高値", "高値日", "倍率"]
        df["倍率"] = pd.to_numeric(df["倍率"], errors="coerce").map(lambda x: f"{x:.2f}倍")
        df["銘柄コード"] = df["銘柄コード"].apply(lambda x: f"[{x}](https://www.google.com/search?q={x}+株価)")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"データ整形中のエラー: {e}")
