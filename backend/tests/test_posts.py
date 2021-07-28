import tempfile
import base64
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from api.models import Recipe, RecipeComponent, Tag, User, Ingredient
from PIL import Image
import io
import json


class TestPost(APITestCase):
    """
    Still doesn't work correctly
    """
    def setUp(self):
        """
        Common procedures and objects for futher usage
        """
        self.tag_1 = Tag.objects.create(name='breakfast', slug='breakfast')
        self.tag_2 = Tag.objects.create(name='lunch', slug='lunch')
        self.tag_3 = Tag.objects.create(name='dinner', slug='dinner')
        self.ingr_1 = Ingredient.objects.create(name='coffe', units='g')
        self.ingr_2 = Ingredient.objects.create(name='milk', units='l')
        # self.user = User.objects.create_user('john', 'johnsnow@winterfell.org', 'passwd')
        # self.client.force_login(self.user)
        self.factory = APIRequestFactory
        self.auth_headers = {}
        self.test_post = {
            'ingredients': [
                {'id': 1, 'amount': 25},
                {'id': 2, 'amount': 30}
            ],
            'tags': [
                self.tag_1.id,
                self.tag_2.id
            ],
            'name': 'A test post',
            'image': 'not an image',
            'text': 'Another test post',
            'cooking_time': 30
        }
        img = Image.new('RGB', (250, 250), color='blue')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        self.image = base64.b64encode(buffer.getvalue())

    def test_00user(self):
        user_data = {
            'email': "john@winterfell.org",
            'username': "john.snow",
            'first_name': "John",
            'last_name': "Snow",
            'password': "aQuarius_324"
        }

        response = self.client.post('/api/users/', user_data, format='json')
        # Вижу, что в redoc указан ответ 201, но Djoser отдает 204 и не думаю,
        # нужно переопределять ответ
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user_data = {
            'email': 'john@winterfell.org',
            'password': 'aQuarius_324'
        }
        response = self.client.post('/api/auth/token/login/', user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        try:
            self.token = response.data['auth_token']
        except KeyError:
            raise AssertionError("Didn't get auth token in response")
        token = json.loads(response.content)
        print(token['auth_token'])
        self.auth_headers = {
            'Authorization': 'Token ' + token['auth_token']
        }

    def test_create(self):
        url = '/api/recipes/'
        img = Image.new('RGB', (250, 250), color='blue')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        image = base64.b64encode(buffer.getvalue())
        data = {'ingredients': [
            {'id': self.ingr_1.id, 'amount': 25},
            {'id': self.ingr_2.id, 'amount': 30}
        ],
            'tags': [
                self.tag_1.id,
                self.tag_2.id
            ],
            'name': 'A test post',
            'text': 'Another test post',
            'image': image,
            'cooking_time': 30
        }
        response = self.client.post(
            url, data,format='json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_wrong_image(self):
        url = '/api/recipes/'
        data = {
            'ingredients': [
                {'id': 1, 'amount': 25},
                {'id': 2, 'amount': 30}
            ],
            'tags': [
                self.tag_1.id,
                self.tag_2.id
            ],
            'name': 'A test post',
            'image': 'not an image',
            'text': 'Another test post',
            'cooking_time': 30
        }
        response = self.client.post(url, data, format='json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pagination(self):
        url = '/api/recipes'
        for n in range(22):
            self.client.post(ur, self.test_post, self.auth_headers)
