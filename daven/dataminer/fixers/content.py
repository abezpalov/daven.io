import gc
import json
import time
import datetime
from django.utils import timezone

from dataminer.models import *


class Worker():

    def __init__(self):
        self.start_time = timezone.now()

    def run(self):

        infos_count = PairInfo.objects.all().count()

        count_on_party = 100

        count_of_party = int(infos_count / count_on_party) + 1

        for n in range(count_of_party):

            # Чистим мусор
            print('\n{} of {}'.format(n, count_of_party))
            gc.collect()

            # Загружаем партию объектов
            count = PairInfo.objects.all()[n*count_on_party: (n+1)*count_on_party].count()
            print(count)
            infos = PairInfo.objects.all()[n*count_on_party: (n+1)*count_on_party]

            for info in infos:
                print(info.id)
                info.content = str(info.content)
                info.content = info.content.replace("'", '"')
                info.content = info.content.replace('None', 'null')
                info.content = json.loads(info.content)
                info.content = json.dumps(info.content)
                info.save()
