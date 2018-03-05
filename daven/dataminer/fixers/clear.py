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

        i = 1

        print('to del:', PairInfo.objects.exclude(exported_at = None).count())

        while True:
            ids = PairInfo.objects.exclude(exported_at = None).values_list('id', flat=True)[0:1000]
            ids = list(ids)
            if len(ids) > 0:
                PairInfo.objects.filter(id__in=list(ids)).delete()
                print(i, len(ids))
                i += 1
            else:
                break
