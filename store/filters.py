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
