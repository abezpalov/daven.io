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

        infos_ids = PairInfo.objects.all().values('id')

        for n, info_id in enumerate(infos_ids):
            info_id = info_id['id']
            info = PairInfo.objects.get(id = info_id)
            print('{} of {} - {}'.format(n, infos_count, str(info.id)))
            info.content = str(info.content)
            info.content = info.content.replace("'", '"')
            info.content = info.content.replace('None', 'null')
            info.content = json.loads(info.content)
            info.content = json.dumps(info.content)
            info.save()
