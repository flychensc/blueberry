from rqalpha.apis import *

import datetime as dt
import numpy as np
import pandas as pd

import configparser


def classify(context, order_book_id, order_day, historys):
    cost = historys['close'][0]
    stop_loss = cost*context.STOP_LOSS
    take_profit = cost*context.TAKE_PROFIT

    holding_days = 0
    profit = 0
    label = "holding"
    for price in historys['close'][1:]:
        holding_days += 1
        if price < stop_loss:
            label = "loss"
            profit = 1 - price/cost
            break
        if price > take_profit:
            label = "profit"
            profit = 1 - price/cost
            break

    context.classifying.loc[(context.classifying['order_day'] == order_day) & (context.classifying['order_book_id'] == order_book_id), 'holding_days'] = int(holding_days)
    context.classifying.loc[(context.classifying['order_day'] == order_day) & (context.classifying['order_book_id'] == order_book_id), 'profit'] = round(profit, 2)
    context.classifying.loc[(context.classifying['order_day'] == order_day) & (context.classifying['order_book_id'] == order_book_id), 'classify'] = label


def init(context):
    print(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "START")
    config = configparser.ConfigParser()
    config.read('config.ini')

    context.BAR_COUNT = 270
    context.FREQUENCY = '1d'

    context.POSITION_DAY = config.getint('POLICY', 'POSITION_DAY')
    context.STOP_LOSS = config.getfloat('POLICY', 'STOP_LOSS')
    context.TAKE_PROFIT = config.getfloat('POLICY', 'TAKE_PROFIT')

    # context.classifying = pd.DataFrame(columns=['order_day','order_book_id', 'holding_days', 'profit', 'classify'])
    context.classifying = pd.read_csv("sample.csv", index_col=0, parse_dates=["order_day"], date_parser=lambda x: dt.datetime.strptime(x, "%Y-%m-%d"))
    # CONVERT dtype: datetime64[ns] to datetime.date
    context.classifying['order_day'] = context.classifying['order_day'].dt.date

    context.classifying = context.classifying.assign(holding_days="", profit=np.nan, classify="")


def after_trading(context):
    day = context.now.date()
    stocks = all_instruments(type="CS")
    for order_book_id in stocks['order_book_id']:
        historys = history_bars(order_book_id, context.BAR_COUNT, context.FREQUENCY, fields=['datetime', 'close'], include_now=True)

        if not historys.size: continue

        order_data = context.classifying[(context.classifying['order_book_id'] == order_book_id) &
                                     (context.classifying['order_day'] < day) &
                                     (context.classifying['classify'] == "")]

        for order_day in order_data['order_day'].sort_values():
            order_day64 = np.int64(order_day.strftime("%Y%m%d%H%M%S"))
            # 逐次缩小historys
            historys = historys[(historys['datetime'] >= order_day64)]
            # 数据不足
            if historys.size < context.POSITION_DAY:
                break
            classify(context, order_book_id, order_day, historys[:context.POSITION_DAY])

    if context.run_info.end_date == day:
        context.classifying.to_csv('classifying.csv')
        print(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "END")
