### data_pools 通过代码获取A股市场交易数据（持续更新中）

#### 目前能够获取的数据包括：
- 业绩报表
- 资产负债表
- 现金流量表
- 利润表
- 停复牌信息
- 解禁个股信息
- 板块概念
- 20年的历史交易数据
- 个股公告
- 以上数据支持全量下载，比如根据时间下载任何季度的业绩报表

#### 代码需要的运行环境：
- Python3，本机的Python版本为3.7.9，[下载地址](https://www.python.org/downloads/)
- redis，代码使用了redis作为队列临时存储数据，下载地址
- MySQL，作为数据存储，[下载地址](https://www.mysql.com/downloads/)
- Python的第三方包，包括pandas，pymysql等，详情参照requirements.txt文件及**安装依赖**项

##### 安装依赖:

```bash
pip3 install -r requirements.txt
```
附依赖包：

```
numpy==1.19.2
pandas==1.1.2
Pillow==7.2.0
PyMySQL==0.10.1
redis==3.5.3
requests==2.20.0
seaborn==0.11.0
selenium==3.141.0
SQLAlchemy==1.3.20
```


##### 数据库配置
- window环境配置文件名为conf.ini
- linux环境配置文件名为conf.cnf
- 包括MySQL和redis配置
###### 列出的配置中只需要将对应的配置值改成自己的，注意：redis如果没有密码，password项不需要填写

```
[mysql]
host = 127.0.0.1
port = 3306
user = root
password = root
database = stock
charset = utf8mb4

[redis]
host = localhost
port = 6379
queue_db = 1
password = 
```

#### 代码的文件及说明
- create_tables 文件夹，里面放的是数据库建表语句，导入或者当个执行建表
- data_urls.py，数据接口链接地址
- conf.ini，配置文件地址
- comm_funcs.py，公用的方法/类库
- coroutine_balancesheets_down.py，资产负债表下载程序，里面附有示例
- coroutine_cashflow_down.py，现金流量表下载程序，附有使用示例
- coroutine_financial_down.py，利润表下载程序，附有使用示例
- coroutine_statements_down.py，业绩报表下载程序，附有使用示例
- coroutine_suspended_down.py，停复牌信息下载程序，附有使用示例
- coroutine_unlocked_down.py，解禁个股信息下载程序，附有使用示例
- coroutine_tradedetail_down.py，个股每日交易信息下载程序，附有使用示例
- history_trade_down.py，历史交易数据下载
- coroutine_lhblist_down.py，龙虎榜数据下载
- financing_notices_down.py，公告下载
- concepts_down.py 个股概念板块下载

#### 问题反馈
任何问题欢迎在[Issues]中反馈，或者添加微信：hi-huangsir ； QQ：1762934298

你的反馈会让此项目变得更加完美。


