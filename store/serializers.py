from django.core.validators import MinValueValidator
from django.db import transaction
from decimal import Decimal
from rest_framework import serializers
from .models import Product, Collection, Reviews, Cart, CartItem, Customer, Order, OrderItem


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'unit_price',
                  'price_with_tax', 'inventory', 'collection']

    price_with_tax = serializers.SerializerMethodField(
        method_name="get_price_with_tax")

    def get_price_with_tax(self, product: Product):
        TAX = 1.1
        return product.unit_price * Decimal(TAX)


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.SerializerMethodField(
        method_name="get_products_count")

    def get_products_count(self, collection: Collection):
        return collection.products.count()


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ['id', 'user_id', 'description']

    def create(self, validated_data):
        user_id = self.context['user_id']
        product_id = self.context['product_id']
        return Reviews.objects.create(product_id=product_id, user_id=user_id, **validated_data)


class CartItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

    product = CartItemProductSerializer()
    total_price = serializers.SerializerMethodField(
        method_name="get_total_price")

    def get_total_price(self, cartiem: CartItem):
        return cartiem.quantity * cartiem.product.unit_price


class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['cart_id', 'product_id', 'quantity']

    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        ERROR_NO_PRODUCT = serializers.ValidationError(
            "There is no product with given ID")

        if not Product.objects.filter(pk=value).exists():
            raise ERROR_NO_PRODUCT
        return value

    def save(self, **kwargs):
        VALIDATED = self.validated_data
        INSTANCE = self.instance

        product_id = VALIDATED['product_id']
        quantity = VALIDATED['quantity']
        cart_id = self.context['cart_id']
        try:
            cartitem = CartItem.objects.get(
                product_id=product_id, cart_id=cart_id)
            cartitem.quantity += quantity
            cartitem.save()
            INSTANCE = cartitem
        except CartItem.DoesNotExist:
            cartitem = CartItem.objects.create(cart_id=cart_id, **VALIDATED)
            cartitem.save()
            INSTANCE = cartitem
        return INSTANCE


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']

    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(
        method_name="get_total_price")

    def get_total_price(self, cart: Cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']

    user_id = serializers.IntegerField(read_only=True)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']

    product = CartItemProductSerializer()
    unit_price = serializers.SerializerMethodField()

    def get_unit_price(self, orderitem: OrderItem):
        return orderitem.product.unit_price * orderitem.quantity


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer', 'payment_status', 'placed_at', 'items']

    items = OrderItemSerializer(many=True)


class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['cart_id']

    cart_id = serializers.UUIDField()

    def validate_cart_id(self, value):
        error_no_cart = serializers.ValidationError(
            "No cart with given ID was found")
        error_empty_cart = serializers.ValidationError(
            "This shopping cart is empty")
        minimum_cart_items = 1

        if not Cart.objects.filter(id=value).exists():
            raise error_no_cart
        elif CartItem.objects.filter(cart_id=value).count() < minimum_cart_items:
            raise error_empty_cart
        return value

    def save(self):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            user_id = self.context['user_id']

            (customer, created) = Customer.objects.get_or_create(user_id=user_id)
            order = Order.objects.create(customer=customer)

            cartitems = CartItem.objects.filter(cart_id=cart_id)
            orderitems = [OrderItem(order=order,
                                    product=item.product,
                                    quantity=item.quantity,
                                    unit_price=item.product.unit_price) for item in cartitems]

            OrderItem.objects.bulk_create(orderitems)

            Cart.objects.filter(id=cart_id).delete()

            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']
