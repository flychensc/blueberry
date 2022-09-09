# run_func_demo
from dataclasses import replace
from tkinter.filedialog import dialogstates
from rqalpha.api import *
from rqalpha import run_func

import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd


def init(context):
    print(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "START")

    context.BAR_COUNT = 260
    context.FREQUENCY = '1d'
    context.idx = "000001.XSHG"

    # context.classifying = pd.DataFrame(columns=['order_day','order_book_id', 'holding_days', 'profit', 'classify'])
    context.classifying = pd.read_csv("picking.csv", parse_dates=["order_day"], date_parser=lambda x: dt.datetime.strptime(x, "%Y-%m-%d"))
    # CONVERT dtype: datetime64[ns] to datetime.date
    context.classifying['order_day'] = context.classifying['order_day'].dt.date

    context.group = context.classifying.groupby('order_day').count()


def after_trading(context):
    day = context.now.date()

    historys = history_bars(context.idx, context.BAR_COUNT, context.FREQUENCY, fields=['datetime', 'close'], include_now=True)

    COUNT = historys.shape[0]

    # numpy to dataframe
    historys = pd.DataFrame(historys)
    historys['order_day'] = historys['datetime'].map(lambda x: dt.datetime.strptime(str(x), "%Y%m%d%H%M%S").date())
    historys.drop('datetime', axis=1, inplace=True)
    historys.set_index("order_day", inplace=True)

    datas = context.group[-COUNT:]
    datas.columns = ['count']

    # 按historys的日期, 合并datas. 因为有时候某天count是0
    datas = pd.concat([datas, historys], axis=1).fillna(0).sort_index()[-COUNT:]

    # refer https://www.cnblogs.com/Atanisi/p/8530693.html

    lns1 = plt.plot(datas.index, historys['close'], color='red', linewidth=2, label=context.idx[:6])
    # 双Y轴
    plt2 = plt.twinx()
    lns2 = plt2.plot(datas.index, datas['count'], color='green', linewidth=2, label='wizard')

    #合并图例
    lns = lns1+lns2
    labs = [l.get_label() for l in lns]
    plt.legend(lns, labs, loc=0)

    plt.show()

    if context.run_info.end_date == day:
        print(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "END")


config = {
  "base": {
    "start_date": "2022-08-31",
    "end_date": "2022-08-31",
  },
  "extra": {
    "log_level": "warning",
  },
  "mod": {
    "sys_analyser": {
      "enabled": False
    }
  }
}


# 您可以指定您要传递的参数
run_func(init=init, after_trading=after_trading, config=config)
