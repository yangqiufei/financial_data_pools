import io
import time
import pyperclip
from time import sleep
from pywinauto import clipboard
from pywinauto import mouse
import pandas as pd
import warnings
from pywinauto.application import Application
import subprocess


warnings.filterwarnings('ignore')


class AutoTrade:
    def __init__(self):
    	# 关闭同花顺
    	subprocess.call('taskkill /F /IM xiadan.exe', creationflags=0x08000000)
    	time.sleep(2)

    	app = Application(backend="win32").start(r"E:\pyauto_soft\同花顺软件\同花顺\xiadan.exe")
    	time.sleep(2)
    	app = Application(backend="win32").connect(process=app.process)
    	self.app_ths = app.window(title=u'网上股票交易系统5.0')


    def common(self):
        account = self.app_ths.window(best_match=u'ComboBox2').texts()[0]
        name = self.app_ths.window(best_match=u'StatusBar').texts()[3]
        print(account)
        print(name)



    def shx(self):
        self.app_ths.post_message(0x111, 32790, 0)
        sleep(0.02)

    def sell_stock(self, code):
        """
        卖出股票
        :param code: 股票代码
        :return:
        """
        self.app_ths.post_message(0x111, 162, 0)
        # shx()
        self.app_ths.Edit1.set_focus()
        time.sleep(0.02)
        pyperclip.copy(code)
        self.app_ths.Edit1.post_message(0x0302, 12, 0)
        time.sleep(0.02)
        amount_str = self.app_ths.static2.texts()[0]
        if amount_str != '' and amount_str != '0':
            amount = int(amount_str)
            if amount > 0:
                pyperclip.copy(amount)  # 全部卖出
                self.app_ths.Edit3.post_message(0x0302, 12, 0)
                time.sleep(0.01)

                i = 0
                while self.app_ths.static2.texts()[0] != '':
                    self.app_ths.button1.click()
                    time.sleep(0.01)
                    i = i + 1
                    if i >= 1:
                        break
            else:
                return


    def buy_stock(self, amount, code):
        """
        买入股票
        :param amount: 买入股票数量
        :param code: 股票代码
        :return:
        """
        self.app_ths.post_message(0x111, 161, 0)
        self.shx()
        self.app_ths.Edit1.set_focus()
        time.sleep(0.02)
        pyperclip.copy(code)
        self.app_ths.Edit1.post_message(0x0302, 12, 0)
        time.sleep(0.01)
        mouse.click(button='left', coords=(496, 151))  # 卖二
        # app_ths.post_message(0x111, 161, 0)
        pyperclip.copy(amount)
        self.app_ths.Edit3.post_message(0x0302, 12, 0)
        time.sleep(0.01)
        # self.app_ths.button1.click()(369,324),(429,345)
        mouse.click(button='left', coords=(390, 330))
        time.sleep(0.1)

    def button43(self, code):
        # a.post_message(0x111, 1691, 380898)    # 新增帐户
        self.app_ths.post_message(0x111, 512, 0)  # 双向委托
        time.sleep(0.02)
        self.app_ths.Edit1.set_focus()

        pyperclip.copy(code)
        self.app_ths.Edit1.post_message(0x0302, 12, 0)
        time.sleep(0.01)
        self.app_ths.print_control_identifiers(depth=4)
        self.app_ths.Edit4.post_message(0x0302, 12, 0)

    def withdraw_buy(self):
        """
        撤买
        :return:
        """
        self.app_ths.post_message(0x111, 163, 0)
        self.shx()
        # a.Edit1.set_focus()
        time.sleep(0.02)
        self.app_ths.Button3.click()

    def withdraw_sell(self):
        """
        撤卖
        :return:
        """
        self.app_ths.post_message(0x111, 163, 0)
        self.shx()
        time.sleep(0.02)
        self.app_ths.Button5.click()

    def copy_frozen(self):
        """
        定位到撤单按钮
        :return:
        """
        self.app_ths.post_message(0x111, 163, 0)
        self.shx()
        self.app_ths.CVirtualGridCtrl.post_message(0x111, 57634, 0)
        sleep(0.03)


    def get_data_frozen(self):
        """
        获取同花顺撤单股票明细
        读取ListView中的信息
        :return: 清洗后的数据
        """
        self.copy_frozen()
        data = clipboard.GetData()
        df = pd.read_csv(io.StringIO(data), delimiter='\t', na_filter=False)
        df = pd.DataFrame(df, columns=[u'证券代码', u'证券名称', u'操作', u'委托数量'])
        df.set_index([u'证券代码'], inplace=True)
        print(df)

    def get_available_amount(self):
        # 获取可用金额
        self.app_ths.post_message(0x111, 165, 0)
        self.shx()
        Available_amount = self.app_ths.static6.texts()[0]

        return float(Available_amount)

    def get_frozen_funds(self):
        """
        获取冻结资金
        :return:
        """
        self.app_ths.post_message(0x111, 165, 0)
        self.shx()
        frozen_assets = self.app_ths.static5.texts()[0]
        return float(frozen_assets)

    def stock_market_value(self):
        """
        获取股票市值
        获取总资金total assets
        :return:
        """
        self.app_ths.post_message(0x111, 165, 0)
        self.shx()

        stock_values = self.app_ths.static11.texts()[0]  # 获取股票市值

        return float(stock_values)

    def get_total_assets(self):
        """
        获取总资金total assets
        :return:
        """
        self.app_ths.post_message(0x111, 165, 0)
        # shx()
        total_assets = self.app_ths.static12.texts()[0]  # 获取总资金total assets
        available_amount = self.app_ths.static6.texts()[0]  # 可用余额
        return float(total_assets), float(available_amount)

    def copyto(self):
        self.app_ths.post_message(0x111, 165, 0)
        self.app_ths.CVirtualGridCtrl.post_message(0x111, 57634, 0)
        sleep(0.1)

    def get_position_data(self):
        """
        #获取同花顺持仓股票明细
        读取ListView中的信息
        :return: 清洗后的数据
        """
        self.copyto()
        data1 = clipboard.GetData()

        data = data1.replace("(%)", "")
        df = pd.read_csv(io.StringIO(data), delimiter='\t', na_filter=False)
        ret = df.to_dict('records')
        for i in ret:
            i[u'证券代码'] = str(i[u'证券代码']).zfill(6)

        return ret




if __name__ == '__main__':
	# 示例 买入000001，100股
	ths_trade = AutoTrade()
	data = ths_trade.buy_stock(amount=100, code='000001')
