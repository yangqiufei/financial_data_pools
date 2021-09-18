# -*- coding:utf-8 -*-
# /usr/bin/env python
"""
获取全量历史交易数据
"""
import time
import json
import threading
import math

from data_urls import a_detail_url
from comm_funcs import requests_get
from comm_funcs import except_handle
from comm_funcs import down_symbol


def download(symbols: list, period: str = "daily", adjust: str = ""):
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
                down_symbol(symbol, period=period, adjust=adjust)
                print("{} ok".format(symbol))
                time.sleep(0.5)
        except ValueError as e:
            except_handle(e)


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

            thread = threading.Thread(target=download, args=(symbols[begin:end], period, adjust))
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
