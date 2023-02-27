import pytest
from user.models import User
from rest_framework import status
from model_bakery import baker
from store.models import Reviews, Product


@pytest.fixture
def create_review(api_client):
    def do_create_review(product_id, review):
        return api_client.post(f'/products/{product_id}/reviews/', review)
    return do_create_review


@pytest.mark.django_db
class TestCreateReview:
    def test_if_user_is_anonymous_returns_401(self, create_review):
        product = baker.make(Product)

        response = create_review(product_id=product.id, review={
                                 'name': 'a', 'description': 'aa'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_data_is_invalid_returns_400(self, create_review, authenticate):
        product = baker.make(Product)
        user = baker.make(User)

        authenticate(user=user)
        response = create_review(product_id=product.id, review={
                                 'name': '', 'description': 'aa'})
        response2 = create_review(product_id=product.id, review={
                                  'name': 'a', 'description': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
