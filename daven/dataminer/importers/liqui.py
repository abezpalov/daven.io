import json
import requests
import time
import datetime
from django.utils import timezone

from dataminer.models import *

class Worker():

    def __init__(self):
        self.bourse = Bourse.objects.take(**{'name': 'liqui', 'full_name': 'Liqui.io',
                                             'base_url': 'https://api.liqui.io/api/3'})
        print('Bourse:', self.bourse)
        self.start_time = timezone.now()

    def run(self):

        # Получаем список валютных пар
        pairs = self.get_pairs()

        # Проходим по каждой паре и загружаем данные
        for pair in pairs:
            info = self.get_pair_info(pair)
            print(pair)
            PairInfo.objects.add(pair = pair, content = info)

        print('Цикл завершен.\nВремя завершения: {}\nВремя выполнения{}\n\n'.format(
                timezone.now(), timezone.now() - self.start_time))

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
                return r.json()
            except requests.exceptions.ConnectionError:
                print('Ошибка! Нет связи.')
                time.sleep(5)
            except requests.exceptions.Timeout:
                print('Ошибка! Истекло время ожидания.')
                time.sleep(1)

        return None

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

    def get_pair_info(self, pair):

        if pair.hidden:
            return None

        info = {}

        data = self.load('ticker', pair=pair.name)
        info['ticker'] = data.get(pair.name, None)

        data = self.load('depth', pair=pair.name, limit=2000)
        info['orders'] = data.get(pair.name, None)

        data = self.load('trades', pair=pair.name, limit=2000)
        info['trades'] = data.get(pair.name, None)

        return json.dumps(info)
