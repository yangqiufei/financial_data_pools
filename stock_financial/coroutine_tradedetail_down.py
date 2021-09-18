# -*- coding:utf-8 -*-
# /usr/bin/env python
"""
Date: 2021/8/28 21:26
Desc: 东方财富网-行情首页-上证 A 股-每日行情

获取最近一个交易日的交易信息

使用示例（直接运行main函数，获取最近一个交易日的交易信息）：
main()
"""
import datetime
import time
import json
import pandas as pd
import os
from data_urls import a_detail_url as url
from comm_funcs import requests_get
from comm_funcs import get_config
from comm_funcs import find_trade_date


def main(page_size: int = 6000) -> pd.DataFrame:
    """
    获取a股当前交易日个股交易信息
    :param page_size: 一次拉取的数量
    :return: pandas.DataFrame
    """
    res = json.loads(requests_get(url(psize=page_size)))

    if "data" in res and "diff" in res["data"]:
        data = res['data']['diff']

        detail_df = pd.DataFrame(data)
        save_df = detail_df.loc[:, ['f12', 'f14', 'f17', 'f15', 'f16', 'f2', 'f18', 'f4', 'f3',
                                    'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f20', 'f21']]

        # 去掉没有交易的
        find_index = save_df[save_df["f15"] == "-"].index
        save_df.drop(index=find_index, inplace=True)

        save_df.columns = [
            '股票代码',
            '股票名称',
            '开盘',
            '最高',
            '最低',
            '最新价',
            '昨收',
            '涨跌额',
            '涨跌幅',
            '成交量',
            '成交额',
            '振幅',
            '换手率',
            '市盈率',
            '量比',
            '流通市值',
            '总市值'
        ]

        save_df["开盘"] = pd.to_numeric(save_df["开盘"], errors="coerce")
        save_df["最高"] = pd.to_numeric(save_df["最高"], errors="coerce")
        save_df["最低"] = pd.to_numeric(save_df["最低"], errors="coerce")
        save_df["最新价"] = pd.to_numeric(save_df["最新价"], errors="coerce")
        save_df["昨收"] = pd.to_numeric(save_df["昨收"], errors="coerce")
        save_df["涨跌额"] = pd.to_numeric(save_df["涨跌额"], errors="coerce")
        save_df["涨跌幅"] = pd.to_numeric(save_df["涨跌幅"], errors="coerce")
        save_df["成交量"] = pd.to_numeric(save_df["成交量"], errors="coerce")
        save_df["成交额"] = pd.to_numeric(save_df["成交额"], errors="coerce")
        save_df["振幅"] = pd.to_numeric(save_df["振幅"], errors="coerce")
        save_df["换手率"] = pd.to_numeric(save_df["换手率"], errors="coerce")
        save_df["市盈率"] = pd.to_numeric(save_df["市盈率"], errors="coerce")
        save_df["量比"] = pd.to_numeric(save_df["量比"], errors="coerce")
        save_df["流通市值"] = pd.to_numeric(save_df["流通市值"], errors="coerce")
        save_df["总市值"] = pd.to_numeric(save_df["总市值"], errors="coerce")

        return save_df


def save(save_df: pd.DataFrame):
    """
    :param save_df:
    :return:
    """
    try:
        config = get_config("save_path")
        save_path = config["stock"]["detail"]["path"]
        today = find_trade_date(return_format="str")
        file_name = config["stock"]["detail"]["file_name"].replace("<<date>>", today)
        file_name.replace('.csv', '')
        save_name = os.path.join(save_path, file_name)
        if save_name:
            save_df['股票代码'] = save_df['股票代码'].map(lambda x: ";" + x)
            save_df.to_csv(save_name, index=False)
        return True
    except:
        return False


# https://github.com/huangsir250/financial_data_pools
if __name__ == '__main__':
    # 最近一个交易日市场的交易信息
    begin_time = time.time()
    df = main()
    print(df)

    # 保存到本地

    save(df)
    total_time = time.time() - begin_time
    print(total_time)
