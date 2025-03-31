from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .serializers import UserSerializer, CategorySerializer, InventoryItemSerializer, InventoryLogSerializer, SupplierSerializer, InventoryItemSupplierSerializer, InventoryItemCreateUpdateSerializer
from .models import Category, InventoryItem, Supplier, InventoryLog, InventoryItemSupplier
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsOwnerOrReadOnly, IsOwner



from rest_framework.views import APIView

class IndexView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        
        data = {
            "message": "Welcome to  Inventory Management System API!",
            "endpoints": {
                "users": "api/inventory/users/",
                "categories": "api/inventory/categories/",
                "items": "api/inventory/items/",
                "logs": "api/inventory/logs/",
                "suppliers": "api/inventory/suppliers/",
                "item-suppliers": "api/inventory/item-suppliers/",
            },
            "docs":  "Documentation coming soon!"
        }
        return Response(data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        elif self.action == 'retrieve': 
            return [IsAuthenticated()]
        return [IsAdminUser()]  # admin only for list and other actions
    
    def get_queryset(self):
        user = self.request.user 
        if user.is_staff: # If the user is an admin, return all users
            return User.objects.all()
        return User.objects.filter(id=user.id) # Otherwise, only return the user making the request
    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend,filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()] 
        return [IsAuthenticated()]
    

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    filterset_fields = ['category']
    ordering_fields = ['name', 'quantity', 'price', 'date_added', 'last_updated']
    
    def get_queryset(self):
        user = self.request.user
        queryset = InventoryItem.objects.filter(owner=user)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filter by low stock
        low_stock = self.request.query_params.get('low_stock')
        if low_stock:
            try:
                threshold = int(low_stock)
                queryset = queryset.filter(quantity__lte=threshold)
            except ValueError:
                pass
        
        return queryset
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return InventoryItemCreateUpdateSerializer
        return InventoryItemSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        
    def perform_update(self, serializer):
        instance = self.get_object()
        old_quantity = instance.quantity
        updated_instance = serializer.save()
        new_quantity = updated_instance.quantity
        
     # Log the inventory change
        if old_quantity != new_quantity:
            quantity_change = new_quantity - old_quantity
            action = 'ADD' if quantity_change > 0 else 'REMOVE'
            
            InventoryLog.objects.create(
                item=updated_instance,
                user=self.request.user,
                action=action,
                quantity_change=abs(quantity_change),
                previous_quantity=old_quantity,
                new_quantity=new_quantity,
                notes=f"Quantity updated from {old_quantity} to {new_quantity}"
            ) 
            
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        item = self.get_object()
        logs = item.logs.all()
        serializer = InventoryLogSerializer(logs, many=True)
        return Response(serializer.data)               


class InventoryLogViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return InventoryLog.objects.all()
        return InventoryLog.objects.filter(item__owner=user)              


class SupplierViewSet(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'contact_name', 'email']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        return Supplier.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    


class InventoryItemSupplierViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryItemSupplierSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return InventoryItemSupplier.objects.filter(item__owner=self.request.user)
    
    def perform_create(self, serializer):
        item_id = serializer.validated_data.get('item').id
        item = InventoryItem.objects.get(id=item_id)
        
        if item.owner != self.request.user:
            return Response({'error': 'You do not own this inventory item'}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        serializer.save()    