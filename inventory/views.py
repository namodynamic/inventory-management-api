from django.shortcuts import render
from rest_framework import viewsets
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import UserSerializer, CategorySerializer, InventoryItemSerializer
from .models import Category, InventoryItem, Supplier


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
    

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
              
    