
from test.trategies import TestSuite
import time
import os

class TestCase(TestSuite):

    name = "the signal dialog works well"

    def test(self):
        # self.double_click(title='50ETF', control_type="DataItem")
        # self.check_element_exist(title='50ETF', control_type="Window")
        #
        # self.click(title="信号下单", control_type="Button")
        # self.check_element_exist(title="开仓", control_type="TabItem")
        # self.check_element_exist(title="平仓", control_type="TabItem")
        # # self.app.print_control_identifiers()
        # self.find_element(auto_id="MainWindow.Dialog.tabWidget.qt_tabwidget_stackedwidget.open.open_list1",
        #                   control_type="List").child_window(title="open", control_type="ListItem").click_input()
        # self.select(auto_id="MainWindow.Dialog.tabWidget.qt_tabwidget_stackedwidget.open.openbox",
        #             control_type="ComboBox", item="上穿")
        # self.find_element(auto_id="MainWindow.Dialog.tabWidget.qt_tabwidget_stackedwidget.open.open_list2",
        #                   control_type="List").child_window(title="close", control_type="ListItem").click_input()
        #
        # self.click(title="平仓", control_type="TabItem")
        # self.find_element(auto_id="MainWindow.Dialog.tabWidget.qt_tabwidget_stackedwidget.close.close_list1",
        #                   control_type="List").child_window(title="open", control_type="ListItem").click_input()
        # self.select(auto_id="MainWindow.Dialog.tabWidget.qt_tabwidget_stackedwidget.close.closebox",
        #             control_type="ComboBox", item="下穿")
        # self.find_element(auto_id="MainWindow.Dialog.tabWidget.qt_tabwidget_stackedwidget.close.close_list2",
        #                   control_type="List").child_window(title="close", control_type="ListItem").click_input()
        #
        # self.click(title="OK", control_type="Button")
        # self.check_element_exist(title="signal", control_type="Header")

        self.click(title="开始回测", control_type="Button")
        self.check_element_exist(title="交易中心", control_type="Window")
        #self.click(title="2019", control_type="Button")
        # self.app.print_control_identifiers()
        print(self.find_elements(title="", control_type="Spinner"))
        self.find_elements(title="", control_type="Spinner").get_value()
        time.sleep(20)
        self.app.print_control_identifiers()



if __name__ == '__main__':
    TestCase.main()

