import sys
import json

sys.path.append("../..")

from stock_financial.comm_funcs import RedisClient
from stock_financial.comm_funcs import get_config
from stock_financial.comm_funcs import find_trade_date
from api.data import StockApi

redis_client = RedisClient()
redis_conn = redis_client.get_redis_client()


def update_available_assets():
    pass


def update_buy_info(trade_date, strategy_id):
    # 缓存使用规则：1，如果key不存在，则进入数据库查询，并且回补缓存；2，如果缓存数据为空数据，则不查询数据库；3，中途添加数据请记得加到缓存
    # 存储的是hash结构
    key_str = get_config("cache", "strategies_items")
    key = key_str["name"].replace("<<strategy_id>>", str(strategy_id)).replace("<<trade_date>>", str(trade_date))

    yeah = 1
    status = 0
    req_param = {"condition": {"trade_date": {"value": trade_date, "operator": "="},
                               "strategy_id": {"value": strategy_id, "operator": "="},
                               "yeah": {"value": yeah, "operator": "="},
                               "status": {"value": status, "operator": "="}},
                 }
    waiting_data = StockApi.get_strategies_items(**req_param)

    # 当天需要买入的写入缓存
    json_value = []

    if waiting_data and len(waiting_data) > 0:
        json_value = [{"item_code": row["item_code"], "target_price": row["target_price"], "amount": row["amount"],
                       "status": 0} for row in waiting_data]

    redis_conn.set(key, json.dumps(json_value))

    # 过期时间，有点瑕疵，待优化
    if "expire" in key_str:
        redis_conn.expire(key, key_str["expire"])


def update_sell_info(trade_date, strategy_id):
    key_str = get_config("cache", "trade_list")
    key = key_str["name"].replace("<<strategy_id>>", str(strategy_id))

    direction = "BUY"
    status = 1
    req_param = {"condition": {"trade_date": {"value": trade_date, "operator": "!="},
                               "strategy_id": {"value": strategy_id, "operator": "="},
                               "direction": {"value": direction, "operator": "="},
                               "status": {"value": status, "operator": "="}},
                 }
    waiting_data = StockApi.get_trade_list(**req_param)

    # 今天之前买入的都作为卖出监控对象，并且写入缓存
    json_value = []

    if waiting_data and len(waiting_data) > 0:
        json_value = [
            {"item_code": row["item_code"], "cost_assets": row["cost_assets"], "stop_loss": row["stop_loss"], "stat": 0}
            for row in waiting_data]

    redis_conn.set(key, json.dumps(json_value))

    # 过期时间
    if "expire" in key_str:
        redis_conn.expire(key, key_str["expire"])


if __name__ == "__main__":
    trade_date = find_trade_date(return_format="int")
    update_buy_info(trade_date, 100000001)