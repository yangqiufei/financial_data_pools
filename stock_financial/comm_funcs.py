# -*- coding:utf-8 -*-
# /usr/bin/env python
"""
公用函数库/类
"""
import random
import requests
import datetime
import json
import calendar
import os
import pandas as pd
import threading
import aiohttp
import yaml
import akshare as ak
import sqlalchemy
import smtplib
import pymysql
from pymysql.cursors import DictCursor
from email.mime.text import MIMEText
from redis import StrictRedis


def ua_random():
    """
    随机获取一个user-agent
    :return: user-agent
    """
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393"
    ]

    return random.choice(user_agent_list)


async def async_crawl(url):
    header = {
        'user-agent': ua_random()
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=header) as response:
            return await response.text()


def requests_get(url):
    """
    利用request模拟一个get请求
    :param url:
    :return:
    """
    header = {
        'user-agent': ua_random()
    }

    data = requests.get(url, header)
    if data.status_code == 200:
        return data.text

    return None


def get_current_date():
    """
    获取当前日期
    :return: str,日期
    """
    return datetime.datetime.now().strftime('%Y-%m-%d')


def except_handle(exception_handle):
    print(exception_handle)


def get_page_num(url):
    """
    获取分页数量
    :param url:
    """
    try:
        requests_text = requests_get(url)
        return json.loads(requests_text)
    except Exception as e:
        # 传给异常处理函数
        except_handle(e)


def time_last_day_of_month(year=None, month=None):
    """
    获取当前月的最后一天
    :return:
    """
    if year is None:
        year = datetime.datetime.now().year

    if month is None:
        month = datetime.datetime.now().month

    day = calendar.monthrange(year, month)[1]
    if len(str(month)) == 1:
        month = '0' + str(month)
    return '-'.join([str(year), str(month), str(day)])


class Singleton(object):
    """
    单例模式
    """
    _instance_lock = threading.Lock()
    _conf = None

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        _instance = kwargs.get("instance", cls.__name__ + "_instance")
        if not hasattr(Singleton, _instance):
            with Singleton._instance_lock:
                if not hasattr(Singleton, _instance):
                    Singleton._instance = object.__new__(cls)

        return Singleton._instance


class YamlConfigParser(Singleton):
    """
    单例模式
    """
    _conf = None

    @classmethod
    def get_config(cls):
        if not cls._conf:
            # 读取配置
            work_path = os.path.dirname(os.path.realpath(__file__))
            yaml_file = os.path.join(work_path, 'config.yaml')
            with open(yaml_file, 'r', encoding="utf-8") as file:
                file_data = file.read()

            yaml_config = yaml.safe_load(file_data)
            setattr(cls, "_conf", yaml_config)

        return cls._conf

    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(YamlConfigParser, "_instance"):
    #         with YamlConfigParser._instance_lock:
    #             if not hasattr(YamlConfigParser, "_instance"):
    #                 YamlConfigParser._instance = object.__new__(cls)
    #
    #                 # 读取配置
    #                 work_path = os.path.dirname(os.path.realpath(__file__))
    #                 yaml_file = os.path.join(work_path, 'config.yaml')
    #                 with open(yaml_file, 'r', encoding="utf-8") as file:
    #                     file_data = file.read()
    #
    #                 yaml_config = yaml.safe_load(file_data)
    #                 setattr(YamlConfigParser, "_conf", yaml_config)
    #
    #     return YamlConfigParser._instance


def get_config(read_default_group=None, key=None):
    """
    获取yaml文件参数
    :param read_default_group: 参数分类，可选，如果不传则返回整个yaml配置
    :param key: 参数名，可选，必须和read_default_group一起使用
    :return:dict|string
    """
    config_parser = YamlConfigParser()
    yaml_global_config = config_parser.get_config()

    # 如果不为空，则取值
    if read_default_group is not None:
        if read_default_group not in yaml_global_config:
            raise KeyError("配置项 {} 不存在".format(read_default_group))

        group_config = yaml_global_config[read_default_group]
        if key is not None:
            if key not in group_config:
                raise KeyError("配置项 {} 中 {} 不存在".format(read_default_group, key))

            # 返回单个配置值
            return group_config[key]

        # 返回分类配置所有值
        return group_config

    # 返回整个配置
    return yaml_global_config


def send_main(contents='', subject='', receivers=None):
    """
    发送邮件
    :param contents: 发送内容
    :param subject:  发送主题
    :param receivers: 接收人
    :return:
    """
    # 设置服务器所需信息
    mail_config = get_config()
    mail_host = mail_config['email']['mail_host']

    # 用户名
    mail_user = mail_config['email']['mail_user']

    # 密码(部分邮箱为授权码)
    mail_pass = mail_config['email']['mail_pass']

    # 邮件发送方邮箱地址
    sender = mail_config['email']['mail_sender']

    if receivers is None:
        # 邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
        receivers = ['1762934298@qq.com']
    elif not isinstance(receivers, list):
        raise TypeError("邮箱类型必须为列表")

    # 邮件内容设置纯文本
    message = MIMEText(contents, 'plain', 'utf-8')

    # 邮件主题
    message['Subject'] = subject

    # 发送方信息
    message['From'] = sender

    # 接受方信息
    message['To'] = receivers[0]

    try:
        smtp_obj = smtplib.SMTP()

        # 连接到服务器
        smtp_obj.connect(mail_host, 25)

        # 登录到服务器
        smtp_obj.login(mail_user, mail_pass)

        # 发送
        smtp_obj.sendmail(sender, receivers, message.as_string())

        # 退出
        smtp_obj.quit()

        return True
    except smtplib.SMTPException as e:
        raise smtplib.SMTPException(e)


def get_csv_path(symbol, period="daily") -> str:
    """
    获取个股本地csv路径
    :param period: 日线：daily； 周线：weekly; 月线： monthly
    :param symbol: 个股代码
    :return: str
    """
    config = get_config("save_path")
    save_file_path = config["stock"][period]["path"]
    save_file_name = config["stock"][period]["file_name"].replace("<<stock_code>>", symbol)
    return os.path.join(save_file_path, save_file_name)


def get_symbol(
        symbol: str,
        period: str = "daily",
        adjust: str = "",
        start_date: str = "",
        end_date: str = "",
        downloaded: bool = True
):
    """
    获取df
    :param symbol: 个股代码
    :param period: 日线：daily； 周线：weekly; 月线： monthly
    :param adjust: 复权类型，前复权："qfq"；后复权："hfq"；"不复权"：""， 默认不复权
    :param start_date: 开始时间
    :param end_date: 结束时间
    :param downloaded: 是否需要下载到本地
    :return:
    """
    file_name = get_csv_path(symbol, period)

    # 优先下载最新的到本地
    if downloaded:
        return down_symbol(symbol, period, is_return=True)

    if len(end_date):
        end_date = get_current_date().replace('-', '')

    if os.path.exists(file_name):
        return pd.read_csv(file_name)
        # df.set_index('trade_date', inplace=True, drop=False)
        # df.sort_index(ascending=True, inplace=True)
    else:
        param = {
            "symbol": symbol,
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "adjust": adjust,
        }
        return ak.stock_zh_a_hist(**param)


def down_symbol(
        symbol: str,
        period: str = "daily",
        is_return: bool = False,
        adjust: str = ""
) -> pd.DataFrame:
    """
    下载个股记录并保存为csv到本地
    :param symbol: 个股代码
    :param period: 日线：daily； 周线：weekly; 月线： monthly
    :param is_return: 是否需要返回
    :param adjust: 复权类型，前复权："qfq"；后复权："hfq"；"不复权"：""， 默认不复权
    :return: any
    """
    try:
        save_filename = get_csv_path(symbol, period)
        param = {
            "symbol": symbol,
            "period": period,
            "adjust": adjust,
        }
        symbol_df = ak.stock_zh_a_hist(**param)
        symbol_df.to_csv(save_filename, index=False)

        if is_return:
            return symbol_df

    except Exception as e:
        raise ValueError('{}下载失败,原因: {}'.format(symbol, e))


def find_trade_date(return_format="date", trade_date=None):
    """
    返回最近一个交易日
    :param return_format: 返回的格式，date: 返回 datetime.date; int: 返回整型，如：20210917；str: 返回字符串格式，如2021-09-17
    :param trade_date: 如果传值了，查找距离该值最近的交易日，比如2021-09-18（周六），最近的交易日是2021-09-17；
    如果传值的日期是交易日，则返回本身；因此也可以作为判断某天是否是交易日（只需要判断返回值和传值是否相等）
    :return:
    """
    if trade_date is None:
        trade_date = datetime.datetime.now().date()

    if not isinstance(trade_date, datetime.date):
        # 如果提交的不是datetime，做一个转换
        if isinstance(trade_date, str):
            year, month, day = trade_date.split('-')
            trade_date = datetime.date(int(year), int(month), int(day))

        if isinstance(trade_date, int):
            year = int(str(trade_date)[0:4])
            month = int(str(trade_date)[4:6])
            day = int(str(trade_date)[6:8])
            trade_date = datetime.date(int(year), int(month), int(day))

    find = 0
    last_trade_date = trade_date
    redis_client = RedisClient()
    redis_conn = redis_client.get_redis_client()
    key = get_config("cache", "history_td_set")
    if redis_conn.sismember(key, int(str(trade_date).replace('-', ''))):
        find = 1
        last_trade_date = trade_date

    # 没有找到，则通过接口查找
    if find == 0:
        df = ak.tool_trade_date_hist_sina()
        today_df = df.loc[df['trade_date'] == trade_date]
        if today_df.empty:
            # 继续寻找
            today_df = df.loc[df['trade_date'] < trade_date].tail(1)

        last_trade_date = today_df['trade_date'].values[0]

        # 回写缓存
        redis_conn.sadd(key, int(str(last_trade_date).replace('-', '')))

    if return_format == 'int':
        return int(str(last_trade_date).replace('-', ''))

    if return_format == 'str':
        return str(last_trade_date)

    return last_trade_date


def get_trade_detail(symbol: str = "", trade_date: str = "") -> dict:
    """
    获取一个交易日交易信息
    :param symbol: 代码
    :type symbol: str
    :param trade_date: 交易日
    :type symbol: str
    :return: 交易信息
    :rtype: dict
    """
    param = {
        "symbol": symbol,
        "period": "daily",
        "start_date": trade_date.replace("-", ""),
        "end_date": trade_date.replace("-", ""),
    }
    symbol_df = ak.stock_zh_a_hist(**param)

    if not symbol_df.empty:
        key = symbol_df.columns.values
        val = symbol_df.values[0]
        return dict(zip(key, val))

    return {}


def get_db_config():
    """
    获取服务器链接
    :return: host, user, password, database, port, charset
    """
    db_config = get_config()

    if "mysql" in db_config:
        host = db_config['mysql']['host']
        user = db_config['mysql']['user']
        password = db_config['mysql']['password']
        database = db_config['mysql']['database']
        port = db_config['mysql']['port']
        charset = db_config['mysql']['charset']

        return host, user, password, database, port, charset
    else:
        raise KeyError("mysql configuration must exist")


def get_db_engine_for_pandas():
    """
    获取mysql连接，主要搭配pandas使用
    :return:
    """
    host, user, password, database, port, charset = get_db_config()
    cnf = "mysql+pymysql://{}:{}@{}:{}/{}".format(
        user, password, host, port, database)
    return sqlalchemy.create_engine(cnf)
    # return sqlalchemy.create_engine(cnf, echo=True)


class RedisClient(Singleton):
    _client = None

    @classmethod
    def get_redis_client(cls, db=None):
        """
        获取redis连接
        :return:
        """
        if not cls._client:
            redis_config = get_config()
            redis_db = int(redis_config['redis']['queue_db'])

            if db is not None:
                redis_db = db

            client = StrictRedis(
                host=redis_config['redis']['host'],
                port=int(redis_config['redis']['port']),
                db=redis_db,
                password=redis_config['redis']['password'],
                decode_responses=True)
            setattr(cls, "_client", client)

        return cls._client


def get_redis_client(db=None):
    """
    获取redis连接
    :return:
    """
    redis_config = get_config()
    redis_host = redis_config['redis']['host']
    redis_port = int(redis_config['redis']['port'])
    redis_queue_db = int(redis_config['redis']['queue_db'])
    redis_passwd = redis_config['redis']['password']

    if db is not None:
        redis_queue_db = db

    return StrictRedis(
        host=redis_host,
        port=redis_port,
        db=redis_queue_db,
        password=redis_passwd,
        decode_responses=True)


def get_mysql_client():
    """
    获取数据库连接
    :return:
    """
    host, user, password, database, port, charset = get_db_config()
    db_config = {
        'host': host,
        'user': user,
        'password': password,
        'database': database,
        'port': int(port),
        'charset': charset
    }

    return pymysql.connect(**db_config)


class MysqlClient(Singleton):
    _mysql_client = None

    @classmethod
    def get_client(cls, dict_cursor=True, db=None):
        """
        获取mysql连接
        :return:
        """
        if not cls._mysql_client:
            host, user, password, database, port, charset = get_db_config()

            if db is not None:
                database = db

            db_config = {
                'host': host,
                'user': user,
                'password': password,
                'database': database,
                'port': int(port),
                'charset': charset
            }

            if dict_cursor:
                db_config['cursorclass'] = DictCursor

            client = pymysql.connect(**db_config)

            setattr(cls, "_mysql_client", client)

        return cls._mysql_client


def get_mysql_client_dict():
    """
    获取数据库链接
    :return:
    """
    host, user, password, database, port, charset = get_db_config()
    db_config = {
        'host': host,
        'user': user,
        'password': password,
        'database': database,
        'port': int(port),
        'charset': charset,
        'cursorclass': DictCursor
    }

    return pymysql.connect(**db_config)


def date_to_int(date, slug='-'):
    """
    将日期转换成整数，如2020-10-12 转换成20201012
    :param date:
    :param slug: 分隔符
    :return:
    """
    return str(date).replace(slug, '')


def int_to_date(number, slug='-'):
    """
    将数字转换成日期，如20201012 转成2020-10-12
    :param number:
    :param slug: 分隔符
    :return:
    """
    number_str = str(number)
    if len(number_str) == 8:
        return slug.join([number_str[0:4], number_str[4:6], number_str[6:8]])

    return ''


def check_work_time(**kwargs):
    """
    检测是否在工作时段，如果不在工作时段，则休眠，默认是 9:25:00.000 - 15:00:00.000
    @param: start_hour:开始工作的小时， 默认为上午9
    @param: start_minute:开始工作的分钟， 默认为25
    @param: start_second:开始工作的秒，默认为0
    @param: start_microsecond:开始工作的毫秒，默认为0
    @param: end_hour:结束工作的小时，默认为下午15
    @param: end_minute:结束工作的分钟，默认为0
    @param: end_second:结束工作的秒，默认为0
    @param: end_microsecond:结束工作的毫秒，默认为0
    使用例子：设置工作时间段为上午10点30分30秒 至 下午14点30分20秒
    t = {"end_hour": 14, "end_minute": 30, "end_second": 20, "start_hour": 10, "start_minute": 30, "start_second": 30}
    self.check_work_time(**t)
    """
    now = datetime.datetime.today()
    date = str(now.date())

    # 首先检测是否是交易日
    if date != find_trade_date(return_format="str", trade_date=date):
        # 直接休眠一天
        one_day = 24 * 60 * 60
        return one_day

    start_hour = kwargs.get("start_hour", 9)
    start_minute = kwargs.get("start_minute", 25)
    start_second = kwargs.get("start_second", 0)
    start_microsecond = kwargs.get("start_microsecond", 0)
    start_time = datetime.datetime(now.year, now.month, now.day, start_hour,
                                   start_minute, start_second, start_microsecond)

    # 检测是否是交易时间
    if start_time > now:
        time_delta = start_time - now

        # 还没开始, 进入休眠
        return time_delta.seconds

    end_hour = kwargs.get("end_hour", 15)
    end_minute = kwargs.get("end_minute", 0)
    end_second = kwargs.get("end_second", 0)
    end_microsecond = kwargs.get("end_microsecond", 0)
    end_time = datetime.datetime(now.year, now.month, now.day,
                                 end_hour, end_minute, end_second, end_microsecond)
    if now > end_time:
        next_start_time = start_time + datetime.timedelta(days=1)
        time_delta = next_start_time - now

        # 已经结束了，直接休眠到第二天开始时间
        return time_delta.seconds

    return -1


def is_stock_rise(item_code):
    """
    涨停的百分比
    :param item_code:
    :return:
    """
    if item_code[0:2] == '68' or item_code[0:1] == '3':
        return 1.2

    return 1.1


def rise_percent(item_code):
    """
    获取涨停的百分比
    :param item_code:
    :return:
    """
    return is_stock_rise(item_code)


def get_rise_price(item_code, yclose):
    """
    计算涨停的价格
    :param item_code:
    :param yclose:
    :return:
    """
    yclose = float(yclose)
    stock_rise_percent = rise_percent(item_code)
    return round(yclose * stock_rise_percent, 2)


if __name__ == "__main__":
    # time_param = {"end_hour": 15, "end_minute": 0, "end_second": 0, "start_hour": 9, "start_minute": 30}
    # print(check_work_time(**time_param)/3600)
    # redis_client = RedisClient()
    # redis_conn = redis_client.get_redis_client()
    # print(redis_client)
    redis_client = get_config()
    print(id(redis_client))

    def aa():
        # redis_client = RedisClient()
        redis_client = get_config()
        print(id(redis_client))

    t1 = threading.Thread(target=aa, args=[])
    t2 = threading.Thread(target=aa, args=[])
    t1.start()
    import time
    time.sleep(10)
    t2.start()