import uuid
from django.db import models

from django.utils import timezone

class CurrencyManager(models.Manager):

    def take(self, **kwargs):

        kwargs = clear_kwargs(**kwargs)

        kwargs['name'] = kwargs.get('name', '').strip().lower()
        kwargs['full_name'] = kwargs.get('full_name', kwargs['name']).strip()

        if not kwargs['name']:
            raise(ValueError, 'Where is name?')

        try:
            o = self.get(name = kwargs['name'])
        except Exception:
            o = Currency(**kwargs)
            o.save()

        return o


class Currency(models.Model):
    id = models.BigAutoField(primary_key = True, editable = False)
    name = models.CharField(max_length = 64, unique=True, )
    full_name = models.CharField(max_length = 256, db_index = True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(null = True, default = None)

    objects = CurrencyManager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'currency'
        verbose_name_plural = 'currencies'


class BourseManager(models.Manager):

    def take(self, **kwargs):

        kwargs = clear_kwargs(**kwargs)

        kwargs['name'] = kwargs.get('name', '').strip().lower()
        kwargs['full_name'] = kwargs.get('full_name', kwargs['name']).strip()

        if not kwargs['name']:
            raise(ValueError, 'Where is name?')

        try:
            o = self.get(name = kwargs['name'])
        except Exception:
            o = Bourse(**kwargs)
            o.save()

        return o


class Bourse(models.Model):
    id = models.BigAutoField(primary_key = True, editable = False)
    name = models.CharField(max_length = 64, unique=True)
    full_name = models.CharField(max_length = 256, db_index = True)
    base_url = models.CharField(max_length = 256, null = True, default = None)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(null = True, default = None)

    objects = BourseManager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'bourse'
        verbose_name_plural = 'bources'


class PairManager(models.Manager):

    def take(self, **kwargs):

        kwargs = clear_kwargs(**kwargs)

        kwargs['name'] = kwargs.get('name', '').strip().lower()

        if not kwargs['name']:
            raise(ValueError, 'Where is name?')

        if not kwargs.get('bourse', None):
            raise(ValueError, 'Where is bourse?')

        if not kwargs.get('first_currency', None):
            raise(ValueError, 'Where is first currency?')

        if not kwargs.get('second_currency', None):
            raise(ValueError, 'Where is second currency?')

        try:
            o = self.get(name = kwargs['name'], bourse = kwargs['bourse'])
            o.min_price = kwargs.get('min_price', None)
            o.max_price = kwargs.get('max_price', None)
            o.min_amount = kwargs.get('min_amount', None)
            o.max_amount = kwargs.get('max_amount', None)
            o.min_quantity = kwargs.get('min_quantity', None)
            o.max_quantity = kwargs.get('max_quantity', None)
            o.min_total = kwargs.get('min_total', None)
            o.hidden = kwargs.get('hidden', False)
            o.fee = kwargs.get('fee', None)
            o.updated_at = timezone.now()
            o.save()

        except models.:
            o = Pair(**kwargs)
            o.save()

        return o

# decimal_places: number of decimals allowed during trading.
# min_price: minimum price allowed during trading.
# max_price: maximum price allowed during trading.
# min_amount: minimum sell / buy transaction size.
# hidden: whether the pair is hidden, 0 or 1.
# fee: commission for this pair.
class Pair(models.Model):
    id = models.BigAutoField(primary_key = True, editable = False)
    bourse = models.ForeignKey(Bourse, on_delete = models.CASCADE, related_name = 'pairs')
    name = models.CharField(max_length = 64, db_index = True)
    first_currency = models.ForeignKey(Currency, on_delete = models.CASCADE, related_name = 'first_pairs')
    second_currency = models.ForeignKey(Currency, on_delete = models.CASCADE, related_name = 'second_pairs')
    min_price = models.FloatField(null=True)
    max_price = models.FloatField(null=True)
    min_amount = models.FloatField(null=True)
    max_amount = models.FloatField(null=True)
    min_quantity = models.FloatField(null=True)
    max_quantity = models.FloatField(null=True)
    min_total = models.FloatField(null=True)
    hidden = models.BooleanField(default = False)
    fee = models.FloatField(null=True, default = None)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(null = True)

    objects = PairManager()

    def __str__(self):
        if self.hidden:
            return '{} {} - hidden'.format(self.bourse, self.name)
        else:
            return '{} {}'.format(self.bourse, self.name)

    class Meta:
        ordering = ['name']
        unique_together = ('bourse', 'name')
        verbose_name = 'pair'
        verbose_name_plural = 'pairs'


class PairTickerManager(models.Manager):

    def add(self, **kwargs):

        kwargs = clear_kwargs(**kwargs)

        if not kwargs.get('pair', None):
            raise(ValueError, 'Where is pair?')

        o = PairTicker(**kwargs)
        o.save()

        return o

# high: maximum price.
# low: minimum price.
# avg: average price.
# vol: trade volume.
# vol_cur: trade volume in currency.
# last: the price of the last trade.
# buy: buy price.
# sell: sell price.
# updated: last update of cache. - not used
class PairTicker(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    pair = models.ForeignKey(Pair, on_delete = models.CASCADE, related_name = 'tickets')
    high = models.FloatField(default = 0.0)
    low = models.FloatField(default = 0.0)
    avg = models.FloatField(default = 0.0)
    vol = models.FloatField(default = 0.0)
    vol_cur = models.FloatField(default = 0.0)
    last = models.FloatField(default = 0.0)
    buy = models.FloatField(default = 0.0)
    sell = models.FloatField(default = 0.0)
    min_trade_timestamp = models.BigIntegerField(null=True, default=None)
    max_trade_timestamp = models.BigIntegerField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add = True)

    objects = PairTickerManager()

    def __str__(self):
        return '{} {}'.format(self.pair, self.created_at)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'pair ticker'
        verbose_name_plural = 'pair tickers'


class PairOrderManager(models.Manager):

    def add(self, **kwargs):

        kwargs = clear_kwargs(**kwargs)

        if not kwargs.get('ticker', None):
            raise(ValueError, 'Where is ticker?')

        o = PairOrder(**kwargs)
        o.save()

        return o


# asks: Sell orders.
# bids: Buy orders.
class PairOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticker = models.ForeignKey(PairTicker, on_delete=models.CASCADE, related_name='orders', null=True, default=None)
    price = models.FloatField(default=0.0)
    amount = models.FloatField(default=0.0)
    ask = models.BooleanField(default=False)
    bid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = PairOrderManager()

    def __str__(self):
        return '{} {}'.format(self.ticker, self.created_at)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'pair order'
        verbose_name_plural = 'pair orders'


class PairTradeManager(models.Manager):

    def add(self, **kwargs):

        kwargs = clear_kwargs(**kwargs)

        if not kwargs.get('pair', None):
            raise(ValueError, 'Where is pair?')
        if not kwargs.get('tid', None):
            raise(ValueError, 'Where is tid?')

        try:
            o = self.get(pair = kwargs['pair'], tid = kwargs['tid'])
            return None
        except Exception:
            o = PairTrade(**kwargs)
            o.save()

        return o


# type: ask – Sell, bid – Buy.
# price: Buy price/Sell price.
# amount: the amount of asset bought/sold.
# tid: trade ID.
# timestamp: UTC time of the trade.
class PairTrade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE, related_name='trades')
    price = models.FloatField(default=0.0)
    amount = models.FloatField(default=0.0)
    ask = models.BooleanField(default=False)
    bid = models.BooleanField(default=False)
    tid = models.BigIntegerField()
    timestamp = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = PairTradeManager()

    def __str__(self):
        return '{} {}'.format(self.pair, self.created_at)

    class Meta:
        unique_together = ('pair', 'tid')
        ordering = ['created_at']
        verbose_name = 'pair trade'
        verbose_name_plural = 'pair trades'


class PairJSONInfoManager(models.Manager):

    def add(self, **kwargs):

        kwargs = clear_kwargs(**kwargs)

        if not kwargs.get('pair', None):
            raise(ValueError, 'Where is pair?')

        o = PairJSONInfo(**kwargs)
        o.save()
        return o


class PairJSONInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE, related_name='infos')
    ticker = models.TextField()
    orders = models.TextField()
    trades = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = PairJSONInfoManager()

    class Meta:
        ordering = ['created_at']
        verbose_name = 'pair json info'
        verbose_name_plural = 'pair json infos'

def clear_kwargs(**kwargs):

    for key in kwargs:
        if isinstance(kwargs[key], str):
            kwargs[key] = kwargs[key].strip()

    return kwargs
