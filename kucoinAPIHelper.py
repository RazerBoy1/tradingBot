import requests, certifi, json, time, base64, hmac, hashlib

class Client(object):
    API_URL = 'https://api.kucoin.com'
    API_VERSION = 'v1'
    _language = 'en-US'

    def __init__(self, api_key=None, api_secret=None, request_params=None, language=None):
        self.API_KEY = api_key
        self.API_SECRET = api_secret
        self.request_params = requests_params

        if not key:
            self.API_KEY = _get_key()

        if not secret:
            self.API_SECRET = _get_secret()

        if language:
            self._language = language

        self.session = self._init_session()

    def _get_key(self):
        return _read_authentication_file()[0].rstrip()

    def _get_secret(self):
        return _read_authentication_file()[1].rstrip()

    def _read_authentication_file(self, path=None, name=None):
        location = 'auth.txt'

        if name:
            location = name
        if path:
            location = '{}/{}'.format(path, location)
        if path and name:
            location = '{}/{}'.format(path, name)

        f = open(location, 'r')
        auth_file = f.readlines()
        f.close()

        return auth_file

    def _init_session(self):
        session = requests.session()
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Trade Bot',
            'KC-API-KEY': self.API_KEY,
            'HTTP_ACCEPT_LANGUAGE': self._language,
            'Accept-Language': self._language
        }
        session.headers.update(headers)

        return session

    def _get(self, path, **args):
        return self._request('get', path, **args)

    def _post(self, path, **args):
        return self._request('post', path, **args)

    def _put(self, path, **args):
        return self._request('put', path, **args)

    def _delete(self, path, **args):
        return self._request('delete', path, **args)

    def _create_path(self, method, path):
        return '/{}/{}'.format(self.API_VERSION, path)

    def _create_uri(self, path):
        return '{}{}'.format(self.API_URL, path)

    def _request(self, method, path, signed, **args):
        args['timeout'] = 10

        if self._requests_params:
            args.update(self._requests_params)

        args['data'] = args.get('data', {})
        args['headers'] = args.get('headers', {})

        full_path = self._create_path(method, path)
        uri = self._create_uri(full_path)

        if signed:
            args['headers']['KC-API-NONCE'] = str(_get_nonce)
            args['headers']['KC-API-SIGNATURE'] = self._generate_signature(full_path, args['data'], nonce)

        if args['data'] and method == 'get':
            args['params'] = args['data']
            del (args['data'])

        response = getattr(self.session, method)(uri, **args)
        return self._handle_response(response)

    def _handle_response(self, response):
        if not str(response.status_code).startswith('2'):
            raise KucoinAPIException(response)
        try:
            json = response.json()

            if 'success' in json and not json['success']:
                raise KucoinAPIException(response)

            res = json

            if 'data' in json:
                res = json['data']
            return res
        except ValueError:
            raise KucoinRequestException('Invalid Response: %s' % response.text)

    def _order_params_for_sig(self, data):
        strs = []
        for key in sorted(data):
            strs.append("{}={}".format(key, data[key]))
        return '&'.join(strs)

    def _generate_signature(self, path, data, nonce):
        query_string = self._order_params_for_sig(data)
        sig_str = ("{}/{}/{}".format(path, nonce, query_string)).encode('utf-8')
        m = hmac.new(self.API_SECRET.encode('utf-8'), base64.b64encode(sig_str), hashlib.sha256)

        return m.hexdigest()

    def _get_nonce(self):
        return int(time.time() * 1000)

    def get_coin_balance(self, coin):
        return self._get('account/{}/balance'.format(coin), True)

    def get_all_balances(self):
        data = {}
        return self._get('account/balance', True, data=data)

    def create_order(self, symbol, order_type, price, amount):
        data = {
            'symbol': symbol,
            'type': order_type,
            'price': price,
            'amount': amount
        }

        return self._post('order', True, data=data)

    def create_buy_order(self, symbol, price, amount):
        return self.create_order(symbol, self.SIDE_BUY, price, amount)

    def create_sell_order(self, symbol, price, amount):
        return self.create_order(symbol, self.SIDE_SELL, price, amount)

    def get_active_orders(self, symbol, kv_format=False):
        data = {
            'symbol': symbol
        }

        path = 'order/active'
        if kv_format:
            path += '-map'

        return self._get(path, True, data=data)

    def cancel_order(self, order_id, order_type, symbol=None):
        data = {
            'orderOid': order_id
        }

        if order_type:
            data['type'] = order_type
        if symbol:
            data['symbol'] = symbol

        return self._post('cancel-order', True, data=data)

    def cancel_all_orders(self, symbol=None, order_type=None):
        data = {}

        if order_type:
            data['type'] = order_type
        if symbol:
            data['symbol'] = symbol

        return self._post('order/cancel-all', True, data=data)

    def get_dealt_orders(self, symbol=None, order_type=None, limit=None, page=None, since=None, before=None):
        data = {}

        if symbol:
            data['symbol'] = symbol
        if order_type:
            data['type'] = order_type
        if limit:
            data['limit'] = limit
        if page:
            data['page'] = page
        if since:
            data['since'] = since
        if before:
            data['before'] = before

        return self._get('order/dealt', True, data=data)

    def get_symbol_dealt_orders(self, symbol, order_type=None, limit=None, page=None):
        data = {
            'symbol': symbol
        }

        if order_type:
            data['type'] = order_type
        if limit:
            data['limit'] = limit
        if page:
            data['page'] = page

        return self._get('deal-orders', True, data=data)

    def get_order_details(self, symbol, order_type, limit=None, page=None, order_id=None):
        data = {
            'symbol': symbol,
            'type': order_type
        }

        if limit:
            data['limit'] = limit
        if page:
            data['page'] = page
        if order_id:
            data['orderOid'] = order_id

        return self._get('order/detail', True, data=data)

    def get_order_book(self, symbol, group=None, limit=None):
        data = {
            'symbol': symbol
        }

        if group:
            data['group'] = group
        if limit:
            data['limit'] = limit

        return self._get('open/orders', False, data=data)

    def get_buy_orders(self, symbol, group=None, limit=None):
        data = {
            'symbol': symbol
        }

        if group:
            data['group'] = group
        if limit:
            data['limit'] = limit

        return self._get('open/orders-buy', False, data=data)

    def get_sell_orders(self, symbol, group=None, limit=None):
        data = {
            'symbol': symbol
        }

        if group:
            data['group'] = group
        if limit:
            data['limit'] = limit

        return self._get('open/orders-sell', False, data=data)

    def get_recent_orders(self, symbol, limit=None, since=None):
        data = {
            'symbol': symbol
        }

        if limit:
            data['limit'] = limit
        if since: #Doesn't work.
            data['since'] = since

        return self._get('open/deal-orders', False, data=data)






'''

TEST CRAP

'''



def _get_key():
    return _read_authentication_file()[0].rstrip()

def _get_secret():
    return _read_authentication_file()[1].rstrip()

def _read_authentication_file(name=None, path=None):
    location = 'auth.txt'

    if name:
        location = name
    if path:
        location = '{}/{}'.format(path, location)
    if path and name:
        location = '{}/{}'.format(path, name)

    f = open(location, 'r')
    auth_file = f.readlines()
    f.close()

    return auth_file

def create_sha256_signature(secret, to_sign):
    signature = hmac.new(secret.encode('utf-8'), base64.b64encode(to_sign.encode('utf-8')), hashlib.sha256)
    return signature.hexdigest()

def get_nonce():
    return int(time.time() * 1000)


bla = _read_authentication_file(None, None)



nonce = get_nonce()
host = 'https://api.kucoin.com'
api_version = '/v1/'
endpoint = 'user/info'
query_string = ''
url_to_sign = '{}{}/{}/{}'.format(api_version, endpoint, str(nonce), query_string)

signature = create_sha256_signature(bla[1].rstrip(), url_to_sign)

headers = {
    'KC-API-KEY': _get_key(),
    'KC-API-NONCE': str(nonce),
    'KC-API-SIGNATURE': _get_secret()
}

r = requests.post('https://api.kucoin.com/v1/user/info', headers=headers)
print(r._content)

