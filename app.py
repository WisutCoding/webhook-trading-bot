import json
import config
# import ccxt

from flask import Flask, request
from binance.client import Client
from binance.enums import *

#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------

app = Flask(__name__)
client = Client(config.API_KEY, config.API_SECRET)

# binance = ccxt.binance({
# 	'api_key':'6Zzgfz14jvzugfqRfw8kj3ayEkQFCWyz3LPdE0OSh6GkUbwr8GOly6GLisj2LJlI',
# 	'secret':'0vSAxPZEfEvLX9Oq2kTQ2Po7iiaIV3V4qpKQT3KerCscdJbvqzfWLbHIbYz8pLtp'
#     }
# )

#---------------------------------------------------------------------------------
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
#---------------------------------------------------------------------------------

@app.route("/")
def hello_world():
    return "Trading Bot Project No.1 (Upload 06/03/2022)"

#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------

@app.route('/webhook', methods=['POST'])
def webhook():

    data = json.loads(request.data)

    if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return{
            "code":"error",
            "message":"invalid passpharse"
        }
    
    print('time : ',data['passphrase'])
    print('time : ',data['time'])
    print('ticker : ',data['ticker'])
    print('bar : ',data['bar'])

    side = data['strategy']['order_action'].upper() # BUY / SELL
    quantity = data['strategy']['order_contracts']
    symbol = data['ticker']

    print('side >> ',side)
    print('quantity >> ',quantity)
    print('symbol >> ',symbol)


    order_response = order(side, quantity, symbol)   # Minimum Notional is 20 USD
    print(order_response)

    if order_response:
        return {
            "code" : "Success",
            "message" : "Order Executed"
        }
    else:
        print("Order Failed")
        return{
            "code" : "Error",
            "message" : "Order Failed"
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
#>- heroku (to See all command for heroku)
#>- git init

#>- heroku git:remote -a binance-btc-rsi-strategy-1
#>- git status (Check Status File in Project throught git)

#>- git add . (add files)
#>- git commit -am "Commit Description"

#>- git push heroku master (Deploy App to heroku)