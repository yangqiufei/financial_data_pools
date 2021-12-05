import datetime
import time
import threading
import sys
import math
import json

sys.path.append(".")

from autotrade import AutoTrade
from stock_financial.comm_funcs import send_main
from stock_financial.comm_funcs import find_trade_date
from stock_financial.comm_funcs import get_config
from strategies import Strategies
from api.data import StockApi
import strategy


class MomentBeauty(Strategies):
    marking = "beauty"

    def _get_set_buy_cache(self, trade_date):
        # 缓存使用规则：
        # 1，如果key不存在，则进入数据库查询，并且回补缓存；
        # 2，如果缓存数据为空数据，则不查询数据库；
        # 3，中途添加数据请记得加到缓存
        key_str = get_config("cache", "strategies_items_buying")
        key = key_str["name"].replace("<<trade_date>>", str(trade_date))

        # 查询key是否存在
        if not self.redis_conn.exists(key):
            strategy.update_mb_buy_info(trade_date, self.strategy_id)

        return json.loads(self.redis_conn.get(key))

    def _get_set_sell_cache(self, trade_date):
        key_str = get_config("cache", "strategies_items_selling")
        key = key_str["name"].replace("<<trade_date>>", str(trade_date))

        # 查询key是否存在
        if not self.redis_conn.exists(key):
            strategy.update_mb_sell_info(trade_date, self.strategy_id)

        return json.loads(self.redis_conn.get(key))

    def __init__(self, trade):
        super().__init__(trade)

    def monitor(self):
        # 监控程序

        # 两个线程，1：买入；2：卖出。注意：必须加锁，防止其他进程冲突，造成程序崩溃
        buy_thread = threading.Thread(target=self.condition_buy, args=[])
        sell_thread = threading.Thread(target=self.condition_sell, args=[])
        buy_thread.start()
        sell_thread.start()

    def condition_buy(self):
        # 该处计算买入条件，如果条件达到，则进行买入
        while True:
            print(datetime.datetime.now(), "进入买入线程，持续监控中")
            # 检测时间，不是工作时间则进入休眠
            t = {"start_hour": 9, "start_minute": 24}
            self.check_work_time(**t)

            # 查询是否有需要买的票
            today = find_trade_date(return_format="int")

            # 如果没有设置，先去设置缓存， 设置了话就返回数据
            waiting_data = self._get_set_buy_cache(today)
            if len(waiting_data) > 0:
                for data in waiting_data:
                    if data["status"] != 0:
                        continue

                    # 获取策略是直接买入还是等待到了一定的价格？
                    item_code = data["item_code"]

                    # 获取实时价格/或者提前设置的价格
                    price = StockApi.get_newest(item_code, "price")
                    print()
                    print("等待买入：", data["item_code"], "目标价:", data["target_price"] / 100, "最新价：", price)

                    if data["target_price"] == 0 or data["target_price"] > int(price * 100):

                        # 实时获取可用资金
                        available_assets = int(self.get_strategy_cache("available_assets"))/100
                        print("策略可用资金", available_assets)
                        amount = data["amount"]

                        # 佣金
                        fee = 0.0015

                        if amount == 0:
                            # 买入数量，约定：如果为0表示剩余资金全仓买入
                            # 剩余的资金可买的手数
                            amount = math.ceil(available_assets/price/100)
                            low_number = 1
                            # 科创板需要至少200
                            if item_code[0:2] == "68":
                                low_number = 2

                            # 判断一下是否支持手续费
                            cost_assets = int(price * amount * 100 * (1.0000 + fee))
                            if cost_assets > available_assets:
                                # 不足手续费，买入少一手
                                amount = amount - 1

                            if amount < low_number:
                                print("可用资金不够")
                                continue

                        cost_assets = int(price * amount * 100 * (1.0000 + fee))
                        print("花费：", cost_assets)

                        # 插入到数据库，先注释，因为如果客户端最终没有成交，但是又插入到数据库中了，会比较奇怪
                        # buy_data = {"item_code": data["item_code"], "amount": amount, "trade_date": today}
                        # self.buy(**buy_data)

                        # 减去策略可用金额
                        key_str = get_config("cache", "strategies")
                        key = key_str["name"].replace("<<strategy_id>>", str(self.strategy_id))
                        self.redis_conn.hincrby(key, "available_assets", -cost_assets * 100)

                        # 加锁操作，防止买入卖出同一时间调用
                        key_str = get_config("cache", "trade_lock")
                        lock_key = key_str["name"]
                        lock_val = str(datetime.datetime.now())
                        try:
                            while self.redis_conn.setnx(lock_key, lock_val):
                                self.redis_conn.expire(lock_key, key_str["expire"])
                                # 调用交易去交易
                                self.trade.start_trade()
                                self.trade.buy_stock(amount*100, data["item_code"])
                                time.sleep(1)
                                sub = "策略 [{}] 买入".format(self.name)
                                content = ':'.join([data["item_code"], str(amount*100)])
                                send_main(content, sub)
                        except Exception as ee:
                            raise IOError(str(ee))
                        finally:
                            # 解锁
                            if self.redis_conn.get(lock_key) == lock_val:
                                self.redis_conn.delete(lock_key)

                                # 更新策略买入缓存
                                data["status"] = 1
                                key_str = get_config("cache", "strategies_items")
                                key = key_str["name"].replace("<<strategy_id>>", str(self.strategy_id)).replace("<<trade_date>>", str(today))
                                self.redis_conn.set(key, json.dumps(waiting_data))

                                # 过期时间
                                if "expire" in key_str:
                                    self.redis_conn.expire(key, key_str["expire"])

            time.sleep(1)

    def condition_sell(self):
        # 该处计算卖出条件，如果条件达到，则进行卖出
        while True:
            print(datetime.datetime.now(), "进入卖出线程，持续监控中")

            # 检测时间，不是工作时间则进入休眠
            # 收盘前30分钟执行卖出条件筛选，其余时间不动
            t = {"start_hour": 9, "end_hour": 14, "end_minute": 56}
            self.check_work_time(**t)

            # 查询是否有票需要卖出
            today = find_trade_date(return_format="int")
            waiting_data = self._get_set_sell_cache(today)

            if len(waiting_data) > 0:
                for data in waiting_data:
                    if data["stat"] != 0:
                        continue

                    print("等待卖出：", data)

                    # 获取策略是直接买入还是等待到了一定的价格？
                    item_code = data["item_code"]

                    # 获取实时价格/或者提前设置的价格
                    price = StockApi.get_newest(item_code, "price")

                    sell = 0
                    # 逐条列出卖出条件
                    # 1、买入后跌到止损价
                    # 2、跌破ma10
                    if int(price * 100) <= data["stop_loss"]:
                        sell = 1
                    else:
                        ma = 10
                        ma_df = StockApi.get_newest_ma(item_code=data["item_code"], ma=ma)
                        if not ma_df.empty and int(round(ma_df["ma{}".format(ma)].values.tolist()[0], 2) * 100) > price:
                            sell = 1

                    if sell == 1:
                        # 卖出
                        # 后台添加策略可用金额，此处代码作为一个标识，提醒不要忘记
                        # key_str = get_config("cache", "strategies")
                        # key = key_str["name"].replace("<<strategy_id>>", str(self.strategy_id))
                        # self.redis_conn.hincrby(key, "available_assets", data["stop_loss"])

                        # 加锁操作，防止买入卖出同一时间调用
                        key_str = get_config("cache", "trade_lock")
                        lock_key = key_str["name"]
                        lock_val = str(datetime.datetime.now())
                        try:
                            while self.redis_conn.setnx(lock_key, lock_val):
                                self.redis_conn.expire(lock_key, key_str["expire"])
                                # 调用交易去交易
                                self.trade.start_trade()
                                self.trade.sell_stock(data["item_code"])
                                time.sleep(1)
                                sub = "策略 [{}] 卖出".format(self.name)
                                content = ':'.join([sub, data["item_code"]])
                                send_main(content, sub)

                                # 需要更新状态
                                data["stat"] = 1
                                key_str = get_config("cache", "trade_list")
                                key = key_str["name"].replace("<<strategy_id>>", str(self.strategy_id))
                                self.redis_conn.set(key, json.dumps(waiting_data))

                                # 过期时间
                                if "expire" in key_str:
                                    self.redis_conn.expire(key, key_str["expire"])

                        except Exception as ee:
                            raise IOError(str(ee))
                        finally:
                            # 解锁
                            if self.redis_conn.get(lock_key) == lock_val:
                                self.redis_conn.delete(lock_key)

            time.sleep(1)


if __name__ == '__main__':

    try:
        trade_module = AutoTrade()
        s = MomentBeauty(trade_module)
        s.monitor()
    except Exception as e:
        print(e)
        subject = "策略 [刹那芳华] 运行错误"
        contents = ':'.join([subject, str(e)])
        send_main(contents, subject)

