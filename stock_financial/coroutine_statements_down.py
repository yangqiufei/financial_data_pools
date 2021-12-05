"""
获取财务报表信息

使用示例 （获取2020年二季度数据）
    year = 2020
    month = 6
    main(year=year, month=month)
"""


from data_urls import get_statements_url
from comm_funcs import async_crawl
from comm_funcs import get_db_engine_for_pandas
from comm_funcs import time_last_day_of_month
from comm_funcs import get_page_num
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

    df.set_index('reportdate', inplace=True)
    df['assigndscrpt'].fillna('', inplace=True)
    df.fillna(0, inplace=True)

    df.to_sql(
        name='s_financial_statements',
        con=engine,
        if_exists='append')

def column():
    return [
        'security_code',
        'security_name_abbr',
        'notice_date',
        'reportdate',
        'update_date',
        'eitime',
        'basic_eps',
        'bps',
        'weightavg_roe',
        'mgjyxjje',
        'xsmll',
        'ystz',
        'yshz',
        'sjltz',
        'sjlhz',
        'assigndscrpt'
    ]

def main(year, month):
    engine = get_db_engine_for_pandas()
    report_date = time_last_day_of_month(year=year, month=month)
    total_page = int(get_page_num(get_statements_url(report_date=report_date))['result']['pages'])
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(parse(
            get_statements_url(report_date=report_date, page=p), engine)) for p in range(1, total_page+1) ]
    loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    # 代码地址：
    # https://github.com/huangsir250/financial_data_pools
    begin = time.time()
    # 获取2020年三季度财务报表信息数据
    # [3|6|9|12]
    year = 2020
    month = 12
    main(year=year, month=month)
    end = time.time()
    print(end - begin)
