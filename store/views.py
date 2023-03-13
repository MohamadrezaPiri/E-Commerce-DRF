from django.shortcuts import get_object_or_404
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import api_view, action
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from .serializers import OrderSerializer, UpdateOrderSerializer, CreateOrderSerializer, ProductSerializer, CollectionSerializer, CustomerSerializer, ReviewSerializer, CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer
from .models import Product, Collection, Reviews, Cart, CartItem, Customer, Order, OrderItem
from .filters import ProductFilters
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly

# Create your views here.


class ProductsViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = PageNumberPagination
    filterset_class = ProductFilters
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = ['unit_price']
    search_fields = ['title', 'description']

    def destroy(self, request, pk):
        not_allowed = status.HTTP_405_METHOD_NOT_ALLOWED
        no_content = status.HTTP_204_NO_CONTENT
        minimum_order_items = 1

        product = get_object_or_404(Product, pk=pk)
        if product.orderitem_set.count() >= minimum_order_items:
            return Response(status=not_allowed)
        product.delete()
        return Response(status=no_content)


class CollectionsViewSet(ModelViewSet):
    queryset = Collection.objects.prefetch_related('products').all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, pk):
        not_allowed = status.HTTP_405_METHOD_NOT_ALLOWED
        no_content = status.HTTP_204_NO_CONTENT
        minimum_products_count = 1

        collection = Collection.objects.get(pk=pk)
        if collection.products.count() >= minimum_products_count:
            return Response(status=not_allowed)
        collection.delete()
        return Response(status=no_content)


class ReviewsViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        product_id = self.kwargs["product_pk"]
        review = Reviews.objects.filter(product_id=product_id)

        if review.exists():
            return review
        else:
            raise NotFound('There is no product or review')

    def get_serializer_context(self):
        return {"product_id": self.kwargs['product_pk'], "user_id": self.request.user.id}


class CartViewset(RetrieveModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer


class CariItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        method = self.request.method

        if method == "POST":
            return AddCartItemSerializer
        elif method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        cart_id = self.kwargs['cart_pk']
        return CartItem.objects.filter(cart_id=cart_id).select_related('product')


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        method= self.request.method
        user = request.user
        data = request.data

        (customer, created) = Customer.objects.get_or_create(user_id=user.id)
        if method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif method == "PUT":
            serializer = CustomerSerializer(customer, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        method = self.request.method
        if method == "POST":
            return CreateOrderSerializer
        elif method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()

        (customer_id, created) = Customer.objects.only(
            'id').get_or_create(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)

    def get_permissions(self):
        method = self.request.method
        if method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request):
        context = {'user_id': self.request.user.id}
        data = request.data
        
        serializer = CreateOrderSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)
