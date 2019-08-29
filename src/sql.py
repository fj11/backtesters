# encoding: UTF-8
import os
import pandas as pd
from pysqlcipher3 import dbapi2 as sqlite3

DB_FILE = os.path.normpath(os.path.join(os.path.dirname(__file__), "../db/bt.db"))
SQL = sqlite3.connect(DB_FILE, check_same_thread=False)
CUR_DIR = os.curdir
SQL.text_factory = str

pd.set_option('display.max_rows',None)

pd.set_option('display.max_columns', None)

def encryption(key):
    c = SQL.cursor()
    c.execute("PRAGMA key='%s'" % key)

def read(table_name, select="*", where=""):
    try:
        if where:
            return pd.read_sql_query("SELECT %s FROM '%s' where %s" % (select, table_name, where), SQL)
        else:
            return pd.read_sql_query("SELECT %s FROM '%s'" % (select, table_name), SQL)
    except Exception as err:
        print(("{0}".format(err)))
        return pd.DataFrame()

def read_latest_row(table):
    return pd.read_sql_query("SELECT * FROM '%s' order by %s desc limit 0,1;" % (table, "date"), SQL)

def insert(data, table, if_exists, index=False, index_label=None):
    try:
        if data is not None and not data.empty:
            data.to_sql(table, SQL, if_exists=if_exists, index=index, index_label=index_label)
        return True
    except Exception as err:
        print(("{0}".format(err)))
        return False

def delete(table):
    try:
        cursor = SQL.cursor()
        cursor.executescript("DROP TABLE IF EXISTS '%s'" % table)
        return True
    except Exception as err:
        print(("{0}".format(err)))
        return False

def is_table(table):
    cursor = SQL.cursor()
    f = cursor.execute("SELECT COUNT(*) FROM sqlite_master where type='table' and name='%s'" % table)
    f = cursor.fetchall()
    return f[0][0]

def parse_sec_id(sec_id):
    parsed_list = sec_id.split(".")
    parsed_list.reverse()
    return "/".join(parsed_list)

def list_tables():
    cursor = SQL.cursor()
    tables = cursor.execute("select name from sqlite_master where type = 'table' order by name").fetchall()
    return [i[0] for i in tables]

if __name__ == "__main__":
    encryption("123qwe!@#QWE")
    # print(help(SQL))
    # print(list_tables())
    # print read("/stock/XSHG/600009/daily/bar", where="tradeDate='1998-02-18'")
    #encryption("fengjian1114")
    # for name, group in read("option/contract").groupby(["underlying_order_book_id"]):
    #     print group.columns
    #     break
    df = read("option/contracts/10000001")
    df["date"] = pd.to_datetime(df["date"])
    df = df.resample('M', on="date").mean()
    print(df)
    # print(read("option/underlyings/M1803", select="close", where="date='2017-03-15 00:00:00'").at[0, "close"])
    # print(read("option/contracts/10001307").columns)
    # d = read('option/contract')
    # print(d.columns)
    # print(d.iloc[0,:])

    # d = read("future/contract", where="underlying_symbol='%s' AND symbol LIKE '%%主力连续'" % "CU")
    # print(d)
    # print(d[d["order_book_id"]=="10001307"])
    # print(read("option/contract", where="underlying_symbol='M1811'"))
    #print(read("option/contract", where="maturity_date>='2017-11-20 00:00:00' AND listed_date <= '2017-11-20 00:00:00' AND underlying_symbol='M1811'"))
    #print(read("option/contract").columns)
    # print read("option/contract", where="order_book_id='M1909C3100'").loc[0, "maturity_date"]
    #print list(read("/pool", where="secShortName='%s'" % u"武钢股份").secID)[0]
    pass