import pytest
from model_bakery import baker
from rest_framework import status
from user.models import User


@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post('/collections/', collection)
    return do_create_collection


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
