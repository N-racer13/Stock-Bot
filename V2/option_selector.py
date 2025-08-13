import datetime
from schwab.client import *
from schwab.orders.options import *
from schwab.auth import *
from schwab.client.base import *

def find_affordable_option(client, account_id, call_or_put, ticker):
    # 1. Get your account balance
    account_info = client.get_account(account_id).json()
    available_cash = account_info['securitiesAccount']['initialBalances']['cashAvailableForTrading']
    # Safety
    print(f"Available cash: ${available_cash:.2f}")
    available_cash -= 5

    # 2. Get the SPY option chain
    today = datetime.date.today()
    target_date = today + datetime.timedelta(days=2)
    if call_or_put == 'CALL':
        contract_type = Client.Options.ContractType.CALL
    elif call_or_put == 'PUT':
        contract_type = Client.Options.ContractType.PUT
    else:
        raise ValueError("Invalid option_type. Use 'CALL' or 'PUT'.")
    
    option_chain_response = client.get_option_chain(ticker, contract_type=contract_type, from_date=target_date).json()

    if call_or_put.upper() == 'CALL':
        option_data = option_chain_response.get('callExpDateMap', {})
    elif call_or_put.upper() == 'PUT':
        option_data = option_chain_response.get('putExpDateMap', {})
    else:
        raise ValueError("call_or_put must be 'CALL' or 'PUT'.")

    if not option_data:
        raise Exception(f"No {call_or_put} data found in option chain.")

    # 3. Find expiration date 2 days from today (or next available)
    available_expirations = list(option_data.keys())
    available_expirations = sorted(available_expirations)

    chosen_exp_date = None
    for exp in available_expirations:
        exp_date_str = exp.split(":")[0]
        exp_date = datetime.datetime.strptime(exp_date_str, "%Y-%m-%d").date()
        if exp_date >= target_date:
            chosen_exp_date = exp
            break

    if not chosen_exp_date:
        raise Exception("No suitable expiration found.")

    print(f"Selected expiration: {chosen_exp_date}")

    # 4. Find the most expensive option you can afford
    best_option = None
    best_price = 0

    strikes = option_data[chosen_exp_date]
    for strike_price, contracts in strikes.items():
        for contract in contracts:
            ask_price = contract.get('ask', 0)
            total_cost = ask_price * 100  # options contract = 100 shares

            if total_cost <= available_cash and total_cost > best_price:
                best_price = total_cost
                best_option = contract

    if not best_option:
        raise Exception("No affordable option found for selected expiration.")

    option_symbol = best_option['symbol']
    print(f"Selected option: {option_symbol} at cost ${best_price:.2f}")
 
    return option_symbol
