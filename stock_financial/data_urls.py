'''
数据来源地址
'''

import time
import random
import datetime
from functools import partial
from comm_funcs import get_current_date
from comm_funcs import time_last_day_of_month


def get_suspended_url(**kwargs):
    '''
    获取停牌复牌的个股信息，来自东方财富网
    :param kwargs:
    :param sty : 'SRB',
    :param st : '2', 排序字段，2：停牌开始时间，6：复牌时间
    :param sr : '-1',排序，-1：倒序
    :param mkt:'1',
    :param fd:开始时间，格式为 '2020-01-06',
    :param page: '1',
    :param psize: '30',
    :param type: 'FD',
    :param js: '{"pages":"(pc)","data":[(x)]}',
    :param time_stamp: int(round(time.time(), 3) * 1000)
    :return: str:url
    '''
    domain = 'http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx'
    param_sty = kwargs.get('sty', 'SRB')
    param_st = kwargs.get('st', '2')
    # 排序
    param_sr = kwargs.get('sr', '-1')
    param_mkt = kwargs.get('mkt', '1')
    param_fd = kwargs.get('fd')
    param_page = kwargs.get('page', '1')
    param_psize = kwargs.get('psize', '100')
    parma_type = kwargs.get('type', 'FD')
    parma_js = kwargs.get('js', '{"pages":"(pc)","data":[(x)]}')
    time_stamp = kwargs.get('time_stamp', int(round(time.time(), 3) * 1000))

    dfp_url = '{}?cb=&type={}&sty={}&st={}&sr={}&mkt={}&fd={}&p={}&pageNo=1&ps={}&js={}&_={}'.format(
        domain,
        parma_type,
        param_sty,
        param_st,
        param_sr,
        param_mkt,
        param_fd,
        param_page,
        param_psize,
        parma_js,
        time_stamp
    )
    return dfp_url


def get_unlocked_url(**kwargs):
    '''
    获取解禁的个股信息，来自东方财富网
    :param kwargs:
    :param sr : '-1',解禁时间排序，-1：解禁时间倒序
    :param page: '1',
    :param psize: '30',
    :param begin_date: 格式为'2020-10-20',默认为当前时间
    :param end_date: 格式为'2020-10-20',默认为开始时间的700天后
    :return: str:url
    '''
    domain = 'http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?token=70f12f2f4f091e459a279469fe49eca5&'
    # 排序字段 默认按解禁时间
    param_st = 'ltsj'
    # 排序 1解禁时间由近到远，-1解禁时间由远到近
    param_sr = kwargs.get('sr', '1')
    param_page = kwargs.get('page', '1')
    param_psize = kwargs.get('psize', '100')
    parma_type = 'XSJJ_NJ_PC'
    parma_js = '{"pages":"(tp)","data":(x),"font":(font)}'

    today_date = get_current_date()
    end_date = (
            datetime.datetime.now() +
            datetime.timedelta(
                days=700)).strftime('%Y-%m-%d')

    param_begin_date = kwargs.get('begin_date', today_date)
    param_end_date = kwargs.get('end_date', end_date)
    parma_filter = kwargs.get(
        'filter', '(mkt=)(ltsj>=^{}^ and ltsj<=^{}^)'.format(
            param_begin_date, param_end_date))
    time_rt = kwargs.get('rt', 53529 * 1000 + random.randint(110, 998))

    unlocked_url = '{}st={}&sr={}&p={}&ps={}&type={}&js={}&filter={}&rt={}'.format(
        domain,
        param_st,
        param_sr,
        param_page,
        param_psize,
        parma_type,
        parma_js,
        parma_filter,
        time_rt
    )
    return unlocked_url


def get_financial_url(**kwargs):
    '''
    获取利润表信息，来自东方财富网
    :param kwargs:
    :param st : '2', 排序字段，REPORT_DATE:报道时间
    :param sr : '-1',排序，-1：倒序
    :param page: '1',
    :param psize: '50',
    :param type: 'RPT_DMSK_FN_INCOME',
    :param report_date: 日期，格式为2020-06-31,代表第二季度
    :return: str:url
    '''

    token = '894050c76af8597a853f5b408b759f5d'
    domain = 'http://datacenter.eastmoney.com/api/data/get?callback='
    param_st = kwargs.get('st', 'REPORT_DATE')
    # 排序
    param_sr = kwargs.get('sr', '-1')
    param_psize = kwargs.get('psize', '100')
    param_page = kwargs.get('page', '1')
    parma_type = kwargs.get('type', 'RPT_DMSK_FN_INCOME')
    param_sty = 'ALL'
    report_date = kwargs.get('report_date', time_last_day_of_month())
    param_filter = "(REPORT_DATE='{}')".format(report_date)

    # time_last_day_of_month(year=2020, month=6)

    financial_url = '{}&st={}&sr={}&ps={}&p={}&sty={}&filter=&token={}&type={}&filter={}'.format(
        domain,
        param_st,
        param_sr,
        param_psize,
        param_page,
        param_sty,
        token,
        parma_type,
        param_filter
    )
    return financial_url


def get_statements_url(**kwargs):
    '''
    获取业绩快报信息，来自东方财富网
    主要获取的字段有，每股收益、每股净资产、净资产收益率、每股经营现金流、销售毛利、所处行业
    :param kwargs:
    :param page: '1',分页
    :param psize: '30',每页数量
    :param report_date: 日期，格式为2020-06-31,代表第二季度
    :return: str:url
    '''

    token = '894050c76af8597a853f5b408b759f5d'
    domain = 'http://datacenter.eastmoney.com/api/data/get?callback='
    param_st = 'UPDATE_DATE,SECURITY_CODE'
    # 排序
    param_sr = '-1,-1'
    param_psize = kwargs.get('psize', '100')
    param_page = kwargs.get('page', '1')
    parma_type = 'RPT_LICO_FN_CPD'
    param_sty = 'ALL'
    report_date = kwargs.get('report_date', time_last_day_of_month())

    # (SECURITY_TYPE_CODE+in+("058001001","058001008")):只查询A股，去掉可以查询B股和新三板
    param_filter = "(SECURITY_TYPE_CODE+in+(%22058001001%22%2C%22058001008%22))(REPORTDATE='{}')".format(report_date)

    statements_url = '{}&st={}&sr={}&ps={}&p={}&type={}&sty={}&token={}&filter={}'.format(
        domain,
        param_st,
        param_sr,
        param_psize,
        param_page,
        parma_type,
        param_sty,
        token,
        param_filter
    )
    return statements_url


def get_balance_sheets_url(**kwargs):
    '''
    获取资产负债表信息，来自东方财富网
    :param kwargs:
    :param page: '1',
    :param psize: '50',
    :param report_date: 日期，格式为2020-06-31,代表第二季度
    :return: str:url
    '''
    balance_sheets_url = partial(
        get_financial_url,
        st='NOTICE_DATE,SECURITY_CODE',
        sr='-1,-1',
        type='RPT_DMSK_FN_BALANCE')
    return balance_sheets_url(**kwargs)


def get_cashflow_url(**kwargs):
    '''
    获取现金流数据
    :param kwargs:
    :return:
    '''
    cash_flow_url = partial(
        get_financial_url,
        st='NOTICE_DATE,SECURITY_CODE',
        sr='-1,-1',
        type='RPT_DMSK_FN_CASHFLOW')
    return cash_flow_url(**kwargs)


def a_detail_url(**kwargs):
    """
    获取每日交易信息
    :param kwargs: 
    :return: 
    """
    domain = 'http://88.push2.eastmoney.com/api/qt/clist/get'
    ut = 'bd1d9ddb04089700cf9c27f6f7426281'
    fs = 'm:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23'
    fields = 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f11'
    timestamp = int(round(time.time(), 3) * 1000)
    param_page = kwargs.get('page', '1')
    param_psize = kwargs.get('psize', '10000')
    url = '{}?cb=&pn={}&pz={}&po=1&np=1&ut={}&fltt=2&invt=2&fid=f3&fs={}&fields={}&_={}'.format(
        domain,
        param_page,
        param_psize,
        ut,
        fs,
        fields,
        timestamp
    )

    return url


def get_lhb_list_url(**kwargs):
    """
    获取龙虎版列表信息
    :param kwargs: 
    :return: 
    """
    domain = 'http://data.eastmoney.com/DataCenter_V3/stock2016/TradeDetail/'
    today_date = get_current_date()
    timestamp = int(time.time() / 6)
    param_page = kwargs.get('page', '1')
    param_psize = kwargs.get('psize', '500')
    param_begin_date = kwargs.get('begin_date', today_date)
    param_end_date = kwargs.get('end_date', today_date)
    url = '{}pagesize={},page={},sortRule=-1,sortType=,startDate={},endDate={},gpfw=0,js=.html?rt={}'.format(
        domain,
        param_psize,
        param_page,
        param_begin_date,
        param_end_date,
        timestamp
    )

    return url


def get_lhb_detail_url(**kwargs):
    """
    获取个股龙虎榜详情信息
    :param kwargs:
    :return:
    """
    url = 'https://datapc.eastmoney.com/emdatacenter/ranking/getbuyandsale?code={}&fd={}'
    today_date = get_current_date()
    param_code = kwargs.get('item_code')

    # 格式为：2021-09-09
    param_date = kwargs.get('trade_date', today_date)

    return url.format(param_code, param_date)


def get_lhb_date_by_code(item_code):
    """
    查询个股龙虎榜时间
    :param item_code: 个股代码
    :return:
    """
    return "http://datapc.eastmoney.com/emdatacenter/ranking/getrankingdaysbystockcode?code={}".format(item_code)


def get_bar():
    '''
    获取上证指数等
    :return: 
    '''
    url = 'http://push2.eastmoney.com/api/qt/ulist.np/get?ut=6d2ffaa6a585d612eda28417681d58fb&fields=f1,f2,f3,f4,f14&secids=1.000001,0.399001,0.399006,1.000300&cb=&_=1609909795250'
    return url


def get_leader_url(**kwargs):
    '''
    获取行业龙头
    :param kwargs: 
    :return: 
    '''
    domain = 'http://quote.eastmoney.com/zhuti/api/themerelatestocks'
    param_start = kwargs.get('start', '0')
    param_psize = kwargs.get('psize', '200')
    url = '{}?CategoryCode=112&startIndex={}&pageSize={}'
    return url.format(domain, param_start, param_psize)


def get_history_trade_list(**kwargs):
    '''
    网易历史数据地址
    :return: 
    '''
    item_code = kwargs.get('item_code')
    end_trade_date = kwargs.get('end_trade_date', None)

    if end_trade_date is None:
        end_trade_date = get_current_date().replace('-', '')

    if item_code[0] == '6':
        item_code = ''.join(['0', item_code])
    else:
        item_code = ''.join(['1', item_code])

    domain = 'http://quotes.money.163.com/service/chddata.html'
    fields = 'TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP'
    url = '{}?code={}&end={}&fields={}'.format(domain, item_code, end_trade_date, fields)
    return url


def get_notice_url(**kwargs):
    '''
    获取公告
    :param kwargs: 
    :return: 
    '''
    domain = 'http://data.eastmoney.com/notices/getdata.ashx?'

    param_page = kwargs.get('page', '1')
    param_psize = kwargs.get('psize', '100')
    param_time = kwargs.get('date', '')

    # 公告类型，0：所有公告，1：财务报告，2：融资公告，3：风险提示，4：信息变更，5：重大事项，6：资产重组，7,：持股变动
    param_type = kwargs.get('notice_type', '0')
    rt = 53669667

    url = '{}StockCode=&FirstNodeType={}&CodeType=A&PageIndex={}&PageSize={}&jsObj=&SecNodeType=0&Time={}&rt={}'
    return url.format(domain, param_type, param_page, param_psize, param_time, rt)


def get_financing_notice_url(**kwargs):
    '''
    获取定增公告
    :param kwargs: 
    :return: 
    '''
    url = partial(
        get_notice_url,
        notice_type='2')
    return url(**kwargs)


def get_concept_url(**kwargs):
    """
    获取概念题材
    :param kwargs:
    :return:
    """
    param_page = kwargs.get('page', '1')
    param_psize = kwargs.get('psize', '100')

    domain = 'http://data.eastmoney.com/dataapi/gstc/search'
    url = '{}?st=ChangePercent&sr=-1&ps={}&p={}'.format(domain, param_psize, param_page)

    return url


def get_hsgt_url(**kwargs):
    """
    获取沪深港通总体流入流出的信息
    :param kwargs:
    :return:
    """
    param_page = kwargs.get('page', '1')
    param_psize = kwargs.get('psize', '100')

    token = '894050c76af8597a853f5b408b759f5d'
    domain = 'http://dcfm.eastmoney.com/EM_MutiSvcExpandInterface/api/js/get?type=HSGT20_SC_LS_MX'
    url = '{}&token={}&st=HdDate&sr=-1&p={}&ps={}&js={"pages":(tp),"data":(x)}&filter=(Market=%27005%27)&rt=53676010'
    return url.format(domain, token, param_page, param_psize)


def get_sz_url(**kwargs):
    domain = 'http://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.000001'
    url = '{}&fields1=f1&fields2=f51,f53&klt=101&fqt=0&lmt=600&end=29991010&ut=b2884a393a59ad64002292a3e90d46a5&cb=&_=1610281943586'
    return url.format(domain)


def get_hsgt_detail_url(**kwargs):
    """
    获取沪深港通个股持仓及加减仓的信息
    :return:
    """
    domain = 'http://dcfm.eastmoney.com/EM_MutiSvcExpandInterface/api/js/get'
    url_type = 'HSGT20_GGTJ_SUM'
    token = '894050c76af8597a853f5b408b759f5d'
    st = 'ShareSZ_Chg_One'
    param_page = kwargs.get('page', '1')
    param_psize = kwargs.get('psize', '100')
    param_date = kwargs.get('date', get_current_date())
    js = '{%22pages%22:(tp),%22data%22:(x)}'
    url = '{}?type={}&token={}&st={}&sr=-1&p={}&ps={}&js={}&filter=(DateType=%271%27%20and%20HdDate=%27{}%27)&rt=53677975'
    return url.format(domain, url_type, token, st, param_page, param_psize, js, param_date)


def a_stock_history_list_url(**kwargs):
    """
    a股历史行情数据
    :param kwargs:
    :return:
    """

    adjust_dict = {"qfq": "1", "hfq": "2", "": "0"}
    period_dict = {'daily': '101', 'weekly': '102', 'monthly': '103'}

    symbol = kwargs.get("symbol")
    adjust = kwargs.get("adjust", "")
    period = kwargs.get('period', 'daily')

    timestamp = int(round(time.time(), 3) * 1000)

    code_type = '0'
    if symbol[0:1] == "6":
        code_type = '1'

    domain = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
    param = "?fields1={}&fields2={}&ut={}&klt={}&fqt={}&secid={}&beg=0&end=20500000&_={}"
    fields1 = "f1,f2,f3,f4,f5,f6"
    fields2 = "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"
    ut = "7eea3edcaed734bea9cbfc24409ed989"
    secid = "{}.{}".format(code_type, symbol)
    param = param.format(fields1, fields2, ut, period_dict[period], adjust_dict[adjust], secid, timestamp)
    return ''.join([domain, param])


def hk_detail_url(**kwargs):
    """
    获取每日交易信息
    :param kwargs:
    :return:
    """
    domain = 'http://72.push2.eastmoney.com/api/qt/clist/get?'
    ut = 'bd1d9ddb04089700cf9c27f6f7426281'
    fs = 'm:128 t:3,m:128 t:4,m:128 t:1,m:128 t:2'
    fields = 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,' \
             'f23,f24,f25,f22,f11,f62,f128,f136,f115,f152'
    timestamp = int(round(time.time(), 3) * 1000)
    param_page = kwargs.get('page', '1')
    param_psize = kwargs.get('pagesize', '10000')
    url = '{}pn={}&pz={}&po=1&np=1&ut={}&fltt=2&invt=2&fid=f3&fs={}&fields={}&_={}'.format(
        domain,
        param_page,
        param_psize,
        ut,
        fs,
        fields,
        timestamp
    )

    return url


def high60_url(**kwargs):
    """
    获取每日交易信息
    :param kwargs:
    :return:
    """
    domain = "http://push2ex.eastmoney.com/getAllStockChanges?"
    ut = "7eea3edcaed734bea9cbfc24409ed989"
    timestamp = int(round(time.time(), 3) * 1000)
    param_type = kwargs.get("type", "8213")
    param_page = kwargs.get("page", "0")
    param_psize = kwargs.get("pagesize", "64")
    param_dpt = kwargs.get("dpt", "wzchanges")
    url = "{}type={}&cb=&pageindex={}&pagesize={}&ut={}&dpt={}&_={}".format(
        domain,
        param_type,
        param_page,
        param_psize,
        ut,
        param_dpt,
        timestamp
    )

    return url
