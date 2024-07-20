from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from user_management.models import User, Customer


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'is_cash_collector', 'is_manager', 'is_frozen']
        read_only_fields = ['is_cash_collector', 'is_manager', 'is_frozen']

    def create(self, validated_data):
        user = User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
