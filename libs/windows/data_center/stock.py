from PySide2.QtCore import QObject, QThread, Slot, Signal
# encoding: utf-8
from sqlalchemy import create_engine
import os
import pandas as pd
from pysqlcipher3 import dbapi2 as sqlite3
from .query import Query

class Stock(QThread):

    def __init__(self, root, parent):
        QThread.__init__(self)

        self.query = Query()
        self.parent = parent
        self.root = root
        self._enabled = False
        self.local_sql = None

    def set_enable(self, enabled):
        self._enabled = enabled

    def run(self):
        try:
            DB_FILE = os.path.normpath(os.path.join(self.root, "db/stock.db"))
            local_sql = sqlite3.connect(DB_FILE, check_same_thread=False)
            self.local_sql = local_sql
            c = local_sql.cursor()
            c.execute("PRAGMA key='123qwe!#QWE'")
            remote_sql = create_engine('postgresql://backtester:123qwe!@#QWE@127.0.0.1:5432/stock')
            self.remote_sql = remote_sql
            contracts_df = pd.read_sql_query('select * from "contract"', con=remote_sql)
            ids = contracts_df["order_book_id"]
            self.parent.signals.process_range.emit(0, len(ids))
            for i in range(len(ids)):
                if self._enabled is False:
                    return
                id = ids[i]
                table = "daily_%s" % id
                if self.query.is_local_table_exist(table, local_sql):
                    start_date_string = self.query.get_started_date(table, local_sql)
                    if start_date_string:
                        df = pd.read_sql_query("""select * from "%s" where date > '%s' AND date < '%s'""" % (table, start_date_string, self.query.TODAY_STR),
                                                       con=remote_sql)
                        self.query.write(df, table, local_sql, if_exists='append')
                        self.parent.signals.message.emit(
                                    u"已更新股票：%s 日线行情,开始时间: %s, 结束时间: %s" % (id, start_date_string, self.query.TODAY_STR))
                else:
                    if self.query.is_remote_table_exist(table, remote_sql):
                        df = pd.read_sql_query("""select * from "%s" where date < '%s'""" % (table, self.query.TODAY_STR), con=remote_sql)
                        self.query.write(df, table, local_sql, if_exists='replace')
                        self.parent.signals.message.emit(u"已更新股票：%s 日线行情" % id)
                self.parent.signals.process.emit(i+1)
        except Exception as e:
            self.parent.signals.message.emit(e)
