from rest_framework import serializers
from cash_management.models import Task, Delivery, CollectionRecord
from user_management.serializers import CustomerSerializer, UserSerializer


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    cash_collector = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = '__all__'


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = '__all__'


class CollectionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionRecord
        fields = ['cash_collector', 'collected_amount', 'created_at', 'status']


class DateFilterSerializer(serializers.Serializer):
    date_from = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    date_to = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
