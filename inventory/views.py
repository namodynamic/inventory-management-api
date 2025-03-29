from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import UserSerializer, CategorySerializer, InventoryItemSerializer, InventoryLogSerializer, SupplierSerializer, InventoryItemSupplierSerializer
from .models import Category, InventoryItem, Supplier, InventoryLog, InventoryItemSupplier
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # Default permission: Only authenticated users can access
    
    # Override the default permissions
    def get_permissions(self):
        if self.action == 'create':
            return []  # Anyone can create a new user
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]  # Only the user themselves or admin can modify
        elif self.action == 'retrieve': 
            return [IsAuthenticated()] # Only the user themselves or admin can view
        return [IsAdminUser()]  # Default to admin only for list and other actions
    
    # Override the default queryset
    def get_queryset(self):
        user = self.request.user # Get the user making the request
        if user.is_staff: # If the user is an admin, return all users
            return User.objects.all()
        return User.objects.filter(id=user.id) # If non-admin, only return the user making the request
    
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
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class InventoryLogViewSet(viewsets.ModelViewSet):
    queryset = InventoryLog.objects.all()
    serializer_class = InventoryLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return InventoryLog.objects.all()
        return InventoryLog.objects.filter(item__owner=user)              


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    


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