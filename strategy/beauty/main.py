import pandas as pd
import sys
import os
import json

sys.path.append("../..")

from api.data import StockApi
from stock_financial.comm_funcs import get_rise_price
from stock_financial.comm_funcs import get_db_engine_for_pandas
from stock_financial.comm_funcs import get_mysql_client
from stock_financial.comm_funcs import get_config
from stock_financial.comm_funcs import find_trade_date
from stock_financial.comm_funcs import RedisClient
from stock_financial.draw_kline import draw_line


def find_all(start_date, end_date=None):
    if end_date is None:
        end_date = StockApi.get_current_trade_date()

    data_filter_list = []
    # 查找连扳票
    param = {"condition": {"date_time": [{"value": start_date, "operator": ">"}, {"value": end_date, "operator": "<="}],
                           "continue_num": [{"value": min_rise, "operator": ">="},
                                            {"value": max_rise, "operator": "<"}]},
             "fields": ["`continue_num`", "item_code", "date_time"],
             "table": "s_continue_last"
             }
    data_list = StockApi.get_common_data(**param)

    if len(data_list) == 0:
        print('s_continue_last表没有查到相关数据, 程序退出')
        exit()

    for row in data_list:
        c_num = row["continue_num"]
        item_code = row["item_code"]
        trade_date = row["date_time"]
        print(row)

        if item_code.startswith('3'):
            continue

        nxt_day = StockApi.get_next_date(trade_date)
        nn_date = StockApi.get_next_date(nxt_day)

        param = {"condition": {"trade_date": {"value": nxt_day, "operator": "="},
                               "item_code": {"value": item_code, "operator": "="},
                               "no_parse": "`open` > `close`"
                               },
                 "fields": ["`open`", "`close`", "`yclose`", "`percent`"],
                 "table": "s_trade_day_kline"
                 }
        find_row = StockApi.get_common_data(**param)
        if not find_row:
            # print("{}没有找到{}".format(nxt_day, item_code))
            continue

        exists_row = find_row[0]
        if exists_row:
            nn_param = {"condition": {"trade_date": {"value": nn_date, "operator": "="},
                                      "item_code": {"value": item_code, "operator": "="}
                                      },
                        "fields": ["`open`", "`yclose`"],
                        "table": "s_trade_day_kline"
                        }
            find_nn_row = StockApi.get_common_data(**nn_param)
            if not find_nn_row:
                # print("{}-{}没有找到{}".format(nxt_day, nn_date, item_code))
                continue
            nn_row = find_nn_row[0]

            if nn_row:
                nn_open = nn_row['open']
                nn_yclose = nn_row['yclose']

                open_percent = round(
                    100 * (nn_open - nn_yclose) / nn_yclose, 2)

                if open_percent < buy_open_per_min:
                    # print("开盘低于1p淘汰{}".format(item_code))
                    continue

                if get_rise_price(item_code, nn_yclose) == nn_open:
                    # print("开盘涨停淘汰{}".format(item_code))
                    continue

                data_filter_list.append([c_num, item_code, trade_date, nxt_day, nn_date])

    df = pd.DataFrame(data_filter_list)

    if not df.empty:
        df.columns = ["连板高度", "股票代码", "连板日期", "首阴日期", "买入日期"]

        # 合并名称
        engine = get_db_engine_for_pandas()
        sql = 'select item_code as `股票代码`,item_name as `名字` from s_items'
        df_name = pd.read_sql(sql, engine)
        new_df = pd.merge(left=df, right=df_name, on='股票代码', how='left')
        print(new_df)
        new_df.to_csv(save_find_file, index=False)
    else:
        print("无数据，无法生成{}文件，程序退出".format(save_find_file))
        exit()


def item_code_callback(item_code):
    tmp = '00000' + str(item_code)
    return tmp[::-1][0:6][::-1]


def get_record():
    try:
        df = pd.read_csv(save_find_file)

        if not df.empty:
            conn = get_mysql_client()

            cursor = conn.cursor()

            df.loc[:, '股票代码'] = df['股票代码'].map(item_code_callback)

            df = df[df['连板高度'].map(lambda x: (min_rise <= x <= max_rise))]
            fly_data = []

            date_continue_map = {}
            for row in df.itertuples():
                try:
                    item_code = getattr(row, '股票代码')
                    trade_date = getattr(row, '连板日期')
                    continue_num = getattr(row, '连板高度')
                    item_name = getattr(row, '名字')
                    print(item_code)
                    nxt_date = getattr(row, '首阴日期')
                    buy_date = getattr(row, '买入日期')

                    # 60验证
                    param60 = {"condition": {
                        "trade_date": [{"value": trade_date, "operator": ">="}, {"value": nxt_date, "operator": "<="}],
                        "item_code": {"value": item_code, "operator": "="}
                    },
                        "fields": ["`id`"],
                        "table": "s_changes",
                        "limit": 1,
                        "debug": 1
                    }
                    high_60 = StockApi.get_common_data(**param60)
                    if not high_60:
                        print("{}未达到60日淘汰".format(item_code))
                        continue

                    if trade_date not in date_continue_map:
                        new_item_time = trade_date - 10000
                        sql = 'select a.continue_num from s_continue_last as a ' \
                              'left join s_items as b on a.item_code=b.item_code ' \
                              'where date_time={} and continue_num>{} and item_time<{} ' \
                              'GROUP BY a.continue_num ' \
                              'order by a.continue_num desc limit 2'.format(trade_date, min_rise, new_item_time)
                        cursor.execute(sql)
                        exists_rows = cursor.fetchall()
                        date_continue_map[trade_date] = [row[0] for row in exists_rows]

                    if continue_num not in date_continue_map[trade_date]:
                        print("{}不是排名最高的两个，淘汰".format(item_code))
                        continue

                    open_sql = 'select `open_f2`,open_percent_f3,open_amount_f6,yesterday_close_f18 ' \
                               'from s_open where item_code="{}" and trade_date={} LIMIT 1'.format(item_code, buy_date)
                    cursor.execute(open_sql)
                    open_row = cursor.fetchone()

                    sql = 'select `open`,is_last,yclose from s_trade_day_kline where item_code="{}" ' \
                          'and trade_date={} LIMIT 1'.format(item_code, buy_date)

                    cursor.execute(sql)
                    buy_row = cursor.fetchone()
                    buy_price, is_last, buy_yclose = buy_row
                    if open_row:
                        buy_price, open_percent, open_amount, buy_yclose = open_row
                    else:
                        open_amount = 0
                        open_percent = round(
                            100 * (buy_price - buy_yclose) / buy_yclose, 2)

                    sell_date = StockApi.get_next_date(buy_date)
                    sql = 'select `close`,is_last,trade_date,`open`,`yclose` from s_trade_day_kline where item_code="{}" ' \
                          'and trade_date={}  LIMIT 1'.format(item_code, sell_date)
                    cursor.execute(sql)
                    sell_row = cursor.fetchone()

                    if not sell_row:
                        print("{}没有找到卖出日记录".format(item_code))
                        continue

                    sell_price, sell_is_last, sell_date, nn_open, nn_yclose = sell_row
                    # 卖出条件
                    if str(is_last) == '1':
                        while str(sell_is_last) == '1':
                            sell_date = StockApi.get_next_date(sell_date)
                            sql = 'select `close`,is_last,trade_date,`open`,`yclose` from s_trade_day_kline where ' \
                                  'item_code="{}" and trade_date={}  LIMIT 1'.format(item_code, sell_date)
                            cursor.execute(sql)
                            sell_row = cursor.fetchone()
                            sell_price, sell_is_last, sell_date, nn_open, nn_yclose = sell_row
                    else:
                        sell_open_percent = round(
                            100 * (nn_open - nn_yclose) / nn_yclose, 2)

                        if sell_open_percent < run_open_per_max:
                            sell_price = nn_open

                    tmp = (
                        item_code,
                        item_name,
                        trade_date,
                        open_percent,
                        open_amount,
                        buy_price,
                        buy_date,
                        sell_price,
                        sell_date,
                        continue_num)
                    fly_data.append(tmp)
                except Exception as e:
                    print(e)
                    continue

            if fly_data:
                fly_df = pd.DataFrame(fly_data)
                fly_df.columns = ["股票代码",
                                  '名字',
                                  '连板日期',
                                  '买入日开盘涨跌幅',
                                  '买入日竞价成交金额',
                                  '买入价格',
                                  '买入日期',
                                  '卖出价格',
                                  '卖出日期',
                                  '连板高度']
                fly_df.to_csv(fly_file, index=False)

            cursor.close()
            conn.close()
        else:
            print("{}文件无数据，程序退出".format(save_find_file))
            exit()
    except FileNotFoundError:
        print("{}不存在，请在第一步中生成该文件, 程序退出".format(save_find_file))
        exit()
    except Exception as e:
        print(e)
        exit()



def get_continue_top(df, top_num):
    """
    这里的df，是分组group的df
    """
    return df.sort_values(["买入日竞价成交金额", "买入日开盘涨跌幅"])[-top_num:]


def get_profit():
    try:
        df = pd.read_csv(fly_file)
        df.loc[:, '股票代码'] = df['股票代码'].map(item_code_callback)
        df.loc[:, '利润'] = 100 * (df['卖出价格'] - df['买入价格']) / df['买入价格']
        print(df)
        df = df.groupby("连板日期").apply(get_continue_top, top_num=1)

        # 买入次数
        buy_num = 0

        # 成功次数（赚钱的次数）
        success_num = 0

        # 用模拟资金代替
        amount = 100000

        res = {"初始金额": amount}

        i = 0
        position = {}

        # 手续费
        total_fee = 0
        fee = 0.00015

        # 印花税
        total_fax = 0
        fax = 0.0001
        line_x = []
        line_y = []
        for row in df.itertuples():
            item_code = getattr(row, '股票代码')
            item_name = getattr(row, '名字')
            buy_date = getattr(row, '买入日期')
            buy_price = getattr(row, '买入价格')
            sell_price = getattr(row, '卖出价格')
            sell_date = getattr(row, '卖出日期')

            if i == 0:
                i = 1
            else:
                if 'sell_date' in position and buy_date > position['sell_date']:
                    if position['sell_price'] > position['buy_price']:
                        success_num += 1

                    # 买入日期大于卖出日期，比如买入日期为20200108，卖出日期为20200107，则清空
                    sell_amount = position['num'] * position['sell_price']

                    print(position['item_name'])

                    # 减去手续费和印花税
                    total_fax += sell_amount * fax
                    total_fee += sell_amount * fee
                    amount += sell_amount - sell_amount * fee - sell_amount * fax
                    line_x.append(str(position['sell_date']))
                    line_y.append(amount)
                    # print(amount)
                    position = {}

            if not position:
                av_num = int(amount // (100 * buy_price) * 100)
                buy_amount = av_num * buy_price
                net_amount = amount - buy_amount - fee * buy_amount

                # 如果手续费不够，则少买100股
                if net_amount < 0:
                    av_num = av_num - 100
                    buy_amount = av_num * buy_price
                    amount = amount - buy_amount - fee * buy_amount
                else:
                    amount = net_amount

                if av_num > 0:
                    buy_num += 1

                total_fee += fee * buy_amount

                position = {
                    'item_code': item_code,
                    'item_name': item_name,
                    'num': av_num,
                    'buy_price': buy_price,
                    'sell_price': sell_price,
                    'sell_date': sell_date,
                    'buy_date': buy_date
                }
                # kline(item_code, start_time=buy_date - 300, end_time=sell_date + 300)
            else:
                print('没买上：', getattr(row, '名字'))

        if position:
            amount += position['num'] * position['sell_price']
            line_x.append(str(position['sell_date']))
            line_y.append(amount)

        res["期末资金"] = amount
        res["佣金"] = total_fee
        res["印花税"] = total_fax
        res["交易次数"] = buy_num
        res["盈利次数"] = success_num
        res["成功率"] = round(success_num / buy_num, 4) * 100
        res["收益率"] = round((amount - res["初始金额"]) / res["初始金额"], 4) * 100

        line = draw_line('', line_x, line_y).render('blmx.html')
        os.system('blmx.html')

        return res
    except FileNotFoundError:
        print("{}不存在，请在第一步中生成该文件, 程序退出".format(fly_file))
        exit()
    except Exception as e:
        print(e)
        exit()


def get_items(trade_date=None):
    """
    获取符合策略的票
    """
    if not trade_date:
        trade_date = find_trade_date(return_format="int")

    # 上一个交易日, 首阴日
    pre_date = int(StockApi.get_pre_date(trade_date))

    # 前面两个交易日，连续涨停日
    pre_pre_date = int(StockApi.get_pre_date(pre_date))

    # 查找连扳票, 查找首阴
    param = {"condition": {"t.date_time": [{"value": pre_pre_date}],
                           "t.continue_num": [{"value": min_rise, "operator": ">="},
                                              {"value": max_rise, "operator": "<"}],
                           "a.trade_date": {"value": pre_date},
                           "a.is_last": {"value": 0},
                           "no_parse": "a.`open` > a.`close`"
                           },
             "fields": ["`continue_num`", "t.item_code", "date_time"],
             "join": [{"table": "s_trade_day_kline a", "on": "t.item_code=a.item_code", "how": "left"}],
             "table": "s_continue_last"
             }
    data_list = StockApi.get_common_data(**param)

    container = []
    if len(data_list):

        date_continue_map = {}
        conn = get_mysql_client()
        cursor = conn.cursor()
        new_item_time = pre_pre_date - 10000
        sql = 'select a.continue_num from s_continue_last as a ' \
              'left join s_items as b on a.item_code=b.item_code ' \
              'where date_time={} and continue_num>{} and item_time<{} ' \
              'GROUP BY a.continue_num ' \
              'order by a.continue_num desc limit 2'.format(pre_pre_date, min_rise, new_item_time)
        cursor.execute(sql)
        exists_rows = cursor.fetchall()
        date_continue_map[pre_pre_date] = [row[0] for row in exists_rows]

        item_codes = []
        for row in data_list:
            item_code = row["item_code"]
            continue_num = row["continue_num"]
            # 60验证
            param60 = {"condition": {
                "trade_date": [{"value": pre_pre_date, "operator": ">="}, {"value": pre_date, "operator": "<="}],
                "item_code": {"value": item_code, "operator": "="}
            },
                "fields": ["`id`"],
                "table": "s_changes",
                "limit": 1
            }
            high_60 = StockApi.get_common_data(**param60)
            if not high_60:
                continue

            if continue_num not in date_continue_map[pre_pre_date]:
                continue

            container.append(row)
            item_codes.append(item_code)

        if len(container):
            engine = get_db_engine_for_pandas()

            container_df = pd.DataFrame(container)
            strategy_df = pd.DataFrame()

            strategy_df["get_date"] = container_df["date_time"]
            strategy_df["item_code"] = container_df["item_code"]
            strategy_df["strategy_id"] = "100000001"
            strategy_df["trade_date"] = trade_date
            strategy_df["amount"] = 0
            item_codes = list(map(lambda x: '"' + x + '"', item_codes))
            open_sql = 'select item_code,open_f2,open_percent_f3 as `买入日开盘涨跌幅`,open_amount_f6 as `买入日竞价成交金额` ' \
                       'from s_open where item_code in({}) and trade_date={} and open_percent_f3>{}'.format(",".join(item_codes), trade_date, buy_open_per_min)

            df_name = pd.read_sql(open_sql, engine)
            new_df = pd.merge(left=df_name, right=container_df, on='item_code', how='left')
            new_df = new_df.groupby("date_time").apply(get_continue_top, top_num=1)
            print(new_df)

            if not new_df.empty:
                key_str = get_config("cache", "strategies_items_buying")
                key = key_str["name"].replace("<<trade_date>>", str(trade_date))

                redis_client = RedisClient()
                redis_conn = redis_client.get_redis_client()

                item_value = new_df.values.tolist()
                yeah_item_code = item_value[0][0]
                strategy_df["yeah"] = strategy_df["item_code"].map(lambda x: x == yeah_item_code)
                strategy_df.to_sql(
                    name='s_strategies_items',
                    con=engine,
                    if_exists='append', index=False)

                json_value = [
                    {"item_code": item_value[0][0], "target_price": (item_value[0][1] + 0.1) * 100, "amount": 0,
                     "status": 0}]

                redis_conn.set(key, json.dumps(json_value))

                if "expire" in key_str:
                    redis_conn.expire(key, key_str["expire"])


if __name__ == '__main__':
    """
    买入条件
        股票连续涨停（大于两板且低于6连板）;
        首阴（开盘价低于收盘价）；
        首阴后一日，高开1个点且不能涨停开盘；
        首阴当天或者首阴前一日创60新高；
        
    卖出条件
        从第二天开始不涨停走，涨停就留；
        买入当天不涨停，第二天低开两个点及以下竞价/开盘走
    """
    try:
        # 2板
        min_rise = 2
        # 最高6板
        max_rise = 7
        # 买入日开盘价不低于1%
        buy_open_per_min = 1
        # 买入日不涨停，第二天开盘低于-2就卖
        run_open_per_max = -2

        # 保存找到的csv文件
        save_find_file = "blmx.csv"
        # 保存最终的csv
        fly_file = "fly_blmx.csv"
        # 第一步，扫数据
        begin_time = 20200101
        end_time = 20210422
        find_all(begin_time, end_time)
        # 第二步，找出历史上符合策略的票
        get_record()

        # 第三步，模拟计算成功率和收益率
        result = get_profit()
        print(result)

        # 每日运行
        # find_date = find_trade_date(return_format="int")
        # find_date = 20211116
        # get_items(find_date)
    except Exception as e:
        print(e)
