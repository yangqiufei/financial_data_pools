"""
获取龙虎板列表信息

使用示例（获取2020-12-31龙虎榜列表数据）：
main('2020-12-31', '2020-12-31')
"""

import time
import json
import pandas as pd
import os
from data_urls import get_lhb_list_url
from data_urls import get_lhb_detail_url
from comm_funcs import async_crawl
from comm_funcs import get_config
from comm_funcs import get_current_date
from comm_funcs import find_trade_date
from comm_funcs import requests_get
from comm_funcs import except_handle
import asyncio


async def parse_detail(item_code, trade_date):
    url = get_lhb_detail_url(item_code=item_code, trade_date=trade_date)
    response = await async_crawl(url)
    res = json.loads(response)
    res["symbol"] = item_code
    res["trade_date"] = trade_date
    return res


def get_list(begin_date, end_date, is_save=True):
    """
    获取龙虎榜列表数据
    :param begin_date: 开始时间
    :param end_date:  结束时间
    :param is_save: 是否保存，如果需要保存为csv文件，需要配置config.yaml文件中配置文件地址
    :return: 返回列表
    """
    try:
        pages = data_pages = 1
        data_list = []

        # 判断是否有多页，多页的话进行循环拉取
        while data_pages >= pages:
            url = get_lhb_list_url(begin_date=begin_date, end_date=end_date, page=pages)
            response = requests_get(url)
            lhb_list = json.loads(response)
            data_list.extend(lhb_list['data'])
            data_pages = lhb_list['pages']
            pages = pages + 1

        # 将龙虎榜列表数据存入数据库中
        # parse(data_list, engine)

        if is_save:
            df = pd.DataFrame(data_list)
            df = df[["Tdate", "SCode", "SName", "Ntransac", "Turnover", "ClosePrice", "Chgradio", "Dchratio",
                     "Ctypedes", "JmMoney", "Smoney", "Bmoney"]]

            df.columns = ["日期", "代码", "股票", "成交量", "成交金额", "收盘价", "涨跌幅", "换手率", "上榜原因", "净买入",
                          "卖出金额", "买入金额"]

            df.loc[:, '代码'] = df['代码'].map(lambda x: ';' + x)

            config = get_config("save_path")
            file_name = config["lhb"]["list"]["file_name"]

            # 判断一下文件是否存在，如果存在则合并数据
            old_df = pd.DataFrame()
            if os.path.exists(file_name):
                old_df = pd.read_csv(file_name)

            if not old_df.empty:
                old_df = old_df.append(df)
                old_df.drop_duplicates(inplace=True)
                old_df.sort_values("日期", inplace=True, ascending=False)
                old_df.to_csv(file_name, index=False)
            else:
                df.to_csv(file_name, index=False)

        return data_list

    except Exception as e:
        except_handle(e)


def detail(begin_date, end_date):
    try:
        data_list = get_list(begin_date, end_date, is_save=False)

        target_data = [{r['SCode']: r['Tdate']} for r in data_list]

        # 龙虎榜详情使用协程创建任务
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(parse_detail(item_code, trade_date)) for row in target_data for item_code, trade_date in row.items()]
        loop.run_until_complete(asyncio.wait(tasks))

        all_df = pd.DataFrame()
        for t in tasks:
            res = t.result()
            # print(res)
            # exit()
            for r in res["BuySaleList"]:
                buy_df = pd.DataFrame(r["BuyList"])
                buy_df["类型"] = "买入"
                sale_df = pd.DataFrame(r["SaleList"][0:5])
                sale_df["类型"] = "卖出"

                df = buy_df.append(sale_df)
                df.columns = ["席位代码", "排序", "席位名称", "买入金额", "买入占比", "卖出金额", "卖出占比", "净额", "类型"]

                df["代码"] = res["symbol"]
                df["日期"] = res["trade_date"]
                df["上榜原因"] = r["Title"]

                all_df = pd.concat([df, all_df])

        all_df.loc[:, '代码'] = all_df['代码'].map(lambda x: ';' + x)

        if not all_df.empty:
            config = get_config("save_path")
            file_name = config["lhb"]["detail"]["file_name"]

            old_df = pd.DataFrame()
            if os.path.exists(file_name):
                old_df = pd.read_csv(file_name)

            if not old_df.empty:
                old_df = old_df.append(all_df)
                old_df.drop_duplicates(inplace=True)
                old_df.sort_values("日期", inplace=True, ascending=False)
                old_df.to_csv(file_name, index=False)
            else:
                all_df.to_csv(file_name, index=False)

    except Exception as e:
        except_handle(e)


if __name__ == '__main__':
    # 最近一个交易日市场的交易信息
    lhb_date = find_trade_date("str")
    begin_time = time.time()
    # 获取列表
    # get_list("2021-09-17", "2021-09-17", True)

    # 获取个股龙虎榜详情
    detail("2021-09-17", "2021-09-17")
    # detail(lhb_date, lhb_date)

    total_time = time.time() - begin_time
    print(total_time)
