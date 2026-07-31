# Version 1 – Guest Workspace (Full Documentation)

This file contains the full Version 1 guest-workspace specification from the original source document.

--- BEGIN VERSION 1 SECTION ---

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


---

# Chapter 3 — Version 1 Super Admin Platform Operations

In addition to the Guest Workspace for solo finance operators, Version 1 includes the core backend management and administration capabilities for platform operations.

## 13. Super Admin Authentication & Permissions
- Access controlled via Django `User.is_superuser=True` and `User.is_staff=True`.
- Super Admin routes require JWT tokens containing superuser claims and permissions.

## 14. Workspace & Tenant Management
- `GET /api/v1/admin/workspaces/` — List all registered guest workspaces with pagination, search, and status filters.
- `PATCH /api/v1/admin/workspaces/{id}/` — Modify workspace status (e.g., active, suspended, read-only).
- `GET /api/v1/admin/workspaces/{id}/summary/` — Detailed usage stats (customer count, active collections, storage footprint).

## 15. System Health Telemetry
- `GET /api/v1/admin/system-health/` — Real-time telemetry monitoring for PostgreSQL database pool, Redis cache ping, Celery background worker availability, and API p95 latency.

## 16. Coupon & Discount Code Administration
- `POST /api/v1/admin/coupons/` — Create promotional codes with percentage/flat discounts, usage caps, and expiration windows.
- `GET /api/v1/admin/coupons/` — List and audit active/expired discount codes.

## 17. Platform Audit Logs
- `GET /api/v1/admin/audit-logs/` — Centralized view of system actions (user login failures, workspace status changes, administrative overrides, data exports).

## 18. Global Configuration & Feature Flags
- `GET /api/v1/admin/configuration/` — Retrieve global SaaS feature toggles and default system limits.
- `PUT /api/v1/admin/configuration/` — Update system configuration flags (e.g., enable/disable OTP rate limits, default pagination limits).


---

# Chapter 4 — User Consent & Audit Trail Architecture

## 19. UserConsent Model Specification
Stores immutable, append-only consent records captured during sign-up, login, and terms acceptance.

```python
class UserConsent(BaseModel):
    class ConsentType(models.TextChoices):
        TERMS_OF_SERVICE = "TERMS_OF_SERVICE", "Terms of Service"
        PRIVACY_POLICY = "PRIVACY_POLICY", "Privacy Policy"
        COMMUNICATION_OPT_IN = "COMMUNICATION_OPT_IN", "Communication Opt-In"
        BORROWER_LOAN_AGREEMENT = "BORROWER_LOAN_AGREEMENT", "Borrower Loan Agreement"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consents"
    )
    consent_type = models.CharField(max_length=50, choices=ConsentType.choices)
    version = models.CharField(max_length=20) # e.g. "v1.0"
    is_agreed = models.BooleanField(default=True)
    
    # Audit Trail Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    accepted_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-accepted_at"]
        indexes = [
            models.Index(fields=["user", "consent_type", "version"]),
            models.Index(fields=["accepted_at"]),
        ]
```

## 20. Consent Capture Rules
- **OTP Verification / Sign-up**: Upon verifying OTP, `ConsentService` automatically records `TERMS_OF_SERVICE` and `PRIVACY_POLICY` consents containing the user's IP address and device User-Agent header.
- **Append-Only Policy**: Existing consent records are never overwritten. Updating policy versions creates new rows.


---

# Chapter 5 — Guest Workspace Tier Limits & Admin Overrides

## 21. Tier Limit Evaluation Priority
When a Guest Workspace attempts to create a new customer or record a collection entry on a new business day, `WorkspaceLimitsService` evaluates limits in the following order:

$$\text{Effective Limit} = \text{Per-Workspace Custom Override (if set by Admin)} \;\mathbf{OR}\; \text{Global Plan Tier Default}$$

```python
class WorkspaceLimitsService:
    @staticmethod
    def get_effective_limits(workspace) -> dict:
        # 1. Check for active Per-Workspace Custom Override set by Super Admin
        override = getattr(workspace, 'quota_override', None)
        
        # 2. Get Plan Defaults (Free vs Guest Premium)
        plan_defaults = workspace.subscription_plan.get_defaults()
        
        return {
            "max_collection_days_per_week": (
                override.custom_max_collection_days_per_week 
                if override and override.custom_max_collection_days_per_week is not null 
                else plan_defaults["max_collection_days_per_week"] # Default Free = 2 days/week
            ),
            "max_customers_per_week": (
                override.custom_max_customers_per_week 
                if override and override.custom_max_customers_per_week is not null 
                else plan_defaults["max_customers_per_week"]
            )
        }
```

## 22. Business Day & Customer Quota Rules
- **Weekly Collection Business Days Limit**: Free tier defaults to **2 collection days per rolling 7-day period**. Attempting to add collections on a 3rd distinct date within the week triggers limit enforcement.
- **Weekly Customer Limit**: Restricts the maximum number of new borrowers added per week on the Free tier.
- **Limit Exceeded HTTP Error Response (403 Forbidden)**:
```json
{
  "error_code": "GUEST_PLAN_LIMIT_REACHED",
  "detail": "You have reached your Free Tier limit of 2 collection business days per week.",
  "usage": {
    "collection_days_this_week": 2,
    "limit": 2
  },
  "upgrade_prompt": {
    "message": "Upgrade to Guest Premium for unlimited collection days and higher customer quotas.",
    "upgrade_url": "/app/upgrade"
  }
}
```

## 23. Super Admin Limit Control Endpoints
- `GET/PUT /api/v1/admin/configuration/guest-limits/` — View and edit global Free Tier and Guest Premium Tier defaults.
- `PATCH /api/v1/admin/workspaces/{id}/quota-override/` — Grant a custom limit override (e.g. increase max collection days to 4/week) for a specific guest workspace without altering global Premium settings or forcing an upgrade.
- `POST /api/v1/app/upgrade/` — Self-serve upgrade flow for guest lenders transitioning from Free to Guest Premium.

## 24. Guest Workspace Batch Collections & Auth Extensions
- `POST /api/v1/guest/collections/batch/` — Processes multiple collection entries in a single request (aligning with `/app/collections/batch` UI screen).
  - Request Payload:
    ```json
    {
      "date": "YYYY-MM-DD",
      "entries": [
        {
          "customer_id": "FR1001",
          "expected_amount": 500,
          "collected_amount": 500,
          "payment_mode": "Cash",
          "remarks": "Paid on time"
        }
      ]
    }
    ```
- `POST /api/v1/accounts/oauth/google/` & `POST /api/v1/accounts/oauth/microsoft/` — Social OAuth identity exchanges to support frontend login options alongside primary phone OTP authentication.





