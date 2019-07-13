
from test.data import TestSuite
import time
import os

class TestCase(TestSuite):

    name = "The future's option data can be opened"

    def test(self):
        #self.app.print_control_identifiers()

        self.double_click(title='铜', control_type="DataItem")
        self.check_element_exist(title='铜', control_type="Window")
        self.double_click(title="CU1901", control_type="Header")
        self.check_element_exist(title='CU1901', control_type="Window")
        self.double_click(title="2018-11-13 00:00:00", control_type="Header")
        self.check_element_exist(title="标的CU1901在2018-11-13 00:00:00日的期权全部合约")

if __name__ == '__main__':
    TestCase.main()

