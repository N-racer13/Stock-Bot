from fetch_SPY import *
from option_selector import *
from wait_until import *

import yfinance as yf
import pandas as pd
import datetime
import time
import pytz
import sys
from schwab.auth import easy_client
from schwab.orders.options import *
from schwab.orders.common import Duration, Session

def main():
    #wait_until()

    #Client setup
    client = easy_client(
        api_key='XXX',
        app_secret='XXX',
        callback_url='https://127.0.0.1:8182',
        token_path='tmp/token.json',
        interactive=False
        )
    # Fetch account numbers and hashes
    response = client.get_account_numbers()

    # Check if the request was successful
    if response.status_code == 200:
        account_data = response.json()
        if account_data:
            # Extract the first account's hash value
            account_hash = account_data[0]['hashValue']
        else:
            print("No accounts found.")
            sys.exit()
    else:
        print(f"Failed to retrieve account numbers: {response.status_code}")
        sys.exit()


    # Define parameters
    ticker = 'SPY'

    high, low = get_premarket_high_low(ticker)
    print(low)
    print(high)
    if low > high:
        print("Premarket high > premarket low. Exiting script for safety purposes.")
        sys.exit()
    
    # Breakout loop
    breakout = 'NONE'
    now = datetime.datetime.now()
    power_hour = now.replace(hour=11, minute=30, second=0, microsecond=0)
    while breakout == 'NONE':
        time.sleep(30)
        breakout = check_spy_breakout(low, high)
        print(f"breakout: {breakout}")
        now = datetime.datetime.now()
        print(now)
        if now >= power_hour:
            print("11:30 AM reached, no breakout. Exiting script.")
            sys.exit()
    
    # Get most affordable option
    option_symbol = find_affordable_option(client, account_hash, breakout, ticker)
    
    # Buy option
    ### INCLUDE RSI AS CONDITION ###
    order = option_buy_to_open_market(option_symbol, 1)
    order.set_duration(Duration.DAY)
    order.set_session(Session.NORMAL)
    response = client.place_order(account_hash, order.build())
    print(response)
    if response.status_code == 201:
        print(f"Order placed successfully: {response.json()}")
        #order_info = response.json()
        #print(order_info)
        #order_id = order_info.get('orderId')
    else:
        print(f"Failed to place order: {response.status_code}")
        #sys.exit()

    #filled = False
    #while filled == False:
    #    now = datetime.datetime.now()
    #    target_time = now.replace(hour=10, minute=30, second=0, microsecond=0)
    #    if now >= target_time:
    #        # Time is past 10:30AM, cancel the order
    #        print("Time is past 10:30AM. Cancelling the order...")
    #        cancel_response = client.cancel_order(order_id, account_hash)
    #        if cancel_response.status_code == 200:
    #            print("Order cancelled successfully.")
    #        else:
    #            print(f"Failed to cancel order: {cancel_response.status_code} - {cancel_response.text}")
    #        sys.exit()
    #    # Otherwise, check order status
    #    order_status_response = client.get_order(order_id, account_hash)
    #    order = order_status_response.json()
    #    print(order)
    #    status = order['status']
    #    print(f"Current order status: {status}")
    #    if status == 'FILLED':
    #        filled = True
    #        print("Order has been filled!")
    #    else:
    #        print("Order not filled yet, waiting 5 seconds...")
    #        time.sleep(5)

    # Get option price
    response = client.get_quote(option_symbol)
    response_data = response.json()
    buy_price = response_data[option_symbol]['quote']['askPrice']
    print(buy_price)
    current_price = buy_price
    # Stop-loss / gain limit loop
    #sell_timeout = now.replace(hour=13, minute=30, second=0, microsecond=0)
    current_upper = 1.15*buy_price
    current_lower = 0.85*buy_price
    while current_price < current_upper and current_price > current_lower:
        time.sleep(5)
        response = client.get_quote(option_symbol)
        response_data = response.json()
        current_price = response_data[option_symbol]['quote']['bidPrice']
        print(current_price)
        now = datetime.datetime.now()
        # Special trailing stop loss
        if current_price >= current_upper:
            current_lower = current_upper-0.05
            current_upper +=0.15
        #if now >= sell_timeout:
        #    print("Past 01:30 PM. Selling option.")
        #    break

    # Sell option
    order = option_sell_to_close_market(option_symbol, 1)
    order.set_duration(Duration.DAY)
    order.set_session(Session.NORMAL)
    response = client.place_order(account_hash, order.build())


if __name__ == '__main__':
    main()