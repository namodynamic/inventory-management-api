from django.db import models
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .serializers import (
    UserSerializer, CategorySerializer, InventoryItemSerializer, InventoryLogSerializer, 
    SupplierSerializer, InventoryItemSupplierSerializer, InventoryItemCreateUpdateSerializer, InventoryLevelSerializer,
    LoginSerializer
)
from .models import Category, InventoryItem, Supplier, InventoryLog, InventoryItemSupplier
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsOwnerOrReadOnly, IsOwner
from .filters import InventoryItemFilter
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


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
        elif self.action == 'login':
            return [AllowAny()]
        elif self.action in ['me', 'update', 'partial_update', 'destroy', 'retrieve', 'logout']:
            return [IsAuthenticated()]
        return [IsAdminUser()] 
    
    def get_queryset(self):
        user = self.request.user 
        if user.is_staff: 
            return User.objects.all()
        return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request):
        user = request.user
        if request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(user, data=request.data, partial=(request.method == 'PATCH'))
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_staff': user.is_staff,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):
        refresh_token = request.data.get('refresh_token')
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error': 'Invalid token or user already logged out'}, status=status.HTTP_400_BAD_REQUEST)
       
       
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
    search_fields = ['name', 'description', 'category__name', 'sku']
    filterset_class = InventoryItemFilter
    ordering_fields = ['name', 'quantity', 'price', 'date_added', 'last_updated']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(owner=user)
     
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return InventoryItemCreateUpdateSerializer
        return InventoryItemSerializer
    
    @action(detail=False, methods=['get'], url_path='level')
    def stock_level(self, request):
        queryset = self.get_queryset()
        serializer = InventoryLevelSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        """
        List all items that are low in stock
        """
        low_stock_items = self.get_queryset().filter(quantity__lt=models.F('low_stock_threshold'))
        serializer = self.get_serializer(low_stock_items, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='level')
    def item_stock_level(self, request, pk=None):
        item = self.get_object()
        serializer = InventoryLevelSerializer(item)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        new_item = serializer.save(owner=self.request.user)
        InventoryLog.objects.create(
            item=new_item,
            user=self.request.user,
            action='ADD',
            quantity_change=new_item.quantity,
            previous_quantity= new_item.quantity,
            new_quantity=new_item.quantity,
            notes=f"New item  '{new_item.name}' added with quantity {new_item.quantity} by {self.request.user.username}"
        )
             
    def perform_update(self, serializer):
        instance = self.get_object()
        old_quantity = instance.quantity
        updated_instance = serializer.save()
        new_quantity = updated_instance.quantity
        
        if old_quantity != new_quantity:
            action = 'ADD' if new_quantity > old_quantity else 'REMOVE'
            
            InventoryLog.objects.create(
                item=updated_instance,
                user=self.request.user,
                action=action,
                quantity_change=abs(new_quantity - old_quantity),
                previous_quantity=old_quantity,
                new_quantity=new_quantity,
                notes=f"Item '{updated_instance.name}' updated  by {self.request.user.username}"
            ) 
            
    @action(detail=True, methods=['post'])
    def adjust_quantity(self, request, pk=None):
        item = self.get_object()
        try:
            quantity_change = int(request.data.get('quantity_change', 0))
        except ValueError:
            return Response(
                {"error": "quantity_change must be an integer"}, 
                status=status.HTTP_400_BAD_REQUEST
            ) 
        notes = request.data.get('notes', '')
        
        if quantity_change == 0:
            return Response(
                {"error": "quantity_change cannot be zero"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_quantity = item.quantity
        new_quantity = max(0, old_quantity + quantity_change)
        if quantity_change > 0:
            action = 'ADD'
        else:
            action = 'REMOVE'
            quantity_change = abs(quantity_change)  
        
        item.quantity = new_quantity
        item.save()
        
        log = InventoryLog.objects.create(
            item=item,
            user=self.request.user,
            action=action,
            quantity_change=quantity_change,
            previous_quantity=old_quantity,
            new_quantity=new_quantity,
            notes=f"Quantity updated from {old_quantity} to {new_quantity} by {self.request.user.username}"
        )
        
        return Response({
            'item': InventoryItemSerializer(item).data,
            'log': InventoryLogSerializer(log).data
        })
                         


class InventoryLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryLog.objects.all()
    serializer_class = InventoryLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['item', 'user', 'action']
    ordering_fields = ['timestamp', 'item__name']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return InventoryLog.objects.all()
        return InventoryLog.objects.filter(item__owner=user) 
    
    @action(detail=True, methods=['get'] , url_path='item')
    def item_log(self, request, pk=None):
        
        try:
            if request.user.is_staff:
                item = InventoryItem.objects.get(id=pk)
            else:
                item = InventoryItem.objects.get(id=pk, owner=self.request.user)
                
        except InventoryItem.DoesNotExist:
            return Response({'error': 'Inventory item not found or you do not own it'}, status=status.HTTP_404_NOT_FOUND)
        
        logs = self.get_queryset().filter(item=item)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)            


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
            return Response({'error': 'You do not own this inventory item'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer.save()    