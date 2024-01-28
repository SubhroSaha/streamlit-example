import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

"""
# Welcome to Streamlit!

Edit `/streamlit_app.py` to customize this app to your heart's desire :heart:.
If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
forums](https://discuss.streamlit.io).

In the meantime, below is an example of what you can do with just a few lines of code:
"""

num_points = st.slider("Number of points in spiral", 1, 10000, 1100)
num_turns = st.slider("Number of turns in spiral", 1, 300, 31)

indices = np.linspace(0, 1, num_points)
theta = 2 * np.pi * num_turns * indices
radius = indices

x = radius * np.cos(theta)
y = radius * np.sin(theta)

df = pd.DataFrame({
    "x": x,
    "y": y,
    "idx": indices,
    "rand": np.random.randn(num_points),
})

st.altair_chart(alt.Chart(df, height=700, width=700)
    .mark_point(filled=True)
    .encode(
        x=alt.X("x", axis=None),
        y=alt.Y("y", axis=None),
        color=alt.Color("idx", legend=None, scale=alt.Scale()),
        size=alt.Size("rand", legend=None, scale=alt.Scale(range=[1, 150])),
    ))


# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 23:13:34 2024

@author: Subhro Saha
"""

import MetaTrader5 as mt
from datetime import datetime
import pandas as pd, numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, TrailingStrategy
from backtesting.test import SMA
import pandas_ta as ta
import backtesting
backtesting.set_bokeh_output(notebook=False)
from backtesting.lib import plot_heatmaps
import yfinance as yf
import heikinAishi
import seaborn as sns
import datetime as dt
import tickers as tk

# tickers = ['BANKINDIA.NS','KAUSHALYA.NS','ZOMATO.NS','JPASSOCIAT.NS','QUICKHEAL.NS']
tickers = tk.CA_Arvind_Mangal_top5
# start = dt.datetime.today() - dt.timedelta(5)
# end = dt.datetime.today()
period = '365d'
interval = '1d'
ohlcv_data = {}

for ticker in tickers:
    ohlcv_data[ticker] = yf.download(ticker, period=period, interval=interval)
    
# yfdfhk = heikinAishi.getHeikinAishi(yfdf)

# yfdf['ATR'] = ta.atr(yfdf['High'], yfdf['Low'], yfdf['Close'], 14)

class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 5
    n2 = 15    
    
    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)
        # self.atr = self.I(ta.atr, self.data.High.s, self.data.Low.s, self.data.Close.s, 14)
        # print(self.atr[-1])
    
    def next(self):
        price = self.data.Close[-1]
        # atr = self.atr[-1]
        sl_multiplier = 3
        tp_multiplier = 15
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()
            # self.buy(sl = price - sl_multiplier*atr, tp = price + tp_multiplier*atr)

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()
            # self.sell(sl = price + sl_multiplier*atr, tp = price - tp_multiplier*atr)
            
bt = {}
for ticker in tickers:
    bt[ticker] = Backtest(ohlcv_data[ticker], SmaCross, cash=100000)

stats = {}
for ticker in tickers:
    stats[ticker] = bt[ticker].optimize(n1=range(1, 10, 2),
                        n2=range(1, 20, 2),
                        maximize='Equity Final [$]',
                        constraint=lambda param: param.n1 < param.n2,
                        random_state=0,)
    
# print(stats['RVNL.NS'])

# strategy = stats._strategy
# equity_curve = stats._equity_curve
# trades = stats._trades

performance = {    
    "StockName": [],
    "Start": [],
    "End": [],
    "Duration": [],
    "Exposure Time [%]": [],
    "Equity Final [$]": [],
    "Equity Peak [$]": [],
    "Return [%]": [],
    "Buy & Hold Return [%]": [],
    "Return (Ann.) [%]": [],
    "Volatility (Ann.) [%]": [],
    "Sharpe Ratio": [],
    "Sortino Ratio": [],
    "Calmar Ratio": [],
    "Max. Drawdown [%]": [],
    "Avg. Drawdown [%]": [],
    "Max. Drawdown Duration": [],
    "Avg. Drawdown Duration": [],
    "# Trades": [],
    "Win Rate [%]": [],
    "Best Trade [%]": [],
    "Worst Trade [%]": [],
    "Avg. Trade [%]": [],
    "Max. Trade Duration": [],
    "Avg. Trade Duration": [],
    "Profit Factor": [],
    "Expectancy [%]": [],
    "SQN": [],
}

for ticker in tickers:
    performance['StockName'].append(ticker)
    performance["Start"].append(stats[ticker]["Start"])
    performance["End"].append(stats[ticker]["End"])
    performance["Duration"].append(stats[ticker]["Duration"])
    performance["Exposure Time [%]"].append(stats[ticker]["Exposure Time [%]"])
    performance["Equity Final [$]"].append(stats[ticker]["Equity Final [$]"])
    performance["Equity Peak [$]"].append(stats[ticker]["Equity Peak [$]"])
    performance["Return [%]"].append(stats[ticker]["Return [%]"])
    performance["Buy & Hold Return [%]"].append(stats[ticker]["Buy & Hold Return [%]"])
    performance["Return (Ann.) [%]"].append(stats[ticker]["Return (Ann.) [%]"])
    performance["Volatility (Ann.) [%]"].append(stats[ticker]["Volatility (Ann.) [%]"])
    performance["Sharpe Ratio"].append(stats[ticker]["Sharpe Ratio"])
    performance["Sortino Ratio"].append(stats[ticker]["Sortino Ratio"])
    performance["Calmar Ratio"].append(stats[ticker]["Calmar Ratio"])
    performance["Max. Drawdown [%]"].append(stats[ticker]["Max. Drawdown [%]"])
    performance["Avg. Drawdown [%]"].append(stats[ticker]["Avg. Drawdown [%]"])
    performance["Max. Drawdown Duration"].append(stats[ticker]["Max. Drawdown Duration"])
    performance["Avg. Drawdown Duration"].append(stats[ticker]["Avg. Drawdown Duration"])
    performance["# Trades"].append(stats[ticker]["# Trades"])
    performance["Win Rate [%]"].append(stats[ticker]["Win Rate [%]"])
    performance["Best Trade [%]"].append(stats[ticker]["Best Trade [%]"])
    performance["Worst Trade [%]"].append(stats[ticker]["Worst Trade [%]"])
    performance["Avg. Trade [%]"].append(stats[ticker]["Avg. Trade [%]"])
    performance["Max. Trade Duration"].append(stats[ticker]["Max. Trade Duration"])
    performance["Avg. Trade Duration"].append(stats[ticker]["Avg. Trade Duration"])
    performance["Profit Factor"].append(stats[ticker]["Profit Factor"])
    performance["Expectancy [%]"].append(stats[ticker]["Expectancy [%]"])
    performance["SQN"].append(stats[ticker]["SQN"])
    
    
performance = pd.DataFrame(performance)
# performance.describe()
# print(performance.AnnualReturn.mean())

# Save the DataFrame to a CSV file
# performance.to_csv('sample_dataframe.csv', index=False)
# for ticker in tickers:
#     bt[ticker].plot()

st.table(performance)

# print(stats)
# print(annualReturn)
# print(strategy)