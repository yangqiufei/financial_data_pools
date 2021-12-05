# -*- coding:utf-8 -*-
# /usr/bin/env python
"""
获取全量历史交易数据
"""
import time
import json
import threading
import os
import talib as ta
import akshare as ak
import numpy as np

from data_urls import a_detail_url
from comm_funcs import requests_get
from comm_funcs import except_handle
from comm_funcs import find_trade_date
from comm_funcs import get_config
from comm_funcs import RedisClient


def push_code_queue(redis_conn, queue_key, set_key, data):
    redis_conn.delete(queue_key)

    for code in data:
        if redis_conn.sismember(set_key, code):
            continue

        redis_conn.rpush(queue_key, code)

    redis_conn.expire(queue_key, 60 * 60 * 3)
    redis_conn.expire(set_key, 60 * 60 * 24)


def download(redis_client=None, queue_key='', set_key='', period="daily", adjust=""):
    """
    下载个股历史交易信息
    :param redis_client: redis
    :param queue_key: 待下载的队列
    :param set_key: 下载完成的集合
    :param period: 日线：daily； 周线：weekly; 月线： monthly
    :param adjust: 复权类型，前复权："qfq"；后复权："hfq"；"不复权"：""， 默认不复权
    :return:
    """
    config = get_config("save_path")
    save_file_path = config["stock"][period]["path"]
    while True:
        symbol = ''
        try:
            symbol = redis_client.rpop(queue_key)

            if not symbol:
                break

            save_file_name = config["stock"][period]["file_name"].replace("<<stock_code>>", symbol)
            filename = os.path.join(save_file_path, save_file_name)

            param = {
                "symbol": symbol,
                "period": period,
                "adjust": adjust,
            }

            new_df = ak.stock_zh_a_hist(**param)

            new_df.columns = ["trade_date", "open", "close", "high", "low", "vol", "amount", "aup", "pct_chg", "change",
                              "turnover_rate"]
            new_df["ts_code"] = symbol
            new_df.loc[:, "trade_date"] = new_df["trade_date"].map(lambda x: x.replace("-", ""))
            new_df.loc[:, "pre_close"] = new_df["close"].shift(1)
            new_df.loc[:, "volume_ratio"] = np.round(new_df["vol"] / new_df["vol"].shift(1), 2)
            new_df['ma5'] = ta.MA(new_df['close'], timeperiod=5)
            new_df['ma_v_5'] = ta.MA(new_df['vol'], timeperiod=5)
            new_df['ma10'] = ta.MA(new_df['close'], timeperiod=10)
            new_df['ma_v_10'] = ta.MA(new_df['vol'], timeperiod=10)
            new_df['ma20'] = ta.MA(new_df['close'], timeperiod=20)
            new_df['ma_v_20'] = ta.MA(new_df['vol'], timeperiod=20)
            new_df['ma30'] = ta.MA(new_df['close'], timeperiod=30)
            new_df['ma_v_30'] = ta.MA(new_df['vol'], timeperiod=30)
            new_df['ma60'] = ta.MA(new_df['close'], timeperiod=60)
            new_df['ma_v_60'] = ta.MA(new_df['vol'], timeperiod=60)

            new_df.sort_values("trade_date", ascending=False, inplace=True)
            new_df.to_csv(filename, index=False)

            print("{} 下载ok".format(symbol))
            redis_client.sadd(set_key, symbol)

        except Exception as e:
            # redis_conn.rpush(self.queue_key, code)
            redis_class = RedisClient()
            redis_client = redis_class.get_redis_client()

            except_handle('{} 下载失败,原因: {}'.format(symbol, e))


def main(page_size: int = 10000, period: str = "daily", adjust: str = ""):
    """
    下载入口程序
    :param page_size: a市场46多只，这里默认10000，即下载全部
    :param period: 日线：daily； 周线：weekly; 月线： monthly
    :param adjust: 复权类型，前复权："qfq"；后复权："hfq"；"不复权"：""， 默认不复权
    :return:
    """
    res = json.loads(requests_get(a_detail_url(psize=page_size)))

    if "data" in res and "diff" in res["data"]:
        data = res['data']['diff']
        symbols = [item["f12"] for item in data if item['f15'] != "-"]

        td_date = find_trade_date()

        redis_class = RedisClient()
        redis_client = redis_class.get_redis_client()

        # 待更新的数据队列
        queue_key = get_config('cache', 'pending_down_code_queue').replace('<<trade_date>>', str(td_date))  # redis队列名称

        # 已经更新的集合
        set_key = get_config('cache', 'downing_code_set').replace('<<trade_date>>', str(td_date))  # redis队列名称

        push_code_queue(redis_conn=redis_client, queue_key=queue_key, set_key=set_key, data=symbols)

        # 开启多线程
        crawl_num = 20
        thread_list = []

        for crawl in range(crawl_num):

            thread = threading.Thread(target=download, args=(redis_client, queue_key, set_key, period, adjust))
            thread.start()
            thread_list.append(thread)

        # 结束多线程
        for crawl_thread in thread_list:
            crawl_thread.join()


if __name__ == '__main__':
    # 下载历史交易信息保存在本地，csv格式
    begin_time = time.time()

    # 下载前复权和日线
    main(adjust="qfq", period="daily")
    # down_symbol(symbol="601899")

    end_time = time.time()
    total_time = end_time - begin_time
    print(total_time)
