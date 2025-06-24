import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="スクリーニング", layout="wide")
st.title("📈 [ルール1]スクリーニング")

# データ取得関数
def load_data(source):
    try:
        url = "https://app.kumagai-stock.com/api/highlow/today" if source == "today" else "https://app.kumagai-stock.com/api/highlow/yesterday"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return pd.DataFrame(res.json())
    except:
        return pd.DataFrame()

# ラジオボタン選択
option = st.radio("表示対象を選んでください", ["本日の抽出結果", "昨日の抽出結果"], horizontal=True)
data_source = "today" if option == "本日の抽出結果" else "yesterday"
df = load_data(data_source)

# 表示処理
if df.empty:
    st.info("データがありません。")
else:
    try:
        # カラム整形
        df = df[["code", "name", "low", "low_date", "high", "high_date", "倍率"]]
        df.columns = ["銘柄コード", "企業名", "安値", "安値日", "高値", "高値日", "倍率"]
        df["倍率"] = pd.to_numeric(df["倍率"], errors="coerce").map(lambda x: f"{x:.2f}倍")

        # 銘柄コード列にHTMLリンクを埋め込み
        df["銘柄コード"] = df["銘柄コード"].apply(
            lambda code: f'<a href="https://kabuka-check-app.onrender.com/?code={code}" target="_blank">{code}</a>'
        )

        # HTML形式で表を表示（スクロール不要＆リンク有効）
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"データ整形中のエラー: {e}")
st.markdown("---")
st.markdown("<h4>📌 <strong>注意事項</strong></h4>", unsafe_allow_html=True)

st.markdown("""
<div style='color:red; font-size:14px;'>
<ul>
  <li>抽出結果にはETFなどルール1対象でないものも表示されます。</li>
  <li>平日8時30分～9時に5分程度のメンテナンスが入ることがあります。</li>
  <li>「本日の抽出結果」はおおよそ1時間ごとの更新となります。</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style='
    text-align: center;
    color: gray;
    font-size: 14px;
    font-family: "Segoe UI", "Helvetica Neue", "Arial", sans-serif !important;
    letter-spacing: 0.5px;
    unicode-bidi: plaintext;
'>
&copy; 2025 KumagaiNext All rights reserved.
</div>
""", unsafe_allow_html=True)

