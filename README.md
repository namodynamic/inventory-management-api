# Inventory Management API

A RESTful API for inventory management built with Django and Django REST Framework. This API will allow users to manage inventory items by adding, updating, deleting, and viewing current inventory levels, along with tracking of inventory changes.

## Features

- **User Authentication & Authorization**: Secure JWT-based authentication system
- **Inventory Item Management**: Complete CRUD operations for inventory items
- **Category Management**: Organize items by customizable categories
- **Inventory Tracking**: Monitor changes to inventory quantities with detailed logs
- **Filtering & Searching**: Advanced filtering options for inventory items (e.g., by category, price range, stock level).
- **Pagination**: Efficient handling of large datasets
- **Stock Status**: Real-time stock status (e.g., "In Stock", "Low Stock", "Out of Stock").
- **Role-Based Access Control**: Staff users can manage all items, while regular users can only manage their own items.

## Deployed URL

The API is deployed and accessible at the following URL:

**Base URL**: [https://namodynamic1.pythonanywhere.com/api/inventory/](https://namodynamic1.pythonanywhere.com/)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/namodynamic/inventory-management-api.git
   cd inventory-management-api
   ```

2. Create a virtual environment and activate it:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

5. Create a superuser (optional):

   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:

   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication

- **Register User**: `/api/inventory/users/` (POST)
- **Obtain JWT Token**: `/api/token/` (POST)
- **Refresh JWT Token**: `/api/token/refresh/` (POST)

### Inventory Items

- **List Inventory Items**: `/api/inventory/items/` (GET)
- **Create Inventory Item**: `/api/inventory/items/` (POST)
- **Retrieve Inventory Item**: `/api/inventory/items/{id}/` (GET)
- **Update Inventory Item**: `/api/inventory/items/{id}/` (PUT)
- **Delete Inventory Item**: `/api/inventory/items/{id}/` (DELETE)
- **Stock Level**: `/api/inventory/items/level/` (GET)
- **Item Stock Level**: `/api/inventory/items/{id}/level/` (GET)
- **Adjust Quantity**: `/api/inventory/items/{id}/adjust_quantity/` (POST)

### Categories

- **List Categories**: `/api/inventory/categories/` (GET)
- **Create Category**: `/api/inventory/categories/` (POST)
- **Retrieve Category**: `/api/inventory/categories/{id}/` (GET)
- **Update Category**: `/api/inventory/categories/{id}/` (PUT)
- **Delete Category**: `/api/inventory/categories/{id}/` (DELETE)
- **Search Categories by Name**: `/api/inventory/categories/search={name}/` (GET)

### Inventory Logs

- **List Inventory Logs**: `/api/inventory/logs/` (GET)
- **Item Inventory Logs**: `/api/inventory/logs/{id}/item/` (GET)

### Suppliers

- **List Suppliers**: `/api/inventory/suppliers/` (GET)
- **Create Supplier**: `/api/inventory/suppliers/` (POST)
- **Retrieve Supplier**: `/api/inventory/suppliers/{id}/` (GET)
- **Update Supplier**: `/api/inventory/suppliers/{id}/` (PUT)
- **Delete Supplier**: `/api/inventory/suppliers/{id}/` (DELETE)

### Inventory Item Suppliers

- **List Inventory Item Suppliers**: `/api/inventory/item-suppliers/` (GET)
- **Create Inventory Item Supplier**: `/api/inventory/item-suppliers/` (POST)
- **Retrieve Inventory Item Supplier**: `/api/inventory/item-suppliers/{id}/` (GET)
- **Update Inventory Item Supplier**: `/api/inventory/item-suppliers/{id}/` (PUT)
- **Delete Inventory Item Supplier**: `/api/inventory/item-suppliers/{id}/` (DELETE)

## Documentation

You can find the full API documentation [here](https://documenter.getpostman.com/view/24484793/2sB2cSfiNL).

### Technologies Used

- Backend: Django, Django REST Framework
- Database: PostgreSQL
- Authentication: Django REST Framework SimpleJWT
