# encoding: utf-8
from src.talib_class import Tec

class DataItem(Tec):

    def __init__(self, id, db, select="*", where="", ):
        self.__data = db.read(id, select, where)
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