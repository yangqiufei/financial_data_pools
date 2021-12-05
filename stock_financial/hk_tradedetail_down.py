# -*- coding:utf-8 -*-
# /usr/bin/env python
"""
Date: 2021/8/28 21:26
Desc: 东方财富网-行情首页-上证 港股 股-每日行情

获取最近一个交易日的交易信息

使用示例（直接运行main函数，获取最近一个交易日的交易信息）：
main()
"""
import time
import json
import pandas as pd
import os
import threading
import math
import akshare as ak

from data_urls import hk_detail_url as url
from comm_funcs import requests_get
from comm_funcs import get_config
from comm_funcs import down_symbol
from comm_funcs import except_handle


def download(symbols: list, adjust: str = ""):
    """
    下载个股历史交易信息
    :param symbols: 个股代码列表
    :param period: 日线：daily； 周线：weekly; 月线： monthly
    :param adjust: 复权类型，前复权："qfq"；后复权："hfq"；"不复权"：""， 默认不复权
    :return:
    """
    if len(symbols):
        try:
            for symbol in symbols:
                stock_hk_hist_df = ak.stock_hk_hist(symbol=symbol, start_date="19700101", end_date="22220101",
                                                    adjust=adjust)
                print(stock_hk_hist_df)
                print("{} ok".format(symbol))
                time.sleep(0.5)
        except ValueError as e:
            except_handle(e)


def main(period: str = "daily", adjust: str = ""):
    """
    获取a股当前交易日个股交易信息
    :return: pandas.DataFrame
    """
    data = requests_get(url())
    res = json.loads(data)

    if "data" in res and "diff" in res["data"]:
        data = res['data']['diff']
        symbols = [item["f12"] for item in data if item['f15'] != "-"]

        # 开启多线程
        crawl_num = 20
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

            thread = threading.Thread(target=download, args=(symbols[begin:end], adjust))
            thread.start()
            thread_list.append(thread)

        # 结束多线程
        for crawl_thread in thread_list:
            crawl_thread.join()


def save(save_path: str = '', file_name: str = ''):
    """
    :return:
    """
    save_df = ak.stock_hk_spot_em()

    config = get_config("save_path")
    save_path = config["hk"]["detail"]["path"]
    file_name = config["hk"]["detail"]["file_name"].replace("<<date>>", "2021-09-13")
    try:
        if save_path and file_name:
            file_name.replace('.csv', '')
            save_name = os.path.join(save_path, file_name)
            if save_name:
                save_df.pop('序号')
                # 保存的时候会把0自动去掉
                save_df.loc[:, '代码'] = save_df['代码'].map(lambda x: ';'+x)
                save_df.to_csv(save_name, index=False)
        return True
    except:
        return False


def get_hk_history_list():
    df = main()
    stock_hk_hist_df = ak.stock_hk_hist(symbol="00593", start_date="19700101", end_date="22220101", adjust="")


# https://github.com/huangsir250/financial_data_pools
if __name__ == '__main__':
    # 最近一个交易日市场的交易信息
    begin_time = time.time()
    main()

    save()
    total_time = time.time() - begin_time
    print(total_time)
