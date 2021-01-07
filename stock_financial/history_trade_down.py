"""
获取历史交易
run()
"""

import multiprocessing
from data_urls import get_history_trade_list
from comm_funcs import ua_random
from comm_funcs import except_handle
from comm_funcs import get_mysql_client
import threading
import math
import requests
import os
import shutil
import time


class down_history_csv(threading.Thread):

    def __init__(self, data_list, save_dir):
        super().__init__()
        self.date_list = data_list
        self._save_dir = os.path.abspath(save_dir)

    def run(self):
        print('开启多进程 {} 线程'.format(self.getName()))
        self.scheduler()
        print('结束多进程 {} 线程'.format(self.getName()))

    def scheduler(self):
        if len(self.date_list):
            for item_code in self.date_list:
                header = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'}

                url = get_history_trade_list(item_code=item_code)
                file_name = ''.join([item_code, '.csv'])
                save_name = os.path.join(self._save_dir, file_name)

                try:
                    down_res = requests.get(url, headers=header, stream=True)
                    if down_res.status_code == 200:
                        with open(save_name, 'wb') as f:
                            down_res.raw.deconde_conten = True
                            shutil.copyfileobj(down_res.raw, f)
                            print(
                                '多进程 {} 线程下载{}'.format(
                                    self.getName(), item_code))
                except Exception as e:
                    except_handle(e)


def run():
    # mysql_conn = get_mysql_client()
    # with mysql_conn.cursor() as mysql_cursor:
    #     mysql_cursor.execute('SELECT DISTINCT item_code FROM s_trade_detail')
    #     data_list = mysql_cursor.fetchall()
    # data = tuple(row[0] for row in data_list)
    # mysql_conn.close()

    # 下载指定的某些标的
    data = ['000001','000002','000100','000009','000090','000091']

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
        p.apply_async(main, args=(data[begin:end],))
    p.close()
    p.join()


def main(data):
    # 保存的目录
    save_dir = './csv/'

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    if len(data):
        # 开启多线程
        crawls = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        thread_list = []
        per_num = math.ceil(len(data) / len(crawls))
        for i, crawl in enumerate(crawls):
            if i == 0:
                begin = 0
                end = per_num
            else:
                begin = i * per_num
                end = begin + per_num

            thread = down_history_csv(data[begin:end], save_dir)

            thread.start()
            thread_list.append(thread)

        # 结束多线程
        for crawl_thread in thread_list:
            crawl_thread.join()


if __name__ == '__main__':

    # 下载所有票历史交易数据
    start = time.time()
    run()
    end = time.time()
    print('共运行了{}秒'.format((end - start)))
