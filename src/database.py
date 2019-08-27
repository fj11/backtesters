# encoding: UTF-8
import os
import pandas as pd
from pysqlcipher3 import dbapi2 as sqlite3

class DataBase():

    def __init__(self, file_name):
        file_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../db/%s.db" % file_name))
        self.sql = sqlite3.connect(file_path, check_same_thread=False)
        CUR_DIR = os.curdir
        self.sql.text_factory = str

    def encryption(self, key):
        c = self.sql.cursor()
        c.execute("PRAGMA key='%s'" % key)

    def read(self, table_name, select="*", where=""):
        try:
            if where:
                return pd.read_sql_query("SELECT %s FROM '%s' where %s" % (select, table_name, where), self.sql)
            else:
                return pd.read_sql_query("SELECT %s FROM '%s'" % (select, table_name), self.sql)
        except Exception as err:
            print(("{0}".format(err)))
            return pd.DataFrame()

    def read_latest_row(self, table):
        return pd.read_sql_query("SELECT * FROM '%s' order by %s desc limit 0,1;" % (table, "date"), self.sql)

    def insert(self, data, table, if_exists, index=False, index_label=None):
        try:
            if data is not None and not data.empty:
                data.to_sql(table, self.sql, if_exists=if_exists, index=index, index_label=index_label)
            return True
        except Exception as err:
            print(("{0}".format(err)))
            return False

    def delete(self, table):
        try:
            cursor = self.sql.cursor()
            cursor.executescript("DROP TABLE IF EXISTS '%s'" % table)
            return True
        except Exception as err:
            print(("{0}".format(err)))
            return False

    def is_table(self, table):
        cursor = self.sql.cursor()
        f = cursor.execute("SELECT COUNT(*) FROM sqlite_master where type='table' and name='%s'" % table)
        f = cursor.fetchall()
        return f[0][0]

    def parse_sec_id(sec_id):
        parsed_list = sec_id.split(".")
        parsed_list.reverse()
        return "/".join(parsed_list)

    def list_tables(self):
        cursor = self.sql.cursor()
        tables = cursor.execute("select name from sqlite_master where type = 'table' order by name").fetchall()
        return [i[0] for i in tables]

if __name__ == "__main__":

    pass