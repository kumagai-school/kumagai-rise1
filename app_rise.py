import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="スクリーニング", layout="wide")

st.markdown("""
    <h1 style='text-align:left; color:#2E86C1; font-size:26px; line-height:1.4em;'>
        『ルール1』<br>スクリーニングアプリ
    </h1>
    <h1 style='text-align:left; color:#000000; font-size:15px; line-height:1.4em;'>
        単純に「2週間以内で1.3-2倍に暴騰した銘柄」を抽出しています
    </h1>
""", unsafe_allow_html=True)

st.markdown("""
<div style='
    border: 1px solid red;
    background-color: #ffffff;
    padding: 12px;
    border-radius: 8px;
    font-size: 13px;
    color: #b30000;
    margin-bottom: 20px;
    line-height: 1.6em;
'>
<p>⚠️ 抽出された銘柄のすべてが「ルール1」に該当するわけではございません。</p>
<p>⚠️ ETF など「ルール1」対象外の銘柄も含まれています。</p>
<p>⚠️ 「本日の抽出結果」は約1時間ごとに更新されます。</p>
<p>⚠️ 平日8:30〜9:00の間に短時間のメンテナンスが入ることがあります。</p>
</div>
""", unsafe_allow_html=True)

# データ取得関数
def load_data(source):
    try:
        url_map = {
            "today": "https://app.kumagai-stock.com/api/highlow/today",
            "yesterday": "https://app.kumagai-stock.com/api/highlow/yesterday",
            "target2day": "https://app.kumagai-stock.com/api/highlow/target2day"
            "target3day": "https://app.kumagai-stock.com/api/highlow/target3day"
        }
        url = url_map.get(source, url_map["today"])
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return pd.DataFrame(res.json())
    except:
        return pd.DataFrame()

# 表示対象選択
option = st.radio("表示対象を選んでください", ["本日高値", "昨日高値", "2日前高値", "3日前高値"], horizontal=True)
data_source = {
    "本日高値": "today",
    "昨日高値": "yesterday",
    "2日前高値": "target2day"
    "3日前高値": "target3day"
}[option]
df = load_data(data_source)

if df.empty:
    st.info("データがありません。")
else:
    for _, row in df.iterrows():
        code_link = f'<a href="https://kabuka-check-app.onrender.com/?code={row["code"]}" target="_blank">{row["code"]}</a>'
        name = row.get("name", "")
        st.markdown(
            f"""
            <div style='
                border:1px solid #ccc;
                border-radius:10px;
                padding:10px;
                margin-bottom:10px;
                background:#f9f9f9;
                font-size:20px;
                line-height:1.6em;
            '>
                <b>{name}（{code_link}）</b>　
                <span style='color:#006400; font-weight:bold;'>{row["倍率"]:.2f}倍</span><br>
                📉 安値 ： {row["low"]}（{row["low_date"]}）<br>
                📈 高値 ： {row["high"]}（{row["high_date"]}）
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("""
<hr>
<h4>📍<strong>注意事項</strong></h4>
<div style='color:red; font-size:13px;'>
<ul>
  <li>ETFなど「ルール１」対象外の銘柄も表示されます。</li>
  <li>平日8時30分〜9時に10分程度のメンテナンスが入ることがあります。</li>
  <li>「本日の抽出結果」はおおよそ1時間ごとの更新となります。</li>
</ul>
</div>
<hr>
""", unsafe_allow_html=True)

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
