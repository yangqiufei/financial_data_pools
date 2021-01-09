"""
获取历史交易
run()
"""

import multiprocessing
from data_urls import get_notice_url
from comm_funcs import except_handle
from comm_funcs import requests_get
from comm_funcs import get_db_engine_for_pandas
from comm_funcs import get_current_date
import threading
import math
import os
import time
import json
import pandas as pd


class DownNotices(threading.Thread):

    '''
    爬取公告信息类
    '''

    def __init__(self, page_list, type=0, time=''):
        super().__init__()
        self._page_list = page_list
        self._type = type
        self._time = time

    def run(self):
        print('开启多进程 {} 线程'.format(self.getName()))
        self.scheduler()
        print('结束多进程 {} 线程'.format(self.getName()))

    def scheduler(self):
        '''
        调度函数
        :return:
        '''
        engine = get_db_engine_for_pandas()
        column = self.columns()
        if len(self._page_list):
            for page_num in self._page_list:
                url = get_notice_url(page=page_num, notice_type=self._type, date=self._time)

                try:
                    notice = requests_get(url)
                    notice = notice.replace('var  = ', '')
                    notices = notice.rstrip(';')
                    data_all = json.loads(notices)

                    if len(data_all['data']):

                        insert_values = []
                        for row in data_all['data']:
                            tmp_data = []
                            tmp_data.append(row['codes'][0]['stock_code'])
                            tmp_data.append(row['codes'][0]['short_name'])
                            tmp_data.append(
                                row['notice_date'][:10].replace('-', ''))
                            tmp_data.append(row['columns'][0]['column_code'])
                            tmp_data.append(row['columns'][0]['column_name'])
                            tmp_data.append(row['art_code'])
                            tmp_data.append(row['title'])
                            insert_values.append(tmp_data)

                        df = pd.DataFrame(insert_values, columns=column)

                        df.set_index('notice_date', inplace=True)
                        df.to_sql(
                            name='s_notices',
                            con=engine,
                            if_exists='append')
                    print('第{}下载完成'.format(page_num))

                except Exception as e:
                    except_handle(e)

    def columns(self):
        '''
        pandas dataframe列名和数据库列名
        :return:
        '''
        return [
            'item_code',
            'item_name',
            'notice_date',
            'column_code',
            'column_name',
            'art_code',
            'title',
        ]


def run(total_page=100, notice_type=0, notice_date=''):
    '''
    多进程运行程序入口
    :param total_page: 需要获取的总页数
    :param notice_type: 公告类型
    :param notice_date: 公告时间
    :return:
    '''

    if isinstance(total_page, int):
        data = tuple(range(1, total_page+1))
    else:
        data = tuple(range(1, 101))

    # 开启多进程
    p = multiprocessing.Pool()
    pool_num = multiprocessing.cpu_count()
    per_num = math.ceil(len(data) / pool_num)
    for i in range(pool_num):
        if i == 0:
            begin = 0
            end = per_num
        else:
            begin = i * per_num
            end = begin + per_num
        p.apply_async(main, args=(data[begin:end], notice_type, notice_date))
    p.close()
    p.join()


def main(data, notice_type=0, notice_date=''):
    '''
    主函数：多线程程序
    :param data:
    :param notice_type: 公告类型
    :param notice_date: 公告时间
    :return:
    '''
    if len(data):
        # 开启多线程
        crawls = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        thread_list = []
        per_num = math.ceil(len(data) / len(crawls))
        for i, crawl in enumerate(crawls):
            if i == 0:
                begin = 0
                end = per_num
            else:
                begin = i * per_num
                end = begin + per_num

            thread = DownNotices(data[begin:end], notice_type, notice_date)

            thread.start()
            thread_list.append(thread)

        # 结束多线程
        for crawl_thread in thread_list:
            crawl_thread.join()


if __name__ == '__main__':

    # https://github.com/huangsir250/financial_data_pools

    # 公告类型 type，0：所有，1：财报，2：融资，3：风险提示，4：信息变更，5：重大事项，6：资产重组，7,：持股变动

    start = time.time()

    # 获取指定某天的公告

    # date = '2021-01-07'
    # date = get_current_date()
    # data = tuple(range(1, 101))
    # main(data, notice_type=2, notice_date=date)

    # 获取所有定增的公告
    run(total_page=100, notice_type=2)
    end = time.time()
    print('共运行了{}秒'.format((end - start)))
