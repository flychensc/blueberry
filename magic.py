from rqalpha.apis import *

import pandas as pd

import configparser
import talib


def init(context):
    config = configparser.ConfigParser()
    config.read('config.ini')

    context.MA1 = config.getint('MA', 'MA1')
    context.MA2 = config.getint('MA', 'MA2')
    context.MA3 = config.getint('MA', 'MA3')
    context.RSI1 = config.getint('RSI', 'RSI1')
    context.RSI1_THR = config.getint('RSI', 'THR1')
    context.BAR_COUNT = context.MA3+1
    context.FREQUENCY = '1d'

    context.candidates = pd.DataFrame(columns=['datetime','order_book_id'])


def after_trading(context):
    stocks = all_instruments(type="CS")
    stocks = stocks[(stocks["special_type"] == "Normal") & (stocks["status"] == "Active") & ((stocks["board_type"] == "MainBoard") | (stocks["board_type"] == "GEM"))]
    for order_book_id in stocks['order_book_id']:
        prices = history_bars(order_book_id, context.BAR_COUNT, context.FREQUENCY, fields='close', include_now=True)
        price = prices[-1]
        ma1 = talib.SMA(prices, context.MA1)[-1]
        ma2 = talib.SMA(prices, context.MA2)[-1]
        ma3 = talib.SMA(prices, context.MA3)[-1]
        rsi = talib.RSI(prices, timeperiod=context.RSI1)[-1]
        if price > ma1 > ma2 > ma3 and rsi > context.RSI1_THR:
            context.candidates.append([[context.now, order_book_id]])

