from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from user_management.managers import CustomUserManager
from django.conf import settings


# Create your models here.
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    username = None
    email = models.EmailField(verbose_name=_('email address'), unique=True)
    is_cash_collector = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_frozen = models.BooleanField(default=False)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def check_frozen_status(self):
        threshold_days = int(settings.THRESHOLD_DAYS)
        threshold_amount = int(settings.THRESHOLD_AMOUNT)
        two_days_ago = timezone.now() - timedelta(days=threshold_days)
        total_collected = self.task_set.filter(
            status='collected',
            collected_at__gte=two_days_ago
        ).aggregate(total=models.Sum('amount_due'))['total'] or 0

        if total_collected >= threshold_amount:
            self.is_frozen = True
        else:
            self.is_frozen = False
        self.save()


class Customer(TimeStampedModel):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name
