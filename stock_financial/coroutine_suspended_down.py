"""
获取停牌牌个股信息

使用示例（获取2019-05-01及以后的所有停复牌数据）：
    fd = '2019-05-01'
    main(fd)
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

    insert_values = []
    for row in parse_data_list['data']:

        row_list = row.split(',')

        tuple_list = tuple(row_list)
        if len(tuple_list) == 9:
            insert_values.append(tuple_list)

    columns = [
        'item_code',
        'item_name',
        'begin_datetime',
        'end_datetime',
        'suspended_type',
        'suspended_reasons',
        'mark_type',
        'begin_date',
        'resumption_date'
    ]
    df = pd.DataFrame(insert_values, columns=columns)

    df.set_index('begin_date', inplace=True)
    df.fillna(0, inplace=True)

    df.to_sql(
        name='s_suspended_items',
        con=engine,
        if_exists='append')

def main(fd):
    engine = get_db_engine_for_pandas()
    total_page = int(get_page_num(get_suspended_url(fd=fd))['pages'])
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(parse(
            get_suspended_url(fd=fd, page=p), engine)) for p in range(1, total_page+1) ]
    loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    begin = time.time()
    # 获取2019-05-01之后所有的停复牌个股
    fd = '2019-05-01'
    main(fd)
    print(time.time() - begin)
