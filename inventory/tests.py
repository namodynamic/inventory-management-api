from django.test import TestCase

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Category, InventoryItem, InventoryLog, Supplier

class InventoryAPITests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='password123'
        )
        
        self.category1 = Category.objects.create(name='Electronics')
        self.category2 = Category.objects.create(name='Furniture')
        
        self.item1 = InventoryItem.objects.create(
            name='Laptop',
            description='A high-end laptop',
            quantity=10,
            price=1200.00,
            category=self.category1,
            owner=self.user1
        )
        self.item2 = InventoryItem.objects.create(
            name='Chair',
            description='Office chair',
            quantity=5,
            price=150.00,
            category=self.category2,
            owner=self.user2
        )
        
        self.client = APIClient()
    
    def test_user_can_view_own_items(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('items-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Laptop')
    
    def test_user_cannot_view_others_items(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('items-detail', args=[self.item2.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_user_can_create_item(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'Mouse',
            'description': 'Wireless mouse',
            'quantity': 20,
            'price': 50.00,
            'category': self.category1.id
        }
        response = self.client.post(reverse('items-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(InventoryItem.objects.count(), 3)
    
    def test_user_can_update_own_item(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'Updated Laptop',
            'description': 'An updated high-end laptop',
            'quantity': 15,
            'price': 1300.00,
            'category': self.category1.id
        }
        response = self.client.put(reverse('items-detail', args=[self.item1.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.name, 'Updated Laptop')
        self.assertEqual(self.item1.quantity, 15)
        
    def test_user_cannot_update_others_item(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'Updated Chair',
            'description': 'An updated office chair',
            'quantity': 10,
            'price': 200.00,
            'category': self.category2.id
        }
        response = self.client.put(reverse('items-detail', args=[self.item2.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)    
        
        
    def test_user_can_delete_own_item(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(reverse('items-detail', args=[self.item1.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(InventoryItem.objects.filter(id=self.item1.id).count(), 0)

    def test_user_cannot_delete_others_item(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(reverse('items-detail', args=[self.item2.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_view_item_logs(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('logs-item-log', args=[self.item1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_staff_can_view_any_item_logs(self):
        self.user1.is_staff = True
        self.user1.save()
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('logs-item-log', args=[self.item2.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)     