import streamlit as st
import akshare as ak
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from xgboost import XGBClassifier
import joblib
import talib
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

def add_features(df):
    df['MA5'] = talib.SMA(df['close'], timeperiod=5)
    df['RSI'] = talib.RSI(df['close'], timeperiod=14)
    df['MACD'], _, _ = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    return df

def prepare_data(df):
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
    df = add_features(df)
    df.dropna(inplace=True)
    return df

st.set_page_config(page_title="stock predicate", layout="wide")
st.title("stock predicate")

stock_code = st.text_input("pls enter stock symbol (e.g.600919)", "600919")
start_date = st.date_input("start date", pd.to_datetime("2025-01-01"))
end_date = st.date_input("end_date", pd.to_datetime("2025-07-08"))

if st.button("start prediction"):
  ##  try:
        st.info("fetching and processing data...")

        df_raw = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date.strftime('%Y%m%d'),
                                    end_date=end_date.strftime('%Y%m%d'), adjust="qfq")
        df = df_raw.rename(columns={
                "开盘", "open",
                "收盘", "close"
                "最高", "high"
                "最低", "low"
                "成交量", "volume",
                "日期", "date"
                })
        df['date'] = pd.to_datetime(df['date'])
        df.set_index("date", inplace=True)
        df = prepare_data(df)

        features = ['MA5', 'RSI', 'MACD']
        X = df[features]
        y = df['target']

        X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)

        model = XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.1)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)

        print("prediction accuracy: {acc:.2f}")
        st.success(f"prediction accuracy: {acc:.2f}")
        print(df)
        print(len(y_pred))

        df.loc[X_test.index, 'pred'] = y_pred
        df.loc[X_test.index, 'correct'] = df.loc[X_test.index, 'pred'] == df.loc[X_test.index, 'target']
        print(df)

        fig = go.Figure(data=[
            go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name="K stick"
                )
            ])
        df.dropna(inplace=True)
        correct_df = df[df['correct'] & (df['pred'] == 1)]
        fig.add_trace(go.Scatter(
            x=correct_df.index,
            y=correct_df['close'],
            mode = 'markers',
            marker = dict(symbol='triangle-up', color='green', size=10),
            name = 'prediction up correct'
            ))

        wrong_df = df [~df['correct'] & (df['pred'] == 1)]
        fig.add_trace(go.Scatter(
            x=wrong_df.indec,
            y=wrong_df['close'],
            mode='markers',
            marker=dict(symbol='triangle-down', color='red', size=10),
            name='prediction up wrong'
            ))
        st.plotly_chart(fig, use_container_width=True)
        st.caption("risk on your own")
##    except Exception as e:
##        st.error(f" ai ya: {e}")
