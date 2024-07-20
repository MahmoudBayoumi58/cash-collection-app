from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.generics import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from cash_management.pagination import CustomPagination
from user_management.models import Customer, User
from user_management.permissions import IsManager
from user_management.serializers import UserSerializer, CustomerSerializer


# Create your views here.
class UserRegistrationView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        try:
            user_serializer = self.get_serializer(data=request.data)
            if user_serializer.is_valid():
                user = user_serializer.save()
                user.is_cash_collector = True
                user.save()
                status_code = status.HTTP_201_CREATED
                message = {
                    "status": "success",
                    "message": "User registered successfully"
                }
                return Response(message, status=status_code)

            status_code = status.HTTP_400_BAD_REQUEST
            message = user_serializer.errors

        except Exception as ex:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            message = str(ex)
        return Response(message, status=status_code)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(data, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerCreateView(CreateAPIView):
    queryset = Customer.objects.all()
    permission_classes = [IsManager]
    serializer_class = CustomerSerializer

    def post(self, request, *args, **kwargs):
        try:
            customer_serializer = self.get_serializer(data=request.data)
            if customer_serializer.is_valid():
                customer_serializer.save()
                status_code = status.HTTP_201_CREATED
                message = customer_serializer.data
                return Response(message, status=status_code)

            status_code = status.HTTP_400_BAD_REQUEST
            message = customer_serializer.errors

        except Exception as ex:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            message = str(ex)
        return Response(message, status=status_code)


class UserStatusListView(ListAPIView):
    queryset = User.objects.all()
    permission_classes = [IsManager]
    pagination_class = CustomPagination
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        tasks = self.get_queryset().exclude(id=request.user.id)
        page = self.paginate_queryset(tasks)
        if page is not None:
            tasks_serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(tasks_serializer.data)

        tasks_serializer = self.get_serializer(tasks, many=True)

        return Response(tasks_serializer.data, status=status.HTTP_200_OK)
