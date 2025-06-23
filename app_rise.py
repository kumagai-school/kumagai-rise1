import streamlit as st
import pandas as pd
import requests

# APIエンドポイント
TODAY_API_URL = "https://app.kumagai-stock.com/api/highlow"
YESTERDAY_API_URL = "https://app.kumagai-stock.com/api/highlow/yesterday"

# 表示用関数
def fetch_and_display(api_url, label):
    st.subheader(label)
    try:
        res = requests.get(api_url, timeout=15)
        res.raise_for_status()
        data = res.json()

        if not data:
            st.info("該当はありません。")
            return

        df = pd.DataFrame(data)

        # 日付フォーマット
        df["高値日"] = pd.to_datetime(df["high_date"], format="%Y%m%d").dt.strftime("%Y/%m/%d")
        df["安値日"] = pd.to_datetime(df["low_date"], format="%Y%m%d").dt.strftime("%Y/%m/%d")

        # 表示用整形
        df_display = df[["code", "name", "low", "安値日", "high", "高値日"]].copy()
        df_display.columns = ["銘柄コード", "銘柄名", "安値", "安値日", "高値", "高値日"]

        # 倍率（小数点2桁）＋リンク
        df_display["倍率"] = (df["high"] / df["low"]).apply(lambda x: f"{x:.2f} 倍")
        df_display["銘柄コード"] = df_display["銘柄コード"].apply(
            lambda code: f"[{code}](https://kabuka-check-app.onrender.com/?code={code})"
        )

        # インデックス1スタート
        df_display.index = range(1, len(df_display) + 1)

        st.table(df_display)

    except Exception as e:
        st.error(f"データ取得エラー: {e}")

# アプリ表示
st.title("📈 [ルール１]スクリーニング")

# 昨日の抽出結果（JSON）
fetch_and_display(YESTERDAY_API_URL, "🔹 昨日の抽出結果")

with st.expander("🔸 本日の抽出結果（時間がかかる場合があります）"):
# 本日の抽出結果（リアルタイム）
fetch_and_display(TODAY_API_URL, "🔸 本日の抽出結果")

# フッター
st.markdown("<div style='text-align: center; color: gray; font-size: 14px;'>© 2025 KumagaiNext All rights reserved.</div>", unsafe_allow_html=True)
