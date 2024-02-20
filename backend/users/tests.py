from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient
from users.models import Account

class TestAccounts(APITestCase):
    def setUp(self):
        account = Account.objects.create_user(
            email='samsung@beeline.com',
            password='MagicPass123',
            type='shop',
            is_active=True)
        account.save()
        self.account_token = Token.objects.create(user=account)

    def test_account_register_valid(self):
        url = '/api/v1/user/register'
        data = {
            "first_name": "Ivan",
            "email": "grrove@promodj.ru",
            "password": "SUperUserPass123"
        }
        response = self.client.post(url, data, format='json')
        r = response.json()
        # print(response.status_code, r)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Account.objects.count(), 2)

        data = {
            'token': r['token'],
            'uid': r['uid']
        }
        url = '/api/v1/user/confirm'
        response = self.client.post(url, data, format='json')
        r = response.json()
        print(response.status_code, r)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(url, {}, format='json')
        r = response.json()
        print(response.status_code, r)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url, {'token':'', 'uid':''}, format='json')
        r = response.json()
        print(response.status_code, r)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)




    def test_account_register_badrequest(self):
        url = '/api/v1/user/register'
        data = {
            "first_name": "Ivan",
            "password": "SUperUserPass123"
        }
        response = self.client.post(url, data, format='json')
        # print(response.json())
        print(response.status_code)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Account.objects.count(), 1)

    def test_account_register_invalid(self):
        url = '/api/v1/user/register'
        data = {
            'email': 'Petrov',
            "first_name": "Ivan",
            "password": "SUperUserPass123"
        }
        response = self.client.post(url, data, format='json')
        # print(response.json())
        print(response.status_code)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Account.objects.count(), 1)

    def test_account_register_badpassword(self):
        url = '/api/v1/user/register'
        data = {
            "first_name": "Ivan",
            "email": "grrove@promodj.ru",
            "password": "123456"
        }
        response = self.client.post(url, data, format='json')
        # print(response.json())
        print(response.status_code)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Account.objects.count(), 1)

    def test_account_login_valid(self):
        url = '/api/v1/user/login'
        data = {
            'email': 'samsung@beeline.com',
            'password': 'MagicPass123'
        }
        response = self.client.post(url, data, format='json')
        r = response.json()
        # print(response.status_code, r)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_account_login_invalid(self):
        url = '/api/v1/user/login'
        data = {
            'email': 'samsung@beeline.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        r = response.json()
        print(response.status_code, r)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        data = {
            'email': 'samsung@beeline.com'

        }
        response = self.client.post(url, data, format='json')
        r = response.json()
        print(response.status_code, r)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

