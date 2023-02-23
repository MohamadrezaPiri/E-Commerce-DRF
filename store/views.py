from django.shortcuts import get_object_or_404
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import api_view, action
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from .serializers import OrderSerializer, UpdateOrderSerializer, CreateOrderSerializer, ProductSerializer, CollectionSerializer, CustomerSerializer, ReviewSerializer, CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer
from .models import Product, Collection, Reviews, Cart, CartItem, Customer, Order, OrderItem
from .filters import ProductFilters
from .permissions import IsAdminOrReadOnly

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
        NOT_ALLOWED = status.HTTP_405_METHOD_NOT_ALLOWED
        NO_CONTENT = status.HTTP_204_NO_CONTENT
        MINIMUM_ORDER_ITEMS = 1

        product = get_object_or_404(Product, pk=pk)
        if product.orderitem_set.count() >= MINIMUM_ORDER_ITEMS:
            return Response(status=NOT_ALLOWED)
        product.delete()
        return Response(status=NO_CONTENT)


class CollectionsViewSet(ModelViewSet):
    queryset = Collection.objects.prefetch_related('products').all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, pk):
        NOT_ALLOWED = status.HTTP_405_METHOD_NOT_ALLOWED
        NO_CONTENT = status.HTTP_204_NO_CONTENT
        MINIMUM_PRODUCTS_COUNT = 1

        collection = Collection.objects.get(pk=pk)
        if collection.products.count() >= MINIMUM_PRODUCTS_COUNT:
            return Response(status=NOT_ALLOWED)
        collection.delete()
        return Response(status=NO_CONTENT)


class ReviewsViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs["product_pk"]
        return Reviews.objects.filter(product_id=product_id)

    def get_serializer_context(self):
        return {"product_id": self.kwargs['product_pk']}


class CartViewset(RetrieveModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer


class CariItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        METHOD = self.request.method

        if METHOD == "POST":
            return AddCartItemSerializer
        elif METHOD == "PATCH":
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
        METHOD = self.request.method
        USER = request.user
        DATA = request.data

        (customer, created) = Customer.objects.get_or_create(user_id=USER.id)
        if METHOD == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif METHOD == "PUT":
            serializer = CustomerSerializer(customer, data=DATA)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        METHOD = self.request.method
        if METHOD == "POST":
            return CreateOrderSerializer
        elif METHOD == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        USER = self.request.user
        if USER.is_staff:
            return Order.objects.all()

        (customer_id, created) = Customer.objects.only(
            'id').get_or_create(user_id=USER.id)
        return Order.objects.filter(customer_id=customer_id)

    def get_permissions(self):
        METHOD = self.request.method
        if METHOD in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request):
        CONTEXT = {'user_id': self.request.user.id}
        DATA = request.data
        serializer = CreateOrderSerializer(data=DATA, context=CONTEXT)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)
