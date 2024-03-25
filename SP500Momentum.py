#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 11:30:12 2024

@author: lcancino
"""

import streamlit as st
import yfinance as yf
import pandas as pd
from bs4 import BeautifulSoup
import requests

@st.cache_data
@st.cache_resource

def get_sp500_symbols():
    # Fetch S&P 500 symbols from Wikipedia
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})
    symbols = []
    for row in table.find_all('tr')[1:]:
        symbol = row.find_all('td')[0].text.strip()
        symbols.append(symbol)
    return symbols

def calculate_acceleration(prices, n_days):
    # Calculate the acceleration based on the average daily percentage change
    price_change = (prices.iloc[-1] - prices.iloc[-n_days]) / prices.iloc[-n_days]  # Total percentage change
    avg_daily_change = price_change / n_days  # Average daily percentage change
    return avg_daily_change * 100  # Convert to percentage

def main():
    # Set the title of the Streamlit app
    st.title('S&P 500 Momentum')

    # Sidebar for selecting positive or negative acceleration
    selection = st.sidebar.radio("Select acceleration type", ("Positive Acceleration", "Negative Acceleration"))

    # Fetch S&P 500 symbols
    sp500_symbols = get_sp500_symbols()

    # Fetch stock data for all symbols
    stock_data = yf.download(sp500_symbols, period='1y')['Adj Close']

    # Display the results for different timeframes
    st.title(f'Top 10 Stocks with highest {"Positive" if selection == "Positive Acceleration" else "Negative"} Acceleration')

    for timeframe in [2, 3, 5, 10, 20]:
        # Calculate acceleration for current timeframe
        acceleration = calculate_acceleration(stock_data, timeframe)

        # Select top accelerating or decelerating stocks
        if selection == "Positive Acceleration":
            top_stocks = acceleration.sort_values(ascending=False)[:10]
        else:
            top_stocks = acceleration.sort_values()[:10]

        # Display the results for current timeframe
        st.subheader(f'{timeframe} Days')
        df = pd.DataFrame({'Symbol': top_stocks.index, 'Average Daily Acceleration (%)': top_stocks.values})
        st.write(df)

if __name__ == "__main__":
    main()
