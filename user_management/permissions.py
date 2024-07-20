from rest_framework.permissions import BasePermission
from cash_management.models import Task
from rest_framework.exceptions import PermissionDenied

from user_management.models import User


class IsManager(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_manager:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_manager:
            return True

        return False


class IsCashCollector(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_cash_collector:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_cash_collector:
            if isinstance(obj, Task):
                if obj.cash_collector != request.user:
                    raise PermissionDenied()

                return True

            elif isinstance(obj, User):
                if obj != request.user:
                    raise PermissionDenied()

                return True

        return False


class IsManagerOrCashCollector(BasePermission):

    def has_permission(self, request, view):

        is_manager = False
        is_cash_collector = False

        try:
            is_manager = IsManager().has_permission(request, view)
        except PermissionDenied:
            pass

        try:
            is_cash_collector = IsCashCollector().has_permission(request, view)
        except PermissionDenied:
            pass

        if not is_manager and not is_cash_collector:
            raise PermissionDenied()

        return is_manager or is_cash_collector

    def has_object_permission(self, request, view, obj):

        is_manager = False
        is_cash_collector = False

        try:
            is_manager = IsManager().has_object_permission(request, view, obj)
        except PermissionDenied:
            pass

        try:
            is_cash_collector = IsCashCollector().has_object_permission(request, view, obj)
        except PermissionDenied:
            pass

        if not is_manager and not is_cash_collector:
            raise PermissionDenied()

        return is_manager or is_cash_collector
