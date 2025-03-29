from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, InventoryItem, InventoryLog, InventoryItemSupplier, Supplier

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'is_staff')
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    # override create method for user creation
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
    # override update method for user update
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user   
    
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['created_at']
        
        
class InventoryLogSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = InventoryLog
        fields = ['id', 'item', 'item_name', 'user', 'username', 'action', 
                  'quantity_change', 'previous_quantity', 'new_quantity', 
                  'timestamp', 'notes']
        read_only_fields = ['id', 'timestamp']       


class SupplierSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_name', 'email', 'phone', 
                  'owner', 'address', 'created_at']
        
    def create(self, validated_data):
        return Supplier.objects.create(**validated_data)       


class InventoryItemSupplierSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    supplier_name = serializers.ReadOnlyField(source='supplier.name')
    
    class Meta:
        model = InventoryItemSupplier
        fields = [
            'id', 'item', 'item_name', 'supplier', 'supplier_name',
            'supplier_sku', 'supplier_price', 'lead_time_days', 'notes'
        ]
        read_only_fields = ['id']

class InventoryItemSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')
    category_name = serializers.ReadOnlyField(source='category.name')
    logs = InventoryLogSerializer(many=True, read_only=True)
    suppliers = InventoryItemSupplierSerializer(many=True, read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'description', 'category', 'category_name',
            'quantity', 'price', 'sku', 'location','owner_username', 'logs', 'suppliers',
            'date_added', 'last_updated'
        ]
        read_only_fields = ['id', 'date_added', 'last_updated']


class InventoryItemCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ['id', 'name', 'description', 'category', 
                  'quantity', 'price', 'sku', 'location']
                