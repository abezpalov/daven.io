import os
import sys
from decouple import config

from django.utils import timezone

SYS_PATH = config('SYS_PATH')
sys.path.append(SYS_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'daven.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Выполняем необходимый загрузчик
print("Пробую выполнить загрузчик " + sys.argv[1])
Worker = __import__('dataminer.exporters.' + sys.argv[1], fromlist=['Worker'])

# Тестовый режим больше логов на экране
for arg in sys.argv:
    if '-t' == arg:
        test = True
        break
    else:
        test = False

# Режим многопоточности
for arg in sys.argv:
    if '-m' == arg:
        mp = True
        break
    else:
        mp = False

worker = Worker.Worker()
worker.test = test
worker.mp = mp
worker.run()

exit()
