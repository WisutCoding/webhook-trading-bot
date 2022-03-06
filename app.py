import json
import config
from flask import Flask, request, render_template
from binance.client import Client
from binance.enums import *
import pandas as pd
# import math
# import decimal
#---------------------------------------------------------------------------------
app = Flask(__name__)
client = Client(config.API_KEY, config.API_SECRET)
#---------------------------------------------------------------------------------
# def round_down(n, decimals=0):
#     multiplier = 10 ** decimals
#     return math.floor(n * multiplier) / multiplier
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
@app.route('/webhook', methods=['POST'])
def webhook():

    #---------------------------------------------------
    # Check Balance

    account_info= client.get_account()
    df = pd.DataFrame(account_info['balances'])

    usdt_info = df.loc[df['asset']== 'USDT']
    usdt_amount = round(pd.to_numeric(usdt_info['free'].values[0]),2)-0.01

    btc_info = df.loc[df['asset']== 'BTC']
    btc_amount = round(pd.to_numeric(btc_info['free'].values[0]),4)-0.0001

    #---------------------------------------------------
    # Data from Webhook
    data = json.loads(request.data)
    if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return{
            "code":"error",
            "message":"invalid passpharse"
        }

    # BUY/SELL
    order_action = data['strategy']['order_action'].upper() # BUY / SELL
    
    if order_action == "BUY":
        amount = usdt_amount
    else:
        amount = btc_amount

    symbol = data['ticker']

    print('passphrase : ',data['passphrase'])
    print('time : ',data['time'])
    print('ticker : ',data['ticker'])
    print('bar : ',data['bar'])
    print('side >> ',order_action)
    print('amount >> ',amount)
    print('symbol >> ',symbol)

    order_response = order(order_action, amount, symbol)   # Minimum Notional is 20 USD

    if order_response:
        return {
            "code" : "Success",
            "message" : "Order Executed",
            "Symbol" : str(symbol),
            "Action" : str(order_action),
            "Amount" : str(amount),
        }
    else:
        print("Order Failed")
        return{
            "code" : "Error",
            "message" : "Order Failed",
            "Symbol" : str(symbol),
            "Action" : str(order_action),
            "Amount" : str(amount),
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