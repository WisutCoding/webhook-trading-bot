import json
import config
from flask import Flask, request, render_template
from binance.client import Client
from binance.enums import *
import pandas as pd
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
    #---------------------------------------------------
    # Get Webhook
    data = json.loads(request.data)                         # Get json
    if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return{
            "code":"error",
            "message":"invalid passpharse"
        }
    
    symbol = data['ticker']                                     # Get Symbol
    price_close = pd.to_numeric(data['bar']['close'])           # Get Close 
    order_action = data['strategy']['order_action'].upper()     # Get BUY/SELL
    
    #---------------------------------------------------
    # Check Balance

    account_info= client.get_account()

    df = pd.DataFrame(account_info['balances'])

    usdt_info = df.loc[df['asset'] == 'USDT']
    btc_info = df.loc[df['asset'] == 'BTC']

    usdt_amount = pd.to_numeric(usdt_info['free'].values[0])
    btc_amount = pd.to_numeric(btc_info['free'].values[0])

    #---------------------------------------------------
    # Money Management
    buy_ratio = pd.to_numeric(data['strategy']['buy_ratio'])    # Get buy ratio > defualt=1
    sell_ratio = pd.to_numeric(data['strategy']['sell_ratio'])  # Get sell ratio > defualt=1

    # Calculate Order Quantity
    buy_btc_amt = (buy_ratio*usdt_amount/price_close)*100000//1/100000      #>> convert to 5 decimal point
    sell_btc_amt = (sell_ratio*btc_amount)*100000//1/100000                 #>> convert to 5 decimal point

    # identify BUY/SELL amount
    if order_action == "BUY":
        if config.POSITION_SIZING == 'FIXED':   # Select Buy Amount Fixed / Account Balance Ratio
            amount = config.BUY_AMOUNT_FIXED
        else:
            amount = buy_btc_amt
    else:
        amount = sell_btc_amt

    #---------------------------------------------------
    print('passphrase : ',data['passphrase'])
    print('time : ',data['time'])
    print('symbol >> ',symbol)
    print('Price : ',price_close)
    print('side >> ',order_action)
    print('amount >> ',amount)

    order_response = order(order_action, amount, symbol)   # Minimum Notional is 20 USD

    if order_response:
        return {
            "code" : "Success",
            "message" : "Order Executed",
            "Symbol" : symbol,
            "Action" : order_action,
            "Amount" : amount,
            "Price" : price_close
        }
    else:
        print("Order Failed")
        return{
            "code" : "Error",
            "message" : "Order Failed",
            "Symbol" : str(symbol),
            "Action" : str(order_action),
            "Amount" : str(amount),
            "Price" : str(price_close)
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