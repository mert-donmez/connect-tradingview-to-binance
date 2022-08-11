import json, config
from flask import Flask, request, jsonify, render_template
from binance.client import Client
from binance.enums import *
import telebot

app = Flask(__name__)

client = Client(config.API_KEY, config.API_SECRET)
telegramBotToken = config.TELEGRAM_BOT_TOKEN
telegramUserId = config.TELEGRAM_USER_ID



def order(side, quantity, symbol_, leverage_,order_type=ORDER_TYPE_MARKET):
    try:
        client.futures_change_leverage(symbol=symbol_,leverage = leverage_)
        client.futures_change_margin_type(symbol=symbol_,marginType="ISOLATED")
        print(f"sending order {order_type} - {side} {quantity} {symbol_}")
        order = client.create_order(symbol=symbol_, side=side, type=order_type, quantity=quantity)
        telebot.Telebot(telegramBotToken).send_message(telegramUserId,f"sending order {order_type} - {side} {quantity} {symbol_}")
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return order

@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():

    data = json.loads(request.data)
    
    if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            "code": "error",
            "message": "Nice try, invalid passphrase"
        }

    side = data['strategy']['order_action'].upper()
    quantity = data['strategy']['order_contracts']
    ticker = data['ticker']
    leverage_ = data['leverage']
    order_response = order(side, quantity, ticker,leverage_)

    if order_response:
        return {
            "code": "success",
            "message": "order executed"
        }
    else:
        print("order failed")

        return {
            "code": "error",
            "message": "order failed"
        }