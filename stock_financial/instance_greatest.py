import akshare as ak
import pandas as pd
import talib as ta
import threading

import coroutine_tradedetail_down as trade_detail


def find_new_high(symbol, timeperiod=90):
    new_high_df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date="20170301", end_date=current_date,
                                     adjust="qfq")
    new_high_df['区间最高'] = ta.MAX(new_high_df['最高'], timeperiod=timeperiod)
    find_new_high = new_high_df[new_high_df['区间最高'] == new_high_df['最高']]
    find_last_date = find_new_high.tail(1)['日期'].values.tolist()[0]
    if current_date == find_last_date.replace('-', ''):
        print(new_df.loc[new_df.index == symbol])
        print('=========================')


current_date = '20210915'
# 今日全部都在这里了
df = trade_detail.main()
df['均价'] = pd.to_numeric(df['成交额'] / df['成交量'] / 100)
df.set_index("股票代码", inplace=True)

previous_df = ak.stock_em_zt_pool_previous(date=current_date)
pre_code_list = previous_df['代码'].values.tolist()

# 去掉今日涨停的
current_df = ak.stock_em_zt_pool(date=current_date)
current_code_list = current_df['代码'].values.tolist()

#  pre_code_list中有而current_code_list中没有的
# print(list(set(pre_code_list).difference(set(current_code_list))))
diff_code = list(set(pre_code_list).difference(current_code_list))
diff_df = pd.DataFrame(diff_code)
diff_df.columns = ['股票代码']
diff_df.set_index("股票代码", inplace=True)

# print(pd.concat(diff_df, df))
fina_df = diff_df.join(df)
f_df = fina_df[(fina_df['均价'] < fina_df['最新价']) &
               (fina_df['总市值'] > 10000000000) &
               (fina_df['涨跌幅'] > -2) &
               (fina_df['成交额'] > 600000000)
               ]
f_df.loc[:, '成交额'] = round(f_df['成交额'].map(lambda x: (x / 100000000)), 2)
f_df.loc[:, '总市值'] = round(f_df['总市值'].map(lambda x: (x / 100000000)), 2)
f_df.loc[:, '均价'] = f_df['均价'].round(2)

new_df = f_df.loc[:, ['股票名称', '最新价', '均价', '成交额', '总市值', '涨跌幅']]

# 计算新高
f_symbols = f_df.index.values.tolist()

thread_list = []
for symbol in f_symbols:
    thread = threading.Thread(target=find_new_high, args=(symbol, 90))
    thread.start()
    thread_list.append(thread)

    # 结束多线程
for crawl_thread in thread_list:
    crawl_thread.join()


