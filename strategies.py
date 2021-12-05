import sys
import time
import json

sys.path.append(".")

from stock_financial.comm_funcs import RedisClient
from stock_financial.comm_funcs import get_config
from stock_financial.comm_funcs import check_work_time
from api.data import StockApi


class Strategies:
    """
    策略基类
    """

    # 策略标识
    marking = ''

    account_id = 10000010

    strategy = None
    trade = None

    def __init__(self, trade):
        self.trade = trade

        # 启动交易，提高速度
        # self.trade.start_trade()

        redis_client = RedisClient()
        self.redis_conn = redis_client.get_redis_client()

        # 通过marking获取策略
        param = {"condition": {"marking": {"value": self.marking, "operator": "="}}, "limit": 1, "debug": 1}
        strategy = StockApi.get_strategy(**param)
        if len(strategy):
            data = strategy[0]
            # 判断状态
            if data["status"] != 1:
                raise ValueError("策略必须是激活状态，请修改对应的status为1")

            # 判断金额是否大于0
            if data["assets"] <= 0:
                raise ValueError("策略的金额必须大于0，请修改对应的assets值，以分为单位，比如设置金额为一万，则值应该为1000000")

            self.strategy = data
            self.name = data["proud_name"]
            self.strategy_id = data["strategy_id"]

            # 缓存
            key_str = get_config("cache", "strategies")
            key = key_str["name"].replace("<<strategy_id>>", str(self.strategy_id))
            # data.pop("desc")
            # data.pop("created_at")
            # self.redis_conn.set(key, json.dumps(data))
            self.redis_conn.hset(key, "available_assets", data["available_assets"])

            # 过期时间
            if "expire" in key_str:
                self.redis_conn.expire(key, key_str["expire"])

    def buy(self, **kwargs):
        item_code = kwargs.get("item_code")
        amount = kwargs.get("amount")
        trade_date = kwargs.get("trade_date")
        data = {"account_id": self.account_id, "trade_date": trade_date, "direction": "BUY",
                "item_code": item_code, "amount": amount, "strategy_id": self.strategy_id}

        StockApi.insert_trade_list(data=data)

    def sell(self, item_code):
        # 查询出对应策略的数据
        param = {"condition": {"strategy_id": {"value": self.strategy["strategy_id"], "operator": "="}}}
        data_list = StockApi.get_trade_list(**param)

        if len(data_list) > 0:
            data = []
            for row in data_list:
                row["direction"] = "SELL"
                row["trade_date"] = 20211028
                row["trade_time"] = "09:10:12"
                row.pop('trade_list_id')

                data.append(row)

            StockApi.insert_trade_list(data=data)

    @classmethod
    def check_work_time(cls, **kwargs):
        time_delta = check_work_time(**kwargs)
        if time_delta != -1:
            print("睡眠中, 还剩下 {} 秒".format(time_delta))
            time.sleep(time_delta)

    def get_strategy_cache(self, filed_key=""):
        # 获取策略缓存数据
        key_str = get_config("cache", "strategies")
        key = key_str["name"].replace("<<strategy_id>>", str(self.strategy_id))
        return self.redis_conn.hget(key, filed_key)
