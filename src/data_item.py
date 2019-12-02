# encoding: utf-8
from src.talib_class import Tec
import pandas as pd

class DataItem(Tec):

    def __init__(self, id, db, select="*", where=""):
        self.__data = db.read(id, select, where)
        self.__org_data = self.__data
        Tec.__init__(self, self.__data)
        self.text = self.__data.to_string(max_rows=10, max_cols=10)

    def to_daily(self):
        self.__data = self.__org_data
        self.__data["date"] = pd.to_datetime(self.__data["date"])
        self.__data.set_index("date", inplace=True)
        Tec.__init__(self, self.__data)
        self.text = self.__data.to_string(max_rows=10, max_cols=10)

    def to_monthly(self):
        self.__data = self.__org_data
        self.__data["date"] = pd.to_datetime(self.__data["date"])
        self.__data = self.__data.resample('M', on="date").mean()
        Tec.__init__(self, self.__data)
        self.text = self.__data.to_string(max_rows=10, max_cols=10)

    def to_weekly(self):
        self.__data = self.__org_data
        self.__data["date"] = pd.to_datetime(self.__data["date"])
        self.__data = self.__data.resample('W', on="date").mean()
        Tec.__init__(self, self.__data)
        self.text = self.__data.to_string(max_rows=10, max_cols=10)

    def column(self, name):
        return self.__data[name]

    def columns(self):
        return list(self.__data.columns)

    def rows(self):
        return self.__data.index

    def row(self, name):
        return self.__data[self.__data["date"]==name]

    def add_signal(self, sig):
        sig = self._handle_signal(sig)
        self.__data["signal"] = sig
        return self.__data["signal"]

    def _handle_signal(self, list):
        length = len(list)
        check_first_signal = True
        check_last_signal = True

        for i in range(length):
            n = list[i]
            m = list[length - i - 1]
            if check_first_signal or check_last_signal:
                if check_first_signal:
                    if n > 0:
                        check_first_signal = False
                    elif n < 0:
                        list[i] = 0
                if check_last_signal:
                    if m < 0:
                        check_last_signal = False
                    elif m > 0:
                        list[length - i - 1] = 0
            else:
                break
        return list