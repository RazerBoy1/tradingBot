import time, math
from decimal import Decimal, getcontext
from kucoinAPIHelper import Client

class tradeBot(object):
    DECIMAL_PRECISION = 6

    def __init__(self, symbol, percent_per_trade):
        self.h = Client()
        self._symbol = symbol
        self._percent_per_trade = percent_per_trade

        pair = self.get_trading_pair()
        self.buy_coin = pair[0]
        self.sell_coin = pair[1]

        self.trade_loop()

    def get_trading_pair(self):
        return self._symbol.split('-')

    def get_coin_balances(self):
        stable_coin_balances = {self.buy_coin: {'balance': 0.0},
                                self.sell_coin: {'balance': 0.0}}

        balances = self.h.get_all_balances()

        for coin in balances:
            coin_name = coin['coinType']
            if coin_name in stable_coin_balances:
                stable_coin_balances[coin_name]['balance'] = coin['balance']

        return stable_coin_balances

    def balance_above_one_dollar(self, balances):
        for coin_name in balances:
            if balances[coin_name]['balance'] > 1.0:
                return True

        return False

    def get_optimal_price(self, order_book, target_price, order_type):
        for order in order_book[order_type]:
            if order_type == 'SELL' and order[0] > target_price:
                return self._increment_one_at_last_digit(order[0])
            elif order_type == 'BUY' and order[0] < target_price:
                return self._decrement_one_at_last_digit(order[0])

        return target_price

    def round_down(self, n, decimals=6):
        multiplier = 10 ** decimals
        return math.floor(n * multiplier) / multiplier

    def _get_decimal_representation(self, input_number):
        dec = Decimal(input_number)
        getcontext().prec = self.DECIMAL_PRECISION

        return dec

    def _increment_one_at_last_digit(self, input_number):
        dec = self._get_decimal_representation(input_number)
        return dec.next_plus()

    def _decrement_one_at_last_digit(self, input_number):
        dec = self._get_decimal_representation(input_number)
        return dec.next_minus()

    def trade_loop(self):
        while (True):
            while (True):
                try:
                    balances = self.get_coin_balances()
                    break
                except:
                    print("Getting client balance failed. The client and server timestamps were more than 2 seconds off or the internet connection failed.")
                    time.sleep(0.5)
                    continue

            if self.balance_above_one_dollar(balances):
                order_book = self.h.get_order_book(self._symbol)

                buy_price = self.get_optimal_price(order_book, 1 - self._percent_per_trade, 'BUY')
                sell_price = self.get_optimal_price(order_book, 1 + self._percent_per_trade, 'SELL')

                sell_balance = balances[self.sell_coin]['balance']
                buy_balance = balances[self.buy_coin]['balance']

                amount_to_buy = self.round_down(sell_balance / (1 - self._percent_per_trade), self.DECIMAL_PRECISION)
                amount_to_sell = self.round_down(buy_balance, self.DECIMAL_PRECISION)

                while (True):
                    try:
                        if sell_balance > 1.0:
                            self.h.create_buy_order(self._symbol, buy_price, amount_to_buy)
                            print("Trying to buy {} {} for price {}".format(amount_to_buy, self.buy_coin, buy_price))
                        if buy_balance > 1.0:
                            self.h.create_sell_order(self._symbol, sell_price, amount_to_sell)
                            print("Trying to sell {} {} for price {}".format(amount_to_sell, self.sell_coin, sell_price))

                        break
                    except:
                        print("Setting sell/buy order failed. The client and server timestamps were more than 2 seconds off or the internet connection failed.")
                        time.sleep(0.5)
                        continue

            time.sleep(0.5)

t = tradeBot('USDT-PAX', 0.005)
