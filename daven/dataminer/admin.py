from django.contrib import admin

from .models import *

admin.site.register(Currency)
admin.site.register(Bourse)
admin.site.register(Pair)
admin.site.register(PairInfo)
