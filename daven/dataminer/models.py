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

        except Exception:
            o = Pair(**kwargs)
            o.save()

        return o


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


class PairInfoManager(models.Manager):

    def add(self, **kwargs):

        kwargs = clear_kwargs(**kwargs)

        if not kwargs.get('pair', None):
            raise(ValueError, 'Where is pair?')

        o = PairInfo(**kwargs)
        o.save()
        return o


class PairInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE, related_name='infos')
    content = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    exported_at = models.DateTimeField(null=True, db_index=True)

    objects = PairInfoManager()

    class Meta:
        ordering = ['created_at']
        verbose_name = 'pair info'
        verbose_name_plural = 'pair infos'


def clear_kwargs(**kwargs):

    for key in kwargs:
        if isinstance(kwargs[key], str):
            kwargs[key] = kwargs[key].strip()

    return kwargs
