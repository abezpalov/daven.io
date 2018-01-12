import requests
import json
import time
import datetime
from django.utils import timezone

from dataminer.models import *

class Worker():

    def __init__(self):
        self.bourse = Bourse.objects.take(**{'name': 'liqui', 'full_name': 'Liqui.io',
                                             'base_url': 'https://api.liqui.io/api/3'})
        print('Bourse:', self.bourse)

    def run(self):

        pairs = self.get_pairs()

        start_time = timezone.now()

        for pair in pairs:
            info = self.get_pair_json_info(pair)
            if info is not None:
                PairJSONInfo.objects.add(**info)
                print(pair)

        print('Цикл завершен.\nВремя завершения: {}\nВремя выполнения{}\n\n'.format(timezone.now(), timezone.now() - start_time))

    def load(self, method, pair = None, limit = None, timeout = 30, quantity_of_try = 3):
        'Функция загрузки открытых данных'

        if method in ('depth', 'trades'):
            limit = 2000

        if pair and limit:
            url = '{}/{}/{}?limit={}'.format(self.bourse.base_url, method, pair, limit)
        elif pair:
            url = '{}/{}/{}'.format(self.bourse.base_url, method, pair)
        else:
            url = '{}/{}'.format(self.bourse.base_url, method)

        for i in range(quantity_of_try):
            try:
                r = requests.get(url, timeout = timeout)
                return json.loads(r.text)
            except requests.exceptions.ConnectionError:
                print('Ошибка! Нет связи.')
                time.sleep(5)
            except requests.exceptions.Timeout:
                print('Ошибка! Истекло время ожидания.')
                time.sleep(1)
            except json.decoder.JSONDecodeError:
                print('Ошибка! Не удаётся декодировать JSON.')
                time.sleep(1)
            except json.decoder.SSLError:
                print('Ошибка! Подменён сертификат SSL.')
                return False

        return False

    def get_pairs(self):
        'Загрузка информации о валютах и валютных парах'

        pairs_ = self.load('info')['pairs']

        currencies = set()
        for pair_name in pairs_:
            for currency_name in pair_name.split('_'):
                currencies.add(currency_name)
        for currency_name in currencies:
            currency = Currency.objects.take(name=currency_name)
            print('Currency:', currency)

        pairs = set()
        for pair_name in pairs_:
            pair_ = {}
            pair_['bourse'] = self.bourse
            pair_['name'] = pair_name
            pair_['first_currency'], pair_['second_currency'] = pair_name.split('_')
            pair_['first_currency'] = Currency.objects.take(name=pair_['first_currency'])
            pair_['second_currency'] = Currency.objects.take(name=pair_['second_currency'])
            pair_['min_price'] = pairs_[pair_name]['min_price']
            pair_['max_price'] = pairs_[pair_name]['max_price']
            pair_['min_amount'] = pairs_[pair_name]['min_amount']
            pair_['max_amount'] = pairs_[pair_name]['max_amount']
            pair_['min_total'] = pairs_[pair_name]['min_total']
            pair_['hidden'] = pairs_[pair_name]['hidden']
            pair_['fee'] = pairs_[pair_name]['fee']
            pair = Pair.objects.take(**pair_)
            print('Pair', pair)
            pairs.add(pair)

        return pairs

    def get_pair_json_info(self, pair):

        if pair.hidden:
            return None

        info = {}
        info['pair'] = pair

        data = self.load('ticker', pair=pair.name)
        info['ticker'] = data.get(pair.name, None)
        if info['ticker'] is None:
            print(pair, '- no ticker')
            print(data)
            return None

        data = self.load('depth', pair=pair.name, limit=2000)
        info['orders'] = data.get(pair.name, None)
        if info['orders'] is None:
            print(pair, '- no orders')
            print(data)
            return None

        data = self.load('trades', pair=pair.name, limit=2000)
        info['trades'] = data.get(pair.name, None)
        if info['trades'] is None:
            print(pair, '- no trades')
            print(data)
            return None

        return info


    def get_pair_info(self, pair):

        # Если пара валют скрыта - дальнейшая обработка бессмысленна
        if pair.hidden:
            return None

        # Сводная информация по валютной паре за сутки
        ticker_ = self.load('ticker', pair=pair.name).get(pair.name, None)

        if ticker_ is None:
            return None
        ticker_['pair'] = pair
        del ticker_['updated']
        ticker = PairTicker.objects.add(**ticker_)

        # Лоты
        depth_ = self.load('depth', pair=pair.name, limit=2000)
        count_of_orders = 0

        try:
            orders_ = depth_[pair.name]['asks']
        except KeyError:
            return None
        for order__ in orders_:
            order_ = {}
            order_['ticker'] = ticker
            order_['price'] = order__[0]
            order_['amount'] = order__[1]
            order_['ask'] = True
            order_['bid'] = False
            order = PairOrder.objects.add(**order_)
            count_of_orders += 1

        try:
            orders_ = depth_[pair.name]['bids']
        except KeyError:
            return None
        for order__ in orders_:
            order_ = {}
            order_['ticker'] = ticker
            order_['price'] = order__[0]
            order_['amount'] = order__[1]
            order_['ask'] = False
            order_['bid'] = True
            order = PairOrder.objects.add(**order_)
            count_of_orders += 1

        # Совершенные сделки
        trades_ = self.load('trades', pair=pair.name, limit=2000)
        trades_ = trades_.get(pair.name, None)
        if trades_ is None:
            return None

        count_of_trades = 0

        for i, trade_ in enumerate(trades_):

            if i == 0:
                min_trade_timestamp = trade_['timestamp']
                max_trade_timestamp = trade_['timestamp']
            else:
                if min_trade_timestamp < trade_['timestamp']:
                    min_trade_timestamp = trade_['timestamp']
                if max_trade_timestamp > trade_['timestamp']:
                    max_trade_timestamp = trade_['timestamp']

            trade_['pair'] = pair
            if trade_['type'] == 'ask':
                trade_['ask'] = True
                trade_['bid'] = False
            else:
                trade_['ask'] = False
                trade_['bid'] = True

            del trade_['type']
            trade = PairTrade.objects.add(**trade_)
            if trade is not None:
                count_of_trades += 1

        ticker.min_trade_timestamp = min_trade_timestamp
        ticker.max_trade_timestamp = max_trade_timestamp
        ticker.save()

        print('{} ({} orders, {} trades)'.format(pair, count_of_orders, count_of_trades))
