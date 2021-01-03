"""
获取解禁个股信息

使用示例（获取从当前时间到2021-12-10所有解禁股票）：
    begin_date = get_current_date()
    end_date = '2021-12-10'
    main(begin_date=begin_date, end_date=end_date)
"""

import json
import time
from comm_funcs import async_crawl
from comm_funcs import get_current_date
from comm_funcs import get_db_engine_for_pandas
from comm_funcs import get_page_num
from data_urls import get_unlocked_url
import pandas as pd
import asyncio


async def parse(url, engine):
    data = await async_crawl(url)
    parse_data_list = json.loads(data)
    data_all = parse_data_list['data']
    font_map = parse_data_list['font']['FontMapping']
    fonts = {x['code']: x['value'] for x in font_map}

    insert_values = []
    for row in data_all:
        data_tmp = []
        data_tmp.append(row['gpdm'])
        data_tmp.append(row['sname'])
        ltsj_date = row['ltsj'].replace('-', '')[0:8]
        data_tmp.append(ltsj_date)

        # 限售股类型
        data_tmp.append(row['xsglx'])

        # 占解禁前流通市值比例(%)
        if row['zb'] == '-':
            data_tmp.append(0)
        else:
            data_tmp.append(round(float(row['zb']) * 100, 2))

        # 占解禁前流通市值比例(%)
        data_tmp.append(row['mkt'])

        # 总占比(%)
        if row['zzb'] == '-':
            data_tmp.append(0)
        else:
            data_tmp.append(round(float( row['zzb']) * 100, 2))

        # 解禁股东数,需要计算
        gpcjjgds = row['gpcjjgds']
        for key, val in fonts.items():
            gpcjjgds = gpcjjgds.replace(key, str(val))

        data_tmp.append(gpcjjgds)  # 解禁股东数

        kjjsl = row['kjjsl']  # 解禁数量（万）
        for key, val in fonts.items():
            kjjsl = kjjsl.replace(key, str(val))
        data_tmp.append(int(float(kjjsl) * 10000))

        jjsl = row['jjsl']  # 实际解禁数量（万），需要计算
        for key, val in fonts.items():
            jjsl = jjsl.replace(key, str(val))
        data_tmp.append(int(float(jjsl) * 10000))  # 实际解禁数量（万）

        yltsl = row['yltsl']  # 解禁后 已流通数量，需要计算
        for key, val in fonts.items():
            yltsl = yltsl.replace(key, str(val))
        data_tmp.append(int(float(yltsl) * 10000))  # 解禁后 已流通数量

        wltsl = row['wltsl']  # 未解禁数量
        for key, val in fonts.items():
            wltsl = wltsl.replace(key, str(val))
        data_tmp.append(int(float(wltsl) * 10000))  # 未解禁数量

        insert_values.append(tuple(data_tmp))

    columns = column()
    df = pd.DataFrame(insert_values, columns=columns)

    df.set_index('unlocked_time', inplace=True)
    df.fillna(0, inplace=True)

    df.to_sql(
        name='s_unlocked_items',
        con=engine,
        if_exists='append')


def column():
    return [
        'item_code',
        'item_name',
        'unlocked_time',
        'unlocked_type',
        'circulation_percent',
        'mark_type',
        'total_percent',
        'shareholders_num',
        'unlocked_total',
        'true_unlocked_total',
        'circulation_total',
        'locked_total'
    ]


def main(begin_date, end_date):
    engine = get_db_engine_for_pandas()
    total_page = int(
        get_page_num(
            get_unlocked_url(
                begin_date=begin_date,
                end_date=end_date))['pages'])
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(
            parse(
                get_unlocked_url(
                    begin_date=begin_date,
                    end_date=end_date,
                    page=p),
                engine)) for p in range(
            1,
            total_page +
            1)]
    loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    begin = time.time()
    # 获取从当前日期后 2021-12-10 的解禁股信息
    begin_date = get_current_date()
    end_date = '2021-12-10'
    main(begin_date=begin_date, end_date=end_date)
    print(time.time() - begin)
