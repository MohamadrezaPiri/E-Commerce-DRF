from django_filters.rest_framework import FilterSet
from django.db.models.query import QuerySet
from django.db.models import Count
from django.contrib import admin
from .models import Product


class ProductFilters(FilterSet):
    class Meta:
        model = Product
        fields = {
            'collection_id': ['exact'],
            'unit_price': ['gt', 'lt']
        }


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low')
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)


class ProductsCountFilter(admin.SimpleListFilter):
    title = 'Products count'
    parameter_name = 'Products_count'

    def lookups(self, request, model_admin):
        return [
            ('0<', 'With product'),
            ('<1', 'Without product')
        ]

    def queryset(self, request, queryset: QuerySet):
        annotated_value = queryset.annotate(products_count=Count('products'))

        if self.value() == '0<':
            return annotated_value.filter(products_count__gt=0)
        elif self.value() == '<1':
            return annotated_value.filter(products_count__lt=1)


class OrdersCountFilter(admin.SimpleListFilter):
    title = 'Orders count'
    parameter_name = 'order_set'

    def lookups(self, request, model_admin):
        return [
            ('0<', 'With order'),
            ('<1', 'Without order')
        ]

    def queryset(self, request, queryset: QuerySet):
        annotated_value = queryset.annotate(orders_count=Count('order'))

        if self.value() == '0<':
            return annotated_value.filter(orders_count__gt=0)
        elif self.value() == '<1':
            return annotated_value.filter(orders_count__lt=1)


class OrderItemsCountFilter(admin.SimpleListFilter):
    title = 'Items count'
    parameter_name = 'items'

    def lookups(self, request, model_admin):
        return [
            ('1<', 'More than one'),
            ('<2', 'One')
        ]

    def queryset(self, request, queryset: QuerySet):
        annotated_value = queryset.annotate(items_count=Count('items'))

        if self.value() == '1<':
            return annotated_value.filter(items_count__gt=1)
        elif self.value() == '<2':
            return annotated_value.filter(items_count__lt=2)


class ReviewsCountFilter(admin.SimpleListFilter):
    title = 'Reviews count'
    parameter_name = 'reviews'

    def lookups(self, request, model_admin):
        return [
            ('0<', 'With review'),
            ('<1', 'Without review')
        ]

    def queryset(self, request, queryset: QuerySet):
        annotated_value = queryset.annotate(reviews_count=Count('reviews'))

        if self.value() == '0<':
            return annotated_value.filter(reviews_count__gt=0)
        elif self.value() == '<1':
            return annotated_value.filter(reviews_count__lt=1)
