import pytest
from rest_framework import status


@pytest.mark.django_db
class TestCreateCart:
    def test_if_post_request_is_sent_returns_201(self, api_client):

        response = api_client.post('/carts/')

        assert response.status_code == status.HTTP_201_CREATED
