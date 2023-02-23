import pytest
from user.models import User
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticate(api_client):
    def do_authenticate(user=User):
        return api_client.force_authenticate(user=user)
    return do_authenticate
