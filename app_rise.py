import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="上昇銘柄リスト", layout="wide")
st.title("📈 上昇銘柄 抽出リスト")

# データ取得関数
def load_data(source):
    try:
        url = "https://app.kumagai-stock.com/api/highlow/today" if source == "today" else "https://app.kumagai-stock.com/api/highlow/yesterday"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return pd.DataFrame(res.json())
    except:
        return pd.DataFrame()

# ラジオボタン
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

        # 銘柄コードをリンク付きHTMLで表示（Renderの詳細ページに遷移）
        df["銘柄コード"] = df["銘柄コード"].apply(
            lambda code: f'<a href="https://kabuka-check-app.onrender.com/?code={code}" target="_blank">{code}</a>'
        )

        # 表をHTMLとして描画（スクロールなし）
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"データ整形中のエラー: {e}")
