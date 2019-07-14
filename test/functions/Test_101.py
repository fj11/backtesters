
from test.functions import TestSuite
import time
import os

class TestCase(TestSuite):

    name = "The future's option data can be opened"

    def test(self):

        new_columne = "added"
        self.double_click(title='50ETF', control_type="DataItem")
        self.check_element_exist(title='50ETF', control_type="Window")

        self.click(title="函数", control_type="Button")
        self.check_element_exist(title="运算函数", control_type="TabItem")
        self.check_element_exist(title="关系函数", control_type="TabItem")
        self.check_element_exist(title="技术函数", control_type="TabItem")

        self.input(auto_id="MainWindow.Dialog.column_name", control_type="Edit", message=new_columne)
        self.find_element(auto_id="MainWindow.Dialog.function_tab.qt_tabwidget_stackedwidget.cal_tab.cal_list1",
                          control_type="List").child_window(title="high", control_type="ListItem").click_input()
        self.find_element(auto_id="MainWindow.Dialog.function_tab.qt_tabwidget_stackedwidget.cal_tab.cal_list2",
                          control_type="List").child_window(title="close", control_type="ListItem").click_input()
        self.select(auto_id="MainWindow.Dialog.function_tab.qt_tabwidget_stackedwidget.cal_tab.function_box", control_type="ComboBox", item="求积")
        self.click(title="OK", control_type="Button")
        self.check_element_exist(title=new_columne, control_type="Header")

        new_columne = "and"
        self.click(title="函数", control_type="Button")
        self.input(auto_id="MainWindow.Dialog.column_name", control_type="Edit", message=new_columne)
        self.click(title="关系函数", control_type="TabItem")
        self.find_element(auto_id="MainWindow.Dialog.function_tab.qt_tabwidget_stackedwidget.rel_tab.rel_list1",
                          control_type="List").child_window(title="high", control_type="ListItem").click_input()
        self.find_element(auto_id="MainWindow.Dialog.function_tab.qt_tabwidget_stackedwidget.rel_tab.rel_list2",
                          control_type="List").child_window(title="close", control_type="ListItem").click_input()

        self.select(auto_id="MainWindow.Dialog.function_tab.qt_tabwidget_stackedwidget.rel_tab.rel_box",
                    control_type="ComboBox", item="大于")
        self.click(title="OK", control_type="Button")
        self.check_element_exist(title=new_columne, control_type="Header")

        new_columne = "ma"
        self.click(title="函数", control_type="Button")
        self.input(auto_id="MainWindow.Dialog.column_name", control_type="Edit", message=new_columne)
        self.click(title="技术函数", control_type="TabItem")
        self.input(auto_id="MainWindow.Dialog.function_tab.qt_tabwidget_stackedwidget.tec_tab.search_input", control_type="Edit", message="ma")
        time.sleep(4)
        # self.app.print_control_identifiers()
        self.find_element(auto_id="MainWindow.Dialog.function_tab.qt_tabwidget_stackedwidget.tec_tab.tec_tree", control_type="Tree").get_item("\MA").click_input()
        self.click(title="OK", control_type="Button")
        self.check_element_exist(title=new_columne, control_type="Header")

if __name__ == '__main__':
    TestCase.main()

