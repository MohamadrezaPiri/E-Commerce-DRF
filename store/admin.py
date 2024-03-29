from django.contrib import admin, messages
from django.db.models.aggregates import Count, Sum
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models
from .filters import InventoryFilter, ProductsCountFilter, OrdersCountFilter, ReviewsCountFilter, OrderItemsCountFilter


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug': ['title']
    }
    actions = ['clear_inventory', 'delete_reviews']
    list_display = ['title', 'unit_price',
                    'inventory_status', 'collection', 'ordered_times', 'reviews_count']
    list_editable = ['unit_price']
    list_filter = ['collection', 'last_update',
                   InventoryFilter, ReviewsCountFilter]
    list_per_page = 10
    list_select_related = ['collection']
    search_fields = ['title']

    @admin.display(ordering='collection')
    def collection(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'

    @admin.display(ordering='ordered_times')
    def ordered_times(self, product):
        return product.ordered_times

    @admin.display(ordering='reviews_count')
    def reviews_count(self, product):
        url = (
            reverse('admin:store_reviews_changelist')
            + '?'
            + urlencode({
                'product__id': str(product.id)
            }))
        return format_html('<a href="{}">{}</a>', url, product.reviews_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            ordered_times=Count('orderitem'),
            reviews_count=Count('reviews')
        )

    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} products were successfully updated.',
            messages.ERROR
        )

    @admin.action(description='Delete reviews')
    def delete_reviews(self, request, queryset):
        total_reviews_count = sum(product.reviews.count()
                                  for product in queryset)

        for product in queryset:
            product.reviews.all().delete()

        self.message_user(
            request,
            f'{total_reviews_count} were successfully deleted.',
            messages.SUCCESS
        )


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    list_filter = [ProductsCountFilter]
    list_per_page = 10
    autocomplete_fields = ['featured_product']
    search_fields = ['title']
    actions = ['delete_products']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({
                'collection__id': str(collection.id)
            }))
        return format_html('<a href="{}">{} Products</a>', url, collection.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('products')
        )

    @admin.action(description="Delete products")
    def delete_products(self, request, queryset):
        total_products_count = sum(collection.products.count()
                                   for collection in queryset)

        for collection in queryset:
            collection.products.all().delete()

        self.message_user(
            request,
            f'{total_products_count} were successfully deleted',
            messages.SUCCESS
        )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name',
                    'last_name',  'membership', 'orders']
    list_select_related = ['user']
    list_editable = ['membership']
    list_filter = ['membership', OrdersCountFilter]
    list_per_page = 10
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['user__username']
    autocomplete_fields = ['user']

    @admin.display(ordering='orders_count')
    def orders(self, customer):
        url = (
            reverse('admin:store_order_changelist')
            + '?'
            + urlencode({
                'customer__id': str(customer.id)
            }))
        return format_html('<a href="{}">{} Orders</a>', url, customer.orders_count)

    def username(self, customer):
        url = (
            reverse('admin:user_user_changelist')
            + '?'
            + urlencode({
                'customer__id': str(customer.id)
            }))
        return format_html('<a href="{}">{}</a>', url, customer.user)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders_count=Count('order')
        )


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'placed_at', '_customer',
                    'payment_status', 'items_count']
    list_filter = ['customer__user', 'payment_status', OrderItemsCountFilter]
    list_select_related = ['customer__user']
    list_per_page = 10
    autocomplete_fields = ['customer']
    search_fields = ['customer__user__username']
    inlines = [OrderItemInline]

    @admin.display(ordering='customer')
    def _customer(self, order):
        url = (
            reverse('admin:store_customer_changelist')
            + '?'
            + urlencode({
                'order__id': str(order.id)
            }))
        return format_html('<a href="{}">{}</a>', url, order.customer.user.username)

    @admin.display(ordering='items_count')
    def items_count(self, order):
        return order.items_count

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(items_count=Count('items'))


@admin.register(models.Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ['user', '_product', 'date']
    list_select_related = ['user', 'product']
    list_filter = ['user']
    list_per_page = 10
    search_fields = ['user__username', 'product__title']
    autocomplete_fields = ['user', 'product']

    @admin.display(ordering='product')
    def _product(self, reviews):
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({
                'reviews__id': str(reviews.id)
            }))
        return format_html('<a href="{}">{}</a>', url, reviews.product.title)


@admin.register(models.Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['street', 'city', '_customer']
    list_filter = ['city', 'customer__user__username']
    list_select_related = ['customer__user']
    list_per_page = 10
    autocomplete_fields = ['customer']
    search_fields = ['customer__user__username']

    def _customer(self, address):
        url = (
            reverse('admin:store_customer_changelist')
            + '?'
            + urlencode({
                'address__id': str(address.id)
            }))
        return format_html('<a href="{}">{}</a>', url, address.customer.user.username)
