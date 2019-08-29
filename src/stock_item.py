# encoding: utf-8

from . import data_item

class StockItem():

    def __init__(self, parent, id, db, select="*", where=""):

        self.stock_id = id
        self.select = select
        self.where = where
        self.db = db
        self.parent = parent

    def add_to_pool(self, name):
        sub_window = [i for i in self.parent.mdi_area.subWindowList() if i.windowTitle().split("-", 1)[-1].strip() == name][0]
        if hasattr(sub_window, "btPoolList"):
            list = getattr(sub_window, "btPoolList")
            list.addItem(self.stock_id)

    def daily(self):
        return data_item.DataItem("daily_%s" % self.stock_id, self.db, self.select, self.where)

    def _monthly(self):
        return data_item.DataItem("montyly_%s" % self.stock_id, self.db, self.select, self.where)