import json
import time
import datetime
from django.utils import timezone

import numpy as np
import pandas as pd

from dataminer.models import *


class Worker():

    def __init__(self):
        self.bourse = Bourse.objects.take(**{'name': 'liqui', 'full_name': 'Liqui.io',
                                             'base_url': 'https://api.liqui.io/api/3'})
        print('Bourse:', self.bourse)

    def run(self):

        start_time = timezone.now()

        pairs = Pair.objects.filter(bourse = self.bourse)
        for n, pair in enumerate(pairs):
            df = self.pair_infos_to_df(pair)
            date = np.max(df.created_at)
            date = str(date).split(' ')[0]
            file_name = '~/export/{} {}.csv.tar.gz'.format(date, str(pair))
            df.to_csv(file_name, compression='gzip', index_label='idx')
            print(n, file_name)



        print('Цикл завершен.\nВремя завершения: {}\nВремя выполнения{}\n\n'.format(timezone.now(), timezone.now() - start_time))


    def pair_infos_to_df(self, pair):

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

        infos = PairJSONInfo.objects.filter(pair = pair).values('id', 'ticker', 'orders', 'trades',
                                                                'created_at')
        for info in infos:

            # Base info
            print(str(info['id']))
            data['info_id'].append(str(info['id']))
            data['bourse_name'].append(str(self.bourse.name))
            data['pair_id'].append(str(pair.id))
            data['pair_name'].append(str(pair.name))

            # Ticker
            ticker = json.loads(info['ticker'].replace("'", '"'))
            data['ticker_high'].append(ticker['high'])
            data['ticker_low'].append(ticker['low'])
            data['ticker_avg'].append(ticker['avg'])
            data['ticker_vol'].append(ticker['vol'])
            data['ticker_vol_cur'].append(ticker['vol_cur'])
            data['ticker_last'].append(ticker['last'])
            data['ticker_buy'].append(ticker['buy'])
            data['ticker_sell'].append(ticker['sell'])
            data['ticker_updated'].append(ticker['updated'])

            # Orders
            orders = json.loads(str(info['orders'].replace("'", '"')))

            i = 0
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
            trades = json.loads(str(info['trades'].replace("'", '"')))
            i = 0
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

        return pd.DataFrame(data, columns = keys)
