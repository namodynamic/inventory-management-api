from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, InventoryItem, InventoryLog, InventoryItemSupplier, Supplier

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        validated_data.pop('is_staff', None)
        user = User.objects.create_user(**validated_data)
        return user
    
    def update(self, instance, validated_data):
        validated_data.pop('is_staff', None)
        validated_data.pop('is_superuser', None)
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user   

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField() 
    
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['created_at']
        
        
class InventoryLogSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    username = serializers.ReadOnlyField(source='user.username')
    action_display = serializers.ReadOnlyField(source='get_action_display')
    
    class Meta:
        model = InventoryLog
        fields = ['id', 'item', 'item_name', 'user', 'username', 'action', 'action_display', 
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
    supplier_name = serializers.ReadOnlyField(source='supplier.name')
    item_name = serializers.ReadOnlyField(source='item.name')  
      
    class Meta:
        model = InventoryItemSupplier
        fields = '__all__'

class InventoryItemSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')
    category_name = serializers.ReadOnlyField(source='category.name')
    suppliers = InventoryItemSupplierSerializer(many=True, read_only=True)
    is_low_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'description', 'category', 'category_name',
            'quantity', 'price', 'sku', 'location','owner_username', 'suppliers', 'low_stock_threshold',
            'date_added', 'last_updated', 'is_low_stock'
        ]
        read_only_fields = ['id', 'date_added', 'last_updated']
        
    def get_is_low_stock(self, obj):
        return obj.is_low_stock()


class InventoryItemCreateUpdateSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    
    class Meta:
        model = InventoryItem
        fields = '__all__'
        read_only_fields = ['owner', 'date_added', 'last_updated']



class InventoryLevelSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'sku', 'quantity', 'category_name',
            'location', 'price', 'stock_status', 'last_updated'
        ]
    
    def get_stock_status(self, obj):
        if obj.quantity <= 0:
            return "Out of Stock"
        elif obj.quantity < 20: 
            return "Low Stock"
        elif obj.quantity < 50: 
            return "Medium Stock"
        else:
            return "In Stock"                