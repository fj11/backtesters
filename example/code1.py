stock_id = get_stock_ids()
stock_item = get_stock(stock_id[1])

daily = stock_item.daily()
close = daily.column("close")

ma5 = talib.MA(close, 5)
#print(ma5)

ma20 = talib.MA(close, 20)
#print(ma20)

cu = cross_up(ma5, ma20)
#print(cu)


cd = cross_down(ma5, ma20)
#print(cd)

sig = cu | (cd * -1)

daily.add_signal(sig)

print(sig)