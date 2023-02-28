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


@pytest.fixture
def update_review(api_client):
    def do_update_review(product_id, review_id, review):
        return api_client.put(f'/products/{product_id}/reviews/{review_id}/', review)
    return do_update_review


@pytest.fixture
def delete_review(api_client):
    def do_delete_review(product_id, review_id):
        return api_client.delete(f'/products/{product_id}/reviews/{review_id}/')
    return do_delete_review


@pytest.mark.django_db
class TestCreateReview:
    def test_if_user_is_anonymous_returns_401(self, create_review):
        product = baker.make(Product)

        response = create_review(product_id=product.id, review={
            'description': 'aa'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_data_is_invalid_returns_400(self, create_review, authenticate):
        product = baker.make(Product)
        user = baker.make(User)

        authenticate(user=user)
        response = create_review(product_id=product.id, review={
            'description': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_data_is_valid_returns_201(self, create_review, authenticate):
        user = baker.make(User)
        product = baker.make(Product)

        authenticate(user=user)
        response = create_review(product_id=product.id, review={
            'description': 'aa'})

        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestUpdateReview:
    def test_if_user_is_anonymous_returns_401(self, update_review):
        review = baker.make(Reviews)

        response = update_review(
            product_id=review.product.id,
            review_id=review.id,
            review={'description': 'aa'}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_author_returns_403(self, update_review, authenticate):
        author = baker.make(User)
        user = baker.make(User)
        review = baker.make(Reviews, user=author)

        authenticate(user=user)
        response = update_review(
            product_id=review.product.id,
            review_id=review.id,
            review={'description': 'aa'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, update_review, authenticate):
        user = baker.make(User)
        review = baker.make(Reviews, user=user)

        authenticate(user=user)
        response = update_review(
            product_id=review.product.id,
            review_id=review.id,
            review={'description': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_user_is_admin_returns_200(self, update_review, authenticate):
        author = baker.make(User)
        admin = baker.make(User, is_staff=True)
        review = baker.make(Reviews, user=author)

        authenticate(user=admin)
        response = update_review(
            product_id=review.product.id,
            review_id=review.id,
            review={'description': 'aa'})

        assert response.status_code == status.HTTP_200_OK

    def test_if_data_is_valid_returns_200(self, update_review, authenticate):
        user = baker.make(User)
        review = baker.make(Reviews, user=user)

        authenticate(user=user)
        response = update_review(
            product_id=review.product.id,
            review_id=review.id,
            review={'description': 'a'})

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestDeleteReview:
    def test_if_user_is_anonymous_returns_401(self, delete_review):
        review = baker.make(Reviews)

        response = delete_review(
            product_id=review.product.id,
            review_id=review.id
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_author_returns_403(self, delete_review, authenticate):
        author = baker.make(User)
        user = baker.make(User)
        review = baker.make(Reviews, user=author)

        authenticate(user=user)
        response = delete_review(
            product_id=review.product.id,
            review_id=review.id
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_returns_204(self, delete_review, authenticate):
        author = baker.make(User)
        admin = baker.make(User, is_staff=True)
        review = baker.make(Reviews, user=author)

        authenticate(user=admin)
        response = delete_review(
            product_id=review.product.id,
            review_id=review.id
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_if_user_is_author_returns_204(self, delete_review, authenticate):
        author = baker.make(User)
        review = baker.make(Reviews, user=author)

        authenticate(user=author)
        response = delete_review(
            product_id=review.product.id,
            review_id=review.id
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestGetReviewsList:
    def test_if_there_is_no_review_for_product_returns_404(self, api_client):
        product = baker.make(Product)

        response = api_client.get(f'/products/{product.id}/reviews/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_there_is_no_product_with_given_id_returns_404(self, api_client):

        response = api_client.get('/products/1/reviews/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_returns_200(self, api_client):
        product = baker.make(Product)
        review = baker.make(Reviews, product=product)

        response = api_client.get(f'/products/{product.id}/reviews/')

        assert response.status_code == status.HTTP_200_OK
