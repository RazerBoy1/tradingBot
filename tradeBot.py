import time
from kucoinAPIHelper import Client

h = Client()

def get_coin_balances():
    stable_coin_balances = {'USDT': {'balance': 0.0},
                            'TUSD': {'balance': 0.0},
                            'USDC': {'balance': 0.0},
                            'PAX': {'balance': 0.0},
                            'DAI': {'balance': 0.0}}

    balances = h.get_all_balances()

    for coin in balances:
        coin_name = coin['coinType']
        if coin_name in stable_coin_balances:
            stable_coin_balances[coin_name]['balance'] = coin['balance']

    return stable_coin_balances

while(True):
    balances = get_coin_balances()


    time.sleep(0.25)

#a = h.get_recent_orders("ONT-ETH", 10)
#h.create_buy_order('GO-KCS', 0.001, 62783.4875) Ko je cena 0.001 kup 62783.4875 GOja
