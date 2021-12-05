"""
获取60日新高

使用示例（获取2020年第2季度利润）：
    year = 2020
    month = 6
    main(year, month)
"""
import json
import time
import pandas as pd
import asyncio
import math
import sys

from stock_financial.data_urls import high60_url as down_url
from stock_financial.comm_funcs import async_crawl
from stock_financial.comm_funcs import get_db_engine_for_pandas
from stock_financial.comm_funcs import get_page_num
from api.data import StockApi

sys.path.append("..")


async def parse(url):
    data = await async_crawl(url)
    parse_data_list = json.loads(data)
    data_all = parse_data_list["data"]["allstock"]

    insert_values = []
    for row in data_all:
        insert_values.append(row["c"])

    return insert_values


def main():
    engine = get_db_engine_for_pandas()
    page_size = 64
    total_number = int(get_page_num(down_url())['data']['tc'])
    total_page = math.ceil(total_number/page_size)
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(parse(
            down_url(pagesize=page_size, page=p))) for p in range(0, total_page)]
    loop.run_until_complete(asyncio.wait(tasks))

    merge_data = []
    for t in tasks:
        merge_data.extend(t.result())

    df = pd.DataFrame(set(merge_data))
    df.columns = ["item_code"]

    df["trade_date"] = StockApi.get_current_trade_date()

    df.to_sql(
        name='s_changes',
        con=engine,
        if_exists='append',
        index=False)


if __name__ == '__main__':
    begin = time.time()
    main()
    end = time.time()
    print(end - begin)
