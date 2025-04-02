from django.contrib import admin
from .models import Category, InventoryItem, InventoryLog, Supplier, InventoryItemSupplier

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'created_at', 'updated_at')
    search_fields = ('name',)
admin.site.register(Category, CategoryAdmin)

class InventoryLogInline(admin.TabularInline):
    model = InventoryLog
    extra = 0
    readonly_fields = ('user', 'action', 'quantity_change', 'previous_quantity', 'new_quantity', 'timestamp', 'notes')
    can_delete = False
    max_num = 0

class InventoryItemSupplierInline(admin.TabularInline):
    model = InventoryItemSupplier
    extra = 1

class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'category', 'quantity', 'price', 'owner', 'stock_level', 'date_added', 'last_updated')
    list_filter = ('category', 'owner')
    search_fields = ('name', 'description', 'category__name')
    inlines = [InventoryLogInline, InventoryItemSupplierInline]
    
    def stock_level(self, obj):
        if obj.quantity <= 0:
            return "Out of Stock"
        elif obj.quantity < 20:
            return "Low Stock"
        elif obj.quantity < 50:
            return "Medium Stock"
        else:
            return "In Stock"
    stock_level.short_description = 'Stock Level'
     
admin.site.register(InventoryItem, InventoryItemAdmin)

class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('item', 'action', 'quantity_change', 'previous_quantity', 'new_quantity', 'user', 'timestamp', 'notes')
    list_filter = ('action', 'item', 'user')
    readonly_fields = ('user', 'item', 'action', 'quantity_change', 'previous_quantity', 'new_quantity', 'timestamp')
admin.site.register(InventoryLog, InventoryLogAdmin)

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'contact_name', 'email', 'phone', 'owner')
    list_filter = ('owner',)
    search_fields = ('name', 'contact_name', 'email')
admin.site.register(Supplier, SupplierAdmin)

class InventoryItemSupplierAdmin(admin.ModelAdmin):
    list_display = ('id','item', 'supplier', 'supplier_sku', 'supplier_price', 'lead_time_days')
    list_filter = ('supplier',)
    search_fields = ('item__name', 'supplier__name', 'supplier_sku')
admin.site.register(InventoryItemSupplier, InventoryItemSupplierAdmin)