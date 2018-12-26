import time
from decimal import Decimal, getcontext
from kucoinAPIHelper import Client

class tradeBot(object):
    DECIMAL_PRECISION = 6

    def __init__(self, symbol, percent_per_trade):
        self.h = Client()
        self._symbol = symbol
        self._percent_per_trade = percent_per_trade

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

    def get_decimal_representation(self, input_number):
        dec = Decimal(input_number)
        getcontext().prec = self.DECIMAL_PRECISION

        return dec

    def increment_one_at_last_digit(self, input_number):
        dec = self.get_decimal_representation(input_number)
        return dec.next_plus()

    def decrement_one_at_last_digit(self, input_number):
        dec = self.get_decimal_representation(input_number)
        return dec.next_minus()

    def get_optimal_buy_price(self, order_book, target_price): # undercutamo en druzga??? maybe keep this for myself? YEEEES YEEEEEEEEEEESSSSSSS
        for order in order_book['BUY']:
            if order[0] < target_price:
                return self.decrement_one_at_last_digit(order[0])

        return target_price

    def get_optimal_sell_price(self, order_book, target_price):
        for order in order_book['SELL']:
            if order[0] > target_price:
                return self.increment_one_at_last_digit(order[0])

        return target_price

    def trade_loop(self):
        while (True):
            balances = self.get_coin_balances()
            order_book = self.h.get_order_book(self._symbol)

            buy_price = self.get_optimal_buy_price(order_book, 1 - self._percent_per_trade)
            sell_price = self.get_optimal_sell_price(order_book, 1 + self._percent_per_trade)

            balanceA = balances[self.coinA]['balance']
            balanceB = balances[self.coinB]['balance']

            to_buy = balanceB * (1 + self._percent_per_trade)

            amount_to_buy = round(balanceB * (1 + self._percent_per_trade), self.DECIMAL_PRECISION)
            amount_to_sell = round(balanceA * (1 + self._percent_per_trade), self.DECIMAL_PRECISION)

            if balanceA > 1:
                self.h.create_buy_order(self._symbol, buy_price, amount_to_buy)
            elif balanceB > 1:
                self.h.create_sell_order(self._symbol, sell_price, amount_to_sell)
                a = 1

            time.sleep(0.25)

t = tradeBot('USDT-PAX', 0.05)




'''
orders_dealt = self.h.get_symbol_dealt_orders('KCS-ETH')
trading_symbols = self.h.get_trading_symbols('DAI')
buy_orders = self.h.get_active_orders('KCS-ETH')

a = h.get_recent_orders("ONT-ETH", 10)
h.create_buy_order('GO-KCS', 0.001, 62783.4875) #Ko je cena 0.001 kup 62783.4875 GOja
'''
