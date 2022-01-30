from rqalpha.apis import *

import numpy as np
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

    context.picking = pd.DataFrame(columns=['order_day', 'order_book_id'])


def after_trading(context):
    day = context.now.date()
    day64 = np.int64(day.strftime("%Y%m%d%H%M%S"))
    stocks = all_instruments(type="CS")
    for order_book_id in stocks['order_book_id']:
        # 免费的日级别数据每个月月初更新，下载命令: rqalpha download-bundle
        historys = history_bars(order_book_id, context.BAR_COUNT, context.FREQUENCY, fields=['datetime', 'close'], include_now=True)

        # 数据不足: 新股
        if historys['datetime'].size < context.BAR_COUNT:
            continue
        # 今日无数据: 停牌
        if historys['datetime'][-1] < day64:
            continue
        prices = historys['close']
        price = prices[-1]
        ma1 = talib.SMA(prices, context.MA1)[-1]
        ma2 = talib.SMA(prices, context.MA2)[-1]
        ma3 = talib.SMA(prices, context.MA3)[-1]
        rsi = talib.RSI(prices, timeperiod=context.RSI1)[-1]
        if price > ma1 > ma2 > ma3 and rsi > context.RSI1_THR:
            context.picking = context.picking.append({
                    "order_day": day,
                    "order_book_id": order_book_id,
                }, ignore_index=True)

    if context.run_info.end_date == day:
        context.picking.to_csv('picking.csv')

