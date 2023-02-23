import pytest
from user.models import User
from rest_framework import status
from model_bakery import baker
from store.models import Product, Collection


@pytest.fixture
def create_product(api_client):
    def do_create_product(product):
        return api_client.post('/products/', product)
    return do_create_product


@pytest.mark.django_db
class TestCreateProduct:
    def test_if_user_is_anonymous_returns_401(self, create_product):
        collection = baker.make(Collection)

        response = create_product({'title': 'a', 'description': 'aa',
                                  'unit_price': 22.00, 'inventory': 10, 'collection': collection})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, create_product, authenticate):
        collection = baker.make(Collection)
        user = baker.make(User)

        authenticate(user=user)
        response = create_product({'title': 'a', 'description': 'aa',
                                  'unit_price': 22.00, 'inventory': 10, 'collection': collection})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_returns_201(self, create_product, authenticate):
        collection = baker.make(Collection)
        user = baker.make(User, is_staff=True)

        authenticate(user=user)
        response = create_product({"title": 'a', "description": 'aa',
                                  "unit_price": 22.00, "inventory": 10, "collection": collection.id})

        assert response.status_code == status.HTTP_201_CREATED

    def test_if_data_is_invalid_returns_400(self, create_product, authenticate):
        collection = baker.make(Collection)
        user = baker.make(User, is_staff=True)

        authenticate(user=user)
        response = create_product({"title": '', "description": 'aa',
                                  "unit_price": 20, "inventory": 10, "collection": collection.id})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
