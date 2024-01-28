# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 21:51:26 2024

@author: Subhro Saha
"""

def getHeikinAishi(df):
    #assigning existing columns to new variable HAdf
    HAdf = df[['Open', 'High', 'Low', 'Close']]

    HAdf['Close'] = round(((df['Open'] + df['High'] + df['Low'] + df['Close'])/4),2)
    #round function to limit results to 2 decimal places
    for i in range(len(df)):
        if i == 0:
            HAdf.iat[0,0] = round(((df['Open'].iloc[0] + df['Close'].iloc[0])/2),2)
        else:
            HAdf.iat[i,0] = round(((HAdf.iat[i-1,0] + HAdf.iat[i-1,3])/2),2)
    #Taking the Open and Close columns we worked on in Step 2 & 3
    #Joining this data with the existing HIGH/LOW data from rel_df
    #Taking the max value in the new row with columns OPEN, CLOSE, HIGH
    #Assigning that value to the HIGH/LOW column in HAdf
    HAdf['High'] = HAdf.loc[:,['Open', 'Close']].join(df['High']).max(axis=1)
    HAdf['Low'] = HAdf.loc[:,['Open', 'Close']].join(df['Low']).min(axis=1)
    
    return HAdf