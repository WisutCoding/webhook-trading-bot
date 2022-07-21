from flask import Flask, request, render_template
from binance.client import Client
from binance.enums import *
import pandas as pd
import json

import config
import binance_script as my_bnc
#---------------------------------------------------------------------------------
app = Flask(__name__)
client = Client(config.API_KEY, config.API_SECRET)

#---------------------------------------------------------------------------------
def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print(f"sending order {order_type} - {side} {quantity} {symbol}")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)

    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return order

#---------------------------------------------------------------------------------
@app.route("/")
def welcome():
    return render_template('index.html')

#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
@app.route('/webhook', methods=['POST'])
def webhook():

    #----------------------------------------------------------------------------
    # recieve Webhook
    wbhook = json.loads(request.data)
    
    if wbhook['passphrase'] != config.WEBHOOK_PASSPHRASE_1:
        return{
            "invalid passphase"
        }

    if wbhook['passphrase'] != config.WEBHOOK_PASSPHRASE_2:
        return{
            "invalid passphase"
        }
    
    # get webhook data

    passphrase = wbhook['passphrase']
    base_currency = wbhook['base_currency']

    symbol = wbhook['symbol']
    target_symbol = symbol.split(base_currency)[0]

    side = wbhook['side']

    buy_ratio_percent = float(wbhook['buy_ratio_percent'])
    buy_fixed_amount_USDT = float(wbhook['buy_fixed_amount_USDT'])
    buy_fixed_or_ratio = wbhook['buy_fixed_or_ratio']

    sell_ratio_percent = float(wbhook['sell_ratio_percent'])
    sell_fixed_amount_USDT = float(wbhook['sell_fixed_amount_USDT'])
    sell_fixed_or_ratio = wbhook['sell_fixed_or_ratio']

    # take_profit_percent = float(wbhook['take_profit_percent'])
    # stop_loss_percent = float(wbhook['stop_loss_percent'])

    # trailing_stop_Type = wbhook['trailing_stop_(no/historical/callback)']
    # trailing_stop_activation_percent = float(wbhook['trailing_stop_activation_percent'])
    # trailing_stop_historical_bar = float(wbhook['trailing_stop_historical_bar'])
    # trailing_stop_callback_rate = float(wbhook['trailing_stop_callback_rate'])

    # check user
    if passphrase == config.WEBHOOK_PASSPHRASE_1:
        client = Client(config.API_KEY_1, config.API_SECRET_1)
        user_no = 1
    elif passphrase == config.WEBHOOK_PASSPHRASE_2:
        client = Client(config.API_KEY_2, config.API_SECRET_2)
        user_no = 2
    else:
        user_no = "N/A"

    # check account balance
    base_balance = float(my_bnc.check_balance(base_currency, user_no))

    # check account balance (target symbol)
    target_balance = float(my_bnc.check_balance(target_symbol, user_no))

    #----------------------------------------------------------------------------

    # get all tick
    all_price = client.get_all_tickers()
    df_all_price = pd.DataFrame(all_price)

    # check target price
    price = df_all_price[(df_all_price.symbol == symbol)]
    price = float(price['price'])
    price
    
    #----------------------------------------------------------------------------

    # Position Sizing

    # BUY

    if buy_fixed_or_ratio == "fixed":
        buy_amount = buy_fixed_amount_USDT / price
        buy_amount

    elif buy_fixed_or_ratio == "ratio":
        buy_amount = (base_balance * buy_ratio_percent) / price
        buy_amount

    else:
        buy_amount = 0

    # SELL

    if sell_fixed_or_ratio == "fixed":
        sell_amount = sell_fixed_amount_USDT / price
        sell_amount

    elif sell_fixed_or_ratio == "ratio":
        sell_amount = (target_balance * sell_ratio_percent) / 100
        sell_amount

    else:
        sell_amount = 0


    #----------------------------------------------------------------------------

    # order execution

    if side == "BUY":
        order_amount = round(buy_amount,5)
    elif side == "SELL":
        order_amount = round(sell_amount,5)
    else:
        order_amount = "N/A"

    order_response = client.create_order(symbol=symbol, side=side, type=ORDER_TYPE_MARKET, quantity=order_amount)

    if order_response:
        return {
            "code" : "Success",
            "message" : "Order Executed",
            "symbol" : symbol,
            "side" : side,
            "order amount" : order_amount,
            "price" : price,
        }
    else:
        print("Order Failed")
        return{
            "code" : "Error",
            "message" : "Order Failed",
            "symbol" : symbol,
            "side" : side,
            "amount" : order_amount,
            "price" : price,
        }

#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------

### Run bot on flask via Local PC

## 1. Setup Python Kernel
## 2. pip install -r requirements.txt

#>- set FLASK_APP=app.py
#>- set FLASK_ENV=development
#>- python -m flask run

#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------

### Run bot on flask via Heroku

#>- heroku login
#>- heroku                                  (to See all command for heroku)
#>- git init

#>- heroku git:remote -a binance-btc-rsi-strategy-1
#>- git status                              (Check Status File in Project throught git)

#>- git add .                               (add files)
#>- git commit -am "Commit Description"     (Tell Server to use new version)
#>- git push heroku master                  (Deploy App to heroku)