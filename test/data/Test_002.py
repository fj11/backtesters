
from test.data import TestSuite
import time
import os

class TestCase(TestSuite):

    name = "The history data can be open/saved as excel file"

    def test(self):
        #self.app.print_control_identifiers()

        self.double_click(title='铜', control_type="DataItem")

        self.click(title='保存', control_type="Button")
        self.input(title='File name:', control_type="Edit", message="test_data")
        self.click(title='Save', control_type="Button")

        time.sleep(10)

        self.check_file_exist("test_data.xlsx")
        self.click(title='打开', control_type="Button")
        self.input(title='File name:', control_type="Edit", message="test_data")
        self.click(title='Open', control_type="Button", auto_id="1")
        self.check_element_exist(title_re="test_data", control_type="Window")

    def clear_data(self):
        os.remove("test_data.xlsx")

if __name__ == '__main__':
    TestCase.main()

