"""
获取资产负债表信息

使用示例（获取2018年4季度资产负债率数据）：
bal_run = BalancesheetsRun(
    data_queue='balancesheet_data_queue',
    page_queue='balancesheet_page_queue')
report_date = time_last_day_of_month(year=2018, month=12)

bal_run.run(report_date=report_date)
"""

import time
import json
import pandas as pd
from data_urls import *
from comm_funcs import *
import asyncio
import aiohttp


async def parse(url, engine):
    data = await async_crawl(url)
    parse_data_list = json.loads(data)
    data_all = parse_data_list['result']['data']
    columns = column()

    insert_values = []
    for row in data_all:
        insert_values.append(
            tuple(map(lambda x: row[x.upper()], columns)))

    df = pd.DataFrame(insert_values, columns=columns)

    df.set_index('report_date', inplace=True)
    df.fillna(0, inplace=True)

    df.to_sql(
        name='s_balance_sheets',
        con=engine,
        if_exists='append')

def column():
    return [
        'security_code',
        'security_name_abbr',
        'report_date',
        'monetaryfunds',
        'monetaryfunds_ratio',
        'accounts_rece',
        'accounts_rece_ratio',
        'inventory',
        'inventory_ratio',
        'total_assets',
        'total_assets_ratio',
        'accounts_payable',
        'accounts_payable_ratio',
        'advance_receivables',
        'advance_receivables_ratio',
        'total_liabilities',
        'total_liab_ratio',
        'debt_asset_ratio',
        'total_equity',
        'total_equity_ratio',
        'fixed_asset',
        'industry_code',
        'industry_name'
    ]

def main(year, month):
    engine = get_db_engine_for_pandas()
    report_date = time_last_day_of_month(year=year, month=month)
    total_page = int(get_page_num(get_balance_sheets_url(report_date=report_date))['result']['pages'])
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(parse(
            get_balance_sheets_url(report_date=report_date, page=p), engine)) for p in range(1, total_page+1) ]
    loop.run_until_complete(asyncio.wait(tasks))

class Coroutine(object):
    pass

# https://github.com/huangsir250/financial_data_pools
if __name__ == '__main__':
    betime = time.time()
    # 获取A股2020年三季报的资产负债信息
    year = 2010
    month = 3
    main(year, month)
    total_time = time.time()-betime
    print('总计耗时：{}'.format(total_time))
