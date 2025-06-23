
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="上昇銘柄リスト", layout="wide")

def load_data(source):
    try:
        if source == "today":
            url = "https://app.kumagai-stock.com/api/highlow/today"
        else:
            url = "https://app.kumagai-stock.com/api/highlow/yesterday"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return pd.DataFrame(res.json())
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
    df = df[["code", "low", "low_date", "high", "high_date", "倍率"]]
    df.columns = ["銘柄コード", "最安値", "最安値日", "高値", "高値日", "倍率"]
    df["倍率"] = df["倍率"].map(lambda x: f"{x:.2f}倍")
    df["銘柄コード"] = df["銘柄コード"].apply(lambda x: f"[{x}](https://www.google.com/search?q={x}+株価)")
    st.dataframe(df, use_container_width=True)

st.markdown("<div style='text-align: center; color: gray; font-size: 14px;'>© 2025 KumagaiNext All rights reserved.</div>", unsafe_allow_html=True)
