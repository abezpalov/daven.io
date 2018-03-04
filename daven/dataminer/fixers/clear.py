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

        count = PairInfo.objects.exclude(exported_at = None).count()
        PairInfo.objects.exclude(exported_at = None).delete()
        print('del', count)

        count = PairInfo.objects.filter(exported_at = None).count()
        print('not_del', count)


