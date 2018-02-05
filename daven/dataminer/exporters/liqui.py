import os
import json
import time
import datetime
from decouple import config
from django.utils import timezone

import numpy as np
import pandas as pd

from dataminer.models import *


class Worker():

    def __init__(self):
        self.bourse = Bourse.objects.take(**{'name': 'liqui', 'full_name': 'Liqui.io',
                                             'base_url': 'https://api.liqui.io/api/3'})
        print('Bourse:', self.bourse)
        self.start_time = timezone.now()

        # Базовая папка выгрузки
        self.export_path = config('EXPORT_PATH')
        try:
            os.mkdir(self.export_path)
        except FileExistsError:
            pass

        # Папка выгрузки текущей биржи
        self.export_path = '{}{}/'.format(self.export_path, self.bourse.name)
        try:
            os.mkdir(self.export_path)
        except FileExistsError:
            pass

    def run(self):

        pairs = Pair.objects.filter(bourse = self.bourse)
        for n, pair in enumerate(pairs):
            print('\n{} {}'.format(n, pair))

            self.export_pair_info(pair)

        print('Цикл завершен.\nВремя завершения: {}\nВремя выполнения{}\n\n'.format(
                timezone.now(), timezone.now() - self.start_time))


    def export_pair_info(self, pair):

        # Максимальное количество записей в одном датафрейме
        max_infos_in_df = 500 # 1000

        # Количество записей по данной валютной паре
        infos_count = PairInfo.objects.filter(pair = pair).count()
        print(infos_count)

        # Количество необходимых датафреймов
        df_count = int(infos_count / max_infos_in_df)

        for n in range(df_count):
            infos = PairInfo.objects.filter(pair = pair).values(
                    'id', 'content', 'created_at')[n*max_infos_in_df : (n+1)*max_infos_in_df]
            df = self.pair_infos_to_df(pair, infos)

            # Создаём папку

            path = '{}{}'.format(self.export_path, pair.name)
            try:
                os.mkdir(path)
            except FileExistsError:
                pass

            # Пишем в файл
            date = np.max(df.created_at)
            date = str(date).split('+')[0]
            file_name = '{}/{}.csv.tar.gz'.format(path, date)
            df.to_csv(file_name, compression='gzip', index_label='idx')
            print(n, file_name)


    def pair_infos_to_df(self, pair, infos):

        # Готовим словарь с массивами
        keys = ['info_id', 'bourse_name', 'pair_id', 'pair_name',
                 'ticker_high', 'ticker_low', 'ticker_avg', 'ticker_vol', 'ticker_vol_cur', 'ticker_last',
                 'ticker_buy', 'ticker_sell', 'ticker_updated']
        for i in range(2000):
            keys.append('order_ask_{}_price'.format(i))
            keys.append('order_ask_{}_vol'.format(i))
        for i in range(2000):
            keys.append('order_bid_{}_price'.format(i))
            keys.append('order_bid_{}_vol'.format(i))
        for i in range(2000):
            keys.append('trade_{}_ask'.format(i))
            keys.append('trade_{}_bid'.format(i))
            keys.append('trade_{}_price'.format(i))
            keys.append('trade_{}_amount'.format(i))
            keys.append('trade_{}_tid'.format(i))
            keys.append('trade_{}_timestamp'.format(i))
        keys.append('created_at')

        data = {}
        for key in keys:
            data[key] = []

        for info in infos:

            # Base info
            print(str(info['id']))
            data['info_id'].append(str(info['id']))
            data['bourse_name'].append(str(self.bourse.name))
            data['pair_id'].append(str(pair.id))
            data['pair_name'].append(str(pair.name))

            content = info['content']
            content = json.loads(content)

            # Ticker
            try:
                ticker = content['ticker']
            except TypeError:
                ticker = None
            if ticker:
                data['ticker_high'].append(ticker['high'])
                data['ticker_low'].append(ticker['low'])
                data['ticker_avg'].append(ticker['avg'])
                data['ticker_vol'].append(ticker['vol'])
                data['ticker_vol_cur'].append(ticker['vol_cur'])
                data['ticker_last'].append(ticker['last'])
                data['ticker_buy'].append(ticker['buy'])
                data['ticker_sell'].append(ticker['sell'])
                data['ticker_updated'].append(ticker['updated'])
            else:
                data['ticker_high'].append(None)
                data['ticker_low'].append(None)
                data['ticker_avg'].append(None)
                data['ticker_vol'].append(None)
                data['ticker_vol_cur'].append(None)
                data['ticker_last'].append(None)
                data['ticker_buy'].append(None)
                data['ticker_sell'].append(None)
                data['ticker_updated'].append(None)

            # Orders
            try:
                orders = content['orders']
            except TypeError:
                orders = None

            i = 0
            if orders:
                for order in orders['asks']:
                    price, vol = order
                    data['order_ask_{}_price'.format(i)].append(price)
                    data['order_ask_{}_vol'.format(i)].append(vol)
                    i += 1

            while i < 2000:
                data['order_ask_{}_price'.format(i)].append(None)
                data['order_ask_{}_vol'.format(i)].append(None)
                i += 1

            i = 0
            if orders:
                for order in orders['bids']:
                    price, vol = order
                    data['order_bid_{}_price'.format(i)].append(price)
                    data['order_bid_{}_vol'.format(i)].append(vol)
                    i += 1

            while i < 2000:
                data['order_bid_{}_price'.format(i)].append(None)
                data['order_bid_{}_vol'.format(i)].append(None)
                i += 1

            # Trades
            try:
                trades = content['trades']
            except TypeError:
                trades = None

            i = 0
            if trades:
                for trade in trades:
                    if trade['type'] == 'ask':
                        data['trade_{}_ask'.format(i)].append(True)
                        data['trade_{}_bid'.format(i)].append(False)
                    else:
                        data['trade_{}_ask'.format(i)].append(False)
                        data['trade_{}_bid'.format(i)].append(True)
                    data['trade_{}_price'.format(i)].append(trade['price'])
                    data['trade_{}_amount'.format(i)].append(trade['amount'])
                    data['trade_{}_tid'.format(i)].append(trade['tid'])
                    data['trade_{}_timestamp'.format(i)].append(trade['timestamp'])
                    i += 1

            while i < 2000:
                data['trade_{}_ask'.format(i)].append(False)
                data['trade_{}_bid'.format(i)].append(False)
                data['trade_{}_price'.format(i)].append(None)
                data['trade_{}_amount'.format(i)].append(None)
                data['trade_{}_tid'.format(i)].append(None)
                data['trade_{}_timestamp'.format(i)].append(None)
                i += 1

            data['created_at'.format(i)].append(info['created_at'])

        df = pd.DataFrame(data, columns = keys)

        return df
