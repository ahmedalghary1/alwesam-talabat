# Alwesam-Talabat: Complete Project Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Design Patterns](#architecture--design-patterns)
3. [Database Schema](#database-schema)
4. [API Endpoints](#api-endpoints)
5. [Authentication & Authorization](#authentication--authorization)
6. [Frontend Components](#frontend-components)
7. [Admin Panel](#admin-panel)
8. [Deployment Guide](#deployment-guide)
9. [Developer Guide](#developer-guide)
10. [User Guide](#user-guide)

---

## Project Overview

### Description

**Alwesam-Talabat** is a comprehensive wholesale e-commerce platform built with Django 5.2.8. The system is designed specifically for bulk sales (carton-based ordering) with advanced features for product management, order processing, and user administration.

### Key Features

- 🛒 **Smart Shopping Cart**: AJAX-powered cart with localStorage support for guest users
- 📦 **Advanced Order System**: Complete order lifecycle management with status tracking
- 👤 **Custom User Management**: Email/phone authentication with admin approval workflow
- 🎨 **Theme Support**: Light/Dark mode toggle with session persistence
- 🌐 **RTL Support**: Full Arabic language support with right-to-left layout
- 🔐 **Enhanced Security**: Rate limiting, CSRF protection, and password validation
- ⚡ **Performance Optimized**: Database indexing, query optimization, and caching
- 📊 **Comprehensive Admin Panel**: Custom-built admin dashboard for complete system management

### Technology Stack

- **Backend Framework**: Django 5.2.8
- **Database**: SQLite (Development) / PostgreSQL (Production recommended)
- **Image Processing**: Pillow with custom compression utilities
- **Configuration**: python-decouple for environment management
- **Security**: django-ratelimit for rate limiting
- **Development Tools**: django-debug-toolbar

---

## Architecture & Design Patterns

### Project Structure

```
alwesam-talabat1/
├── accounts/              # User authentication and profile management
├── products/              # Product catalog and categories
├── cart/                  # Shopping cart functionality
├── orders/                # Order processing and management
├── home/                  # Homepage and custom admin panel
├── utils/                 # Shared utilities and helpers
├── core/                  # Project constants and configurations
├── static/                # Static assets (CSS, JS, Images)
├── templates/             # HTML templates
├── media/                 # User-uploaded files
├── logs/                  # Application logs
└── project/               # Django project settings
```

### Design Patterns

#### 1. **MVC (Model-View-Controller) Pattern**

Django follows the MVT (Model-View-Template) variation:

- **Models**: Define data structure and business logic
- **Views**: Handle request processing and business logic
- **Templates**: Render HTML with dynamic content

#### 2. **Repository Pattern**

Each Django app acts as a repository for its domain:

- `accounts/`: User data and authentication
- `products/`: Product catalog
- `cart/`: Shopping cart state
- `orders/`: Order transactions

#### 3. **Middleware Pattern**

Custom middleware for cross-cutting concerns:

- `CheckUserActiveMiddleware`: Validates user authentication status
- Session management for theme/language preferences
- CSRF protection and security headers

#### 4. **Context Processor Pattern**

Global template variables:

- `theme_processor`: Current theme (light/dark)
- `pending_users_count`: Admin notification count
- `cart_count`: Global cart item counter

#### 5. **Signal Pattern**

Django signals for decoupled operations:

- Profile creation on user registration
- Cart synchronization on login

### Core Modules

#### Accounts Module

- **Purpose**: User authentication, profile management, and theme preferences
- **Key Features**:
  - Custom user model with email as primary identifier
  - Dual authentication (email/phone)
  - Admin approval workflow for new users
  - Profile management with image compression
  - Multiple address support
  - Theme and language preferences

#### Products Module

- **Purpose**: Product catalog, categories, and variant management
- **Key Features**:
  - Category-based organization
  - Product variants (colors, sizes)
  - Multiple product images
  - Slug-based URLs for SEO
  - Availability tracking
  - Automatic image compression

#### Cart Module

- **Purpose**: Shopping cart management with guest support
- **Key Features**:
  - User-specific carts (database)
  - Guest cart via localStorage
  - Automatic cart synchronization on login
  - Unit type support (pieces/cartons)
  - Variant and size selection
  - Real-time updates via AJAX

#### Orders Module

- **Purpose**: Order creation, tracking, and management
- **Key Features**:
  - Order lifecycle management
  - Status tracking (pending, confirmed, shipped, delivered, cancelled)
  - Order history for users
  - Preserved variant information
  - Total calculations (pieces/cartons)
  - Admin order management

#### Home Module

- **Purpose**: Homepage and custom admin panel
- **Key Features**:
  - Landing page
  - Custom admin dashboard
  - Product management (CRUD)
  - Category management
  - Order management
  - User approval system
  - Search functionality

### Security Measures

1. **Authentication Security**:
   - Password hashing with Django's PBKDF2
   - Email/Phone dual authentication
   - Rate limiting on login (5 attempts/minute)
   - CSRF protection on all forms
   - Session-based authentication

2. **Data Security**:
   - SQL injection protection (ORM)
   - XSS protection (template auto-escaping)
   - Secure password validation
   - Environment-based secret key

3. **Access Control**:
   - Login required decorators
   - Staff member required for admin
   - User approval workflow
   - Active user middleware check

### Performance Optimizations

1. **Database Optimization**:
   - Strategic indexing on frequently queried fields
   - `select_related()` for foreign key queries
   - `prefetch_related()` for many-to-many queries
   - Database-level aggregations

2. **Image Optimization**:
   - Custom `ImageCompressionMixin` for automatic compression
   - WebP format support
   - Thumbnail generation

3. **Query Optimization**:
   - Reduced N+1 queries with prefetching
   - Lazy loading where appropriate
   - Database indexes on slug, category, availability

4. **Caching Strategy**:
   - Local memory cache (development)
   - 15-minute default timeout
   - Ready for Redis/Memcached in production

---

*Continue to the next sections for detailed documentation on Database Schema, API Endpoints, and more.*
