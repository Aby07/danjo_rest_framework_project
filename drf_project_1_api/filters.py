import django_filters
from .models import Product, Order

class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            'name': ['exact', 'contains'],
            'price': ['exact', 'gt', 'lt', 'range'],
        }


class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = {
            'status': ['exact'],
            'created_at': ['exact', 'gt', 'lt'],
        }
