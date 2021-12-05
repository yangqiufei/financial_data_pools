import pandas as pd
import numpy as np
import talib as ta
import json
import threading
import math
import os
import time

from comm_funcs import get_config
from comm_funcs import find_trade_date
from data_urls import a_detail_url
from comm_funcs import requests_get
from comm_funcs import down_symbol
from comm_funcs import get_redis_client


def aa(sub_df, f, s, percent):
    if np.round((sub_df[f] - sub_df[s]) / sub_df[s], 3) >= percent:
        return 1

    return 0


# 第一步，获取数据并且计算指标
def get_data(item_code, trade_data, first_ma=5, second_ma=10, time_period=5, percent=0.05):
    file_name = pp.replace("<<stock_code>>", item_code)

    if not os.path.exists(file_name):
        stock_df = down_symbol(symbol=item_code, is_return=True)
    else:
        stock_df = pd.read_csv(file_name)

    # stock_df['日期'] = pd.to_datetime(stock_df['日期'])

    stock_df.rename(columns={"日期": "date", '开盘': "open", "收盘": "close", "最高": "high", "最低": "low",
                             "成交量": "volume", "成交额": "value", "振幅": "amplitude", "涨跌额": "change",
                             "涨跌幅": "pct_change",  "换手率": "turnover_rate"},
                    inplace=True)

    # stock_df.set_index("date", inplace=True)

    f = 'MA{}'.format(first_ma)
    s = 'MA{}'.format(second_ma)
    stock_df[f] = ta.MA(stock_df['close'], timeperiod=first_ma)
    stock_df[s] = ta.MA(stock_df['close'], timeperiod=second_ma)

    stock_df.fillna(0, inplace=True)

    new_df = stock_df.tail(time_period)

    if not new_df.loc[(new_df["date"] == trade_data)].empty and new_df[f].all() and new_df[s].all() and len(new_df) == time_period :
        # 全部有数才计算，否则淘汰
        # new_df["btw_per"] = np.round((new_df[f] - new_df[s]) / new_df[s], 3) >= 0.05
        new_df.loc[:, "btw_per"] = new_df.apply(aa, axis=1, args=(f, s, percent))
        if new_df["btw_per"].sum() == time_period:
            return item_code

    return None


def foreach(symbols, trade_data, first_ma, second_ma, time_period, percent):
    t = []
    for s in symbols:
        try:
            res = get_data(s, trade_data, first_ma, second_ma, time_period, percent)
            if res is not None:
                redis_conn.rpush(ma_lte_key, res)
        except Exception as e:
            print(e)

    return t


def main(trade_data, first_ma=5, second_ma=10, time_period=5, percent=0.05):
    res = json.loads(requests_get(a_detail_url(psize=10000)))

    if "data" in res and "diff" in res["data"]:
        data = res['data']['diff']
        symbols = [item["f12"] for item in data if item['f15'] != "-"]

        # 开启多线程
        crawl_num = 30
        crawls = [i for i in range(crawl_num)]
        thread_list = []

        # 计算每个线程下载的数量
        per_num = math.ceil(len(symbols) / len(crawls))

        for i, crawl in enumerate(crawls):
            if i == 0:
                begin = 0
                end = per_num
            else:
                begin = i * per_num
                end = begin + per_num

            # get_data(item_code, trade_data, first_ma=5, second_ma=10, time_period=5, percent=0.05)
            thread = threading.Thread(target=foreach, args=(symbols[begin:end], trade_data, first_ma, second_ma, time_period, percent))
            thread.start()
            thread_list.append(thread)

        # 结束多线程
        for crawl_thread in thread_list:
            crawl_thread.join()

        if redis_conn.llen(ma_lte_key) > 0 and ma_lte_expire > 0:
            redis_conn.expire(ma_lte_key, ma_lte_expire)
            return redis_conn.lrange(ma_lte_key, 0, -1)

        return []


if __name__ == "__main__":
    begin_time = time.time()
    config = get_config("save_path")
    save_file_path = config["stock"]['daily']["path"]
    save_file_name = config["stock"]['daily']["file_name"]
    pp = os.path.join(save_file_path, save_file_name)

    today = find_trade_date(return_format="str")

    redis_conn = get_redis_client()
    redis_key_config = get_config("cache")
    ma_lte_key = redis_key_config["ma_lte"]["name"].replace("<<date>>", today)
    ma_lte_expire = redis_key_config["ma_lte"]["expire"]

    ma1 = 5
    ma2 = 10
    tp = 5

    data = main(trade_data=today, first_ma=ma1, second_ma=ma2, time_period=tp)
    print(data)

    end_time = time.time()
    total_time = end_time - begin_time
    print(total_time)
