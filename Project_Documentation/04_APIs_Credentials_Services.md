# APIs, Credentials, Services, and Integrations (Full Documentation)

This file consolidates the API families, credentials, service requirements, and integration dependencies described in the source documents.

--- BEGIN API AND SERVICES COMPILATION ---

Backend PRD
Finance Business ERP
Version

1.0

Document Type

Backend Product Requirements Document (Backend PRD)

Primary Technology Stack
Django 5.x
Django REST Framework
PostgreSQL
JWT Authentication
Swagger / OpenAPI
Redis (V2)
Celery (V2)
Django Channels (V2)
1. Introduction

The Finance Business ERP is a Software-as-a-Service (SaaS) platform designed to digitize and modernize the operations of traditional finance businesses that provide loans and collect installments on daily, weekly, monthly, or custom schedules. Many small and medium finance businesses still rely on handwritten collection books, manual calculations, spreadsheets, and informal tracking methods. These approaches often result in calculation errors, missed collections, duplicate entries, limited visibility into business performance, and poor data security.

The objective of this platform is to provide a scalable backend capable of supporting both individual finance operators and multi-branch finance organizations through a phased implementation strategy. Instead of attempting to deliver a complete ERP in the initial release, the platform begins with a lightweight Guest Workspace that functions as a digital collection register. This enables users to experience the product immediately without committing to a subscription or learning a complex enterprise system.

The backend is designed so that every piece of data created in the Guest Workspace can later be upgraded into the full ERP without requiring data migration, duplicate entry, or structural modifications. This migration path is a core architectural principle and influences the database design, service layer, and application structure from the very beginning.

The system follows a strict service-oriented architecture where business logic is isolated from presentation logic. Every business operation—including customer creation, loan calculations, collection recording, report generation, dashboard statistics, and upgrade workflows—is handled through dedicated service classes. Views remain lightweight and are responsible only for authentication, permissions, validation, request processing, filtering, pagination, and response generation.

The backend is intentionally designed for long-term scalability. Future releases will introduce lenders, employees, route management, attendance, cash reconciliation, subscription billing, analytics, GPS-assisted collections, SMS notifications, WhatsApp Business integration, AI-powered insights, and additional enterprise capabilities without requiring fundamental architectural changes.

2. Product Vision

The long-term vision of the Finance Business ERP is to become the operating system for finance businesses of every size—from individual lenders managing a few dozen customers to organizations operating multiple branches with hundreds of employees and thousands of active loans.

Rather than serving only as loan management software, the platform aims to become a complete business management ecosystem covering customer onboarding, loan issuance, installment collection, expense tracking, employee management, business analytics, operational reporting, subscriptions, communication, and future AI-assisted decision support.

The first release deliberately focuses on solving the most immediate and universal problem faced by finance businesses: maintaining a reliable digital collection register. Once users begin managing their daily operations through the Guest Workspace, the platform will provide a seamless upgrade path to the complete ERP, allowing businesses to grow without changing systems or re-entering historical data.

3. Objectives

The backend must satisfy the following objectives:

Primary Objectives (Version 1)
Provide a simple digital collection register through Guest Workspace.
Allow users to manage customers without creating a full ERP account.
Record daily, weekly, monthly, and custom collections.
Track customer balances and outstanding amounts automatically.
Record business expenses.
Generate dashboard statistics and operational reports.
Ensure all Guest Workspace data can later be upgraded into a complete ERP account.
Secondary Objectives (Version 2)
Multi-user business accounts.
Employee management.
Loan lifecycle management.
Area and route management.
Cash reconciliation.
GPS-assisted collections.
Subscription billing.
Premium add-ons.
Business analytics.
Notification services.
Enterprise integrations.
4. Release Strategy
Version 1 — Guest Workspace (Highest Priority)

Version 1 is intentionally limited in scope to maximize development speed, reduce onboarding complexity, and validate the product with real finance businesses.

The Guest Workspace serves as a fully functional digital finance register where a business owner can:

Verify the account first using OTP sent to the registered mobile number.
After successful verification, use the password-based login flow for regular access.
Create a personal workspace.
Add and manage customers.
Record collections.
Track outstanding balances.
Record expenses.
View dashboards.
Generate reports.
Use the built-in loan calculator.
Upgrade to the ERP in the future without data loss.

Although the internal backend architecture already supports future ERP capabilities, only Guest Workspace functionality will be exposed during the initial release.

This phase represents the highest development priority for the project.

Version 2 — Complete Finance ERP

Version 2 transforms the Guest Workspace into a complete multi-user Finance Business ERP.

Major additions include:

Lender accounts.
Employee accounts.
Role-based permissions.
Branch management.
Area management.
Route optimization.
Loan approval workflows.
Employee attendance.
Salary management.
Cash reconciliation.
Subscription billing.
Premium add-ons.
Business analytics.
Google Maps integration.
SMS Gateway.
WhatsApp Business API.
AI-powered insights.

The backend architecture created for Version 1 must already be capable of supporting these features without requiring significant database redesign or service refactoring.

5. Technology Stack
Layer	Technology
Backend Framework	Django 5.x
API Framework	Django REST Framework
Database	PostgreSQL
Authentication	JWT (SimpleJWT)
Documentation	Swagger / OpenAPI
File Storage	Local (Development), S3 Compatible (Production)
Password Hashing	Django Authentication System
Background Jobs (V2)	Celery
Cache (V2)	Redis
Realtime (V2)	Django Channels
Maps	Google Maps API
Deployment	Docker, Railway, AWS, Azure (Future)
6. Backend Design Principles

The backend follows several non-negotiable architectural principles that apply to every application and module.

1. Service-Oriented Architecture

Every business operation must be implemented inside service classes. Views, serializers, and models should never contain business rules.

2. Single Responsibility Principle

Each layer performs one responsibility only.

Models define database structure.
Serializers validate and transform data.
Services implement business rules.
Views coordinate requests and responses.
URLs define routing.
3. Domain-Based Application Structure

Applications are organized by business domain rather than by screens or API endpoints. This ensures that related functionality remains together and the system remains maintainable as new features are added.

4. Forward Compatibility

Every database table, relationship, and service created in Version 1 must support future ERP functionality. No temporary schemas or disposable implementations should be introduced.

5. Consistent API Standards

Every endpoint follows identical request, response, validation, pagination, filtering, authentication, and error handling conventions to simplify frontend development and long-term maintenance.

This completes Chapter 1 (Introduction & Foundation).

Next Chapter (Chapter 2) will begin the technical implementation and will include:
Complete Backend Architecture
5-Layer Architecture
Request Lifecycle
Folder Structure
App Structure
Coding Standards
Naming Conventions
Service Layer Standards
Database Standards
Base Classes
Common Module
Transactions
Exception Handling
API Response Standards

From there, we'll move into the detailed implementation of each app, starting with accounts, then masters, and finally the guest_workspace app, where every model, field, serializer, service, business rule, view, and API endpoint will be specified in the same detailed style as your reference document.


-------------------

Chapter 2 – Backend Architecture & Engineering Standards
7. Backend Architecture

The Finance Business ERP backend follows a layered, service-oriented architecture that separates business logic from request handling and database operations. The objective of this architecture is to improve maintainability, scalability, testing, code readability, and long-term extensibility.

Unlike traditional Django projects where business logic is spread across models, serializers, and views, this project centralizes all business operations inside dedicated service classes. Every module—whether it is customer management, loan management, collection tracking, reporting, or future employee management—must follow the same architectural principles.

The architecture is designed to ensure that new modules can be added without affecting existing code, allowing the application to grow from a simple Guest Workspace into a complete enterprise Finance ERP.

8. Five Layer Architecture

Every API request follows a strict five-layer processing pipeline.

                 HTTP Request
                      │
                      ▼
                  URL Routing
                      │
                      ▼
                    View
                      │
          Authentication & Permissions
                      │
           Request Parsing & Validation
                      │
                      ▼
                 Serializer
                      │
          Field Validation
          Object Validation
          Data Transformation
                      │
                      ▼
                  Service Layer
                      │
       Business Rules
       CRUD Operations
       Calculations
       Transactions
       Reports
       Integrations
                      │
                      ▼
                    Models
                      │
          ORM & Database Queries
                      │
                      ▼
                 PostgreSQL
                      │
                      ▼
                HTTP Response

Every layer has a clearly defined responsibility.

9. Layer Responsibilities
9.1 Models Layer

The Models layer represents the database schema.

Models should never contain business logic.

Responsibilities
Database schema
Relationships
Constraints
Choices
Database indexes
Meta configuration
Allowed
customer_name = models.CharField(...)
loan_amount = models.DecimalField(...)
Not Allowed
def calculate_interest():
def create_collection():
def generate_report():

Business logic inside models is strictly prohibited.

9.2 Serializers Layer

Serializers act as the boundary between HTTP requests and the internal application.

Responsibilities include:

Input validation
Output serialization
Nested serialization
Field validation
Object validation
Request transformation
Allowed
validate_phone_number()
validate_collection_amount()
validate_due_date()
Not Allowed
Save loan schedule
Create collections
Update reports
Calculate dashboards
9.3 Service Layer

The Service Layer is the core of the backend.

Every business operation belongs here.

Examples:

Create Customer
Update Loan
Record Collection
Generate Dashboard
Generate Reports
Upgrade Workspace
Assign Employee
Optimize Route

No business logic should exist outside service classes.

Service Standards

Each service is represented by a dedicated class.

Example

class CustomerService:

    @staticmethod
    def create_customer():
        pass

    @staticmethod
    def update_customer():
        pass

    @staticmethod
    def archive_customer():
        pass

    @staticmethod
    def delete_customer():
        pass

Standalone functions are not permitted for business operations.

Responsibilities

The Service Layer handles:

CRUD Operations
Business Rules
Calculations
Transactions
Dashboard Calculations
Report Generation
Integration Calls
Audit Logs
Notifications
Cache Updates
Future AI Operations
9.4 Views Layer

Views coordinate the request lifecycle.

Views should remain lightweight.

Responsibilities include:

Authentication
Permissions
Serializer Execution
Pagination
Search
Ordering
Filtering
Calling Service Methods
Returning Responses

Views must never perform business calculations.

Example:

serializer = CustomerCreateSerializer(data=request.data)
serializer.is_valid(raise_exception=True)

customer = CustomerService.create_customer(
    serializer.validated_data
)

return success_response(customer)
9.5 URL Layer

The URL layer performs only routing.

No validation.

No business logic.

No serializer execution.

Example

POST   /api/v1/customers/
GET    /api/v1/customers/
PATCH  /api/v1/customers/{id}/
DELETE /api/v1/customers/{id}/
10. Request Lifecycle

Every request follows the same lifecycle.

Frontend

↓

URL

↓

APIView

↓

Authentication

↓

Permission Check

↓

Serializer Validation

↓

Service Layer

↓

Model

↓

Database

↓

Response Formatter

↓

HTTP Response

If validation fails, the request immediately returns a standardized error response.

If any business rule fails, the Service Layer raises a custom exception.

11. Project Structure
finance_erp_backend/

├── manage.py
├── requirements.txt
├── .env
├── README.md
│
├── config/
│   ├── settings/
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── __init__.py
│
├── apps/
│   ├── accounts/
│   ├── masters/
│   ├── guest_workspace/
│   ├── finance/
│   ├── employees/
│   ├── subscriptions/
│   ├── integrations/
│   ├── audit_logs/
│   └── common/
│
├── media/
├── static/
├── logs/
└── scripts/
12. App Structure Standard

Every application must follow the exact same internal structure.

guest_workspace/

models.py

serializers.py

views.py

urls.py

permissions.py

filters.py

pagination.py

validators.py

constants.py

choices.py

signals.py

tasks.py

tests.py

services/

    __init__.py

--- BEGIN VERSION 2 / ENTERPRISE ERP SECTION ---

Chapter 6 — Finance ERP / Lender V2
344. Purpose

Version 2 converts the lightweight Guest Workspace and Super Admin Platform Console into a complete multi-user finance-business management platform.

The 3 official user roles across V1 & V2 are:

1. **`ADMIN` (Super Admin)** — FinRoute SaaS platform operator managing tenants, system health telemetry, coupons, audit logs, and global settings.
2. **`LENDER_OWNER` (Lender Owner)** — Business owner managing customers, loans, routes, cash reconciliation, expenses, and workspace configuration.
3. **`FIELD_COLLECTOR` (Field Collector / Agent)** — On-ground field agent using the mobile PWA app to execute daily collection routes, record payments, geo-attendance, and cash handover.

The V2 system adds:

Finance-business management.
Multiple collection areas.
Employees/collectors.
Area assignments.
Customer-area assignments.
GPS customer locations.
Editable collection routes.
In-app Google Maps directions.
Collection assignments.
Collector activity.
Employee expenses.
Salaries.
Cash reconciliation.
Penalties/additional charges.
Advanced lender dashboards.
Reports.
Permissions.
SMS add-on.
WhatsApp add-on.
345. V1 → V2 Upgrade

The architecture defined previously becomes important here.

Before upgrade:

User
 │
 ▼
Workspace
 │
 ├── Customers
 ├── Finance Accounts
 ├── Collections
 └── Expenses

workspace_type = guest

After upgrade:

Same User
 │
 ▼
Same Workspace
 │
 ├── Existing Customers
 ├── Existing Finance Accounts
 ├── Existing Collections
 ├── Existing Expenses
 │
 ├── Business Profile
 ├── Areas
 ├── Routes
 ├── Employees
 ├── Assignments
 ├── Salaries
 └── Cash Reconciliation

workspace_type = finance_business

No customer or financial history needs to be recreated.

346. Lender Role

The Lender is the owner/administrator of one finance workspace.

The lender should have complete visibility over:

Business
Customers
Finance Accounts
Areas
Employees
Collections
Expenses
Routes
Cash
Salaries
Reports
Analytics
Settings

The lender is effectively the business administrator.

However, this must remain different from the platform Admin.

347. Platform Admin vs Lender
Platform Admin

Controls:

Entire SaaS Platform

Can manage:

Users.
Lenders.
Plans.
Subscriptions.
Platform master data.
Feature availability.
Add-ons.

## Recommended Credentials / Environment Variables
- DJANGO_SECRET_KEY
- DEBUG
- DB_NAME
- DB_USER
- DB_PASSWORD
- DB_HOST
- DB_PORT
- REDIS_URL
- CELERY_BROKER_URL
- CELERY_RESULT_BACKEND
- JWT_ACCESS_TOKEN_LIFETIME
- JWT_REFRESH_TOKEN_LIFETIME
- JWT_SIGNING_KEY
- EMAIL_BACKEND
- EMAIL_HOST
- EMAIL_PORT
- EMAIL_HOST_USER
- EMAIL_HOST_PASSWORD
- DEFAULT_FROM_EMAIL
- SMS_PROVIDER
- SMS_API_KEY
- SMS_SENDER_ID
- SMS_BASE_URL
- WHATSAPP_PROVIDER
- WHATSAPP_API_KEY
- WHATSAPP_PHONE_NUMBER_ID
- WHATSAPP_ACCESS_TOKEN
- GOOGLE_MAPS_API_KEY
- GOOGLE_MAPS_ENABLED
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_STORAGE_BUCKET_NAME
- AWS_S3_REGION_NAME
- PAYMENT_PROVIDER
- PAYMENT_API_KEY
- PAYMENT_WEBHOOK_SECRET
- OTP_TTL_MINUTES
- OTP_MAX_ATTEMPTS
- OTP_RATE_LIMIT

## Required Service Layers
- accounts/services/auth_service.py
- accounts/services/account_service.py
- accounts/services/otp_service.py
- accounts/services/session_service.py
- accounts/services/consent_service.py
- masters/services/master_data_service.py
- masters/services/location_service.py
- masters/services/location_import_service.py
- guest_workspace/services/workspace_service.py
- guest_workspace/services/customer_service.py
- guest_workspace/services/finance_account_service.py
- guest_workspace/services/collection_service.py
- guest_workspace/services/expense_service.py
- guest_workspace/services/dashboard_service.py
- guest_workspace/services/report_service.py
- guest_workspace/services/calculator_service.py
- guest_workspace/services/workspace_limits_service.py
- finance/services/area_service.py
- finance/services/employee_service.py
- finance/services/route_service.py
- finance/services/cash_reconciliation_service.py
- finance/services/salary_service.py
- finance/services/adjustment_service.py
- subscriptions/services/coupon_service.py
- core/services/health_check_service.py
- field/services/offline_sync_service.py
- field/services/collector_performance_service.py
- support/services/support_ticket_service.py
- integrations/services/google_maps_service.py
- integrations/services/notification_service.py

## Required External Services
- Email service for authentication and notifications
- SMS gateway for OTP and reminders
- WhatsApp Business API for reminders and notifications
- Google Maps for geocoding, places, routing, and route optimization
- Object storage for receipts, logos, profile photos, and documents
- Payment provider for plans and subscriptions
- Monitoring/logging & System Telemetry service for production operations
- Public Marketing CMS & Lead Inquiry intake engine

## Supplementary Gap Resolution Endpoints & Contracts

### 1. Authentication & OAuth Endpoint Additions
- `POST /api/v1/accounts/token/refresh/`
  - Request: `{ "refresh": "string" }`
  - Response: `{ "access": "string", "access_expires_at": "ISO-8601" }`
- `POST /api/v1/accounts/oauth/google/`
  - Request: `{ "id_token": "string" }`
  - Response: `{ "access": "string", "refresh": "string", "user": { "id": "uuid", "email": "string" } }`
- `POST /api/v1/accounts/oauth/microsoft/`
  - Request: `{ "id_token": "string" }`
  - Response: `{ "access": "string", "refresh": "string", "user": { "id": "uuid", "email": "string" } }`

### 2. Field Agent PWA Offline Batch Sync Endpoint
- `POST /api/v1/field/sync/`
  - Request:
    ```json
    {
      "device_id": "string",
      "sync_timestamp": "ISO-8601",
      "batch": [
        {
          "offline_id": "uuid",
          "customer_id": "string",
          "loan_id": "string",
          "collected_amount": 500,
          "expected_amount": 500,
          "payment_mode": "cash|upi",
          "gps_latitude": 12.9716,
          "gps_longitude": 77.5946,
          "collected_at": "ISO-8601",
          "remarks": "string"
        }
      ]
    }
    ```
  - Response:
    ```json
    {
      "status": "success",
      "synced_count": 1,
      "failed_count": 0,
      "ack_tokens": [
        { "offline_id": "uuid", "server_collection_id": "COL-10023", "status": "processed" }
      ]
    }
    ```

### 3. V1 → V2 Workspace Upgrade Endpoint
- `POST /api/v1/workspaces/upgrade/`
  - Request: `{ "workspace_id": "uuid", "target_tier": "finance_business", "business_name": "string", "business_address": "string" }`
  - Response: `{ "status": "upgraded", "workspace_type": "finance_business", "new_role": "Lender", "new_token": "string" }`

### 4. Admin Overrides & Quotas Endpoint
- `GET /api/v1/admin/overrides/`
- `POST /api/v1/admin/overrides/`
  - Request: `{ "user_id": "uuid", "operating_days_per_week": 4, "customer_quota": 100, "note": "Custom grant" }`



