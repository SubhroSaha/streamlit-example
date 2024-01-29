# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 20:30:49 2024

@author: Subhro Saha
"""

import streamlit as st
from datetime import datetime
import pandas as pd, numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas_ta as ta
import backtesting
backtesting.set_bokeh_output(notebook=False)
from backtesting.lib import plot_heatmaps
import yfinance as yf

date_from = datetime(2023, 1, 1)
date_to = datetime.now()
yfdf = yf.download('RVNL.NS', start=date_from, end=date_to, interval='1d')

class SmaCross(Strategy):
    n1 = 5
    n2 = 15    
    
    def init(self):
        self.sma1 = self.I(ta.sma, self.data.Close.s, self.n1)
        self.sma2 = self.I(ta.sma, self.data.Close.s, self.n2)
    
    def next(self):
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()
            
bt = Backtest(yfdf, SmaCross, cash=100000)
stats = bt.run()
equity_curve = stats._equity_curve
trades = stats._trades
st.dataframe(trades)  # Same as st.write(df)