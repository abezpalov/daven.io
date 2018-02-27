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

        PairInfo.objects.all().update(exported_at = None)
