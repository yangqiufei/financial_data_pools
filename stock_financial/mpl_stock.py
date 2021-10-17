import pandas as pd
import numpy as np
import mplfinance as mpf  # pip install mplfinance
import akshare as ak
import talib as ta


# 第一步，获取数据并且计算指标
def get_data(item_code):
    stock_df = ak.stock_zh_a_hist(symbol=item_code, adjust="qfq")
    stock_df['日期'] = pd.to_datetime(stock_df['日期'])

    stock_df.rename(columns={"日期": "date", '开盘': "open", "收盘": "close", "最高": "high", "最低": "low",
                             "成交量": "volume", "成交额": "value", "振幅": "amplitude", "涨跌额": "change",
                             "涨跌幅": "pct_change",  "换手率": "turnover_rate"},
                    inplace=True)

    stock_df.set_index("date", inplace=True)
    stock_df['average'] = round(stock_df['high'] + stock_df['low'] / 2, 2)
    stock_df['upper_lim'] = round(stock_df['open'] * 1.1, 2)
    stock_df['lower_lim'] = round(stock_df['open'] * 0.9, 2)
    stock_df['last_close'] = stock_df['close'].shift(1)

    stock_df['MA5'] = ta.MA(stock_df['close'], timeperiod=5)
    stock_df['MA10'] = ta.MA(stock_df['close'], timeperiod=10)
    stock_df['MA20'] = ta.MA(stock_df['close'], timeperiod=20)
    stock_df['MA60'] = ta.MA(stock_df['close'], timeperiod=60)

    # 计算macd
    stock_df['macd-m'], stock_df['macd-s'], stock_df['macd-h'] = ta.MACD(stock_df['close'], fastperiod=12,
                                                                         slowperiod=26, signalperiod=9)
    # 计算布林线
    stock_df['bb-upper'], stock_df['bb-middle'], stock_df['bb-lower'] = ta.BBANDS(stock_df['close'], timeperiod=5,
                                                                                  nbdevup=2, nbdevdn=2, matype=0)
    # dema
    stock_df['dema'] = ta.DEMA(stock_df['close'], timeperiod=30)

    # rsi
    stock_df['rsi'] = ta.RSI(stock_df['close'], timeperiod=14)

    return stock_df


# 绘制K线图
symbol = "000001"
stock_name = "平安银行"
data = get_data(symbol)

# 取一段数据绘图
data = data.loc["2021-05-20":, :]

my_color = mpf.make_marketcolors(up='r',
                                 down='g',
                                 edge='inherit',
                                 wick='inherit',
                                 volume='inherit')

my_style = mpf.make_mpf_style(marketcolors=my_color,
                              rc={'font.family': 'SimHei', 'axes.unicode_minus': 'False'},
                              figcolor='(0.82, 0.83, 0.85)',
                              gridcolor='(0.82, 0.83, 0.85)')

title_font = {
    'size': '16',
    'color': 'black',
    'weight': 'bold',
    'va': 'bottom',
    'ha': 'center'}

large_red_font = {
    'fontname': 'Arial',
    'size': '24',
    'color': 'red',
    'weight': 'bold',
    'va': 'bottom'}

large_green_font = {
    'fontname': 'Arial',
    'size': '24',
    'color': 'green',
    'weight': 'bold',
    'va': 'bottom'}

small_red_font = {
    'fontname': 'Arial',
    'size': '12',
    'color': 'red',
    'weight': 'bold',
    'va': 'bottom'}

small_green_font = {
    'fontname': 'Arial',
    'size': '12',
    'color': 'green',
    'weight': 'bold',
    'va': 'bottom'}

normal_label_font = {
    'size': '12',
    'color': 'black',
    'weight': 'normal',
    'va': 'bottom',
    'ha': 'right'}

normal_font = {
    'fontname': 'Arial',
    'size': '12',
    'color': 'black',
    'weight': 'normal',
    'va': 'bottom',
    'ha': 'left'}

# 初始化figure对象，在figure上建立三个Axes对象并分别设置好它们的位置和基本属性
fig = mpf.figure(style=my_style, figsize=(12, 8), facecolor=(0.82, 0.83, 0.85))
ax1 = fig.add_axes([0.08, 0.25, 0.88, 0.60])
ax2 = fig.add_axes([0.08, 0.15, 0.88, 0.10], sharex=ax1)
ax2.set_ylabel('volume')
ax3 = fig.add_axes([0.08, 0.05, 0.88, 0.10], sharex=ax1)
ax3.set_ylabel('macd')

# 初始化figure对象，在figure上预先放置文本并设置格式，文本内容根据需要显示的数据实时更新
t1 = fig.text(0.50, 0.94, '{} - {}'.format(symbol, stock_name), **title_font)
t2 = fig.text(0.12, 0.90, '开/收: ', **normal_label_font)
t3 = fig.text(0.14, 0.89, f'', **large_red_font)
t4 = fig.text(0.14, 0.86, f'', **small_red_font)
t5 = fig.text(0.22, 0.86, f'', **small_red_font)
t6 = fig.text(0.12, 0.86, f'', **normal_label_font)
t7 = fig.text(0.40, 0.90, '高: ', **normal_label_font)
t8 = fig.text(0.40, 0.90, f'', **small_red_font)
t9 = fig.text(0.40, 0.86, '低: ', **normal_label_font)
t10 = fig.text(0.40, 0.86, f'', **small_green_font)
t11 = fig.text(0.55, 0.90, '量(万手): ', **normal_label_font)
t12 = fig.text(0.55, 0.90, f'', **normal_font)
t13 = fig.text(0.55, 0.86, '额(亿元): ', **normal_label_font)
t14 = fig.text(0.55, 0.86, f'', **normal_font)
t15 = fig.text(0.70, 0.90, '涨停: ', **normal_label_font)
t16 = fig.text(0.70, 0.90, f'', **small_red_font)
t17 = fig.text(0.70, 0.86, '跌停: ', **normal_label_font)
t18 = fig.text(0.70, 0.86, f'', **small_green_font)
t19 = fig.text(0.85, 0.90, '换手: ', **normal_label_font)
t20 = fig.text(0.85, 0.90, f'', **normal_font)
t21 = fig.text(0.85, 0.86, '昨收: ', **normal_label_font)
t22 = fig.text(0.85, 0.86, f'', **normal_font)

""" 更新K线图上的价格文本
"""
# data.iloc[-1]是一个交易日内的所有数据，将这些数据分别填入figure对象上的文本中
t3.set_text(f'{np.round(data.iloc[-1]["open"], 3)} / {np.round(data.iloc[-1]["close"], 3)}')
t4.set_text(f'{np.round(data.iloc[-1]["change"], 3)}')
t5.set_text(f'[{np.round(data.iloc[-1]["pct_change"], 3)}%]')
t6.set_text(f'{data.iloc[-1].name.date()}')
t8.set_text(f'{np.round(data.iloc[-1]["high"], 3)}')
t10.set_text(f'{np.round(data.iloc[-1]["low"], 3)}')
t12.set_text(f'{np.round(data.iloc[-1]["volume"] / 10000, 3)}')
t14.set_text(f'{np.round(data.iloc[-1]["value"]/100000000, 3)}')
t16.set_text(f'{np.round(data.iloc[-1]["upper_lim"], 3)}')
t18.set_text(f'{np.round(data.iloc[-1]["lower_lim"], 3)}')
t20.set_text(f'{np.round(data.iloc[-1]["turnover_rate"], 3)}')
t22.set_text(f'{np.round(data.iloc[-1]["last_close"], 3)}')
# 根据本交易日的价格变动值确定开盘价、收盘价的显示颜色
if data.iloc[-1]['change'] > 0:  # 如果今日变动额大于0，即今天价格高于昨天，今天价格显示为红色
    close_number_color = 'red'
elif data.iloc[-1]['change'] < 0:  # 如果今日变动额小于0，即今天价格低于昨天，今天价格显示为绿色
    close_number_color = 'green'
else:
    close_number_color = 'black'
t3.set_color(close_number_color)
t4.set_color(close_number_color)
t5.set_color(close_number_color)

avg_type = "bb"
indicator = "macd"
ap = []
# 添加K线图重叠均线，根据均线类型添加移动均线或布林带线
if avg_type == 'ma':
    ap.append(mpf.make_addplot(data['MA5'], ax=ax1, color="#000000"))
    ap.append(mpf.make_addplot(data['MA10'], ax=ax1, color="#ff0000"))
    ap.append(mpf.make_addplot(data['MA20'], ax=ax1, color="#00ff00"))
    ap.append(mpf.make_addplot(data['MA60'], ax=ax1, color="#0000ff"))
elif avg_type == 'bb':
    ap.append(mpf.make_addplot(data[['bb-upper', 'bb-middle', 'bb-lower']], ax=ax1))

# 添加指标，根据指标类型添加MACD或RSI或DEMA
if indicator == 'macd':
    ap.append(mpf.make_addplot(data[['macd-m', 'macd-s']], ylabel='macd', ax=ax3))
    bar_r = np.where(data['macd-h'] > 0, data['macd-h'], 0)
    bar_g = np.where(data['macd-h'] <= 0, data['macd-h'], 0)
    ap.append(mpf.make_addplot(bar_r, type='bar', color='red', ax=ax3))
    ap.append(mpf.make_addplot(bar_g, type='bar', color='green', ax=ax3))
elif indicator == 'rsi':
    ap.append(mpf.make_addplot([75] * len(data), color=(0.75, 0.6, 0.6), ax=ax3))
    ap.append(mpf.make_addplot([30] * len(data), color=(0.6, 0.75, 0.6), ax=ax3))
    ap.append(mpf.make_addplot(data['rsi'], ylabel='rsi', ax=ax3))
else:  # 'dema'
    ap.append(mpf.make_addplot(data['dema'], ylabel='dema', ax=ax3))

# 绘制图表
mpf.plot(data,
         ax=ax1,
         volume=ax2,
         addplot=ap,
         type='candle',
         style=my_style,
         datetime_format='%Y-%m-%d',
         xrotation=0)
fig.show()
# 保存到本地
# fig.savefig('a.png')
