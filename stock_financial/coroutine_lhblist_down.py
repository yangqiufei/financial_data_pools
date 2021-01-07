"""
获取龙虎板列表信息

使用示例（获取2020-12-31龙虎榜列表数据）：
main('2020-12-31', '2020-12-31')
"""

import time
import json
import pandas as pd
import math
from data_urls import get_lhb_list_url
from data_urls import get_lhb_detail_url
from comm_funcs import async_crawl
from comm_funcs import get_db_engine_for_pandas
from comm_funcs import get_page_num
from comm_funcs import get_current_date
from comm_funcs import requests_get
from comm_funcs import except_handle
from comm_funcs import get_mysql_client
import asyncio
import lxml.etree


def columns_dict():
    return {
        'trade_date': 'Tdate',
        'item_code': 'SCode',
        'item_name': 'SName',
        'close': 'ClosePrice',
        'percent': 'Chgradio',
        'turnoverrate': 'Dchratio',
        'circulate': 'Ltsz',
        'total_rate': 'ZeRate',
        'net_buying': 'JmMoney',
        'amount': 'Turnover',
        'total_buying': 'ZeMoney',
        'buying': 'Bmoney',
        'selling': 'Smoney',
        'buying_rate': 'JmRate',
        'reasons': 'Ctypedes',
        'volume': 'Ntransac'
    }


async def parse_detail(row):
    item_code = row['SCode']
    trade_date = row['Tdate']
    url = get_lhb_detail_url(item_code=item_code, trade_date=trade_date)
    response = await async_crawl(url)
    # response.decode('utf8').encode('gb2312')
    # response = response.decode("gb2312")
    # response = requests_get(url)
    try:
        trade_date = trade_date.replace('-', '')
        selector = lxml.etree.HTML(response)
        content = selector.xpath('//*[@id="main-wrap"]/div/div[2]/div/div[@class="content-sepe"]')
        conn = get_mysql_client()
        cursor = conn.cursor()

        for row in content:
            buy_table = row.xpath('./table[1]')[0]
            sell_table = buy_table.xpath('./following-sibling::table[1]')[0]
            buy_tr = buy_table.xpath('./tbody/tr')
            sell_tr = sell_table.xpath('./tbody/tr')
            for sell_row in sell_tr:
                b_sort = sell_row.xpath('./td[1]/text()')[0]
                if b_sort == '(买入前5名与卖出前5名)':
                    for buy_row in buy_tr:
                        detail_type = 1
                        b_sort = buy_row.xpath('./td[1]/text()')[0]
                        sc_name = buy_row.xpath('./td[2]/div[1]/a[2]/text()')[0]
                        sc_id = buy_row.xpath('./td[2]/div[2]/input[@class="sales-code"]/@value')
                        buying = buy_row.xpath('./td[3]/text()')[0]
                        buying_rate = buy_row.xpath('./td[4]/text()')[0]
                        selling = buy_row.xpath('./td[5]/text()')[0]
                        selling_rate = buy_row.xpath('./td[6]/text()')[0]
                        cursor.execute(
                            'insert into s_lhb_detail(trade_date,item_code,s_sort,sc_name,buying,selling,sc_id,detail_type) '
                            'values(%s, %s, %s,%s, %s, %s, %s, %s);',
                            (trade_date, item_code, b_sort, sc_name, buying, selling, sc_id, detail_type))
                    continue
                sc_name = sell_row.xpath('./td[2]/div[1]/a[2]/text()')[0]
                sc_id = sell_row.xpath('./td[2]/div[2]/input[@class="sales-code"]/@value')
                buying = sell_row.xpath('./td[3]/text()')[0]
                buying_rate = sell_row.xpath('./td[4]/text()')[0]
                selling = sell_row.xpath('./td[5]/text()')[0]
                selling_rate = sell_row.xpath('./td[6]/text()')[0]
                detail_type = 2
                cursor.execute(
                    'insert into s_lhb_detail(trade_date,item_code,s_sort,sc_name,buying,selling,sc_id, detail_type) '
    'values(%s, %s, %s,%s, %s, %s, %s, %s);',
                    (trade_date, item_code, b_sort, sc_name, buying, selling, sc_id, detail_type))
    except Exception as e:
        except_handle(e)
    finally:
        conn.commit()
        cursor.close()
        conn.close()


def parse(data, engine):
    column_dict = columns_dict()
    column = list(column_dict.keys())
    map_dict = list(column_dict.values())

    insert_values = []
    for row in data:
        data_tmp = tuple(map(lambda x: row[x], map_dict))
        insert_values.append(tuple(data_tmp))


    if insert_values:
        # column.append('trade_date')
        df = pd.DataFrame(insert_values, columns=column)
        df.set_index('item_code', inplace=True)
        df.fillna(0, inplace=True)
        # df.fillna(0, inplace=True)

        df['trade_date'] = df['trade_date'].str.replace('-', '')
        # df['trade_date'] = 20201231
        df.to_sql(
            name='s_lhb',
            con=engine,
            if_exists='append')


def main(begin_date, end_date):
    engine = get_db_engine_for_pandas()
    try:
        pages = 1
        data_list = []
        url = get_lhb_list_url(begin_date=begin_date, end_date=end_date)
        response = requests_get(url)
        lhb_list = json.loads(response)
        data_list = lhb_list['data']

        data_pages = lhb_list['pages']
        while data_pages > pages:
            pages = pages + 1
            url = get_lhb_list_url(begin_date=begin_date, end_date=end_date, page=pages)
            response = requests_get(url)
            lhb_list = json.loads(response)
            data_list.append(lhb_list['data'])

        # 将龙虎榜列表数据存入数据库中
        # parse(data_list, engine)

        # 龙虎榜详情使用协程创建任务
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(parse_detail(row)) for row in data_list]
        loop.run_until_complete(asyncio.wait(tasks))
    except Exception as e:
        except_handle(e)


# https://github.com/huangsir250/financial_data_pools
if __name__ == '__main__':
    # 最近一个交易日市场的交易信息
    betime = time.time()
    main('2020-12-31', '2020-12-31')
    total_time = time.time() - betime
    print(total_time)
