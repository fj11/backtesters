# encoding: utf-8
import pandas as pd
import datetime

class Query():

    def __init__(self):
        self.TODAY = datetime.datetime.today()
        self.TODAY = datetime.datetime(year=2011, month=12, day=31)
        self.TODAY_STR = self.TODAY.strftime('%Y%m%d')
        self.DELTA = datetime.timedelta(days=1)

    def is_local_table_exist(self, table, sql):
        cursor = sql.cursor()
        f = cursor.execute("SELECT COUNT(*) FROM sqlite_master where type='table' and name='%s'" % table)
        f = cursor.fetchall()
        return f[0][0]

    def is_remote_table_exist(self, table, sql):
        con = sql.raw_connection()
        cursor = con.cursor()
        f = cursor.execute("select exists(select * from information_schema.tables where table_name=%s)", (table,))
        f = cursor.fetchall()
        return f[0][0]

    def write(self, df, table, sql, if_exists='append', index=False, index_label=None):

        if df is None:
            return
        if df.empty:
            return
        df.to_sql(table, sql, if_exists=if_exists, index=index, index_label=index_label)

    def get_started_date(self, table, SQL):
        df = pd.read_sql_query("""SELECT * FROM '%s' order by %s desc limit 0,1;""" % (table, "date"), SQL)
        if df.empty:
            return False
        last_date = str(df.loc[0, "date"])
        last_date_datetime = datetime.datetime(year=int(last_date[0:4]), month=int(last_date[5:7]),
                                               day=int(last_date[8:10]))
        start_date_string = (last_date_datetime + self.DELTA).strftime('%Y%m%d')
        if self.TODAY.date() > last_date_datetime.date():
            return start_date_string
        else:
            return False