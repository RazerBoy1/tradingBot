import time
from kucoinAPIHelper import Client
h = Client()

while(True):
    a = h.get_recent_orders("ONT-ETH", 10)
    print(a)

    time.sleep(0.25)
