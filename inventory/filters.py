from django_filters import rest_framework as filters
from .models import InventoryItem

class InventoryItemFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    low_stock = filters.NumberFilter(field_name="quantity", lookup_expr='lte')
    category = filters.CharFilter(field_name="category__name", lookup_expr='icontains')
    
    class Meta:
        model = InventoryItem
        fields = ['category', 'location', 'min_price', 'max_price', 'low_stock']
                      
        