from rqalpha.apis import *

import numpy as np
import pandas as pd

import configparser
import datetime
import talib


def classify(context, order_book_id, day, historys):
    if day in context.cache and order_book_id in context.cache[day]:
        order_day = context.cache[day].pop(order_book_id)
        if not len(context.cache[day]):
            context.cache.pop(day)

        label = "holding"
        if historys['datetime'][0] == np.int64(order_day.strftime("%Y%m%d%H%M%S")):
            # 数据正常
            price = historys['close'][0]
            stop_loss = price*context.STOP_LOSS
            take_profit = price*context.TAKE_PROFIT
            for price in historys['close']:
                if price < stop_loss:
                    label = "loss"
                    break
                if price > take_profit:
                    label = "profit"
                    break

            context.picking.loc[(context.picking['date'] == order_day) & (context.picking['order_book_id'] == order_book_id), 'classify'] = label
        else:
            # 定位入选日，只会找到一项[0]，且只需要这项的行号[0]
            delta_days = np.where(historys['datetime'] == np.int64(order_day.strftime("%Y%m%d%H%M%S")))[0][0]
            # 继续平移停牌的这段时间
            verify_day = day + datetime.timedelta(days=int(delta_days))
            context.cache.setdefault(verify_day, {})
            # 价格可能复权，所以保存入选日期
            context.cache[verify_day][order_book_id] = order_day


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

    context.POSITION_DAY = config.getint('POLICY', 'POSITION_DAY')
    context.STOP_LOSS = config.getfloat('POLICY', 'STOP_LOSS')
    context.TAKE_PROFIT = config.getfloat('POLICY', 'TAKE_PROFIT')

    context.picking = pd.DataFrame(columns=['date','order_book_id', 'classify'])
    context.cache = {}


def after_trading(context):
    day = context.now.date()
    stocks = all_instruments(type="CS")
    for order_book_id in stocks['order_book_id']:
        # 免费的日级别数据每个月月初更新，下载命令: rqalpha download-bundle
        historys = history_bars(order_book_id, context.BAR_COUNT, context.FREQUENCY, fields=['datetime', 'close'], include_now=True)

        # 包含入选日
        classify(context, order_book_id, day, historys[-1-context.POSITION_DAY:])

        # 今日无数据: 停牌
        if historys['datetime'][-1] < np.int64(day.strftime("%Y%m%d%H%M%S")):
            continue
        # 数据不足: 新股
        if historys['datetime'].size < context.BAR_COUNT:
            continue
        prices = historys['close']
        price = prices[-1]
        ma1 = talib.SMA(prices, context.MA1)[-1]
        ma2 = talib.SMA(prices, context.MA2)[-1]
        ma3 = talib.SMA(prices, context.MA3)[-1]
        rsi = talib.RSI(prices, timeperiod=context.RSI1)[-1]
        if price > ma1 > ma2 > ma3 and rsi > context.RSI1_THR:
            context.picking = context.picking.append({
                    "date": day,
                    "order_book_id": order_book_id,
                }, ignore_index=True)

            verify_day = day + datetime.timedelta(days=context.POSITION_DAY)
            context.cache.setdefault(verify_day, {})
            # 价格可能复权，所以保存入选日期
            context.cache[verify_day][order_book_id] = day

    if context.run_info.end_date == day:
        context.picking.to_csv('picking.csv')

