# encoding: utf-8
from talib import abstract
from . import data_item

class StockItem():

    def __init__(self, parent, id, db, select="*", where=""):

        self.parent = parent
        self.daily = self._daily("daily_%s" % id, select, where, db)

    def add_to_pool(self, name):
        sub_window = [i for i in self.parent.mdi_area.subWindowList() if i.windowTitle().split("-", 1)[-1] == name][0]
        if hasattr(sub_window, "btPoolList"):
            list = getattr(sub_window, "btPoolList")
            list.addItem(id)

    def _daily(self, id, select, where, db):
        return data_item.DataItem(id, db, select, where)

    def _monthly(self, id, select, where, db):
        return