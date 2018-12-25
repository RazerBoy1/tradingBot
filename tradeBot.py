import time
from decimal import Decimal, getcontext
from kucoinAPIHelper import Client

class tradeBot(object):
    def __init__(self, symbol):
        self.h = Client()
        self._symbol = symbol

        pair = self.get_trading_pair()
        self.coinA = pair[0]
        self.coinB = pair[1]

        self.trade_loop()

    def get_trading_pair(self):
        return self._symbol.split('-')

    def get_coin_balances(self):
        stable_coin_balances = {'USDT': {'balance': 0.0},
                                'TUSD': {'balance': 0.0},
                                'USDC': {'balance': 0.0},
                                'PAX': {'balance': 0.0},
                                'DAI': {'balance': 0.0}}

        balances = self.h.get_all_balances()

        for coin in balances:
            coin_name = coin['coinType']
            if coin_name in stable_coin_balances:
                stable_coin_balances[coin_name]['balance'] = coin['balance']

        return stable_coin_balances

    def increment_one_at_last_digit(self, input_string):
        dec = Decimal(input_string)
        getcontext().prec = len(dec.as_tuple().digits)

        return dec.next_plus()

    def decrement_one_at_last_digit(self, input_string):
        dec = Decimal(input_string)
        getcontext().prec = len(dec.as_tuple().digits)

        return dec.next_minus()

    def get_optimal_buy_price(self, order_book, target_price):
        for order in order_book['SELL']:
            if order[0] < target_price:
                return increment_one_at_last_digit(order[0])

        return target_price

    def get_optimal_sell_price(self, order_book, target_price):
        for order in order_book['BUY']:
            if order[0] > target_price:
                return decrement_one_at_last_digit(order[0])

        return target_price

    def trade_loop(self):
        while (True):
            balances = self.get_coin_balances()
            order_book = self.h.get_order_book(self._symbol)

            buy_price = self.get_optimal_buy_price(order_book, 0.98)
            sell_price = self.get_optimal_sell_price(order_book, 1.02)

            balanceA = balances[self.coinA]['balance']
            balanceB = balances[self.coinB]['balance']

            amount_to_sell = balanceA / sell_price
            amount_to_buy = balanceB / buy_price



            orders_dealt = self.h.get_symbol_dealt_orders('KCS-ETH')
            trading_symbols = self.h.get_trading_symbols('DAI')
            buy_orders = self.h.get_active_orders('KCS-ETH')



            if balanceA > 0.1:
                a = 0
            elif balanceB > 0.1:
                a = 1

            time.sleep(0.25)

t = tradeBot('USDT-USDC')






#a = h.get_recent_orders("ONT-ETH", 10)
#h.create_buy_order('GO-KCS', 0.001, 62783.4875) #Ko je cena 0.001 kup 62783.4875 GOja
