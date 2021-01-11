"""
获取概念题材
run()
"""

from data_urls import get_concept_url
from comm_funcs import except_handle
from comm_funcs import requests_get
from comm_funcs import get_db_engine_for_pandas
from comm_funcs import ua_random
import threading
import math
import time
import json
import pandas as pd
import asyncio
import aiohttp


class ConceptDown(object):
    def __init__(self, data, page_size=100, engine=None):
        self._data = data
        self._engine = engine
        self._page_size = page_size
        self.num = 1

    async def _get_content(self, link):  # 传入的是资源链接
        header = {
            'user-agent': ua_random()
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(link, headers=header) as respose:
                return await respose.text()

    async def _download(self, page):
        content = await self._get_content(get_concept_url(page=page, psize=self._page_size))
        columns = {
            'item_code': 'SECURITYCODE',
            'item_name': 'SECURITYSHORTNAME',
            'concept_list': 'BK'
        }

        column = list(columns.keys())
        map_dict = list(columns.values())

        data = json.loads(content)
        insert_values = []
        if data['Data'] and len(data['Data']):
            for row in data['Data']:
                row['BK'] = row['BK'].replace(' ', ',')
                insert_values.append(
                    tuple(map(lambda x: row[x.upper()], map_dict)))

        df = pd.DataFrame(insert_values, columns=column)
        df.set_index('item_code', inplace=True)

        # new_df = df.explode('concept_list')
        df.to_sql(
            name='s_concepts',
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


def run():
    try:
        url = get_concept_url(psize=1, page=2)
        tc = json.loads(requests_get(url))['TotalCount']
        p_num = 100
        page_data = tuple(range(1, math.ceil(tc / p_num) + 1))

        engine = get_db_engine_for_pandas()
        spider = ConceptDown(page_data, p_num, engine)
        spider.run()
    except Exception as e:
        print(e)


# https://github.com/huangsir250/financial_data_pools
if __name__ == '__main__':

    '''
    sql使用例子：

    查询某个股票所属概念
    SELECT concept_list FROM `s_concepts` WHERE item_code='002131'

    根据概念名称查询所有股票
    SELECT * FROM `s_concepts` WHERE FIND_IN_SET('新能源车', concept_list)

    板块模糊匹配
    SELECT * FROM `s_concepts` WHERE concept_list LIKE '%新能源%'
    '''
    start_time = time.time()
    run()
    print('total {}'.format((time.time() - start_time)))
