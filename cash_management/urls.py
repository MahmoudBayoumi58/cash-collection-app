from django.urls import path
from cash_management.views import (
    TaskCreateView, CashCollectorCompletedTasksView,
    CashCollectorNextTaskRetrieveView, CashCollectorStatusRetrieveView,
    CashCollectorCollectCashView, CashCollectorDeliverCashView,
    CollectionRecordView, CashCollectorTasksView
)

urlpatterns = [
    path('task/add/', TaskCreateView.as_view(), name='create_task'),
    path('tasks/', CashCollectorTasksView.as_view(), name='get_tasks_by_status'),
    path('cash_collector/tasks', CashCollectorCompletedTasksView.as_view(), name='cash_collector_tasks'),
    path('cash_collector/records/<int:pk>/', CollectionRecordView.as_view(), name='cash_collector_records'),
    path('cash_collector/task/next', CashCollectorNextTaskRetrieveView.as_view(), name='cash_collector_next_task'),
    path('cash_collector/task/collect/<int:pk>/', CashCollectorCollectCashView.as_view(), name='collect_cash'),
    path('cash_collector/task/pay/', CashCollectorDeliverCashView.as_view(), name='pay_cash_to_manager'),
    path('cash_collector/status/<int:pk>/', CashCollectorStatusRetrieveView.as_view(), name='collector_status'),
]
