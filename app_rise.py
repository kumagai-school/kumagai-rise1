import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

# ✅ 許可するパスワードを複数指定（リスト形式）
VALID_PASSWORDS = ["kuma", "0123"]

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    pwd = st.text_input("🔐 パスワードを入力してください", type="password")
    if pwd in VALID_PASSWORDS:
        st.session_state["authenticated"] = True
        st.rerun()  # ← 再描画して中身を表示
    elif pwd:
        st.error("パスワードが違います。")
    st.stop()

st.set_page_config(page_title="スクリーニング", layout="wide")

st.markdown("""
    <h1 style='text-align:left; color:#2E86C1; font-size:26px; line-height:1.4em;'>
        『ルール1』<br>スクリーニングアプリ
    </h1>
    <h1 style='text-align:left; color:#000000; font-size:15px; line-height:1.4em;'>
        「2週間以内で1.3～2倍に暴騰した銘柄」を抽出しています。
    </h1>
""", unsafe_allow_html=True)

st.markdown("""
<div style='
    background-color: #ffffff;
    padding: 12px;
    border-radius: 8px;
    font-size: 13px;
    color: #000000;
    margin-bottom: 20px;
    line-height: 1.6em;
'>
<p>銘柄名をクリックすると、「直近高値」「高値から過去2週間以内の安値」が表示されます。<br>
表示された画面下の「計算する」をクリックすると、「上昇率」「上げ幅」「上げ幅の半値」「上げ幅の半値押し」が算出されます。<br>
銘柄選別でご活用下さいませ。</p>
</div>
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
    line-height: 1.3em;
'>
<p style='margin: 6px 0;'>⚠️ 抽出された銘柄のすべてが「ルール1」に該当するわけではございません。</p>
<p style='margin: 6px 0;'>⚠️ ETF など「ルール1」対象外の銘柄も含まれています。</p>
<p style='margin: 6px 0;'>⚠️ 「本日の抽出結果」は約1時間ごとに更新されます。</p>
<p style='margin: 6px 0;'>⚠️ 平日8:30〜9:00の間に短時間のメンテナンスが入ることがあります。</p>
<p style='margin: 6px 0;'>⚠️ 表示されるチャートは昨日までの日足チャートです。</p>
<p style='margin: 6px 0;'>⚠️株式分割や株式併合などがあった場合、過去の株価は分割・併合を考慮しておりません。</p>
</div>
""", unsafe_allow_html=True)

def load_data(source):
    try:
        url_map = {
            "today": "https://app.kumagai-stock.com/api/highlow/today",
            "yesterday": "https://app.kumagai-stock.com/api/highlow/yesterday",
            "target2day": "https://app.kumagai-stock.com/api/highlow/target2day",
            "target3day": "https://app.kumagai-stock.com/api/highlow/target3day",
            "target4day": "https://app.kumagai-stock.com/api/highlow/target4day",
            "target5day": "https://app.kumagai-stock.com/api/highlow/target5day"
        }
        url = url_map.get(source, url_map["today"])
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return pd.DataFrame(res.json())
    except:
        return pd.DataFrame()

option = st.radio("『高値』付けた日を選んでください", ["本日", "昨日", "2日前", "3日前", "4日前", "5日前"], horizontal=True)
data_source = {
    "本日": "today",
    "昨日": "yesterday",
    "2日前": "target2day",
    "3日前": "target3day",
    "4日前": "target4day",
    "5日前": "target5day"
}[option]

df = load_data(data_source)

if df.empty:
    st.info("データがありません。")
else:
    for _, row in df.iterrows():
        code = row["code"]
        name = row.get("name", "")
        code_link = f"https://kabuka-check-app.onrender.com/?code={code}"
        multiplier_html = f"<span style='color:green; font-weight:bold;'>{row['倍率']:.2f}倍</span>"

        st.markdown("<hr style='border-top: 2px solid #ccc;'>", unsafe_allow_html=True)

        st.markdown(f"""
            <div style='font-size:18px; line-height:1.6em;'>
                <b><a href="{code_link}" target="_blank">{name}（{code}）</a></b>　
                {multiplier_html}<br>
                📉 安値 ： {row["low"]}（{row["low_date"]}）<br>
                📈 高値 ： {row["high"]}（{row["high_date"]}）
            </div>
        """, unsafe_allow_html=True)

        try:
            candle_url = "https://app.kumagai-stock.com/api/candle"
            resp = requests.get(candle_url, params={"code": code})
            chart_data = resp.json().get("data", [])

            if chart_data:
                df_chart = pd.DataFrame(chart_data)
                df_chart["date_str"] = pd.to_datetime(df_chart["date"]).dt.strftime("%Y-%m-%d")

                fig = go.Figure(data=[
                    go.Candlestick(
                        x=df_chart["date_str"],
                        open=df_chart["open"],
                        high=df_chart["high"],
                        low=df_chart["low"],
                        close=df_chart["close"],
                        increasing_line_color='red',
                        decreasing_line_color='blue',
                        hoverinfo="skip"
                    )
                ])
                fig.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10),
                    xaxis=dict(visible=False, type="category"),
                    yaxis=dict(visible=False),
                    xaxis_rangeslider_visible=False,
                    height=200,
                    plot_bgcolor='#f8f8f8',  # チャート背景を薄いグレーに
                    paper_bgcolor='#f8f8f8'
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "staticPlot": True})
            else:
                st.caption("（チャートデータなし）")
        except Exception as e:
            st.caption(f"（エラー: {e}）")

    st.markdown("<hr style='border-top: 2px solid #ccc;'>", unsafe_allow_html=True)

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
<p>※ピックアップチャートの銘柄については、あくまで「ルール1」銘柄のレッスンとなります。</p>
<p>※特定の取引を推奨するものではなく、銘柄の助言ではございません。</p>
<p>※本サービスは利益を保証するものではなく、投資にはリスクが伴います。投資の際は自己責任でよろしくお願いいたします。</p>
</div>
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