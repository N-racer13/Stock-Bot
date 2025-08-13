import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

def get_premarket_high_low(ticker_symbol):
    # Define the timezone for Eastern Time
    eastern = pytz.timezone('US/Eastern')

    # Get today's date in Eastern Time
    today = datetime.now(eastern).date()

    # Define the start and end times for the pre-market session
    start_time = eastern.localize(datetime.combine(today, datetime.min.time()) + timedelta(hours=4))  # 4:00 AM ET
    end_time = eastern.localize(datetime.combine(today, datetime.min.time()) + timedelta(hours=9, minutes=30))  # 9:30 AM ET
    # Fetch intraday data with 1-minute intervals
    data = yf.download(ticker_symbol, start=start_time, end=end_time, interval='1m', repair=True, prepost=True, progress=False, auto_adjust=True)
    # Ensure the data is not empty
    if data.empty:
        raise ValueError("No data retrieved. Market might be closed or data unavailable.")

    # Find the highest and lowest prices
    high_price = float(data['Close'].max().item())
    low_price = float(data['Close'].min().item())

    return high_price, low_price

def check_spy_breakout(pre_market_low, pre_market_high):
    # Download recent SPY 5-minute data (past 1 day should be enough)
    data = yf.download('SPY', period='1d', interval='5m')

    # Make sure we have enough candles
    if len(data) < 3:
        print("Not enough data.")
        return 'NONE'

    # Get last 2 candles
    first_candle_open = data.iloc[-1]['Open'].item()
    first_candle_close = data.iloc[-1]['Close'].item()
    second_candle_open = data.iloc[-2]['Open'].item()
    second_candle_close = data.iloc[-2]['Close'].item()
    print(first_candle_open)
    print(first_candle_close)
    print(second_candle_open)
    print(second_candle_close)

    # Conditions
    green = first_candle_open < first_candle_close and second_candle_open < second_candle_close
    red = first_candle_open > first_candle_close and second_candle_open > second_candle_close
    call = green and first_candle_open > pre_market_high and second_candle_open > pre_market_high #and first_candle_open < second_candle_open
    put = red and first_candle_open < pre_market_low and second_candle_open < pre_market_low #and first_candle_open > second_candle_open
  
    # Decision
    if call:
        return 'CALL'
    elif put:
        return 'PUT'
    else:
        return 'NONE'
