"""
获取资产负债表信息

使用示例（直接运行main函数，获取最近一个交易日的交易信息）：
main()
"""

import time
import json
import pandas as pd
import math
from data_urls import get_trade_date_detail_url
from comm_funcs import async_crawl
from comm_funcs import get_db_engine_for_pandas
from comm_funcs import get_page_num
from comm_funcs import get_current_date
import asyncio


def columns_dict():
    return {
        'item_code': 'f12',
        'item_name': 'f14',
        'open': 'f17',
        'high': 'f15',
        'low': 'f16',
        'close': 'f2',
        'pre_close': 'f18',
        'change': 'f4',
        'pct_chg': 'f3',
        'vol': 'f5',
        'amount': 'f6',
        'amplitude': 'f7',
        'turnover_rate': 'f8',
        'pe': 'f9',
        'vol_percent': 'f10',
        'circulate': 'f20',
        'market_capital': 'f21'
    }


async def parse(url, engine):
    data = await async_crawl(url)
    parse_data_list = json.loads(data)
    data_all = parse_data_list['data']['diff']

    column_dict = columns_dict()
    column = list(column_dict.keys())
    map_dict = list(column_dict.values())

    insert_values = []
    for row in data_all:
        if row['f6'] == '-':
            continue

        data_tmp = []
        for f in map_dict:
            if row[f] == '-':
                row[f] = 0

            data_tmp.append(row[f])

        # data_tmp = tuple(map(lambda x: row[x], map_dict))
        insert_values.append(tuple(data_tmp))

    if insert_values:
        # column.append('trade_date')
        df = pd.DataFrame(insert_values, columns=column)
        df.set_index('item_code', inplace=True)
        df.fillna(0, inplace=True)
        # df.fillna(0, inplace=True)

        df['trade_date'] = str(get_current_date()).replace('-', '')
        # df['trade_date'] = 20201231
        df.to_sql(
            name='s_trade_detail',
            con=engine,
            if_exists='append')


def main(page_size=100):
    engine = get_db_engine_for_pandas()
    total_page = math.ceil(
        get_page_num(
            get_trade_date_detail_url(
                psize=page_size))['data']['total'] /
        page_size)
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(
            parse(
                get_trade_date_detail_url(
                    psize=page_size,
                    page=p),
                engine)) for p in range(
            1,
            total_page +
            1)]
    loop.run_until_complete(asyncio.wait(tasks))


# https://github.com/huangsir250/financial_data_pools
if __name__ == '__main__':
    # 最近一个交易日市场的交易信息
    betime = time.time()
    main()
    total_time = time.time() - betime
    print(total_time)
