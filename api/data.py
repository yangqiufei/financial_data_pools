import time
import sys

import pandas as pd
import requests
import json
import akshare as ak
import talib as ta
from functools import partial

sys.path.append("..")

from stock_financial.comm_funcs import find_trade_date
from stock_financial.comm_funcs import get_mysql_client_dict
from stock_financial.comm_funcs import get_db_engine_for_pandas
from stock_financial.comm_funcs import get_mysql_client
from stock_financial.comm_funcs import get_current_date
from stock_financial.comm_funcs import int_to_date
from stock_financial.comm_funcs import get_config
from stock_financial.comm_funcs import RedisClient
from stock_financial.comm_funcs import MysqlClient


redis_client = RedisClient()
re_conn = redis_client.get_redis_client()


class StockApi:

    @classmethod
    def get_next_date(cls, trade_date=None):
        if trade_date is None:
            return get_current_date().replace('-', '')

        key = get_config('cache', 'trade_data_set')
        date_val = re_conn.zrangebyscore(key, min=trade_date, max=trade_date, start=0, num=1)

        if len(date_val) > 0 and int(date_val[0]) > int(trade_date):
            return date_val[0]

    @classmethod
    def get_pre_date(cls, trade_date=None):
        if not trade_date:
            trade_date = cls.get_current_trade_date()

        key = get_config('cache', 'trade_data_set')
        date_val = re_conn.zscore(key, trade_date)

        if date_val and int(date_val) < int(trade_date):
            return str(date_val)[0:8]

        return None

    @classmethod
    def get_num_day(cls, num=5, trade_date=None, slug=1):
        """
        获取给定的trade_date前/后num的日期，不包括参数本身日期
        :param num: 
        :param trade_date: 
        :param slug: 1：前，2：后
        :return: 
        """
        if trade_date is None:
            trade_date = get_current_date().replace('-', '')

        find_date = None
        if slug == 1:
            while num > 0:
                find_date = cls.get_pre_date(trade_date)
                num = num - 1
        else:
            while num > 0:
                find_date = cls.get_next_date(trade_date)
                num = num - 1

        return find_date

    @classmethod
    def get_current_trade_date(cls):
        """
        获取最近一个交易日期
        :return:
        """
        return find_trade_date(return_format="int")

    @classmethod
    def get_newest(cls, item_code, key=''):
        """
        从东方财富网站直接获取单个票交易信息
        :param item_code:
        :param key:
        :return:
        """

        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/66.0.3359.139 Safari/537.36 '
        }
        domain = 'http://push2.eastmoney.com/api/qt/stock/get?'

        fields = 'f43,f44,f45,f46,f47,f48,f51,f52,f57,f58,f60,f107,f116,f117,f168,f169,f170,f168,f152'
        ut = 'b2884a393a59ad64002292a3e90d46a5'

        if item_code[0:1] == '6':
            sub_code = ''.join(['1.', item_code])
        else:
            sub_code = ''.join(['0.', item_code])

        timestamp_ = time.time_ns()
        url = '{}fields={}&fltt=2&invt=2&secid={}&ut={}&cb=&_={}'.format(domain, fields, sub_code, ut, timestamp_)

        down_day = requests.get(url, headers=header, stream=True)
        data = json.loads(down_day.text)

        res = {
            'percent': data['data']['f170'],
            'item_name': data['data']['f58'],
            'price': data['data']['f43'],
            'amount': data['data']['f48'],
            'volume': data['data']['f47'] * 100,
            'open': data['data']['f46'],
            'low': data['data']['f45'],
            'high': data['data']['f44'],
            'rise': data['data']['f51'],
            'fall': data['data']['f52'],
            'pre_close': data['data']['f60'],
            'market_capital': data['data']['f116'],
            'circulate': data['data']['f117'],
            'turnover_rate': data['data']['f168'],
        }

        if len(key) and key in res:
            return res[key]

        return res

    @classmethod
    def date_delta(cls, begin_date, end_date):
        """
        计算两个日期之间相隔的天数
        :param begin_date: 
        :param end_date: 
        :return: 
        """

        key = get_config('cache', 'trade_data_set')
        date_val = re_conn.zrangebyscore(key, min=begin_date, max=end_date)

        if len(date_val):
            return len(date_val)

    @classmethod
    def get_common_data(cls, **kwargs):
        """
        统一sql方法查询
        使用例子：params = {"table": "s_xueqiu_trade_dayk", "condition": {"trade_date": {"value": "1", "operator": ">"}}}
                datalist = StockApi.get_some_data(**params)
        :param kwargs: 参数，说明如下
        :table 表名
        :condition 条件，字典形式，如{"trade_date": {"value":20210801}},多个条件用列表，
        如{"trade_date":[{"value":20210801, "operator": ">="},{"value":20210830, "operator": "<="}]}
        :fields 字段
        :group group by
        :order order by
        :offset 偏移量
        :limit 每次查询数量
        :return:
        """
        table = kwargs.get("table", "")

        if not table:
            return ""

        condition = kwargs.get("condition", {})
        where = "1=1"
        if condition:
            for k, v in condition.items():
                if k == "no_parse":
                    where += " and {}".format(condition["no_parse"])
                    continue

                if isinstance(v, list):
                    for row in v:
                        if "value" not in row:
                            raise ValueError(
                                "condition 必须包含value键，如：{}".format('{"condition": {"item_time": {"value": "1", '
                                                                   '"operator": ">"}}}'))
                        if "operator" not in row:
                            operator = "="
                        else:
                            operator = row['operator']

                        where += " and {} {} '{}'".format(k, operator, row["value"])
                else:
                    if "value" not in v:
                        raise ValueError(
                            "condition 必须包含value键，如：{}".format('{"condition": {"item_time": {"value": "1", '
                                                               '"operator": ">"}}}'))
                    if "operator" not in v:
                        operator = "="
                    else:
                        operator = v['operator']

                    where += " and {} {} '{}'".format(k, operator, v["value"])

        fields = kwargs.get("fields", "*")
        field_str = ""
        if isinstance(fields, (list, set, tuple)):
            field_str = ",".join(list(fields))
        else:
            field_str = fields

        join = kwargs.get("join", {})
        if join:
            if isinstance(join, list):
                for row in join:
                    if "table" not in row:
                        raise ValueError(
                            "join 必须包含table键，如：{}".format('{"join": [{"table": "a", '
                                                          '"on": "t.id=a.tid", "how": "left"}]}'))
                    if "on" not in row:
                        raise ValueError(
                            "join 必须包含on键，如：{}".format('{"join": [{"table": "a", '
                                                       '"on": "t.id=a.tid", "how": "left"}]}'))
                    if "how" not in row:
                        how = "left"
                    else:
                        how = row['how']
                    table = " {} as t {} join {} on {}".format(table, how, row["table"], row["on"])
            else:
                if "table" not in join:
                    raise ValueError(
                        "join 必须包含table键，如：{}".format('{"join": [{"table": "a", '
                                                      '"on": "t.id=a.tid", "how": "left"}]}'))
                if "on" not in join:
                    raise ValueError(
                        "join 必须包含on键，如：{}".format('{"join": [{"table": "a", '
                                                   '"on": "t.id=a.tid", "how": "left"}]}'))
                if "how" not in join:
                    how = "left"
                else:
                    how = join['how']

                table = " {} as t {} join {} on {}".format(table, how, join["table"], join["on"])

        group = kwargs.get("group", "")
        order = kwargs.get("order", "")
        offset = kwargs.get("offset", -1)
        page_size = kwargs.get("limit", -1)
        # mysql_client = MysqlClient()
        # conn = mysql_client.get_client()
        conn = get_mysql_client_dict()
        sql = "select {} from {} where {}".format(field_str, table, where)

        if isinstance(group, str) and len(group) > 0:
            sql = sql + " group by {}".format(group)

        if isinstance(order, str) and len(order) > 0:
            sql = sql + " order by {}".format(order)

        if isinstance(offset, int) and isinstance(page_size, int):
            if offset >= 0 and page_size > 0:
                sql = sql + " limit {}, {}".format(offset, page_size)
            elif offset <= 0 and page_size > 0:
                sql = sql + " limit {}".format(page_size)

        debug = kwargs.get("debug", False)
        if debug:
            print(sql)
        with conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
        conn.close()

        return result

    @classmethod
    def get_strategy(cls, **kwargs):
        """
        查询 s_strategies 表数据
        :param kwargs:
        :return:
        """
        func = partial(cls.get_common_data, table="s_strategies")
        return func(**kwargs)

    @classmethod
    def get_trade_list(cls, **kwargs):
        """
        查询 s_trade_list 表数据
        :param kwargs:
        :return:
        """
        func = partial(cls.get_common_data, table="s_trade_list")
        return func(**kwargs)
        # print(res)

        # 写入缓存
        # if res and len(res) > 0:
        #     redis_client = RedisClient()
        #     redis_conn = redis_client.get_redis_client()
        #     key = get_config("cache", "s_trade_list")

    @classmethod
    def get_strategies_items(cls, **kwargs):
        """
        查询 s_trade_list 表数据
        :param kwargs:
        :return:
        """
        func = partial(cls.get_common_data, table="s_strategies_items")
        return func(**kwargs)

    @classmethod
    def get_trade_date_list(cls, begin, end):
        """
        获取交易日期list
        :param begin: 
        :param end: 
        :return: 
        """
        trade_list = []
        while begin < end:
            begin = cls.get_next_date(begin)

            if begin is not None and begin not in trade_list:
                trade_list.append(begin)

        return trade_list

    @classmethod
    def get_date_list(cls, begin=None, slug=1, num=15):
        """
        获取交易日期list
        :param begin: 开始时间
        :param slug: 1：往后去，比如begin为20201001，则取20201008及之后的，反之亦然
        :param num: list的长度
        :return: list
        """

        if begin is None:
            begin = cls.get_current_trade_date()

        trade_list = []
        i = 0

        while num > i:

            if slug == 1:
                begin = cls.get_next_date(begin)

            else:
                begin = cls.get_pre_date(begin)

            if begin is not None and begin not in trade_list:
                trade_list.append(begin)

            i = i + 1

        return trade_list

    @classmethod
    def insert_common(cls, **kwargs):
        engine = get_db_engine_for_pandas()

        try:
            table = kwargs.get("table", "")

            if not table:
                raise ValueError("数据库表不能为空")

            data = kwargs.get("data", {})
            data_list = [data]

            if len(data) <= 0:
                raise ValueError("数据不能为空")

            df = pd.DataFrame(data_list)
            df.set_index("strategy_id", inplace=True)

            df.to_sql(
                name=table,
                con=engine,
                if_exists='append')
        except Exception as e:
            print("数据库插入数据报错了：", e)

    @classmethod
    def insert_trade_list(cls, **kwargs):
        func = partial(cls.insert_common, table="s_trade_list")
        func(**kwargs)

    @classmethod
    def get_his_list(cls, item_code):
        stock_df = ak.stock_zh_a_hist(symbol=item_code, adjust="qfq")

        stock_df.rename(columns={"日期": "date", '开盘': "open", "收盘": "close", "最高": "high", "最低": "low",
                                 "成交量": "volume", "成交额": "value", "振幅": "amplitude", "涨跌额": "change",
                                 "涨跌幅": "pct_change", "换手率": "turnover_rate"},
                        inplace=True)

        return stock_df

    @classmethod
    def get_newest_ma(cls, item_code, ma=5, trade_date=None):
        stock_df = cls.get_his_list(item_code=item_code)
        # stock_df.set_index("date", inplace=True)

        stock_df['ma{}'.format(ma)] = ta.MA(stock_df['close'], timeperiod=ma)

        if trade_date:
            find_df = stock_df.loc[(stock_df['date'] == trade_date), :]
        else:
            find_df = stock_df.tail(1)

        return find_df


if __name__ == "__main__":
    df = StockApi.get_newest_ma(item_code="000100")
    print(df["ma5"].values.tolist()[0])