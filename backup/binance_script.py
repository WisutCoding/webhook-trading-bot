from binance.client import Client
from binance.enums import *
import pandas as pd
import config

#===========================================================================================================================

def check_balance(symbol, user):
    try:
        # Select API
        if user == 1:
            API_KEY = config.API_KEY_1
            API_SECRET = config.API_SECRET_1
        elif user == 2:
            API_KEY = config.API_KEY_2
            API_SECRET = config.API_SECRET_2
        else:
            API_KEY = ""
            API_SECRET = ""

        client = Client(API_KEY, API_SECRET)

        # Check Balance
        account_info= client.get_account()

        df_account = pd.DataFrame(account_info['balances'])

        df_balance = pd.DataFrame()
        df_balance['asset'] = df_account['asset'].astype(str)
        df_balance['free'] = df_account['free'].astype(float)
        df_balance['locked'] = df_account['locked'].astype(float)

        df_free = df_balance[df_balance['free']>0]

        
        # Select Symbol
        balance_free = pd.to_numeric(df_free['free'].loc[df_free['asset'] == symbol].values[0])

        print(f"{symbol}: {balance_free}")

    except Exception as e:
        print("check balance error - {}".format(e))
        return False

    return balance_free

#===========================================================================================================================

def order_buy(pair='BTCUSDT', amount=20, order_type = ORDER_TYPE_MARKET):
    try:
        print(f"sending order {order_type} - {quantity} {symbol}")

        # Select API
        if user == 1:
            API_KEY = config.API_KEY_1
            API_SECRET = config.API_SECRET_1
        elif user == 2:
            API_KEY = config.API_KEY_2
            API_SECRET = config.API_SECRET_2
        else:
            API_KEY = ""
            API_SECRET = ""

        client = Client(API_KEY, API_SECRET)

        # Get Price
        all_price = client.get_all_tickers()
        df_all_price = pd.DataFrame(all_price)

        price = df_all_price[(df_all_price.symbol == pair)]
        price = pd.to_numeric(price['price'].values[0])

        # Create order
        order_buy = client.create_order(
                        symbol=pair,
                        side=SIDE_BUY,
                        type=ORDER_TYPE_MARKET,
                        quantity=amount)

    except Exception as e:
        print("order buy error - {}".format(e))
        return False

    return order_buy

#===========================================================================================================================

def order_sell(symbol, amount, order_type = ORDER_TYPE_MARKET):
    try:
        print(f"sending order {order_type} - {quantity} {symbol}")

        order_sell = client.create_order(symbol=symbol, side='SELL', type=order_type, quantity=amount)

    except Exception as e:
        print("order sell error - {}".format(e))
        return False

    return order_sell

#===========================================================================================================================