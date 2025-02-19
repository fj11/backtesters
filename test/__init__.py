
import os
import time
import unittest
import pywinauto
from pywinauto import Application

class TestSuites(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        return

    def setUp(self):
        os.system("Taskkill /IM backtester.exe /F 2>nul")
        os.chdir("C:\\Users\\14387\Desktop\\backtester")
        app = Application(backend="uia").start('backtester.exe')
        self.app = app[u'回测者']

    def find_elements(self, title="", control_type=""):
        handle = pywinauto.findwindows.find_windows(title="", control_type=""    )
        return self.app.window_(handle=handle)

    def find_element(self, title=None, control_type=None, auto_id=None, title_re=None):
        return self.app.child_window(title=title, control_type=control_type, auto_id=auto_id, title_re=title_re)

    def select(self, title=None, control_type=None, item="",auto_id=None):
        self.find_element(title=title, control_type=control_type, auto_id=auto_id).select(item)

    def input(self, title=None, control_type=None, message="",auto_id=None):
        self.find_element(title=title, control_type=control_type, auto_id=auto_id).type_keys(message)

    def click(self, title=None, control_type=None, auto_id=None):
        self.find_element(title=title, control_type=control_type, auto_id=auto_id).click_input()

    def double_click(self, title=None, control_type=None):
        self.find_element(title=title, control_type=control_type).double_click_input()

    def check_element_exist(self, title=None, control_type=None, timeout=5, title_re=None, auto_id=None):
        self.find_element(title=title, control_type=control_type, title_re=title_re, auto_id=auto_id).exists(timeout=timeout)

    def check_file_exist(self, filepath, timeout=5):
        for i in range(timeout):
            if os.path.isfile(filepath):
                return
            else:
                time.sleep(1)

    def clear_data(self):
        return

    def clear_subwindows(self):
        return

    def tearDown(self):
        os.system("Taskkill /IM backtester.exe /F 2>nul")
        self.clear_data()




    @classmethod
    def tearDownClass(cls):
        return
