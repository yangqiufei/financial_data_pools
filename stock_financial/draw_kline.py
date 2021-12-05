import os
import sys

from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar, Grid
from pyecharts.commons.utils import JsCode
from stock_financial.comm_funcs import get_symbol

sys.path.append(".")


# 画K线图
def draw_kline(Kname, X, Y):
    kline = (
        Kline().add_xaxis(X).add_yaxis(
            '日k线',
            Y,
            itemstyle_opts=opts.ItemStyleOpts(
                color="#ec0000",
                color0="#00da3c",
                border_color="#FF0000",  # 阳线颜色
                border_color0="#32CD32",  # 阴线颜色
            ),
            markline_opts=opts.MarkLineOpts(
                data=[opts.MarkLineItem(type_="max", value_index=4, name="最大值"),
                      opts.MarkLineItem(type_="min", value_index=3, name="最小值")]
            ),
        ).set_global_opts(
            xaxis_opts=opts.AxisOpts(is_scale=True),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True,
                    areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
            ),

            # 数据缩放滑动，grid添加几个图，进行几条设置
            datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=False,
                    type_="inside",
                    xaxis_index=[0, 0],
                    range_end=100
                ),
                opts.DataZoomOpts(
                    is_show=True,
                    xaxis_index=[0, 1],
                    pos_top="97%",
                    range_end=100
                ),
                # opts.DataZoomOpts(is_show=False, xaxis_index=[0, 2], range_end=100),
            ],
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                axis_pointer_type="cross",
                background_color="rgba(245, 245, 245, 0.8)",
                border_width=1,
                border_color="#ccc",
                textstyle_opts=opts.TextStyleOpts(color="#000"),
            ),
            axispointer_opts=opts.AxisPointerOpts(
                is_show=True,
                link=[{"xAxisIndex": "all"}],
                label=opts.LabelOpts(background_color="#777"),
            ),
            # datazoom_opts=[opts.DataZoomOpts(type_="slider")],
            title_opts=opts.TitleOpts(title=Kname),
        )
    )

    return kline


# 画柱状图
def draw_bar(Bname, X, Y):
    bar = (
        Bar().add_xaxis(X).add_yaxis(
            Bname,
            Y,
            label_opts=opts.LabelOpts(is_show=False),
            yaxis_index=1,
            xaxis_index=1,
            # 改进后在 grid 中 add_js_funcs 后变成如下
            itemstyle_opts=opts.ItemStyleOpts(
                color=JsCode(
                    """
						function(params) {
							var colorList;
							if (barData[params.dataIndex][1] > barData[params.dataIndex][0]) {
								colorList = '#ef232a';
							} else {
								colorList = '#14b143';
							}
							return colorList;
						}
						"""
                )
            ),
        ).set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="category",
                grid_index=1,
                axislabel_opts=opts.LabelOpts(is_show=False),
            ),
            datazoom_opts=[opts.DataZoomOpts(type_="slider")],
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )

    return bar


# 画折线图
def draw_line(lname, X, Y):
    line = (
        Line().set_global_opts(
            tooltip_opts=opts.TooltipOpts(is_show=False),
            xaxis_opts=opts.AxisOpts(type_="category"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(xaxis_data=X)
            .add_yaxis(
            series_name=lname,
            y_axis=Y,
            symbol="emptyCircle",
            is_symbol_show=True,
            label_opts=opts.LabelOpts(is_show=False),
        )
    )

    return line


def round_callback(df):
    df['ma5'] = round(df['ma5'], 2)
    df['ma10'] = round(df['ma10'], 2)
    df['ma20'] = round(df['ma20'], 2)
    df['ma30'] = round(df['ma30'], 2)
    df['ma60'] = round(df['ma60'], 2)
    df['open'] = round(df['open'], 2)
    df['close'] = round(df['close'], 2)
    df['low'] = round(df['low'], 2)
    df['high'] = round(df['high'], 2)
    df['high'] = round(df['high'], 2)
    df['vol'] = round(df['vol'])
    df['amount'] = round(df['amount'])
    return df


def kline(item_code, start_time=None, end_time=None, is_show=True):
    try:

        df = get_symbol(item_code)
    except Exception as e:
        print(e)
        return

    df = df.apply(round_callback, axis=1)
    df.set_index('trade_date', inplace=True)
    df.sort_index(ascending=True, inplace=True)
    # data_df = df.loc[start_time:end_time,['open','close','low','high']]
    if start_time and end_time:
        data_df = df.query('trade_date>{} and trade_date<{}'.format(start_time, end_time))
    else:
        if start_time and not end_time:
            data_df = df.query('trade_date>{}'.format(start_time))
        if not start_time and end_time:
            data_df = df.query('trade_date<{}'.format(end_time))

    data_list = []
    ma5 = []
    ma10 = []
    ma20 = []
    ma30 = []
    ma60 = []
    vols = []
    amounts = []
    for row in data_df.itertuples():
        data_list.append([
            getattr(row, 'open'),
            getattr(row, 'close'),
            getattr(row, 'low'),
            getattr(row, 'high')])
        ma5.append(getattr(row, 'ma5'))
        ma10.append(getattr(row, 'ma10'))
        ma20.append(getattr(row, 'ma20'))
        ma30.append(getattr(row, 'ma30'))
        ma60.append(getattr(row, 'ma60'))
        vols.append(getattr(row, 'vol'))
        amounts.append(getattr(row, 'amount'))

    data_index = data_df.index.map(lambda x: str(x))

    x = list(data_index)

    kline = draw_kline(item_code, x, data_list)
    amount_bar = draw_bar('金额(万)', x, amounts)

    overlap_kline_line = kline.overlap(draw_line('ma5', x, ma5)) \
        .overlap(draw_line('ma10', x, ma10)) \
        .overlap(draw_line('ma20', x, ma20)) \
        .overlap(draw_line('ma30', x, ma30)) \
        .overlap(draw_line('ma60', x, ma60))

    vol_bar = draw_bar('成交量(手)', x, vols)

    bar = vol_bar.overlap(amount_bar)
    # bar.render('index.html')
    # exit()
    grid_chart = Grid(
        init_opts=opts.InitOpts(
            width="1000px",
            height="800px"
        )
    )

    grid_chart.add_js_funcs("var barData = {}".format(data_list))

    grid_chart.add(
        overlap_kline_line,
        grid_opts=opts.GridOpts(pos_left="10%", pos_right="8%", height="50%"),
    )
    grid_chart.add(
        bar,
        grid_opts=opts.GridOpts(
            pos_left="10%", pos_right="8%", pos_top="63%", height="16%"
        ),
    )

    grid_chart.render('index.html')

    if is_show:
        os.system('index.html')


if __name__ == '__main__':
    from pyecharts import options as opts
    from pyecharts.charts import Bar
    from pyecharts.render import make_snapshot

    from snapshot_phantomjs import snapshot


    def bar_chart() -> Bar:
        c = (
            Bar()
                .add_xaxis(["衬衫", "毛衣", "领带", "裤子", "风衣", "高跟鞋", "袜子"])
                .add_yaxis("商家A", [114, 55, 27, 101, 125, 27, 105])
                .add_yaxis("商家B", [57, 134, 137, 129, 145, 60, 49])
                .reversal_axis()
                .set_series_opts(label_opts=opts.LabelOpts(position="right"))
                .set_global_opts(title_opts=opts.TitleOpts(title="Bar-测试渲染图片"))
        )
        return c


    make_snapshot(snapshot, bar_chart().render(), "bar0.png")
