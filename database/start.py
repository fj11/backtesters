from sqlalchemy import create_engine
# encoding: UTF-8
import rqdatac as rq
from rqdatac import *
import pandas as pd
import datetime

rq.init()

START_DATE = datetime.datetime(year=2010, month=1, day=1)
TODAY = datetime.datetime.today()
# TODAY = datetime.datetime(year=2018, month=12, day=31)
TODAY_STR = TODAY.strftime('%Y%m%d')
START_DATE_STR = START_DATE.strftime("%Y%m%d")
DELTA = datetime.timedelta(days=1)
# print(rq.get_price('510050.XSHG','2017-3-23','2018-3-23'))
# Opts = rq.all_instruments(type="Option")
# order_book_id = Opts.loc[0,"order_book_id"]
# print order_book_id
# # Opt = rq.instruments("10000001")
# # print Opt
# # pd = rq.get_price("10000001", end_date="2018-11-25", frequency='1d')
# # print pd
# # print options.get_contracts(underlying="510050.XSHG")

def get_started_date(table, SQL):
    df = pd.read_sql_query("""SELECT * FROM "%s" ORDER BY %s DESC LIMIT 1;""" % (table, "date"), SQL)
    if df.empty:
        return False
    last_date = str(df.loc[0, "date"])
    last_date_datetime = datetime.datetime(year=int(last_date[0:4]), month=int(last_date[5:7]), day=int(last_date[8:10]))
    start_date_string = (last_date_datetime+DELTA).strftime('%Y%m%d')
    if TODAY.date() > last_date_datetime.date():
        return start_date_string
    else:
        return False

def is_future_contract_need_update(table, SQL):
    df = pd.read_sql_query("""SELECT * FROM "%s" ORDER BY %s DESC LIMIT 1;""" % (table, "date"), SQL)
    if df.empty:
        return False
    last_date = df.loc[0, "date"]
    last_date_datetime = datetime.datetime(year=int(last_date[0:4]), month=int(last_date[5:7]),
                                           day=int(last_date[8:10]))
    start_date_string = (last_date_datetime + DELTA).strftime('%Y%m%d')
    if TODAY > last_date_datetime:
        return True
    else:
        return False


def update_future():
    SQL = create_engine('postgresql://backtester:123qwe!@#QWE@127.0.0.1:5432/future')
    all_instruments = rq.all_instruments(type="Future")
    all_instruments.to_sql("contract", SQL, if_exists='replace')
    futures = ["CU", "M", "SR"]
    for i in futures:
        data = all_instruments[all_instruments.underlying_symbol == i]
        data = data[data.symbol.str.contains("主力连续")]
        ids = data.order_book_id
        for id in ids:
            table = "daily_%s" % id
            if is_table_exist(table, SQL):
                start_date_string = get_started_date(table, SQL)
                if start_date_string:
                    df = rq.get_price(id, start_date=start_date_string, end_date=TODAY_STR, frequency='1d')
                    write(df, table, SQL, if_exists='append')
                    print(u"已更新期货合约：%s 主力连续日线数据, 开始时间: %s, 结束时间: %s" % (id, start_date_string, TODAY_STR))
            else:
                df = rq.get_price(id, start_date=START_DATE_STR, end_date=TODAY_STR, frequency='1d')
                write(df, table, SQL, if_exists='replace')
                print(u"已更新期货合约：%s 主力连续日线数据, 开始时间: %s, 结束时间: %s" % (id, START_DATE_STR, TODAY_STR))

    return

def update_stock():

    #SQL = create_engine('postgresql://backtester:123qwe!@#QWE@35.203.38.94:5432/stock')
    SQL = create_engine('postgresql://backtester:123qwe!@#QWE@127.0.0.1:5432/stock')
    all_instruments = rq.all_instruments(type="CS")
    all_instruments.to_sql("contract", SQL, if_exists='replace')

    contracts_df = pd.read_sql_query('select * from "contract"', con=SQL)
    ids = contracts_df["order_book_id"]
    for id in ids:
        table = "daily_%s" % id
        if is_table_exist(table, SQL):
            start_date_string = get_started_date(table, SQL)
            if start_date_string:
                df = rq.get_price(id, start_date=start_date_string, end_date=TODAY_STR, frequency='1d')
                write(df, table, SQL, if_exists='append')
                print(u"已更新股票：%s 日线行情,开始时间: %s, 结束时间: %s" % (id, start_date_string, TODAY_STR))
        else:
            df = rq.get_price(id, start_date=START_DATE_STR, end_date=TODAY_STR, frequency='1d')
            write(df, table, SQL, if_exists='replace')
            print(u"已更新股票：%s 日线行情,开始时间: %s, 结束时间: %s" % (id, START_DATE_STR, TODAY_STR))

    return

def update_option(message=None):
    #Replace all contract infomation
    SQL = create_engine('postgresql://backtester:123qwe!@#QWE@127.0.0.1:5432/option')
    all_instruments = rq.all_instruments(type="Option")
    all_instruments.to_sql("contract", SQL, if_exists='replace')

    for id, group in all_instruments.groupby(["underlying_order_book_id"]):
        #Update option contracts
        contracts = options.get_contracts(id)
        for contract in contracts:
            table = "daily_%s" % contract
            if is_table_exist(table, SQL):
                order_book_id_df = all_instruments[all_instruments["order_book_id"] == contract]
                maturity_date_string = order_book_id_df["maturity_date"].values[0]
                maturity_date_datetime = datetime.datetime(year=int(maturity_date_string[0:4]),
                                                           month=int(maturity_date_string[5:7]),
                                                           day=int(maturity_date_string[8:10]))
                if maturity_date_datetime > TODAY:
                    if get_started_date(table, SQL):
                        start_date_string = get_started_date(table, SQL)
                        df = rq.get_price(contract, start_date=start_date_string, end_date=TODAY_STR, frequency='1d')
                        write(df, table, SQL, if_exists='append')
                        print(u"已更新期权：%s 日线行情,开始时间: %s, 结束时间: %s" % (contract, start_date_string, TODAY_STR))
            else:
                df = rq.get_price(contract, start_date=START_DATE_STR, end_date=TODAY_STR, frequency='1d')
                write(df, table, SQL, if_exists='replace')
                print(u"已更新期权：%s 日线行情,开始时间: %s, 结束时间: %s" % (contract, START_DATE_STR, TODAY_STR))

def is_table_exist(table, SQL):
    con = SQL.raw_connection()
    cursor = con.cursor()
    f = cursor.execute("select exists(select * from information_schema.tables where table_name=%s)", (table,))
    f = cursor.fetchall()
    return False
    return f[0][0]

def write(df, table, sql, if_exists='append', index=True, index_label="date"):

    if df is None:
        return
    if df.empty:
        return
    df.to_sql(table, sql, if_exists=if_exists, index=index, index_label=index_label)

if __name__ == "__main__":
    update_stock()
    update_future()
    update_option()










