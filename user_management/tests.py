from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from user_management.models import User


# Create your tests here.
class UserRegisterTestCase(APITestCase):
    def test_register_user(self):
        initial_users_count = User.objects.count()
        user_attrs = {
            "first_name": "Mahmoud",
            "last_name": "Bayoumi",
            "email": "mahmoudtotti120@gmail.com",
            "password": "anatotti"
        }
        url = reverse('user_registration')
        response = self.client.post(url, user_attrs)
        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            User.objects.count(),
            initial_users_count + 1
        )

        self.assertEqual(
            response.data['status'],
            'success'
        )


class SuperUserCreateTestCase(APITestCase):
    def test_create_user(self):
        initial_users_count = User.objects.count()
        user_attrs = {
            "first_name": "Ahmed",
            "last_name": "Ali",
            "email": "admin@admin.com",
            "password": "admin"
        }
        user = User.objects.create_superuser(**user_attrs)
        self.assertEqual(
            User.objects.count(),
            initial_users_count + 1
        )

        for attr, expected_value in user_attrs.items():
            if attr != 'password':
                self.assertEqual(
                    getattr(user, attr),
                    expected_value
                )

        self.assertEqual(
            user.is_manager,
            True
        )


class UserLoginTestCase(APITestCase):

    def setUp(self) -> None:
        email = 'mahmoudtotti120@gmail.com'
        password = 'anatotti'
        User.objects.create_user(
            email=email,
            password=password
        )

    def test_login_user(self):
        user_attrs = {
            'email': 'mahmoudtotti120@gmail.com',
            'password': 'anatotti'
        }
        url = reverse('login')
        response = self.client.post(url, user_attrs, format='json')
        self.assertEqual(response.status_code, 200)


class UserLogoutTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        email = 'mahmoudtotti120@gmail.com'
        password = 'anatotti'
        user = User.objects.create_user(
            email=email,
            password=password
        )
        refresh = RefreshToken.for_user(user)
        cls.refresh_token = str(refresh)
        cls.access_token = str(refresh.access_token)

    def test_logout_user(self):
        url = reverse('logout')
        refresh_token = {
            'refresh_token': self.refresh_token
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(url, refresh_token)
        self.assertEqual(response.status_code, 205)


class UserListStatusTestCase(APITestCase):

    def setUp(self):
        email = 'admin@admin.com'
        password = 'admin'
        # create admin user to be used in authorization
        self.admin_user = User.objects.create_superuser(email=email, password=password)
        refresh = RefreshToken.for_user(self.admin_user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    def test_list_users_status(self):
        users_count = User.objects.exclude(id=self.admin_user.id).count()
        url = reverse('get_user_status')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], users_count)
        self.assertEqual(len(response.data['results']), users_count)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
