
from test.account import TestSuite
import time
import os

class TestCase(TestSuite):

    name = "the account dialog works well"

    def test(self):

        self.account_name = "test_account"

        self.click(title="账户管理", control_type="Button")
        self.check_element_exist(title="账户", auto_id="MainWindow.Dialog", control_type="Window")

        self.click(title="创建账户", auto_id="MainWindow.Dialog.widget.add_account", control_type="Button")

        self.input(auto_id="MainWindow.Dialog.Dialog.name", control_type="Edit", message=self.account_name)
        self.find_element(title="账户设置", auto_id="MainWindow.Dialog.Dialog", control_type="Window").child_window(title="OK", control_type="Button").click_input()
        self.find_element(title=self.account_name, control_type="ListItem")

    def clear_data(self):
        os.remove("accounts/%s.bt" % self.account_name)

if __name__ == '__main__':
    TestCase.main()

