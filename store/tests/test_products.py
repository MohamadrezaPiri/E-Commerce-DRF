import pytest
from user.models import User
from rest_framework import status
from model_bakery import baker
from store.models import Product, Collection, OrderItem


@pytest.fixture
def create_product(api_client):
    def do_create_product(product):
        return api_client.post('/products/', product)
    return do_create_product


@pytest.fixture
def update_product(api_client):
    def do_update_product(product_id, product):
        return api_client.put(f'/products/{product_id}/', product)
    return do_update_product


@pytest.fixture
def delete_product(api_client):
    def do_delete_product(product_id):
        return api_client.delete(f'/products/{product_id}/')
    return do_delete_product


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


@pytest.mark.django_db
class TestUpdateProduct:
    def test_if_user_is_anonymous_returns_401(self, update_product):
        product = baker.make(Product)

        response = update_product(product.id, {"title": 'a', "description": 'aa',
                                  "unit_price": 22.00, "inventory": 10, "collection": product.collection.id})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, update_product, authenticate):
        product = baker.make(Product)
        user = baker.make(User)

        authenticate(user=user)
        response = update_product(product.id, {"title": 'a', "description": 'aa',
                                  "unit_price": 22.00, "inventory": 10, "collection": product.collection.id})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_product_does_not_exist_returns_404(self, update_product, authenticate):
        admin = baker.make(User, is_staff=True)

        authenticate(user=admin)
        response = update_product(1, {"title": 'a', "description": 'aa',
                                      "unit_price": 22.00, "inventory": 10, "collection": 1})

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_data_is_not_valid_returns_400(self, update_product, authenticate):
        product = baker.make(Product)
        admin = baker.make(User, is_staff=True)

        authenticate(user=admin)
        response = update_product(product.id, {"title": '', "description": 'aa',
                                  "unit_price": 22.00, "inventory": 10, "collection": product.collection.id})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_user_is_admin_returns_200(self, update_product, authenticate):
        product = baker.make(Product)
        admin = baker.make(User, is_staff=True)

        authenticate(user=admin)
        response = update_product(product.id, {"title": 'a', "description": 'aa',
                                  "unit_price": 22.00, "inventory": 10, "collection": product.collection.id})

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestDeleteProduct:
    def test_if_user_is_anonymus_returns_401(self, delete_product):
        product = baker.make(Product)

        response = delete_product(product.id)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, delete_product, authenticate):
        product = baker.make(Product)
        user = baker.make(User)

        authenticate(user=user)
        response = delete_product(product.id)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_product_does_not_exist_returns_404(self, delete_product, authenticate):
        admin = baker.make(User, is_staff=True)

        authenticate(user=admin)
        response = delete_product(1)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_product_has_been_ordered_returns_405(self, delete_product, authenticate):
        product = baker.make(Product)
        orderitem = baker.make(OrderItem, product=product)
        admin = baker.make(User, is_staff=True)

        authenticate(user=admin)
        response = delete_product(product.id)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_user_is_admin_returns_204(self, delete_product, authenticate):
        product = baker.make(Product)
        admin = baker.make(User, is_staff=True)

        authenticate(user=admin)
        response = delete_product(product.id)

        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestGetProductsList:
    def test_if_returns_200(self, api_client):

        response = api_client.get('/products/')

        assert response.status_code == status.HTTP_200_OK
