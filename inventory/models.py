from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

 
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class meta:
        verbose_name_plural = 'Categories'
    
class InventoryItem(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='items')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='inventory_items')
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True, help_text="Stock Keeping Unit")
    location = models.CharField(max_length=100, blank=True, null=True, help_text="Warehouse location")
    low_stock_threshold = models.PositiveIntegerField(default=10, help_text="Minimum stock level before alert")
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold
    
    class Meta:
        ordering = ['name']    


class InventoryLog(models.Model):
    ACTION_CHOICES = (
        ('ADD', 'Added'),
        ('REMOVE', 'Removed'),
        ('UPDATE', 'Updated'),
    )
    
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='inventory_logs')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    quantity_change = models.PositiveIntegerField()
    previous_quantity = models.PositiveIntegerField()
    new_quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.item.name}"
    
    class Meta:
        ordering = ['-timestamp']
        

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='suppliers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        

class InventoryItemSupplier(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='suppliers')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='items')
    supplier_sku = models.CharField(max_length=100, blank=True, null=True)
    supplier_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    lead_time_days = models.PositiveIntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.supplier.name} supplies {self.item.name}"
    
    class Meta:
        unique_together = ('item', 'supplier')                


# Signal to send email alert when stock is low
@receiver(post_save, sender=InventoryItem)
def check_low_stock(sender, instance, **kwargs):
    if instance.is_low_stock():
        send_mail(
            subject=f"Low Stock Alert for {instance.name}",
            message=f"The stock level for {instance.name} is below the threshold. Current quantity: {instance.quantity}.",
            from_email='noreply@inventory.com',
            recipient_list=[instance.owner.email],
            fail_silently=False
        )
        
        