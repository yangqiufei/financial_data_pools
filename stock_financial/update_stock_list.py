import tushare as ts
import threading
import time
import os
import sys

sys.path.append("..")

from api.data import StockApi
from stock_financial.comm_funcs import get_redis_client
from stock_financial.comm_funcs import get_config
from stock_financial.comm_funcs import except_handle


def push_code_queue(redis_conn, queue_key, set_key, trade_date=None):
    redis_conn.delete(queue_key)

    if trade_date is None:
        trade_date = StockApi.get_current_trade_date()

    # 当日交易的
    data = StockApi.get_tradedate_detail(trade_date=trade_date, fileds='item_code')

    filter_date = []

    # 用iterrows()方法循环取数据
    for row in data:
        code = row['item_code']

        if code in filter_date or redis_conn.sismember(set_key, code):
            continue

        redis_conn.rpush(queue_key, code)

    redis_conn.expire(queue_key, 60 * 60 * 3)
    redis_conn.expire(set_key, 60 * 60 * 24)


class DownStock(threading.Thread):
    def __init__(self, t_name, queue_key, set_key, save_dirname, redis_conn, rpoplpush_key=None):
        super().__init__()
        self.thread_id = t_name
        self.queue_key = queue_key
        self.set_key = set_key
        self.save_dirname = save_dirname
        self.redis_conn = redis_conn
        self.rpoplpush_key = rpoplpush_key

    def run(self):
        print('启动 {}'.format(self.thread_id))
        self.scheduler()
        print('结束 {}'.format(self.thread_id))
        # self.redis_conn.expire(self.set_key, 60 * 60 * 3)

    def scheduler(self):
        while True:
            # 使用rpoplpush， 取出一个数后写入另外一个队列，提供计算
            code = self.redis_conn.rpop(self.queue_key)
            if not code:
                break

            if code[0] == '6':
                item_code = ''.join([code, '.SH'])
            else:
                item_code = ''.join([code, '.SZ'])

            file_name = ''.join([code, '.csv'])
            save_name = os.path.join(self.save_dirname, file_name)

            try:
                print('{} 开始下载 {}历史数据, 保存路径 {}'.format(self.thread_id, code, save_name))
                # df = pro.daily(ts_code=code, start_date='', end_date='')
                df = ts.pro_bar(ts_code=item_code, adj='qfq', start_date='', end_date='',
                                ma=[5, 10, 20, 30, 60], factors=['tor', 'vr'])

                try:
                    df.to_csv(save_name, index=False)
                except Exception as e1:
                    pass

                self.redis_conn.sadd(self.set_key, code)

                time.sleep(1)
            except Exception as e:
                # self.redis_conn.rpush(self.queue_key, code)
                except_handle('{} {}下载失败,原因: {}'.format(self.thread_id, code, e))


def run(td_date=None):
    # confirm_input = input('确认下载所有股票的历史交易数据吗吗？[yes|no]')
    ts.set_token(get_config('tushare', 'token'))

    ts.pro_api()
    save_dirname = get_config('tushare', 'savedir')
    redisconn = get_redis_client()

    if td_date is None:
        td_date = StockApi.get_current_trade_date()

    # print(td_date)
    queue_key = get_config('kvcache', 'ts_pending_down_code_queue').replace('{{date}}', str(td_date))  # redis队列名称
    set_key = get_config('kvcache', 'ts_downing_code_set').replace('{{date}}', str(td_date))  # redis队列名称
    bk_oper_queue = get_config('kvcache', 'bk_oper_queue').replace('{{date}}', str(td_date))  # redis队列名称

    push_code_queue(redis_conn=redisconn, queue_key=queue_key, set_key=set_key, trade_date=td_date)

    # p = multiprocessing.Pool()
    # pool_num = multiprocessing.cpu_count()
    # for _ in range(pool_num):
    #     print(11)
    #     p.apply_async(main, args=(queue_key, set_key, save_dirname, redisconn))
    # p.close()
    # p.join()

    main(queue_key, set_key, save_dirname, redisconn, bk_oper_queue)

    # redis_lock = threading.Lock()

    print('主进程结束')


def main(queue_key, set_key, save_dirname, redisconn, bk_oper_queue=None):
    # 开启多线程
    # 线程名称
    crawls = ['14', '15', '21', '22', '23', '24', '25']

    thread_list = []
    for crawl in crawls:

        thread = DownStock(crawl, queue_key, set_key, save_dirname, redisconn, bk_oper_queue)
        thread.start()
        thread_list.append(thread)

    # 结束多线程
    for crawl_thread in thread_list:
        crawl_thread.join()


if __name__ == '__main__':
    StockApi.get_next_day()
    run()

    # num = StockApi.datedelta('20210710', '20210729')
    # print(num)

    # StockApi.update_trade_date_to_cache()
    # cur = StockApi.get_current_trade_date()
    # cur = '20210725'
    #
    # i = 0
    # while i<1:
    #
    #     cur = StockApi.get_next_day(cur)
    #     print(cur)
    #     i = i + 1

    # while True:
    #     td_list.append(cur_date)
    #     cur_date = StockApi.get_next_day(cur_date)
    #     if cur_date is None:
    #         print(111)
    #         break
    # print(len(td_list))

    # print(get_config( 'kvcache', 'trade_data_zset'))
    # print(get_config('tushare', 'savedir'))

    # df = ts.pro_bar(ts_code='000100.SZ', adj='qfq', start_date='', end_date='',
    #                 ma=[5, 10, 20, 30, 60], factors=['tor', 'vr'])
    # print(df)
