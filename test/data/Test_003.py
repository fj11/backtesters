
from test.data import TestSuite
import time
import os

class TestCase(TestSuite):

    name = "The indicator option data can be opened"

    def test(self):
        #self.app.print_control_identifiers()

        self.double_click(title='50ETF', control_type="DataItem")
        self.check_element_exist(title='50ETF', control_type="Window")
        self.double_click(title="2015-02-09 00:00:00", control_type="Header")
        self.check_element_exist(title="标的510050.XSHG在2015-02-09 00:00:00日的期权全部合约")

if __name__ == '__main__':
    TestCase.main()

