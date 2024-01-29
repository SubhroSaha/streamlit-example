# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 20:30:49 2024

@author: Subhro Saha
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, TrailingStrategy
from backtesting.test import SMA
import pandas_ta as ta
import backtesting
backtesting.set_bokeh_output(notebook=False)
from backtesting.lib import plot_heatmaps
import yfinance as yf

date_from = datetime(2023, 1, 1)
date_to = datetime.now()

yfdf = yf.download('RVNL.NS', start=date_from, end=date_to, interval='1d')

class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 5
    n2 = 15    
    
    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)
        self.atr = self.I(ta.atr, self.data.High.s, self.data.Low.s, self.data.Close.s, 14)
        # print(self.atr[-1])
    
    def next(self):
        price = self.data.Close[-1]
        atr = self.atr[-1]
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


class SmaCrossTrailing(TrailingStrategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 5
    n2 = 15    
    
    def init(self):
        super().init()
        super().set_trailing_sl(4)
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)
        self.atr = self.I(ta.atr, self.data.High.s, self.data.Low.s, self.data.Close.s, 14)
        # print(self.atr[-1])
    
    def next(self):
        super().next()
        price = self.data.Close[-1]
        atr = self.atr[-1]
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
            
class Supertrend(Strategy):
    n1 = 10
    n2 = 3
    
    def init(self):
        self.suptrend = self.I(ta.supertrend, self.data.High.s, self.data.Low.s, self.data.Close.s, self.n1, self.n2)
        self.atr = self.I(ta.atr, self.data.High.s, self.data.Low.s, self.data.Close.s, 14)
                    
    def next(self):
        price = self.data.Close[-1]
        atr = self.atr[-1]
        sl_multiplier = 1
        tp_multiplier = 15
        if self.suptrend[1][-1] == 1 and self.suptrend[1][-2] == -1:
            self.position.close()
            self.buy()
            # self.buy(sl = price - sl_multiplier*atr, tp = price + tp_multiplier*atr)
        
        elif self.suptrend[1][-1] == -1 and self.suptrend[1][-2] == 1:
            self.position.close()
            self.sell()
            # self.sell(sl = price + sl_multiplier*atr, tp = price - tp_multiplier*atr)

class SupertrendTrailing(TrailingStrategy):
    n1 = 10
    n2 = 3
    
    def init(self):
        super().init()
        super().set_trailing_sl(5)
        self.suptrend = self.I(ta.supertrend, self.data.High.s, self.data.Low.s, self.data.Close.s, self.n1, self.n2)
        self.atr = self.I(ta.atr, self.data.High.s, self.data.Low.s, self.data.Close.s, 14)
                    
    def next(self):
        super().next()
        price = self.data.Close[-1]
        atr = self.atr[-1]
        sl_multiplier = 1
        tp_multiplier = 15
        if self.suptrend[1][-1] == 1 and self.suptrend[1][-2] == -1:
            self.position.close()
            self.buy()
            # self.buy(sl = price - sl_multiplier*atr, tp = price + tp_multiplier*atr)
        
        elif self.suptrend[1][-1] == -1 and self.suptrend[1][-2] == 1:
            self.position.close()
            self.sell()
            # self.sell(sl = price + sl_multiplier*atr, tp = price - tp_multiplier*atr)
            
bt = Backtest(yfdf, SmaCross, cash=100000)

stats, heatmap = bt.optimize(n1=range(1, 10, 1),
                    n2=range(1, 10, 1),
                    maximize='Equity Final [$]',
                    constraint=lambda param: param.n1 < param.n2,
                    random_state=0,
                    return_heatmap=True)

strategy = stats._strategy
equity_curve = stats._equity_curve
trades = pd.DataFrame(stats._trades)

# import seaborn as sns
# hm = heatmap.unstack()
# Plot on Spyder
# sns.heatmap(hm)

# Plot on browser
# plot_heatmaps(heatmap, agg='mean')

# Plot Strategy graph
# bt.plot()

# print(stats)
# print(strategy)

st.dataframe(trades)  # Same as st.write(df)