# encoding: UTF-8
import rqdatac as rq
from rqdatac import *
import os
os.chdir("../")
from src import sql
import datetime

from PySide2 import QtGui

sql.encryption("123qwe!@#QWE")
rq.init()

START_DATE = datetime.datetime(year=2010, month=1, day=1)
TODAY = datetime.datetime.today()
TODAY = datetime.datetime(year=2018, month=12, day=31)
TODAY_STR = TODAY.strftime('%Y%m%d')
START_DATE_STR = START_DATE.strftime("%Y%m%d")
DELTA = datetime.timedelta(days=1)
# #print rq.get_price('510050.XSHG','2017-3-23','2018-3-23')
# Opts = rq.all_instruments(type="Option")
# order_book_id = Opts.loc[0,"order_book_id"]
# print order_book_id
# # Opt = rq.instruments("10000001")
# # print Opt
# # pd = rq.get_price("10000001", end_date="2018-11-25", frequency='1d')
# # print pd
# # print options.get_contracts(underlying="510050.XSHG")

def get_underlyings():
    return {"CU铜期权":"CU", "M豆粕期权":"M", "SR白糖期权":"SR", "50ETF期权":"510050.XSHG"}

def get_option_contracts(underlying):
    return options.get_contracts(underlying=underlying)

def get_option_ticks(order_book_id, frequency="1d", fields=None):
    return rq.get_price(order_book_id, end_date=TODAY_STR, frequency=frequency)

def is_option_underlying_need_update(table):
    df = sql.read_latest_row(table)
    if df.empty:
        return False
    last_date = df.loc[0, "date"]
    last_date_datetime = datetime.datetime(year=int(last_date[0:4]), month=int(last_date[5:7]), day=int(last_date[8:10]))
    start_date_string = (last_date_datetime+DELTA).strftime('%Y%m%d')
    if TODAY > last_date_datetime:
        return True
    else:
        return False

def is_option_contract_need_update(table):
    order_book_id = table.split("/")[-1]
    maturity_date_string = sql.read("option/contract", where="order_book_id='%s'" % order_book_id).loc[0, "maturity_date"]
    maturity_date_datetime = datetime.datetime(year=int(maturity_date_string[0:4]), month=int(maturity_date_string[5:7]), day=int(maturity_date_string[8:10]))
    if maturity_date_datetime < TODAY:
        return False
    df = sql.read_latest_row(table)
    if df.empty:
        return False
    last_date = df.loc[0, "date"]
    last_date_datetime = datetime.datetime(year=int(last_date[0:4]), month=int(last_date[5:7]), day=int(last_date[8:10]))
    start_date_string = (last_date_datetime+DELTA).strftime('%Y%m%d')
    if TODAY > last_date_datetime:
        return True
    else:
        return False

def is_future_contract_need_update(table):
    df = sql.read_latest_row(table)
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

def get_started_date(table):
    df = sql.read_latest_row(table)
    if df.empty:
        return False
    last_date = df.loc[0, "date"]
    last_date_datetime = datetime.datetime(year=int(last_date[0:4]), month=int(last_date[5:7]), day=int(last_date[8:10]))
    start_date_string = (last_date_datetime+DELTA).strftime('%Y%m%d')
    if TODAY > last_date_datetime:
        return start_date_string
    else:
        return False

def update_stock():
    all_instruments = rq.all_instruments(type="CS")
    sql.insert(all_instruments, "stock/contract", "replace")
    return

def update_future(message=None):
    all_instruments = rq.all_instruments(type="Future")
    sql.insert(all_instruments, "future/contract", "replace")
    futures = ["CU", "M", "SR"]
    for i in futures:
        data = all_instruments[all_instruments.underlying_symbol == i]
        data = data[data.symbol.str.contains("主力连续")]
        ids = data.order_book_id
        for id in ids:
            if message:
                message.append(u"正在更新期货合约：%s 主力连续日线数据" % id)
                message.update()
            else:
                print(u"正在更新期货合约：%s 主力连续日线数据" % id)
            table = "future/contracts/%s" % id
            if sql.is_table(table):
                if is_future_contract_need_update(table):
                    start_date_string = get_started_date(table)
                    df = rq.get_price(id, start_date=start_date_string, end_date=TODAY_STR, frequency='1d')
                    if not sql.insert(df, table, "append", index=True, index_label="date"):
                        df = rq.get_price(id, start_date=START_DATE_STR, end_date=TODAY_STR, frequency='1d')
                        sql.insert(df, table, "replace", index=True, index_label="date")
            else:
                df = rq.get_price(id, start_date=START_DATE_STR, end_date=TODAY_STR, frequency='1d')
                sql.insert(df, table, "replace", index=True, index_label="date")

    return

def update_option(message=None):
    #Replace all contract infomation
    all_instruments = rq.all_instruments(type="Option")
    sql.insert(all_instruments, "option/contract", "replace")
    underlying_order_ids = all_instruments["underlying_order_book_id"]
    #Update option underlyings
    for id, group in all_instruments.groupby(["underlying_order_book_id"]):
        if message:
            message.append(u"正在更新期权标的：%s 日线数据" % id)
            message.update()
        else:
            print(u"正在更新期权标的：%s 日线数据" % id)
        table = "option/underlyings/%s" % id
        if sql.is_table(table):
            if is_option_underlying_need_update(table):
                start_date_string = get_started_date(table)
                df = rq.get_price(id, start_date=start_date_string, end_date=TODAY_STR, frequency='1d')
                if not sql.insert(df, table, "append", index=True, index_label="date"):
                    df = rq.get_price(id, start_date=START_DATE_STR, end_date=TODAY_STR, frequency='1d')
                    sql.insert(df, table, "replace", index=True, index_label="date")
        else:
            df = rq.get_price(id, start_date=START_DATE_STR, end_date=TODAY_STR, frequency='1d')
            sql.insert(df, table, "replace", index=True, index_label="date")

        #Update option contracts

        contracts = options.get_contracts(id)
        option_contract_force_replace = False
        for contract in contracts:
            if message:
                message.append(u"正在更新期权标的：%s 的合约：%s 日线数据" % (id, contract))
                message.update()
            else:
                print(u"正在更新期权标的：%s 的合约：%s 日线数据" % (id, contract))
            table = "option/contracts/%s" % contract
            if sql.is_table(table) and not option_contract_force_replace:
                if is_option_contract_need_update(table):
                    start_date_string = get_started_date(table)
                    df = rq.get_price(contract, start_date=start_date_string, end_date=TODAY_STR, frequency='1d')
                    if not sql.insert(df, table, "append", index=True, index_label="date"):
                        df = rq.get_price(contract, start_date=START_DATE_STR, end_date=TODAY_STR, frequency='1d')
                        sql.insert(df, table, "replace", index=True, index_label="date")
                        option_contract_force_replace = True
            else:
                df = rq.get_price(contract, start_date=START_DATE_STR, end_date=TODAY_STR, frequency='1d')
                sql.insert(df, table, "replace", index=True, index_label="date")

if __name__ == "__main__":
    update_stock()
    update_future()
    update_option()










