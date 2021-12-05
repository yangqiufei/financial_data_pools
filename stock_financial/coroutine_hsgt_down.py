"""
获取沪深港通个股增减仓数据
"""

import threading
import math
import time
import json
import pandas as pd
import asyncio
import aiohttp

from data_urls import get_hsgt_detail_url
from comm_funcs import except_handle
from comm_funcs import requests_get
from comm_funcs import get_db_engine_for_pandas
from comm_funcs import ua_random
from comm_funcs import find_trade_date


class HSGTDetailDown(object):

    '''
    沪港深通个股详情
    '''
    def __init__(self, data, page_size=100, date=None, engine=None):
        '''
        初始化
        :param data: 页码，如[1,2,3,4]代表第一页，第二页，第三页，第四页
        :param page_size: 每页数量，默认为100条
        :param date: 要爬取的日期，格式为 2020-10-10
        :param engine: 数据库引擎，pandas需要调用
        '''
        self._data = data
        self._engine = engine
        self._page_size = page_size
        self._date = date
        self.num = 1

    async def _get_content(self, link):
        header = {
            'user-agent': ua_random()
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(link, headers=header) as respose:
                return await respose.text()

    async def _download(self, page):
        content = await self._get_content(get_hsgt_detail_url(page=page, psize=self._page_size, date=self._date))

        columns = {
            'item_code':'SCode',
            'item_name':'SName',
            'trade_date':'HdDate',
            'industry_name':'HYName',
            'industry_code':'HYCode',
            'institutions_sum':'JG_SUM',
            'shares_rate':'SharesRate',# 占总股本比例
            'share_hold':'ShareHold',# 持股数量
            'share_capital':'ShareSZ',# 持股市值
            'equity_rate':'LTZB',# 占流通股比例
            'total_equity_rate':'ZZB',# 占总股本比例
            'share_hold_chg':'ShareHold_Chg_One',# 当日持股数量变化
            'share_capital_chg':'ShareSZ_Chg_One',# 当日持股市值变化
            'share_capital_chg_rate':'ShareSZ_Chg_Rate_One',# 当日持股市值变化比例
            'circulate_chg_rate':'LTZB_One',# 当日流通市值变化比例
            'capital_chg_rate':'ZZB_One',# 当日总市值变化比例
        }

        column = list(columns.keys())
        map_dict = list(columns.values())

        data = json.loads(content)
        insert_values = []
        if data['data'] and len(data['data']):
            for row in data['data']:
                row['HdDate'] = row['HdDate'].replace('-', '')
                insert_values.append(
                    tuple(map(lambda x: row[x], map_dict)))

        df = pd.DataFrame(insert_values, columns=column)
        df.set_index('trade_date', inplace=True)
        df.fillna(0, inplace=True)

        # new_df = df.explode('concept_list')
        df.to_sql(
            name='s_hgst_detail',
            con=self._engine,
            if_exists='append')

        print('下载第%s页成功' % self.num)
        self.num += 1


    def run(self):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(
                self._download(page)) for page in self._data]
        loop.run_until_complete(asyncio.wait(tasks))


def run(date, pagesize=100):
    try:
        psize = 1
        url = get_hsgt_detail_url(psize=psize, page=1, date=date)
        tc = json.loads(requests_get(url))['pages']

        p_num = pagesize
        page_data = tuple(range(1, math.ceil(tc / p_num) + 1))
        engine = get_db_engine_for_pandas()
        spider = HSGTDetailDown(page_data, p_num, date, engine)
        spider.run()
    except Exception as e:
        except_handle(e)


# https://github.com/huangsir250/financial_data_pools
if __name__ == '__main__':

    start_time = time.time()
    # 获取最近一个交易日
    date = find_trade_date()
    run(date)
    print('total {}'.format((time.time() - start_time)))

