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
        fields = '__all__'
        
        
class InventoryLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    
    class Meta:
        model = InventoryLog
        fields = '__all__'
        read_only_fields = ('user', 'item', 'previous_quantity', 'new_quantity', 'timestamp')        


class SupplierSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ('owner',)        


class InventoryItemSupplierSerializer(serializers.ModelSerializer):
    supplier_name = serializers.ReadOnlyField(source='supplier.name')
    
    class Meta:
        model = InventoryItemSupplier
        fields = '__all__'

class InventoryItemSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    category_name = serializers.ReadOnlyField(source='category.name')
    logs = InventoryLogSerializer(many=True, read_only=True)
    suppliers = InventoryItemSupplierSerializer(many=True, read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = '__all__'
        read_only_fields = ('owner', 'date_added', 'last_updated', 'category_name', 'logs', 'suppliers')


class InventoryItemCreateUpdateSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    
    class Meta:
        model = InventoryItem
        fields = '__all__'
        read_only_fields = ('owner', 'date_added', 'last_updated')
                