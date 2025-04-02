from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'items', views.InventoryItemViewSet, basename='items')
router.register(r'logs', views.InventoryLogViewSet, basename='logs')
router.register(r'suppliers', views.SupplierViewSet, basename='suppliers')
router.register(r'item-suppliers', views.InventoryItemSupplierViewSet, basename='item-suppliers')


urlpatterns = [
    path('', include(router.urls)),
    path('api/inventory/', include(router.urls)),
]