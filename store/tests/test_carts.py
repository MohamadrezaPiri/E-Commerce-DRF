import pytest
from model_bakery import baker
from rest_framework import status
from store.models import Cart


@pytest.mark.django_db
class TestCreateCart:
    def test_if_post_request_is_sent_returns_201(self, api_client):

        response = api_client.post('/carts/')

        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestDeleteCart:
    def test_if_delete_request_is_sent_returns_204(self, api_client):
        cart = baker.make(Cart)
        response = api_client.delete(f'/carts/{cart.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
