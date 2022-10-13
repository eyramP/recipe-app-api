"""
Test for recipe APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def create_recipe(user, **params):
    """Create and return a simple recipe."""
    defaults = {
        'title': 'Simple recipe title.',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user, **defaults)
    return recipe


class PublicRecipeAPITest(TestCase):
    """Test unauthenticated API request."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        result = self.client.get(RECIPE_URL)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe(self):
        """Test retrieving recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        result = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_recipe_list_limited_user(self):
        """Test list of recipes is limited to authenticated usr."""
        other_user = get_user_model().objects.create_user(
            'other_user@example.com',
            'password123'
        )
        create_recipe(usdr=other_user)
        create_recipe(user=self.user)

        result = self.client.get(RECIPE_URL)

        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(result.sttus_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
