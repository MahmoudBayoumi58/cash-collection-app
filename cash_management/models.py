from datetime import timedelta
from django.db import models
from django.utils import timezone
from djmoney.models.fields import MoneyField
from user_management.models import User, TimeStampedModel, Customer
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Task(TimeStampedModel):
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('collected', _('Collected')),
        ('completed', _('Completed')),
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, limit_choices_to={'is_deleted': False})
    cash_collector = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_cash_collector': True})
    amount_due = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    amount_due_at = models.DateTimeField()
    status = models.CharField(max_length=10, default='pending', choices=STATUS_CHOICES)
    collected_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_manager': True},
                                 related_name='manager_tasks')
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'Task for {self.customer.name} - {self.amount_due}'

    class Meta:
        ordering = ['amount_due_at']


class CollectionRecord(TimeStampedModel):
    cash_collector = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_cash_collector': True})
    collected_amount = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', null=True, blank=True)
    status = models.CharField(max_length=20)

    @staticmethod
    def add_record(cash_collector, collected_amount, status):
        record = CollectionRecord(
            cash_collector=cash_collector,
            collected_amount=collected_amount,
            status=status
        )
        record.save()
        return record



class Delivery(models.Model):
    cash_collector = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_cash_collector': True},
                                       related_name='deliveries')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_manager': True},
                                related_name='received_deliveries')
    tasks = models.ManyToManyField(Task)
    delivered_at = models.DateTimeField(auto_now_add=True)
    total_amount = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update task status to completed and cash collector status
        for task in self.tasks.all():
            task.status = 'completed'
            task.delivered_at = timezone.now()
            task.save()

    def __str__(self):
        return f'Delivery by {self.cash_collector.get_full_name()} to {self.manager.get_full_name()} on {self.delivered_at}'
