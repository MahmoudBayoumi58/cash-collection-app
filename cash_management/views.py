from django.db.models import Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import *
from rest_framework.views import APIView
from rest_framework.response import Response
from cash_management.models import Task, Delivery, CollectionRecord
from cash_management.pagination import CustomPagination
from cash_management.serializers import (
    TaskCreateSerializer, TaskSerializer,
    DeliverySerializer, CollectionRecordSerializer,
    DateFilterSerializer
)
from user_management.models import User
from user_management.permissions import IsManager, IsCashCollector, IsManagerOrCashCollector


# Create your views here.
class TaskCreateView(CreateAPIView):
    queryset = Task.objects.all()
    permission_classes = [IsManager]
    serializer_class = TaskCreateSerializer

    def post(self, request, *args, **kwargs):
        try:
            request.data['added_by'] = request.user.id
            task_serializer = self.get_serializer(data=request.data)
            if task_serializer.is_valid():
                task_serializer.save()
                status_code = status.HTTP_201_CREATED
                message = task_serializer.data
                return Response(message, status=status_code)

            status_code = status.HTTP_400_BAD_REQUEST
            message = task_serializer.errors

        except Exception as ex:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            message = str(ex)
        return Response(message, status=status_code)


class CashCollectorCompletedTasksView(ListAPIView):
    queryset = Task.objects.filter(is_deleted=0)
    permission_classes = [IsCashCollector]
    serializer_class = TaskSerializer
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        user = request.user
        tasks = self.get_queryset().filter(cash_collector=user, status='collected')

        page = self.paginate_queryset(tasks)
        if page is not None:
            tasks_serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(tasks_serializer.data)

        tasks_serializer = self.get_serializer(tasks, many=True)

        return Response(tasks_serializer.data, status=status.HTTP_200_OK)


class CashCollectorNextTaskRetrieveView(RetrieveAPIView):
    queryset = Task.objects.filter(is_deleted=0)
    permission_classes = [IsCashCollector]
    serializer_class = TaskSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        user.check_frozen_status()
        next_task = self.get_queryset().filter(status='pending').first()
        cash_collector_status = 'Frozen' if user.is_frozen else 'Not Frozen'
        if user.is_frozen:
            CollectionRecord.add_record(user, None, cash_collector_status)
            message = {
                'message': 'You do not have permission to perform this action'
            }
            return Response(message, status=status.HTTP_403_FORBIDDEN)

        task_serializer = self.get_serializer(next_task)
        return Response(task_serializer.data, status=status.HTTP_200_OK)


class CashCollectorStatusRetrieveView(RetrieveAPIView):
    queryset = User.objects.filter(is_cash_collector=True)
    permission_classes = [IsManagerOrCashCollector]

    def get(self, request, *args, **kwargs):
        cash_collector = self.get_object()
        cash_collector_status = 'Frozen' if cash_collector.is_frozen else 'Not Frozen'
        message = {
            'status': cash_collector_status
        }
        return Response(message, status=status.HTTP_200_OK)


class CashCollectorCollectCashView(UpdateAPIView):
    queryset = Task.objects.filter(is_deleted=0, status='pending')
    permission_classes = [IsCashCollector]
    serializer_class = TaskSerializer

    def put(self, request, *args, **kwargs):
        task = self.get_object()
        task.status = 'collected'
        task.collected_at = timezone.now()
        task.save()
        cash_collector = request.user
        cash_collector_status = 'Frozen' if cash_collector.is_frozen else 'Not Frozen'
        # add record as history for cash-collector
        CollectionRecord.add_record(cash_collector, task.amount_due, cash_collector_status)
        task_serializer = self.get_serializer(task)
        return Response(task_serializer.data, status=status.HTTP_200_OK)


class CashCollectorDeliverCashView(APIView):
    permission_classes = [IsCashCollector]

    def post(self, request, *args, **kwargs):
        try:
            tasks_id = request.data.get('tasks')
            cash_collector_id = request.data.get('cash_collector')
            manager_id = request.data.get('manager')
            collected_tasks = Task.objects.filter(id__in=tasks_id, status='collected',
                                                  cash_collector_id=cash_collector_id)
            if collected_tasks:
                total_amount = collected_tasks.aggregate(total_due=Sum('amount_due'))['total_due']
                delivery = Delivery.objects.create(cash_collector_id=cash_collector_id, manager_id=manager_id,
                                                   total_amount=total_amount)
                delivery.tasks.add(*collected_tasks)
                delivery.save()
                # unfrozen cash-collector status
                delivery.cash_collector.check_frozen_status()
                delivery_serializer = DeliverySerializer(delivery)
                return Response(delivery_serializer.data, status=status.HTTP_200_OK)

            message = {
                'message': 'There is not collected tasks to deliver them'
            }
            status_code = status.HTTP_400_BAD_REQUEST

        except Exception as ex:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            message = str(ex)
        return Response(message, status=status_code)


class CollectionRecordView(CreateAPIView):
    queryset = CollectionRecord.objects.all()
    permission_classes = [IsManager]
    serializer_class = CollectionRecordSerializer
    pagination_class = CustomPagination

    def post(self, request, *args, **kwargs):
        date_filter = (request.data.get('date_from'), request.data.get('date_to'))
        date_filter_serializer = DateFilterSerializer(data=request.data)
        if not date_filter_serializer.is_valid():
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                'message': date_filter_serializer.errors,
            }
            return Response(response_data, status=status_code)

        records = self.get_queryset().filter(cash_collector_id=kwargs['pk'], created_at__range=date_filter)

        page = self.paginate_queryset(records)
        if page is not None:
            tasks_serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(tasks_serializer.data)

        tasks_serializer = self.get_serializer(records, many=True)

        return Response(tasks_serializer.data, status=status.HTTP_200_OK)


class CashCollectorTasksView(CreateAPIView):
    queryset = Task.objects.filter(is_deleted=0)
    permission_classes = [IsManager]
    serializer_class = TaskSerializer
    pagination_class = CustomPagination

    def post(self, request, *args, **kwargs):
        cash_collector_id = request.data.get('cash_collector')
        status_filter = request.data.get('status')
        tasks = self.get_queryset().filter(cash_collector_id=cash_collector_id, status=status_filter)

        page = self.paginate_queryset(tasks)
        if page is not None:
            tasks_serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(tasks_serializer.data)

        tasks_serializer = self.get_serializer(tasks, many=True)

        return Response(tasks_serializer.data, status=status.HTTP_200_OK)
