
import os
import time
import pickle
import threading

from src.setting import *

ORDER_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "../tmp"))

class TradeCenter():

    def __init__(self, params):

        self.performance = Performance()
        self.cash = Cash()
        self.cash.currency = params["currency"]
        self.commission_ratio = params["commission_rate"]
        self.option_commission_rate = params["option_commission_rate"]
        self.profit_ratio = params["profit_ratio"]
        self.slide_point = params["slide_point"]
        # self.open_type = params["open_type"]
        # self.close_type = params["close_type"]
        self.cash.available = params["investment"]
        self.cash.nav = self.cash.available
        self.cash._nav = self.cash.available
        self.orders = {"tradeDate":[]}
        self.optionContractPosition = {}
        self.optionUnderlyingPosition = {}

    def onOptionUnderlyingOrder(self, order):

        response = ExecRpt()
        response.sec_id = order.sec_id
        response.position_effect = order.position_effect
        response.side = order.side
        response.transact_time = order.sending_time
        amount = abs(order.price*order.volume)
        commission = abs(amount*self.commission_ratio)
        if order.side == OrderSide_Bid:
            #买入
            if order.position_effect == PositionEffect_Open:
                #开仓
                if self.cash.available >= (amount + commission):
                    #建仓
                    position = self.optionUnderlyingPosition.get(order.sec_id, Position())
                    position.init_time = order.sending_time
                    position.short_name = order.short_name
                    position.sec_id = order.sec_id
                    position.date = order.sending_time
                    position.side = order.side
                    position.transact_time = order.sending_time
                    position.price = order.price
                    position.volume_today = order.volume
                    position.volume += position.volume_today
                    position.commission += commission
                    position.cost = amount
                    position.cum_cost += (position.cost + commission)
                    position.amount += amount
                    position.vwap = position.cum_cost / position.volume
                    self.cash.cost += position.cum_cost
                    self.cash.cum_commission += commission
                    self.cash.available -= position.cum_cost
                    self.cash.cum_inout += abs(position.cum_cost)
                    self.cash.cum_commission += commission
                    self.optionUnderlyingPosition[order.sec_id] = position
                    response.price = order.price
                    response.volume = order.volume
                    response.amount = amount
                else:
                    response.ord_rej_reason = OrderRejectReason_NoEnoughCash
                    response.ord_rej_reason_detail = u"现金不足"

        elif order.side == OrderSide_Ask:
            #卖出
            if order.position_effect == PositionEffect_Close:
                #平仓
                position = self.optionUnderlyingPosition.get(order.sec_id, Position())
                #因该用avialible_today来判断，但是为了调试方便，改为volume
                if position.volume >= order.volume:
                    position.transact_time = order.sending_time
                    position.short_name = order.short_name
                    position.sec_id = order.sec_id
                    position.side = order.side
                    position.transact_time = order.sending_time
                    position.price = order.price
                    position.date = order.sending_time
                    position.volume_today = order.volume * -1
                    position.volume += position.volume_today
                    position.commission += commission
                    position.amount += amount
                    position.income += amount
                    position.cum_cost += commission
                    position.pnl = position.income - position.cum_cost
                    self.cash.cum_pnl += position.pnl
                    self.cash.income += position.income
                    self.cash.cum_inout += abs(position.income)+abs(commission)
                    self.cash.cum_commission += commission
                    self.cash.cost += commission
                    self.cash.available += (position.income - commission)
                    self.cash.pnl += position.pnl
                    if position.pnl > 0:
                        self.performance.total_win += position.pnl
                        self.performance.win_count += 1
                    elif position.pnl < 0:
                        self.performance.lose_count += 1
                        self.performance.total_loss += abs(position.pnl)
                    if position.volume == 0:
                        position.close_time = order.sending_time
                    response.price = order.price
                    response.volume = order.volume
                    response.amount = amount

                else:
                    response.ord_rej_reason = OrderRejectReason_NoEnoughPosition
                    response.ord_rej_reason_detail = u"仓位不足"
        return response

    def onOptionContractOrder(self, order):
        response = ExecRpt()
        response.sec_id = order.sec_id
        response.position_effect = order.position_effect
        response.side = order.side
        response.transact_time = order.sending_time

        if order.side == OrderSide_Bid:
            #买入
            if order.position_effect == PositionEffect_Open:
                # 开仓
                position = self.optionContractPosition.get(order.sec_id, Position())
                position.init_time = order.sending_time
                position.side = order.side
                position.close_method = order.close_method
                position.var_sec_id = order.var_sec_id
                position.contract_type = order.contract_type
                position.expiration_date = order.expiration_date
                position.price = order.price
                position.strike_price = order.strike_price
                position.transact_time = order.sending_time
                position.sec_id = order.sec_id
                position.change_feq = order.change_feq
                position.volume_today = order.volume
                position.volume += position.volume_today
                slide_cost = self.slide_point * abs(order.volume)
                position.slide_cost += slide_cost
                position.cost = abs(order.price * position.volume_today * 10000)
                position.amount += position.cost
                # 期权手续费按照张数收取
                commission = float(self.option_commission_rate) * abs(position.volume_today)
                cum_cost = (abs(order.price * position.volume_today * 10000) + abs(
                    commission)) + position.deposit_cost + slide_cost
                if self.cash.available >= cum_cost:
                    self.cash.available -= cum_cost
                    self.cash.cost += cum_cost
                    self.cash.cum_commission += commission
                    self.cash.cum_inout += abs(cum_cost)
                    self.optionContractPosition[order.sec_id] = position
                    response.price = order.price
                    response.volume = order.volume
                    response.amount = position.amount
                    position.commission += commission
                else:
                    response.status = OrderStatus_Rejected
                    response.ord_rej_reason = OrderRejectReason_NoEnoughCash
                    response.ord_rej_reason_detail = u"现金不足"
                    #self.dictOption.pop(order.sec_id)
            elif order.position_effect == PositionEffect_Close:
                position = self.optionContractPosition.get(order.sec_id, Position())
                position.init_time = order.sending_time
                position.side = order.side
                position.close_method = order.close_method
                position.var_sec_id = order.var_sec_id
                position.contract_type = order.contract_type
                position.expiration_date = order.expiration_date
                position.price = order.price
                position.strike_price = order.strike_price
                position.transact_time = order.sending_time
                position.sec_id = order.sec_id
                position.change_feq = order.change_feq
                position.volume_today = order.volume
                position.volume += position.volume_today
                slide_cost = self.slide_point * abs(order.volume)
                position.slide_cost += slide_cost
                self.cash.available += position.deposit
                self.cash.frozen -= position.deposit
                # 期权手续费按照张数收取
                commission = float(self.option_commission_rate) * abs(position.volume_today)
                cum_cost = (abs(order.price * position.volume_today * 10000) + abs(
                    commission)) + position.deposit_cost + slide_cost
                if self.cash.available >= cum_cost:
                    self.cash.cost += cum_cost
                    # self.cash.available -= (position.cost + position.deposit_cost)
                    self.cash.available -= cum_cost
                    self.cash.cum_inout += abs(cum_cost)
                    self.cash.pnl += (position.income - cum_cost)
                    position.pnl += (position.income - cum_cost)
                    response.price = order.price
                    response.volume = order.volume
                    response.amount = position.amount
                    position.commission += commission
                else:
                    response.status = OrderStatus_Rejected
                    response.ord_rej_reason = OrderRejectReason_NoEnoughCash
                    response.ord_rej_reason_detail = u"现金不足"

        elif order.side == OrderSide_Ask:
            #卖出
            if order.position_effect == PositionEffect_Open:
                position = self.optionContractPosition.get(order.sec_id, Position())
                position.side = order.side
                position.close_method = order.close_method
                position.var_sec_id = order.var_sec_id
                position.contract_type = order.contract_type
                position.expiration_date = order.expiration_date
                position.price = order.price
                position.strike_price = order.strike_price
                position.transact_time = order.sending_time
                position.sec_id = order.sec_id
                position.change_feq = order.change_feq
                position.volume_today = order.volume
                position.volume += position.volume_today
                slide_cost = self.slide_point * abs(order.volume)
                position.slide_cost += slide_cost
                position.amount += abs(order.price * position.volume_today * 10000)
                # if position.available >= position.volume_today:
                deposit_coefficient = float(order.deposit_coefficient)
                if order.contract_type == "P":
                    deposit = self.put_option_cash_deposit(order.strike_price,
                                        order.var_price, order.settle_price, abs(order.volume*10000)) * deposit_coefficient
                elif order.contract_type == "C":
                    deposit = self.call_option_cash_deposit(order.strike_price,
                                        order.var_price, order.settle_price, abs(order.volume*10000)) * deposit_coefficient
                else:
                    deposit = 0
                if self.cash.available >= deposit:
                    position.deposit = abs(deposit)
                    position.deposit_coefficient = deposit_coefficient
                    position.income = abs(order.price*position.volume_today*10000)
                    self.cash.income += position.income
                    self.cash.frozen += position.deposit
                    self.cash.cum_inout += abs(position.income)
                    self.cash.available += (position.income - position.deposit - slide_cost)
                    self.optionContractPosition[order.sec_id] = position
                    response.price = order.price
                    response.volume = order.volume
                    response.amount = position.amount
                else:
                    response.status = OrderStatus_Rejected
                    response.ord_rej_reason = OrderRejectReason_NoEnoughCash
                    response.ord_rej_reason_detail = u"现金不足，没有足够的保证金"
            elif order.position_effect == PositionEffect_Close:
                position = self.optionContractPosition.get(order.sec_id, Position())
                position.side = order.side
                position.close_method = order.close_method
                position.var_sec_id = order.var_sec_id
                position.contract_type = order.contract_type
                position.expiration_date = order.expiration_date
                position.price = order.price
                position.strike_price = order.strike_price
                position.transact_time = order.sending_time
                position.sec_id = order.sec_id
                position.change_feq = order.change_feq
                position.volume_today = order.volume
                position.volume += position.volume_today
                slide_cost = self.slide_point * abs(order.volume)
                position.slide_cost += slide_cost
                position.amount += abs(order.price * position.volume_today * 10000)
                if position.available >= position.volume_today:
                    commission = float(self.option_commission_rate) * abs(position.volume_today)
                    position.commission += commission
                    position.income = abs(order.price*position.volume_today*10000)
                    self.cash.income += position.income
                    self.cash.cost += commission
                    self.cash.cum_commission += commission
                    self.cash.cum_inout += position.income
                    self.cash.available += (position.income - commission - slide_cost)
                    self.cash.pnl += (position.income - position.cum_cost - commission - slide_cost)
                    position.pnl += (position.income - position.cum_cost - commission - slide_cost)
                    response.price = order.price
                    response.volume = order.volume
                    response.amount = position.amount
                else:
                    response.status = OrderStatus_Rejected
                    response.ord_rej_reason = OrderRejectReason_NoEnoughPosition
                    response.ord_rej_reason_detail = u"仓位不足"
                    self.optionContractPosition.pop(order.sec_id)
        return response

    def put_option_cash_deposit(self, strike_price, var_price, settle_price, volume):
        if volume:
            return min(settle_price+max(0.15*var_price-max(var_price-strike_price, 0),0.07*strike_price), strike_price)*volume
        else:
            return 0

    def call_option_cash_deposit(self, strike_price, var_price, settle_price, volume):
        if volume:
            return (settle_price+max(0.15*var_price-max(strike_price-var_price, 0),0.07*var_price))*volume
        else:
            return 0

    def getOrders(self):
        dir_list = [i for i in os.listdir(ORDER_PATH) if os.path.splitext(i)[-1] == ".od"]
        if not dir_list:
            return []
        else:
            # 注意，这里使用lambda表达式，将文件按照最后修改时间顺序升序排列
            # os.path.getmtime() 函数是获取文件最后修改时间
            # os.path.getctime() 函数是获取文件最后创建时间
            dir_list = sorted(dir_list, key=lambda x: os.path.getmtime(os.path.join(ORDER_PATH, x)))
            # print(dir_list)
            return dir_list

if __name__ == "__main__":
    order = Order()
    order.order_type = "option"
    order.position_effect = PositionEffect_Open
    order.volume = 1
    order.price = 2.5
    order.side = OrderSide_Bid
    with open("../tmp/test.od", 'wb') as f:
        pickle.dump(order, f)

    Test = TradeCenter()
    Test.setUp(ACCOUNT)
    Test.start()