"""
获取现金流信息

使用示例（获取2020年一季度现金流量数据）：
year = 2020
month = 3
main(year, month)
"""

from data_urls import *
from comm_funcs import *
import json
import time
import pandas as pd
import asyncio


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
        name='s_cashflows',
        con=engine,
        if_exists='append')

def column():
    return [
        'security_code',
        'security_name_abbr',
        'notice_date',
        'report_date',
        'cce_add',
        'cce_add_ratio',
        'netcash_operate',
        'netcash_operate_ratio',
        'netcash_invest',
        'netcash_invest_ratio',
        'netcash_finance',
        'netcash_finance_ratio',
        'sales_services',
        'sales_services_ratio',
        'pay_staff_cash',
        'psc_ratio',
        'receive_invest_income',
        'rii_ratio',
        'construct_long_asset',
        'cla_ratio'
    ]

def main(year, month):
    engine = get_db_engine_for_pandas()
    report_date = time_last_day_of_month(year=year, month=month)
    total_page = int(get_page_num(get_cashflow_url(report_date=report_date))['result']['pages'])
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(parse(
            get_cashflow_url(report_date=report_date, page=p), engine)) for p in range(1, total_page+1) ]
    loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    # 获取2020一季度的现金流数据
    begin = time.time()
    year = 2020
    month = 3
    main(year, month)
    end = time.time()
    print(end - begin)
