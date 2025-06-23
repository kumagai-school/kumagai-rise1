import streamlit as st
import pandas as pd
import requests

# APIエンドポイント（Tower設置PC経由）
API_URL = "https://app.kumagai-stock.com/api/highlow/batch"

# ページ設定
st.set_page_config(page_title="上昇銘柄抽出", layout="wide")

st.title("📈 上昇銘柄抽出（2週間以内の最安値 → 高値）")
st.caption("※ Tower API（Cloudflare Tunnel 経由）と連携してリアルタイム表示")

# データ取得
try:
    res = requests.get(API_URL, timeout=10)
    res.raise_for_status()
    data = res.json()

    if not data:
        st.info("該当はありません。")
    else:
        # DataFrameに変換
        df = pd.DataFrame(data)

        # 日付整形
        df["高値日"] = pd.to_datetime(df["high_date"], format="%Y%m%d").dt.strftime("%Y/%m/%d")
        df["安値日"] = pd.to_datetime(df["low_date"], format="%Y%m%d").dt.strftime("%Y/%m/%d")

        # 列整形と並び替え
        df_display = df[["code", "name", "low", "安値日", "high", "高値日"]].copy()
        df_display.columns = ["銘柄コード", "銘柄名", "安値", "安値日", "高値", "高値日"]

        # 倍率計算・追加（小数第2位まで）
        df_display["倍率"] = (df["high"] / df["low"]).apply(lambda x: f"{x:.2f} 倍")

        # 銘柄コードをリンクに
        df_display["銘柄コード"] = df_display["銘柄コード"].apply(
            lambda code: f"[{code}](https://kabuka-check-app.onrender.com/?code={code})"
        )

        # 行番号を1から
        df_display.index = range(1, len(df_display) + 1)

        # 表示
        st.table(df_display)

except Exception as e:
    st.error(f"データ取得エラー: {e}")
