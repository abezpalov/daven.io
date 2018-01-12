import requests
import time
import datetime
from django.utils import timezone

from dataminer.models import *

class Worker():

    def __init__(self):
        self.bourse = Bourse.objects.take(**{'name': 'exmo', 'full_name': 'Exmo.me',
                                             'base_url': 'https://api.exmo.com/v1'})
        print('Bourse:', self.bourse)

    def run(self):

        pairs = self.get_pairs()

        tickers_ = self.get_tickers()

        start_time = timezone.now()

        for pair in pairs:
            info = self.get_pair_json_info(pair, tickers_.get(pair.name.upper()))
            if info is not None:
                PairJSONInfo.objects.add(**info)
                print(pair)

        print('Цикл завершен.\nВремя завершения: {}\nВремя выполнения{}\n\n'.format(timezone.now(), timezone.now() - start_time))

    def load(self, method, pair = None, limit = None, timeout = 30, quantity_of_try = 3):
        'Функция загрузки открытых данных'

        if pair and limit:
            url = '{}/{}/?pair={}&limit={}'.format(self.bourse.base_url, method, pair, limit)
        elif pair:
            url = '{}/{}/?pair={}'.format(self.bourse.base_url, method, pair)
        else:
            url = '{}/{}/'.format(self.bourse.base_url, method)

        for i in range(quantity_of_try):
            try:
                r = requests.get(url, timeout = timeout)
                return r.json()
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

        pairs_ = self.load('pair_settings')

        currencies = set()
        for pair_name in pairs_:
            for currency_name in pair_name.split('_'):
                currencies.add(currency_name.lower())
        for currency_name in currencies:
            currency = Currency.objects.take(name=currency_name)
            print('Currency:', currency)

        pairs = set()
        for pair_name in pairs_:
            pair_ = {}
            pair_['bourse'] = self.bourse
            pair_['name'] = pair_name.lower()
            pair_['first_currency'], pair_['second_currency'] = pair_['name'].split('_')
            pair_['first_currency'] = Currency.objects.take(name=pair_['first_currency'])
            pair_['second_currency'] = Currency.objects.take(name=pair_['second_currency'])
            pair_['min_price'] = pairs_[pair_name]['min_price']
            pair_['max_price'] = pairs_[pair_name]['max_price']
            pair_['min_amount'] = pairs_[pair_name]['min_amount']
            pair_['max_amount'] = pairs_[pair_name]['max_amount']
            pair_['min_quantity'] = pairs_[pair_name]['min_quantity']
            pair_['max_quantity'] = pairs_[pair_name]['max_quantity']
            pair = Pair.objects.take(**pair_)
            print('Pair', pair)
            pairs.add(pair)

        return pairs

    def get_tickers(self):
        'Загрузка статистики объёмов по валютным парам'

        tickers_ = self.load('ticker')
        return tickers_

    def get_pair_json_info(self, pair, ticker_):

        if pair.hidden:
            return None

        info = {}
        info['pair'] = pair

        info['ticker'] = ticker_
        if info['ticker'] is None:
            print(pair, '- no ticker')
            print(data)
            return None

        data = self.load('order_book', pair=pair.name.upper(), limit=1000)
        info['orders'] = data.get(pair.name.upper(), None)
        if info['orders'] is None:
            print(pair, '- no orders')
            print(data)
            return None

        data = self.load('trades', pair=pair.name.upper())
        info['trades'] = data.get(pair.name.upper(), None)
        if info['trades'] is None:
            print(pair, '- no trades')
            print(data)
            return None

        return info
