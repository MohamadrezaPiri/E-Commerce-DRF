import pytest
from model_bakery import baker
from rest_framework import status
from user.models import User
from store.models import Collection, Product


@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post('/collections/', collection)
    return do_create_collection


@pytest.fixture
def update_collection(api_client):
    def do_update_collection(collection_id, collection):
        return api_client.put(f'/collections/{collection_id}/', collection)
    return do_update_collection


@pytest.fixture
def delete_collection(api_client):
    def do_delete_collection(collection_id):
        return api_client.delete(f'/collections/{collection_id}/')
    return do_delete_collection


@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_is_anonymous_returns_401(self, create_collection):

        response = create_collection({"title": 'a'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, create_collection, authenticate):
        user = baker.make(User)

        authenticate(user=user)
        response = create_collection({"title": 'a'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_not_valid_returns_400(self, create_collection, authenticate):
        admin = baker.make(User, is_staff=True)

        authenticate(user=admin)
        response = create_collection({"title": ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_data_is_valid_returns_201(self, create_collection, authenticate):
        admin = baker.make(User, is_staff=True)

        authenticate(user=admin)
        response = create_collection({"title": 'a'})

        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestUpdateCollection:
    def test_if_user_is_anonymous_returns_401(self, update_collection):
        collection = baker.make(Collection)

        response = update_collection(collection.id, {"title": 'a'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, update_collection, authenticate):
        collection = baker.make(Collection)
        user = baker.make(User)

        authenticate(user=user)
        response = update_collection(collection.id, {"title": 'a'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_not_valid_returns_400(self, update_collection, authenticate):
        collection = baker.make(Collection)
        admin = baker.make(User, is_staff=True)

        authenticate(user=admin)
        response = update_collection(collection.id, {"title": ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_data_is_valid_returns_200(self, update_collection, authenticate):
        collection = baker.make(Collection)
        admin = baker.make(User, is_staff=True)

        authenticate(user=admin)
        response = update_collection(collection.id, {"title": 'a'})

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestDeleteCollection:
    def test_if_user_is_anonymous_returns_401(self, delete_collection):
        collection = baker.make(Collection)

        response = delete_collection(collection.id)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, delete_collection, authenticate):
        collection = baker.make(Collection)
        user = baker.make(User)

        authenticate(user=user)
        response = delete_collection(collection.id)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_collection_contains_products_returns_405(self, delete_collection, authenticate):
        collection = baker.make(Collection)
        product = baker.make(Product, collection=collection)
        admin = baker.make(User, is_staff=True)

        authenticate(user=admin)
        response = delete_collection(collection.id)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_if_user_is_admin_returns_204(self, delete_collection, authenticate):
        collection = baker.make(Collection)
        admin = baker.make(User, is_staff=True)

        authenticate(user=admin)
        response = delete_collection(collection.id)

        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestGetCollectionsList:
    def test_if_returns_200(self, api_client):

        response = api_client.get('/collections/')

        assert response.status_code == status.HTTP_200_OK
