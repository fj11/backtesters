
from test.data import TestSuite
import time

class TestCase(TestSuite):

    name = "All of the history data can be opened"

    def test(self):

        self.double_click(title='50ETF', control_type="DataItem")
        self.check_element_exist(title='50ETF', control_type="Window")

        self.double_click(title='铜', control_type="DataItem")
        self.check_element_exist(title='铜', control_type="Window")

        self.double_click(title='豆粕', control_type="DataItem")
        self.check_element_exist(title='豆粕', control_type="Window")

        # bug "Lose SR(白糖) history data #11"
        # self.double_click(title='白糖', control_type="DataItem")
        # self.check_exist(title='白糖', control_type="Window")

        self.click(title='期货数据', control_type="Button")

        time.sleep(5)
        self.double_click(title='铜', control_type="DataItem")
        self.check_element_exist(title='铜主力连续', control_type="DataItem")

        self.double_click(title='豆粕', control_type="DataItem")
        self.check_element_exist(title='豆粕主力连续', control_type="DataItem")

        self.double_click(title='白糖', control_type="DataItem")
        self.check_element_exist(title='白糖主力连续', control_type="DataItem")


if __name__ == '__main__':
    TestCase.main()

