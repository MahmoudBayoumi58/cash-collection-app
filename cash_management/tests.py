from django.utils import timezone
from rest_framework.test import APITestCase
from cash_management.models import Task, CollectionRecord
from user_management.models import User, Customer
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse


# Create your tests here.
class TaskCreateTestCase(APITestCase):

    def setUp(self):
        # setup initial data for all tests
        # create admin account
        email = 'admin@admin.com'
        password = 'admin'
        user = User.objects.create_superuser(
            email=email,
            password=password
        )
        refresh = RefreshToken.for_user(user)
        self.access_token = str(refresh.access_token)

        # create customer record
        self.customer = Customer.objects.create(**{
            "name": "Eman Mohammed",
            "address": "Cairo,Egypt"
        })

        # create cash collector account
        self.cash_collector = User.objects.create_user(**{
            'email': 'mahmoudtotti120@gmail.com',
            'password': 'anatotti',
            'is_cash_collector': True
        })

    def test_create_task(self):
        initial_task_count = Task.objects.count()
        task_attrs = {
            "customer": self.customer.id,
            "cash_collector": self.cash_collector.id,
            "amount_due": 5000,
            "amount_due_at": "2024-07-19 12:03:14.771036"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        url = reverse('create_task')
        response = self.client.post(url, task_attrs, format='json')
        self.assertEqual(response.status_code, 201, msg=response.status_code)

        self.assertEqual(
            Task.objects.count(),
            initial_task_count + 1
        )

        for attr, expected_value in task_attrs.items():
            if attr not in ['amount_due', 'amount_due_at']:
                self.assertEqual(
                    response.data[attr],
                    expected_value
                )

        self.assertEqual(
            response.data['status'],
            'pending'
        )


class CashCollectorListCompletedTasksTestCase(APITestCase):
    def setUp(self) -> None:
        self.cash_collector = User.objects.create_user(**{
            'email': 'mahmoudtotti120@gmail.com',
            'password': 'anatotti',
            'is_cash_collector': True
        })
        refresh = RefreshToken.for_user(self.cash_collector)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    def test_list_completed_tasks(self):
        url = reverse('cash_collector_tasks')
        tasks_count = Task.objects.filter(cash_collector=self.cash_collector, status='completed').count()
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], tasks_count)
        self.assertEqual(len(response.data['results']), tasks_count)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])


class CashCollectorNextTaskTestCase(APITestCase):
    def setUp(self) -> None:
        self.cash_collector = User.objects.create_user(**{
            'email': 'mahmoudtotti120@gmail.com',
            'password': 'anatotti',
            'is_cash_collector': True
        })
        refresh = RefreshToken.for_user(self.cash_collector)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    def test_get_next_task(self):
        url = reverse('cash_collector_next_task')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data['amount_due'])
        self.assertIsNone(response.data['amount_due_at'])


class CashCollectorStatusTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # create admin account, token for this account
        cls.admin = User.objects.create_superuser(
            email='admin@gmail.com',
            password='admin',
        )
        admin_refresh = RefreshToken.for_user(cls.admin)
        cls.admin_access_token = str(admin_refresh.access_token)

        # create cash collector account, token for this account
        cls.cash_collector = User.objects.create_user(**{
            'email': 'mahmoudtotti120@gmail.com',
            'password': 'anatotti',
            'is_cash_collector': True
        })
        cash_collector_refresh = RefreshToken.for_user(cls.cash_collector)
        cls.cash_collector_access_token = str(cash_collector_refresh.access_token)

    def test_get_status_by_cash_collector(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.cash_collector_access_token)
        cash_collector_status = 'Frozen' if self.cash_collector.is_frozen else 'Not Frozen'
        url = reverse('collector_status', kwargs={'pk': self.cash_collector.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], cash_collector_status)

    def test_get_status_by_manager(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        cash_collector_status = 'Frozen' if self.cash_collector.is_frozen else 'Not Frozen'
        url = reverse('collector_status', kwargs={'pk': self.cash_collector.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], cash_collector_status)


class CashCollectorCollectCashTestCase(APITestCase):
    def setUp(self) -> None:
        # create cash collector account, token for this account
        self.cash_collector = User.objects.create_user(**{
            'email': 'mahmoudtotti120@gmail.com',
            'password': 'anatotti',
            'is_cash_collector': True
        })
        refresh = RefreshToken.for_user(self.cash_collector)
        access_token = str(refresh.access_token)

        # create customer record
        self.customer = Customer.objects.create(**{
            "name": "Eman Mohammed",
            "address": "Cairo,Egypt"
        })

        # create cash collector task
        self.task = Task.objects.create(**{
            "customer": self.customer,
            "cash_collector": self.cash_collector,
            'added_by': self.cash_collector,
            "amount_due": 5000,
            "amount_due_at": timezone.now()
        })
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    def test_collect_cash(self):
        url = reverse('collect_cash', kwargs={'pk': self.cash_collector.pk})
        response = self.client.put(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'collected')
        self.assertNotEqual(response.data['status'], self.task.status)
        self.assertNotEqual(response.data['collected_at'], self.task.collected_at)


class CashCollectorDeliverCashTestCase(APITestCase):
    def setUp(self) -> None:
        # create cash collector account, token for this account
        self.cash_collector = User.objects.create_user(**{
            'email': 'mahmoudtotti120@gmail.com',
            'password': 'anatotti',
            'is_cash_collector': True
        })
        refresh = RefreshToken.for_user(self.cash_collector)
        access_token = str(refresh.access_token)

        # create admin account
        self.admin = User.objects.create_superuser(
            email='admin@gmail.com',
            password='admin',
        )

        # create customer record
        self.customer = Customer.objects.create(**{
            "name": "Eman Mohammed",
            "address": "Cairo,Egypt"
        })

        # create cash collector task
        self.task = Task.objects.create(**{
            "customer": self.customer,
            "cash_collector": self.cash_collector,
            'status': 'collected',
            'added_by': self.cash_collector,
            "amount_due": 5000,
            "amount_due_at": timezone.now(),
            "collected_at": timezone.now(),
        })
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    def test_collect_cash(self):
        url = reverse('pay_cash_to_manager')
        tasks_to_deliver = {
            "cash_collector": 1,
            "manager": 2,
            "tasks": [1]
        }
        response = self.client.post(url, tasks_to_deliver, format='json')
        self.assertEqual(response.status_code, 200)


class CashCollectorRecordsTestCase(APITestCase):
    def setUp(self) -> None:
        # create admin account
        self.admin_account = User.objects.create_superuser(
            email='admin@gmail.com',
            password='admin',
        )
        refresh = RefreshToken.for_user(self.admin_account)
        access_token = str(refresh.access_token)

        # create cash collector account, token for this account
        self.cash_collector = User.objects.create_user(**{
            'email': 'mahmoudtotti120@gmail.com',
            'password': 'anatotti',
            'is_cash_collector': True
        })

        # create collection record
        self.record = CollectionRecord.add_record(self.cash_collector, 5000.00, 'Not Frozen')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    def test_list_cash_collector_records(self):
        url = reverse('cash_collector_records', kwargs={'pk': self.cash_collector.pk})
        collection_records_count = CollectionRecord.objects.count()
        date_filter = {
            "date_from": "2024-07-20 15:24:48.253872",
            "date_to": "2024-08-14 15:24:48.253872"
        }
        response = self.client.post(url, date_filter, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], collection_records_count)
        self.assertEqual(len(response.data['results']), collection_records_count)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])


class CashCollectorRecordsTestCase(APITestCase):
    def setUp(self) -> None:
        # create admin account
        self.admin_account = User.objects.create_superuser(
            email='admin@gmail.com',
            password='admin',
        )
        refresh = RefreshToken.for_user(self.admin_account)
        access_token = str(refresh.access_token)

        # create cash collector account, token for this account
        self.cash_collector = User.objects.create_user(**{
            'email': 'mahmoudtotti120@gmail.com',
            'password': 'anatotti',
            'is_cash_collector': True
        })

        # create collection record
        self.record = CollectionRecord.add_record(self.cash_collector, 5000.00, 'Not Frozen')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    def test_list_cash_collector_records(self):
        url = reverse('cash_collector_records', kwargs={'pk': self.cash_collector.pk})
        collection_records_count = CollectionRecord.objects.count()
        date_filter = {
            "date_from": "2024-07-20 15:24:48.253872",
            "date_to": "2024-08-14 15:24:48.253872"
        }
        response = self.client.post(url, date_filter, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], collection_records_count)
        self.assertEqual(len(response.data['results']), collection_records_count)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])