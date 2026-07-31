# Finance Business ERP – Full Application Overview

This file contains the complete content of the original backend PRD so that no topic or line is omitted.

--- BEGIN FULL SOURCE DOCUMENT ---

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

The system follows a strict service-oriented architecture where business logic is isolated from presentation logic. Every business operationâ€”including customer creation, loan calculations, collection recording, report generation, dashboard statistics, and upgrade workflowsâ€”is handled through dedicated service classes. Views remain lightweight and are responsible only for authentication, permissions, validation, request processing, filtering, pagination, and response generation.

The backend is intentionally designed for long-term scalability. Future releases will introduce lenders, employees, route management, attendance, cash reconciliation, subscription billing, analytics, GPS-assisted collections, SMS notifications, WhatsApp Business integration, AI-powered insights, and additional enterprise capabilities without requiring fundamental architectural changes.

2. Product Vision

The long-term vision of the Finance Business ERP is to become the operating system for finance businesses of every sizeâ€”from individual lenders managing a few dozen customers to organizations operating multiple branches with hundreds of employees and thousands of active loans.

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
Version 1 â€” Guest Workspace (Highest Priority)

Version 1 is intentionally limited in scope to maximize development speed, reduce onboarding complexity, and validate the product with real finance businesses.

The Guest Workspace serves as a fully functional digital finance register alongside Super Admin platform management where:

1. Business Owners (Guest Lenders) can:
- Verify the account first using OTP sent to the registered mobile number.
- After successful verification, use the password-based login flow for regular access.
- Create a personal workspace.
- Add and manage customers (subject to plan quotas).
- Record collections (Free tier includes up to 2 collection business days per week; extensible via Guest Premium or custom Admin grants).
- Track outstanding balances.
- Record expenses.
- View dashboards and generate reports.
- Use the built-in loan calculator.
- Upgrade to Guest Premium or full ERP in the future without data loss.

2. Super Admin Staff can:
- Access the Super Admin Platform Console (`/admin`).
- Oversee all registered tenant workspaces and accounts.
- Configure global Free and Premium plan defaults (e.g. max collection days/week, customer quotas).
- Grant custom limit overrides to individual guest users without altering global Premium settings.
- Monitor real-time platform system health, API latency, and Celery background workers.
- Create, manage, and track promo coupons and discounts.
- Inspect platform-wide audit logs.
- Manage global system feature flags and configurations.

This phase represents the highest development priority for the project.

Version 2 â€” Complete Finance ERP

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

Chapter 2 â€“ Backend Architecture & Engineering Standards
7. Backend Architecture

The Finance Business ERP backend follows a layered, service-oriented architecture that separates business logic from request handling and database operations. The objective of this architecture is to improve maintainability, scalability, testing, code readability, and long-term extensibility.

Unlike traditional Django projects where business logic is spread across models, serializers, and views, this project centralizes all business operations inside dedicated service classes. Every moduleâ€”whether it is customer management, loan management, collection tracking, reporting, or future employee managementâ€”must follow the same architectural principles.

The architecture is designed to ensure that new modules can be added without affecting existing code, allowing the application to grow from a simple Guest Workspace into a complete enterprise Finance ERP.

8. Five Layer Architecture

Every API request follows a strict five-layer processing pipeline.

                 HTTP Request
                      â”‚
                      â–¼
                  URL Routing
                      â”‚
                      â–¼
                    View
                      â”‚
          Authentication & Permissions
                      â”‚
           Request Parsing & Validation
                      â”‚
                      â–¼
                 Serializer
                      â”‚
          Field Validation
          Object Validation
          Data Transformation
                      â”‚
                      â–¼
                  Service Layer
                      â”‚
       Business Rules
       CRUD Operations
       Calculations
       Transactions
       Reports
       Integrations
                      â”‚
                      â–¼
                    Models
                      â”‚
          ORM & Database Queries
                      â”‚
                      â–¼
                 PostgreSQL
                      â”‚
                      â–¼
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

â†“

URL

â†“

APIView

â†“

Authentication

â†“

Permission Check

â†“

Serializer Validation

â†“

Service Layer

â†“

Model

â†“

Database

â†“

Response Formatter

â†“

HTTP Response

If validation fails, the request immediately returns a standardized error response.

If any business rule fails, the Service Layer raises a custom exception.

11. Project Structure
finance_erp_backend/

â”œâ”€â”€ manage.py
â”œâ”€â”€ requirements.txt
â”œâ”€â”€ .env
â”œâ”€â”€ README.md
â”‚
â”œâ”€â”€ config/
â”‚   â”œâ”€â”€ settings/
â”‚   â”œâ”€â”€ urls.py
â”‚   â”œâ”€â”€ asgi.py
â”‚   â”œâ”€â”€ wsgi.py
â”‚   â””â”€â”€ __init__.py
â”‚
â”œâ”€â”€ apps/
â”‚   â”œâ”€â”€ accounts/
â”‚   â”œâ”€â”€ masters/
â”‚   â”œâ”€â”€ guest_workspace/
â”‚   â”œâ”€â”€ finance/
â”‚   â”œâ”€â”€ employees/
â”‚   â”œâ”€â”€ subscriptions/
â”‚   â”œâ”€â”€ integrations/
â”‚   â”œâ”€â”€ audit_logs/
â”‚   â””â”€â”€ common/
â”‚
â”œâ”€â”€ media/
â”œâ”€â”€ static/
â”œâ”€â”€ logs/
â””â”€â”€ scripts/
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

    workspace_service.py

    customer_service.py

    collection_service.py

    expense_service.py

    dashboard_service.py

    report_service.py

Every future application must follow this convention.

13. Service Package Structure

Large applications should never contain a single services.py file.

Instead, services are grouped by domain.

Example:

services/

customer_service.py

loan_service.py

collection_service.py

expense_service.py

dashboard_service.py

analytics_service.py

report_service.py

Each file contains one primary service class.

Example:

CustomerService

LoanService

CollectionService

ExpenseService

DashboardService

This keeps each file focused and maintainable.

14. Common Module

The common application contains reusable infrastructure shared across all apps.

Responsibilities
Base API Views
Base Services
Response Helpers
Custom Exceptions
Pagination Classes
Utility Functions
Validators
Constants
Permission Mixins
Date Utilities
File Upload Helpers
Export Utilities

No business-specific code should be placed in the common module.

15. Base Service

Every service class should inherit from a common base service.

Responsibilities include:

Success response formatting
Error response helpers
Common validation methods
Transaction helpers
Logging helpers
Audit helpers

Example:

class BaseService:

    @staticmethod
    def success(data=None, message="Success"):
        ...

    @staticmethod
    def failure(message, errors=None):
        ...
16. Naming Conventions

The project follows consistent naming conventions.

Models

Singular names.

Examples:

Customer

Loan

Collection

Expense
Services
CustomerService

LoanService

CollectionService

ExpenseService
Views
CustomerListCreateAPIView

CustomerDetailAPIView

CollectionCreateAPIView

DashboardAPIView
Serializers
CustomerCreateSerializer

CustomerUpdateSerializer

CustomerDetailSerializer

CustomerListSerializer
URLs

Use plural nouns.

/customers/
/collections/
/expenses/
/reports/
17. API Versioning

Every endpoint must be versioned.

Example:

/api/v1/auth/
/api/v1/customers/
/api/v1/collections/
/api/v1/dashboard/

Future releases will use:

/api/v2/

without breaking older clients.

18. Database Standards

All database tables must follow common conventions.

Every table includes:

id
created_at
updated_at

Where applicable:

created_by
updated_by
is_active
remarks

Foreign keys should use:

on_delete=PROTECT

for critical business data, unless a different deletion strategy is explicitly required.

Primary business entities should use UUIDs for external-facing identifiers if needed in future integrations, while internal integer IDs can be retained based on performance and business requirements.

Next Chapter (Chapter 3)

The next section will start the actual implementation specification with:

accounts App
Purpose
Models
Fields
Relationships
Serializers
Validation Rules
Service Classes
Business Rules
Views
URLs
Authentication Flow
JWT Flow
OTP Flow
Guest Login Flow
Upgrade-to-ERP Flow

After accounts, we'll proceed to masters, and then to the largest and most important section: guest_workspace, where every model, service, API, business rule, and workflow for Version 1 will be documented in exhaustive detail.



------

Chapter 3 â€” accounts Application
19. Purpose

The accounts application is responsible for identity, authentication, account lifecycle, session security, and future role-based access control.

For V1, its major responsibility is authenticating Guest Workspace owners. The authentication design must still be reusable in V2 when Guest users can upgrade into Lenders and Lenders can create Employees.

A critical architectural rule is:

Do not create separate authentication models for Guest, Lender, Employee, and Admin.

All authenticated people use the same User model. Their capabilities are determined through account type, workspace/business relationships, permissions, subscription state, and related profile records.

This prevents major authentication migrations when V2 is introduced.

20. Version Scope
V1 â€” Major Priority

The accounts app must support:

Guest registration
Mobile-number authentication
OTP verification
Password creation
Login
JWT access tokens
JWT refresh tokens
Logout
Forgot password
Reset password
Change password
Current-user profile
Account activation/deactivation handling
Login history
Basic session/device tracking
Guest Workspace creation after registration
Authentication security
Rate limiting for sensitive endpoints
V2

The same authentication system expands to support:

Lender accounts
Employee accounts
Super Admin
Role-Based Access Control
Employee invitation
Business-level permissions
Device/session management
Subscription-related access restrictions
Optional multi-device controls
OTP via SMS add-on where applicable
WhatsApp-based notifications where applicable
21. Account Types

The system should define account types centrally.

class AccountType(models.TextChoices):
    GUEST = "guest", "Guest"
    LENDER = "lender", "Lender"
    EMPLOYEE = "employee", "Employee"
    ADMIN = "admin", "Admin"
V1

Primarily:

guest
admin
V2

Adds:

lender
employee

The account type identifies the broad category of the user.

It must not replace proper permissions.

For example, two Employees may eventually have different permissions even though both have:

account_type = employee
22. accounts/models.py
22.1 User Model
Purpose

User represents every authenticated person on the platform.

It should extend Django's AbstractBaseUser and PermissionsMixin.

Recommended class:

class User(AbstractBaseUser, PermissionsMixin):
    ...
User Fields
id

Primary identifier.

Recommended:

BigAutoField
public_id

UUID used when exposing user identifiers externally.

UUIDField
unique=True
editable=False

This avoids exposing sequential database IDs in public APIs where unnecessary.

mobile_number

Primary login identifier for V1.

Properties:

unique
indexed
required

Store numbers in normalized international format where possible.

Example:

+919876543210
email

Optional during V1.

Properties:

nullable
blank allowed
unique when provided

Can later support email authentication and communication.

full_name

User's display name.

account_type

Choices:

guest
lender
employee
admin

Default:

guest
is_mobile_verified

Indicates whether mobile verification has been completed.

Default:

False
is_email_verified

Default:

False
is_active

Controls account access.

Default:

True

If false, authentication must fail.

is_staff

Used for Django administration access.

is_superuser

Handled through PermissionsMixin.

last_login

Django authentication field.

last_activity_at

Used to record recent platform activity.

created_at

Automatic creation timestamp.

updated_at

Automatic modification timestamp.

User Database Rules

mobile_number must be normalized before persistence.

Duplicate verified accounts using the same mobile number are prohibited.

Indexes should exist for:

mobile_number
public_id
account_type
is_active
23. UserManager

A custom user manager must be implemented.

UserManager
Methods
create_user()

create_superuser()
create_user()

Responsibilities:

Validate mobile number.
Normalize mobile number.
Normalize email if provided.
Hash password.
Set account type.
Create user.
Return user.

Passwords must never be manually hashed.

Always use:

user.set_password(password)
24. OTP Model
Purpose

Stores temporary verification codes required during authentication-related operations.

Recommended model:

OTPVerification
Fields
id
user
mobile_number
purpose
otp_hash
expires_at
attempt_count
max_attempts
is_verified
verified_at
created_at
OTP Purpose Choices
registration
login
forgot_password
mobile_change
account_verification

V1 primarily uses:

registration
forgot_password
25. OTP Security Rules

Plain OTP values should not be permanently stored.

Prefer storing a hash of the OTP.

OTP should have a short expiry.

Recommended default:

5 minutes

Maximum verification attempts should be configurable.

Example:

5 attempts

After reaching the maximum:

OTP becomes invalid.

Resending OTP should invalidate or supersede the previous usable OTP for the same purpose.

Rate limiting must prevent repeated OTP abuse.

26. OTP Delivery in V1

There is an important distinction between authentication OTP and the future customer communication SMS add-on.

SMS Gateway and WhatsApp Business features are planned as premium ERP add-ons.

However, if V1 registration requires real mobile OTP authentication, the platform itself still needs an authentication OTP delivery provider.

Therefore authentication OTP infrastructure should be treated as a platform security cost, not as the lender's SMS add-on.

Alternatively, V1 can initially use:

Email verification
+
Password

until mobile OTP infrastructure is enabled.

The backend should support both approaches.

27. LoginHistory Model
Purpose

Records important authentication activity.

Fields:

id
user
login_at
logout_at
ip_address
user_agent
device_type
browser
operating_system
login_status
failure_reason
created_at

Possible statuses:

success
failed
blocked

This will help with security investigations and future account activity screens.

28. UserSession Model
Purpose

Represents authenticated devices/sessions.

Fields:

id
user
session_id
refresh_token_identifier
device_name
device_type
ip_address
user_agent
last_activity_at
expires_at
is_active
created_at
revoked_at

V1 can implement basic session tracking.

V2 can expose complete device management to users.

Example future screen:

Chrome â€” Windows
Hyderabad
Active now

Android
Rajahmundry
Last active 2 hours ago
29. Why Refresh Tokens Should Not Be Stored Raw

Never store usable JWT refresh tokens directly.

If session identification is required, store:

JTI

or another non-secret identifier.

SimpleJWT blacklist functionality can be used for revoked tokens.

30. Authentication Relationships

Conceptually:

User
 â”‚
 â”œâ”€â”€ OTPVerification
 â”‚
 â”œâ”€â”€ LoginHistory
 â”‚
 â”œâ”€â”€ UserSession
 â”‚
 â””â”€â”€ GuestWorkspace

V2 expands this to:

User
 â”‚
 â”œâ”€â”€ GuestWorkspace
 â”‚
 â”œâ”€â”€ BusinessMembership
 â”‚
 â””â”€â”€ EmployeeProfile

This is why User must remain independent from Guest Workspace.

31. accounts/serializers.py

Separate serializers should be created for individual operations rather than using one large UserSerializer.

Required V1 serializers:

GuestRegistrationSerializer
OTPRequestSerializer
OTPVerifySerializer
LoginSerializer
TokenRefreshSerializer
ForgotPasswordSerializer
ResetPasswordSerializer
ChangePasswordSerializer
UserProfileSerializer
UserProfileUpdateSerializer
LogoutSerializer
32. GuestRegistrationSerializer
Input
full_name
mobile_number
email (optional)
password
confirm_password
Validation

Must verify:

Name is provided.
Mobile number format is valid.
Mobile number is normalized.
Mobile number isn't already registered.
Email format is valid if provided.
Password satisfies security requirements.
password == confirm_password.

The serializer does not create the user directly.

After validation:

AccountService.register_guest(...)

performs the actual creation.

33. OTPRequestSerializer

Input:

mobile_number
purpose

Validation:

Valid mobile format.
Supported OTP purpose.
Account state appropriate for requested purpose.

Example:

For:

forgot_password

the account should exist.

For:

registration

an already verified account should not be recreated.

34. OTPVerifySerializer

Input:

mobile_number
otp
purpose

Validation ensures basic input structure only.

Actual OTP comparison, expiry checks, attempt management, and verification state changes belong to:

OTPService

because these are business/security operations.

35. LoginSerializer

Input:

identifier
password

For V1, identifier primarily represents mobile number.

Future versions may allow:

mobile
email

Validation checks field presence.

Authentication itself should be handled through:

AuthService.login()
36. ChangePasswordSerializer

Input:

current_password
new_password
confirm_password

Validate:

new_password == confirm_password

Actual current-password verification and password modification occur in the service.

37. UserProfileSerializer

Output:

public_id
full_name
mobile_number
email
account_type
is_mobile_verified
is_email_verified
created_at

Sensitive internal fields must never be exposed.

38. accounts/services/

Recommended structure:

accounts/
â””â”€â”€ services/
    â”œâ”€â”€ __init__.py
    â”œâ”€â”€ auth_service.py
    â”œâ”€â”€ account_service.py
    â”œâ”€â”€ otp_service.py
    â””â”€â”€ session_service.py
39. AccountService
class AccountService:
    ...

Required methods:

register_guest()

get_profile()

update_profile()

change_mobile_number()

deactivate_account()

reactivate_account()
40. register_guest()

This is one of the most important V1 service methods.

Input

Validated registration data.

Transaction

Must execute inside:

transaction.atomic()
Flow
Start Transaction
      â†“
Check Mobile Uniqueness
      â†“
Create User
      â†“
Set account_type = guest
      â†“
Create Guest Workspace
      â†“
Create Default Workspace Settings
      â†“
Create Audit Event
      â†“
Commit

If Guest Workspace creation fails, the User must not remain partially created.

The complete transaction rolls back.

41. Important Cross-App Dependency

AccountService.register_guest() needs functionality from:

guest_workspace

Avoid putting Guest Workspace creation logic inside AccountService.

Instead:

workspace = GuestWorkspaceService.create_default_workspace(
    owner=user
)

Therefore:

AccountService
        â”‚
        â–¼
GuestWorkspaceService

This preserves domain ownership.

42. AuthService

Required methods:

login()

logout()

refresh_token()

forgot_password()

reset_password()

validate_account_access()
43. login()
Flow
Receive Identifier + Password
          â†“
Normalize Identifier
          â†“
Find User
          â†“
Validate Password
          â†“
Check is_active
          â†“
Check Account Restrictions
          â†“
Generate JWT
          â†“
Create/Update UserSession
          â†“
Create LoginHistory
          â†“
Return Tokens + User

Response should contain:

{
  "access": "...",
  "refresh": "...",
  "user": {},
  "workspace": {}
}

Workspace information may be minimal.

This prevents the frontend from making unnecessary authentication bootstrap calls.

44. JWT Strategy

Use SimpleJWT.

Recommended token structure:

Access Token

Short-lived.

Example:

15â€“30 minutes
Refresh Token

Longer-lived.

Example:

7â€“30 days

Exact values must be environment-configurable.

Never hardcode token lifetimes inside service classes.

45. JWT Claims

Only include claims that are genuinely useful.

Example:

user_id
account_type

Avoid putting frequently changing information into JWTs.

For example, don't store:

customer_count
subscription_expiry
permissions list

unless there is a clear reason.

Database/cache checks should handle dynamic authorization information.

46. Logout

Logout must:

Validate refresh token.
Blacklist/revoke token.
Mark corresponding session inactive.
Store logout timestamp.
Record security/audit event.

The frontend deleting a token alone is not sufficient for secure logout.

47. OTPService

Required methods:

generate_otp()

send_otp()

verify_otp()

resend_otp()

invalidate_otp()

check_rate_limit()
48. OTP Generation Flow
OTP Request
    â†“
Rate Limit Check
    â†“
Generate Secure Random OTP
    â†“
Hash OTP
    â†“
Store OTP Record
    â†“
Set Expiry
    â†“
Send OTP

Do not use predictable random number generation for authentication OTPs.

49. OTP Verification Flow
Mobile + OTP
      â†“
Find Latest Active OTP
      â†“
Check Expiry
      â†“
Check Attempt Limit
      â†“
Compare Hash
      â†“
Wrong?
 â”Œâ”€â”€â”€â”€â”´â”€â”€â”€â”€â”
Yes       No
 â”‚         â”‚
Increase   Mark Verified
Attempts   â†“
 â”‚         Update User Verification
Return     â†“
Error      Return Success
50. SessionService

Methods:

create_session()

update_activity()

revoke_session()

revoke_all_sessions()

get_active_sessions()

Full session management UI is V2, but implementing a simple internal session model in V1 makes future security features easier.

51. Views

Use DRF class-based views.

Recommended views:

GuestRegistrationAPIView

OTPRequestAPIView

OTPVerifyAPIView

LoginAPIView

LogoutAPIView

TokenRefreshAPIView

ForgotPasswordAPIView

ResetPasswordAPIView

ChangePasswordAPIView

CurrentUserAPIView

UserProfileUpdateAPIView
52. GuestRegistrationAPIView
Permission
AllowAny
Flow
Request
   â†“
GuestRegistrationSerializer
   â†“
Validation
   â†“
AccountService.register_guest()
   â†“
Return User + Workspace

The view must not call:

User.objects.create(...)

directly.

53. LoginAPIView

Permission:

AllowAny

Responsibilities:

Execute serializer.
Read request metadata.
Pass device/IP information to service.
Call AuthService.login().
Return standardized response.
54. CurrentUserAPIView

Permission:

IsAuthenticated

Returns:

User Profile
Account Type
Workspace Summary
Feature Access

This endpoint becomes useful when the frontend reloads.

Recommended endpoint:

GET /api/v1/auth/me/
55. Authentication URLs
POST /api/v1/auth/register/
POST /api/v1/auth/login/

POST /api/v1/auth/otp/request/
POST /api/v1/auth/otp/verify/
POST /api/v1/auth/otp/resend/

POST /api/v1/auth/token/refresh/

POST /api/v1/auth/logout/

POST /api/v1/auth/password/forgot/
POST /api/v1/auth/password/reset/
POST /api/v1/auth/password/change/

GET   /api/v1/auth/me/
PATCH /api/v1/auth/me/
56. Authentication API Response

Example successful login:

{
  "success": true,
  "message": "Login successful.",
  "data": {
    "access_token": "<token>",
    "refresh_token": "<token>",
    "user": {
      "public_id": "uuid",
      "full_name": "Ramesh",
      "mobile_number": "+919876543210",
      "account_type": "guest"
    },
    "workspace": {
      "public_id": "uuid",
      "name": "Ramesh Finance"
    }
  }
}
57. Failed Login Response

The API should avoid exposing whether a particular mobile number exists when doing so creates account-enumeration risk.

Example:

{
  "success": false,
  "message": "Invalid login credentials.",
  "errors": {}
}

Avoid:

Mobile number exists but password is wrong.
58. Authentication Permissions
Public
Registration
Login
OTP Request
OTP Verification
Forgot Password
Reset Password
Token Refresh
Authenticated
Profile
Change Password
Logout
Workspace APIs
59. Account State Rules

Authentication should be rejected when:

is_active = False

Future V2 states can include:

business suspended
employee terminated
subscription restrictions

These checks should eventually flow through:

AuthService.validate_account_access()

rather than being duplicated across endpoints.

60. Rate Limiting

Sensitive endpoints require throttling.

Particularly:

/login/
/otp/request/
/otp/verify/
/password/forgot/
/password/reset/

Limits should be configurable by environment.

Rate limiting can initially use DRF throttling.

Redis-backed throttling can be introduced when production traffic justifies it.

61. Password Security

Passwords must use Django's configured password hashers.

Requirements should include:

Minimum length.
Common-password rejection.
Numeric-only password rejection.
Similarity validation.
Compromised/common-password policies where practical.

Never:

Log passwords.
Return passwords.
Store plaintext passwords.
Include passwords in audit records.
62. Account Upgrade Strategy

This is an important architecture decision.

When a Guest Workspace user upgrades to the ERP in V2, do not create another User account.

Current:

User
account_type = guest
       â”‚
       â–¼
Guest Workspace

Upgrade:

Same User
       â”‚
       â”œâ”€â”€ account_type â†’ lender
       â”‚
       â–¼
Business / Finance Workspace

Authentication history remains intact.

No new password.

No duplicate mobile number.

No second identity.

63. Upgrade Transaction

Future UpgradeService should perform:

Validate Guest Account
        â†“
Validate Upgrade Eligibility
        â†“
Create Business Profile
        â†“
Convert/Attach Existing Workspace
        â†“
Preserve Customers
        â†“
Preserve Collections
        â†“
Preserve Expenses
        â†“
Assign Owner Membership
        â†“
Change Account Type
Guest â†’ Lender
        â†“
Activate Subscription
        â†“
Create Audit Log
        â†“
Commit

This entire operation must be atomic.

64. V2 RBAC Preparation

Do not implement complicated RBAC during V1 unless needed.

But the architecture should prepare for:

Business
   â”‚
   â”œâ”€â”€ Owner
   â”œâ”€â”€ Manager
   â”œâ”€â”€ Collector
   â””â”€â”€ Custom Role

Eventually:

User
   â”‚
BusinessMembership
   â”‚
Role
   â”‚
Permissions

This is better than adding dozens of Boolean fields like:

can_create_customer
can_edit_customer
can_delete_customer
can_view_reports
...

directly to User.

65. Audit Requirements

Important authentication events should be auditable:

Registration
OTP verification
Login success
Login failure
Logout
Password change
Password reset
Mobile number change
Account deactivation
Account upgrade

Sensitive information must not be stored in audit payloads.

66. accounts V1 Completion Criteria

The accounts module is considered complete for Version 1 when a new user can:

Register
   â†“
Verify Identity
   â†“
Automatically Receive Guest Workspace
   â†“
Login
   â†“
Receive JWT
   â†“
Access Protected APIs
   â†“
Refresh Session
   â†“
Manage Profile
   â†“
Change/Reset Password
   â†“
Logout Securely

and the architecture can later convert the same identity into a Lender without recreating the account.

Chapter 4 â€” masters Application

The next implementation module is masters.

This app is important because Guest Workspace should not store free-text versions of everything. Collection frequencies, expense categories, states, districts, and similar reusable data should have controlled sources.

The detailed masters specification will define:

Location Masters: State â†’ District â†’ City/Town â†’ Village/Post Office, PIN-code lookup, external dataset synchronization, and lender-defined areas.

Finance Masters: collection frequencies, interest types, payment modes, collection statuses and business categories.

Expense Masters: default expense categories plus workspace-custom categories.

Architecture: every model and field, serializers, MasterDataService, LocationService, caching strategy, APIs, filtering/search, seed/import strategy, external API synchronization, and the important distinction between platform master locations and business-created collection areas.


----------

Chapter 4 â€” masters Application
67. Purpose

The masters application manages reusable reference data shared across the entire platform.

The objective is to prevent inconsistent free-text values such as:

Daily
daily
DAILY
Day Wise
Every Day

Instead, the backend maintains standardized master values that can be consumed by Guest Workspace in V1 and the full Finance ERP in V2.

The masters application will primarily manage:

Geographic reference data.
Collection frequencies.
Interest types.
Payment modes.
Collection statuses.
Expense categories.
Business categories.
Future loan categories.
Future employee designations.
Future document types.

A major architectural distinction must exist between official geographic locations and finance-business operational areas.

For example:

State
  â†“
District
  â†“
City/Town
  â†“
Village/Locality

are geographic reference data.

But:

Market Route
Railway Station Area
East Collection Area
Route 2

are operational areas created by a finance business.

Operational areas therefore must not be stored in masters. They belong to the workspace/business domain.

68. Version Scope
V1 â€” Required

The following master data is required for Guest Workspace:

States
Districts
Cities/Towns
Villages/Localities where available
PIN/postal information where available
Collection Frequencies
Interest Types
Payment Modes
Collection Statuses
Expense Categories
Business Categories

Guest users should also be able to create their own expense categories where permitted.

V2

Additional master data will include:

Loan Categories
Employee Designations
Document Types
Leave Types
Salary Components
Penalty Types
Notification Types
Route Types
Branch Types
Business Roles
Additional finance configuration.
69. masters/models.py

Recommended core models:

State
District
City
Village
PostalLocation

CollectionFrequency
InterestType
PaymentMode
CollectionStatus

ExpenseCategory
BusinessCategory

Future models:

LoanCategory
EmployeeDesignation
DocumentType
PenaltyType
LeaveType
70. State Model
Purpose

Stores state/union territory information.

Fields
id
public_id
name
code
country_code
is_active
source
external_id
created_at
updated_at
name

Example:

Andhra Pradesh
Telangana
Tamil Nadu
Karnataka

Must be indexed.

code

Optional standardized code.

country_code

V1:

IN

This allows international expansion without redesigning the table.

source

Identifies where the record originated.

Choices could include:

system
government_dataset
external_api
manual
external_id

Stores the identifier used by an imported dataset/API.

It should not become the application's primary key.

71. District Model

Relationship:

State
  â”‚
  â””â”€â”€ District
Fields
id
public_id
state
name
code
is_active
source
external_id
created_at
updated_at
Constraints

The same district name should not be duplicated within the same state.

Recommended logical constraint:

unique(state, name)

Indexes:

state
name
is_active
72. City Model

Represents cities, towns, municipalities, or similar locality levels used by the platform.

Fields
id
public_id
district
name
location_type
latitude
longitude
is_active
source
external_id
created_at
updated_at
Location Type

Possible values:

city
town
municipality
other

Relationship:

State
 â†“
District
 â†“
City

The state does not need to be duplicated on City because it can be obtained through:

city.district.state
73. Village Model

Represents villages or lower-level geographic reference locations.

Fields
id
public_id
district
city (nullable)
name
latitude
longitude
postal_code
is_active
source
external_id
created_at
updated_at

A village may not always belong cleanly to a city, so city should remain nullable.

Relationship can therefore be:

District
   â”‚
   â”œâ”€â”€ City
   â”‚
   â””â”€â”€ Village

rather than forcing every village through a city.

74. PostalLocation Model

Because PIN-code/post-office data doesn't always map perfectly to the City/Village hierarchy, postal information should be modeled separately rather than forcing everything into Village.

Fields
id
postal_code
post_office_name
branch_type
delivery_status
district_name
state_name
latitude
longitude
source
is_active
created_at
updated_at

This supports flows such as:

User enters PIN
      â†“
Backend searches PostalLocation
      â†“
Return matching post offices
      â†“
Frontend suggests address information
75. Why Location Data Should Be Stored Locally

The application should not call external APIs every time the frontend requests states or districts.

Avoid:

Frontend
 â†“
Backend
 â†“
External Location API
 â†“
Response

for every dropdown interaction.

Preferred:

Government/API Dataset
       â†“
Periodic Import
       â†“
PostgreSQL
       â†“
Masters API
       â†“
Frontend

Advantages:

Faster APIs.
Lower external API costs.
Reduced downtime dependency.
Predictable frontend behavior.
Easier searching.
Better reporting.
Consistent identifiers.
76. External Location Import

A service should manage imports.

class LocationImportService:
    ...

Methods:

import_states()
import_districts()
import_cities()
import_villages()
import_postal_locations()

update_existing_locations()
deactivate_removed_locations()

sync_location_dataset()

Imports must be idempotent.

Running the same import twice must not create duplicate records.

77. Location Import Rules

Imported data should use:

source
external_id

to identify origin.

Example:

source = government_dataset
external_id = 123456

Never rely exclusively on names for synchronization because names can change.

Changes should update existing records rather than creating unnecessary duplicates.

78. Location Data Deletion

Geographic master data referenced by customers should generally not be physically deleted.

Instead:

is_active = False

This preserves historical customer records.

For example, if an administrative boundary changes, an old customer's address should remain historically understandable.

79. CollectionFrequency Model
Purpose

Defines how frequently a customer is expected to make collections/payments.

V1 Values
daily
weekly
monthly

The architecture should support future frequencies without migrations.

Fields
id
code
name
description
sort_order
is_active
created_at
updated_at

Example:

code = daily
name = Daily
80. Why Frequency Should Be Master Data

Do not hardcode everywhere:

if frequency == "daily":

where avoidable.

Business calculations may use stable frequency codes, while the UI label remains configurable.

This also makes future options possible:

fortnightly
biweekly
custom

without rewriting every frontend dropdown.

81. InterestType Model
Purpose

Defines supported methods of representing/calculating interest.

Initial values may include:

flat_percentage
fixed_amount
monthly_percentage

The exact supported calculations should remain intentionally limited in V1.

Fields
id
code
name
description
is_active
created_at
updated_at

Important:

InterestType defines what type of calculation is used.

The actual:

interest_rate
interest_amount

belongs to the customer's finance/loan record.

82. PaymentMode Model

The application does not process customer payments in V1. Payment Mode only records how the lender says the money was received.

Initial values:

cash
upi
bank_transfer
cheque
other
Fields
id
code
name
description
is_active
sort_order
created_at
updated_at

This distinction is important:

Recording UPI does not mean the platform processed the UPI payment.

It is simply accounting/collection metadata.

83. CollectionStatus Model

Defines the outcome of an expected collection.

Initial values:

paid
partial
pending
customer_unavailable
promise_to_pay
holiday
skipped
defaulted
Fields
id
code
name
description
requires_reason
affects_outstanding
is_active
sort_order
created_at
updated_at
84. requires_reason

Certain statuses should require remarks/reasons.

For example:

customer_unavailable â†’ true
promise_to_pay â†’ true
skipped â†’ true
defaulted â†’ true

While:

paid â†’ false

The frontend can use this metadata to dynamically display a reason field.

The backend must still validate it.

85. ExpenseCategory Model
Purpose

Defines categories for business expenses.

Default platform categories:

fuel
food
parking
vehicle_maintenance
office
travel
other
Fields
id
workspace
code
name
description
is_system
is_active
created_by
created_at
updated_at

Here we need an important exception to normal master design.

86. System vs Workspace Expense Categories

Users may want custom categories.

Example:

Tea
Collector Petrol
Bike Repair
Festival Expense
Printing

Therefore ExpenseCategory needs to support:

System Category
workspace = NULL
is_system = True

Available to everyone.

Custom Workspace Category
workspace = GuestWorkspace
is_system = False

Available only to that workspace.

The visible categories for a workspace become:

System Categories
       +
Workspace Categories

This pattern can later be reused for other customizable master data.

87. BusinessCategory Model

Purpose:

Identify the general business/finance operation type.

Possible initial values:

daily_finance
weekly_finance
monthly_finance
mixed_finance
other

Fields:

id
code
name
description
is_active
created_at
updated_at

This is primarily useful during onboarding and analytics.

88. Master Data Ownership Rules

Master data falls into three categories.

Platform-Owned

Examples:

State
District
CollectionFrequency
InterestType
PaymentMode
CollectionStatus

Only Admin/system import processes modify these.

Workspace-Customizable

Example:

ExpenseCategory

Users can create custom values for their own workspace.

Business-Owned V2

Examples:

Area
Route
Employee Designation Override
Business-specific Settings

These belong outside masters.

89. masters/serializers.py

Required serializers include:

StateSerializer
DistrictSerializer
CitySerializer
VillageSerializer
PostalLocationSerializer

CollectionFrequencySerializer
InterestTypeSerializer
PaymentModeSerializer
CollectionStatusSerializer

ExpenseCategorySerializer
ExpenseCategoryCreateSerializer

BusinessCategorySerializer

Most master serializers are read-only for normal users.

90. Location Serializer Structure

Example district response:

{
  "id": 12,
  "name": "East Godavari",
  "state": {
    "id": 1,
    "name": "Andhra Pradesh"
  }
}

For list APIs, avoid unnecessary deep nesting.

A lighter response may be:

{
  "id": 12,
  "name": "East Godavari",
  "state_id": 1
}

Detailed serializers can provide nested information when required.

91. ExpenseCategoryCreateSerializer

Input:

name
description

Workspace must not be accepted from the frontend.

Avoid:

{
  "workspace_id": 27
}

The authenticated user's workspace must be determined server-side.

This prevents one workspace from creating data inside another workspace.

92. masters/services/

Recommended structure:

masters/
â””â”€â”€ services/
    â”œâ”€â”€ __init__.py
    â”œâ”€â”€ master_data_service.py
    â”œâ”€â”€ location_service.py
    â”œâ”€â”€ location_import_service.py
    â””â”€â”€ expense_category_service.py
93. MasterDataService
class MasterDataService:
    ...

Methods:

get_collection_frequencies()
get_interest_types()
get_payment_modes()
get_collection_statuses()
get_business_categories()

get_guest_workspace_bootstrap_data()
94. Bootstrap Master API

Instead of making the frontend call:

/frequencies/
/interest-types/
/payment-modes/
/collection-statuses/
/business-categories/

every time the application loads, provide a bootstrap endpoint.

Example:

GET /api/v1/masters/bootstrap/

Response:

{
  "collection_frequencies": [],
  "interest_types": [],
  "payment_modes": [],
  "collection_statuses": [],
  "expense_categories": [],
  "business_categories": []
}

This significantly reduces initial API calls.

Individual endpoints should still exist for independent use.

95. LocationService
class LocationService:
    ...

Methods:

get_states()

get_districts(state_id)

get_cities(district_id)

get_villages(district_id, city_id=None)

search_locations(query)

lookup_postal_code(postal_code)

resolve_location_hierarchy()

get_location_details()
96. Cascading Location Flow

Frontend onboarding should work like:

Select State
    â†“
GET districts?state_id=
    â†“
Select District
    â†“
GET cities?district_id=
    â†“
Select City
    â†“
GET villages?city_id=

Each query must be filtered at database level.

Do not retrieve all Indian villages and filter them in React.

97. Location Search

A generic search endpoint can support users who don't know the hierarchy.

Example:

GET /api/v1/masters/locations/search/?q=anaparthi

Possible response:

Anaparthi â€” Town
Anaparthi â€” Post Office
Anaparthi â€” Mandal/Locality

Results should include enough parent information to distinguish duplicate names.

98. PIN Code Lookup

Endpoint:

GET /api/v1/masters/postal-code/533342/

Possible response:

{
  "postal_code": "533342",
  "state": "Andhra Pradesh",
  "district": "East Godavari",
  "locations": [
    {
      "name": "Anaparthi",
      "type": "Post Office"
    }
  ]
}

This can make Guest Workspace customer creation significantly faster.

99. ExpenseCategoryService

Methods:

get_available_categories()

create_workspace_category()

update_workspace_category()

deactivate_workspace_category()

restore_workspace_category()
100. Expense Category Business Rules

A guest can modify only categories belonging to their workspace.

System categories cannot be:

Renamed by Guest.
Deleted by Guest.
Modified by Guest.

A workspace category can be deactivated rather than deleted if historical expenses reference it.

Example:

Fuel
 â†“
Used by 400 Expense Records
 â†“
User Deletes Category
 â†“
Set is_active=False

Historical expenses remain intact.

101. Master Data Views

Recommended DRF class-based views:

MasterBootstrapAPIView

StateListAPIView
DistrictListAPIView
CityListAPIView
VillageListAPIView

LocationSearchAPIView
PostalCodeLookupAPIView

CollectionFrequencyListAPIView
InterestTypeListAPIView
PaymentModeListAPIView
CollectionStatusListAPIView
BusinessCategoryListAPIView

ExpenseCategoryListCreateAPIView
ExpenseCategoryDetailAPIView
102. View Responsibilities

Example:

DistrictListAPIView

View performs:

Parse state_id.
Validate query parameter.
Apply filters.
Call service.
Apply pagination if necessary.
Serialize.
Return response.

It should not contain:

District.objects.filter(...)

because query/CRUD behavior belongs in services according to your architecture.

The service performs the actual database operation.

103. Master URLs

Recommended:

GET /api/v1/masters/bootstrap/

GET /api/v1/masters/states/
GET /api/v1/masters/districts/?state_id=
GET /api/v1/masters/cities/?district_id=
GET /api/v1/masters/villages/?district_id=&city_id=

GET /api/v1/masters/locations/search/?q=
GET /api/v1/masters/postal-code/{postal_code}/

GET /api/v1/masters/collection-frequencies/
GET /api/v1/masters/interest-types/
GET /api/v1/masters/payment-modes/
GET /api/v1/masters/collection-statuses/
GET /api/v1/masters/business-categories/

GET  /api/v1/masters/expense-categories/
POST /api/v1/masters/expense-categories/

PATCH  /api/v1/masters/expense-categories/{id}/
DELETE /api/v1/masters/expense-categories/{id}/
104. Permissions
Public or Semi-Public

Depending on frontend requirements:

States
Districts
Cities
Business Categories

can potentially be accessible without authentication.

However, there is little benefit in exposing the entire master API publicly.

Recommended V1:

IsAuthenticated

for application master endpoints.

Public registration can use a limited onboarding master endpoint if required.

105. Caching Strategy

Master data is ideal for caching because it changes infrequently.

Examples:

States
Collection Frequencies
Payment Modes
Interest Types

V1 does not require Redis just to launch the product.

Django's local/database cache can initially be used if necessary.

When Redis is introduced:

Request
   â†“
MasterDataService
   â†“
Redis Cache
   â”‚
   â”œâ”€â”€ Hit â†’ Return
   â”‚
   â””â”€â”€ Miss
          â†“
      PostgreSQL
          â†“
       Cache
          â†“
       Return

Cache invalidation occurs when Admin modifies master data.

106. Location Data and Google Maps

These two systems serve different purposes.

Masters Database

Used for:

State
District
City
Village
PIN Code
Structured addresses
Filters
Reports
Google Maps

Used where necessary for:

Address autocomplete.
Geocoding.
Reverse geocoding.
GPS coordinate â†’ address conversion.
Maps.
Future route optimization.

Do not replace your internal master database with Google Places.

107. V1 GPS Consideration

Guest Workspace does not require GPS to provide its core digital collection-book functionality.

Therefore GPS should remain optional in V1.

If the user chooses:

Use Current Location

the frontend obtains:

latitude
longitude

using the browser/device Geolocation API.

The backend may then use an integration service to reverse-geocode the location.

108. Google Integration Boundary

masters must not directly contain Google API implementation.

Correct architecture:

Guest Workspace
      â†“
LocationService
      â†“
Integrations
      â†“
Google Maps

For example:

GoogleMapsService.reverse_geocode(
    latitude,
    longitude
)

LocationService can map the result to internal location records.

This allows Google to be replaced later without rewriting Guest Workspace.

109. Data Integrity

All master tables should use appropriate constraints.

Examples:

State:
unique(country_code, name)

District:
unique(state, name)

CollectionFrequency:
unique(code)

InterestType:
unique(code)

PaymentMode:
unique(code)

CollectionStatus:
unique(code)

Indexes should be added for frequently queried fields.

Avoid adding indexes blindly to every column.

110. Master Data Seed Strategy

V1 should ship with seed data for finance-related masters.

Example fixture/management command:

python manage.py seed_master_data

It creates:

Collection Frequencies
Interest Types
Payment Modes
Collection Statuses
Expense Categories
Business Categories

The command must be idempotent.

Running it multiple times should not create duplicates.

111. Geographic Import Strategy

Geographic data should use a separate command.

Example:

python manage.py import_india_locations

Potential flags:

--states
--districts
--cities
--villages
--postal
--all

This prevents deployment migrations from becoming dependent on a huge geographic import.

Database migrations and master-data imports should remain separate processes.

112. Do Not Put Huge Data in Django Migrations

Avoid creating migrations containing hundreds of thousands of village records.

Migrations should create schemas.

Management commands/import processes should populate large reference datasets.

This keeps deployments manageable.

113. V2 Admin Management

V2 Super Admin will receive interfaces/APIs for:

Activate/deactivate master values.
Add new finance master values.
Manage expense defaults.
Trigger location synchronization.
Inspect import failures.
View source information.

These operations do not need to be exposed to Guest users.

114. Master Audit Requirements

Changes to configurable masters should eventually generate audit entries.

Examples:

Admin disabled payment mode "Cheque"

Admin created collection frequency "Fortnightly"

Workspace created expense category "Bike Repair"

Location imports do not need millions of individual human-facing audit entries. Import runs should instead have summary logs.

115. Location Import Log

Recommended future/supporting model:

LocationImportLog

Fields:

id
source
started_at
completed_at
status
records_created
records_updated
records_skipped
records_failed
error_summary
created_at

Statuses:

running
completed
partially_completed
failed

This is useful when maintaining large location datasets.

116. masters Request Flow

Example: District selection.

Frontend

GET /masters/districts/?state_id=1

        â†“

DistrictListAPIView

        â†“

Validate state_id

        â†“

LocationService.get_districts()

        â†“

District Model

        â†“

PostgreSQL

        â†“

DistrictSerializer

        â†“

Response
117. Expense Category Creation Flow
Authenticated Guest

        â†“

POST /expense-categories/

        â†“

ExpenseCategoryCreateSerializer

        â†“

Validate Name

        â†“

Resolve User Workspace

        â†“

ExpenseCategoryService
.create_workspace_category()

        â†“

Check Duplicate

        â†“

Create Category

        â†“

Audit

        â†“

Response
118. masters V1 Completion Criteria

The module is complete when Guest Workspace can reliably obtain:

Collection frequencies.
Interest types.
Payment modes.
Collection statuses.
Expense categories.
Business categories.
States.
Districts.
Cities/localities where available.
PIN-based location suggestions.

and when workspace owners can create their own expense categories without modifying global platform data.

Chapter 5 â€” guest_workspace Application

This is now the largest and highest-priority section of V1.

Unlike accounts and masters, this module contains the actual finance business behavior.

The module should be internally divided into these domains:

guest_workspace/

models.py
serializers.py
views.py
urls.py

services/
    workspace_service.py
    customer_service.py
    finance_account_service.py
    collection_service.py
    expense_service.py
    dashboard_service.py
    report_service.py
    calculator_service.py
    import_service.py
    export_service.py

The detailed specification starts with an important data-model decision:

A customer and the money taken by that customer must not be the same record.

For example, Ramesh is a Customer, while:

â‚¹20,000
10% interest
20 weeks
â‚¹1,100/week

is a Finance Account / Loan Record.

This matters because the same customer may borrow again later.

Therefore V1 should already use:

GuestWorkspace
      â”‚
      â”œâ”€â”€ Customer
      â”‚      â”‚
      â”‚      â””â”€â”€ FinanceAccount
      â”‚              â”‚
      â”‚              â”œâ”€â”€ CollectionSchedule
      â”‚              â””â”€â”€ Collection
      â”‚
      â””â”€â”€ Expense

rather than putting loan_amount, interest_rate, tenure, and all collection information directly on the Customer table.

That design decision is crucial because it allows the Guest Workspace to grow into V2 without restructuring all customer data.


-----------------------------

Chapter 5 â€” guest_workspace Application
119. Purpose

The guest_workspace application is the primary business application for Version 1.

Its purpose is to give small lenders and traditional finance businesses a lightweight digital replacement for their physical collection books without requiring them to configure the complete ERP.

A Guest Workspace owner must be able to:

Create a workspace.
Configure basic finance preferences.
Add existing customers.
Add historical/current finance accounts.
Enter how much a customer originally received.
Enter interest and tenure information.
Enter how much the customer had already paid before joining the platform.
Track daily, weekly, and monthly collections.
Record partial payments.
Record missed collections and reasons.
Track outstanding amounts.
Record business expenses.
View today's expected and actual collections.
View historical collections.
View customer payment history.
Calculate finance schedules.
Generate reports.
Export records.
Continue using the workspace over multiple days.
Eventually convert the workspace into a complete ERP account.

The Guest Workspace is therefore not a demo and must not be implemented as temporary session data.

Its records are permanent business records.

120. Core Domain Structure

The most important V1 relationship is:

User
 â”‚
 â–¼
GuestWorkspace
 â”‚
 â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
 â–¼               â–¼
Customer       Expense
 â”‚
 â–¼
FinanceAccount
 â”‚
 â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
 â–¼               â–¼
CollectionSchedule
                 â”‚
                 â–¼
             Collection

More precisely:

GuestWorkspace
â”‚
â”œâ”€â”€ Customers
â”‚     â”‚
â”‚     â””â”€â”€ Finance Accounts
â”‚            â”‚
â”‚            â”œâ”€â”€ Collection Schedules
â”‚            â”‚
â”‚            â””â”€â”€ Collections
â”‚
â”œâ”€â”€ Expenses
â”‚
â”œâ”€â”€ Workspace Settings
â”‚
â””â”€â”€ Activity / Summary Data
121. Why Customer and Finance Account Are Separate

Suppose:

Customer: Ramesh

Ramesh initially takes:

â‚¹10,000
10 weeks
Weekly Collection

After completing it, six months later he takes:

â‚¹25,000
20 weeks
Weekly Collection

If loan information is stored directly inside Customer, the old finance history would either be overwritten or require an increasingly complicated customer table.

Instead:

Ramesh
 â”‚
 â”œâ”€â”€ Finance Account #1
 â”‚
 â”‚     â‚¹10,000
 â”‚
 â”‚     Closed
 â”‚
 â””â”€â”€ Finance Account #2
       â‚¹25,000
       Active

This must be implemented from V1.

122. Terminology: FinanceAccount

Internally, I recommend using:

FinanceAccount

rather than immediately calling everything a Loan.

This keeps the Guest Workspace flexible enough to represent the lender's existing finance arrangement without forcing a complete regulated loan-management workflow into V1.

In the UI, terminology can later be configured as:

Finance
Loan
Account
Borrowing

The backend entity remains consistent.

123. Models

Core models:

GuestWorkspace

GuestWorkspaceSettings

GuestCustomer

GuestFinanceAccount

GuestCollectionSchedule

GuestCollection

GuestExpense

Supporting records can later include:

GuestCustomerNote
GuestCollectionCorrection
GuestImportJob
GuestExportJob
124. GuestWorkspace Model
Purpose

Represents the free digital collection workspace owned by a registered Guest user.

A Guest user should have one primary Guest Workspace in V1.

V2 may allow businesses/workspaces to operate under a more general organization model.

Fields
id

public_id

owner

workspace_name

business_name

business_category

mobile_number

email

state

district

city

village

address_line

postal_code

preferred_language

timezone

currency

status

onboarding_status

created_at

updated_at
125. public_id

Use UUID.

Example:

8fc37d51-....

External APIs should prefer this identifier instead of exposing sequential database IDs for workspace-sensitive operations.

126. owner

Relationship:

GuestWorkspace
      â”‚
      â–¼
accounts.User

Recommended:

OneToOneField

for V1.

Business rule:

One Guest User â†’ One Guest Workspace

Do not accept owner_id from frontend requests.

It must always come from:

request.user
127. Workspace Name

workspace_name represents the name shown inside the application.

Example:

Vinay Collections

business_name may be optional.

Example:

Sri Lakshmi Finance

A lender who does not operate under a registered business name can still use the workspace.

128. Workspace Status

Recommended choices:

active
inactive
suspended
converted
active

Normal Guest Workspace.

inactive

Owner voluntarily stopped using it.

suspended

Platform restricted access.

converted

Workspace has been upgraded into the V2 ERP/business structure.

Converted workspaces must not be deleted.

129. Onboarding Status

Recommended:

not_started
in_progress
completed
skipped

This allows onboarding to continue across sessions.

Example:

Register
   â†“
Create Workspace
   â†“
Add Business Information
   â†“
Add First Customer
   â†“
Complete

A user should not be forced to finish all onboarding fields before using the digital collection book.

130. Currency

V1:

INR

Do not hardcode â‚¹ into database values.

Store:

currency = INR

Frontend decides how it is displayed.

This leaves the architecture open to future expansion.

131. Timezone

Default for Indian V1 users:

Asia/Kolkata

This field matters because collection summaries depend on the workspace's business day.

The backend should not assume UTC dates when calculating:

Today's Collection
Today's Expenses
Today's Pending Customers

Database timestamps remain timezone-aware.

132. GuestWorkspaceSettings Model

Workspace preferences should be separated from the core workspace record.

Relationship:

GuestWorkspace
       â”‚
       â–¼
GuestWorkspaceSettings

One-to-one.

133. Settings Fields

Recommended:

id

workspace

default_collection_frequency

default_interest_type

default_interest_rate

default_payment_mode

default_grace_days

allow_partial_collection

allow_advance_collection

allow_overpayment

auto_generate_schedule

show_completed_customers

financial_year_start_month

date_format

created_at

updated_at
134. Why Settings Are Separate

Avoid turning GuestWorkspace into a massive table containing dozens of future configuration fields.

V2 will eventually introduce:

Penalty rules.
Route settings.
Employee settings.
Notifications.
Collection settings.
Salary settings.

Separating settings keeps the workspace identity clean.

135. Default Collection Frequency

Optional.

Example:

weekly

If most of the lender's customers pay weekly, customer/finance-account creation forms can automatically preselect Weekly.

The user can still change it for individual finance accounts.

136. Partial Collection Setting

Example:

allow_partial_collection = True

If expected amount is:

â‚¹500

and customer pays:

â‚¹300

the collection can be recorded as partial.

The remaining:

â‚¹200

remains due according to business rules.

137. Advance Collection

Example:

Expected:

â‚¹500

Customer pays:

â‚¹1,000

If:

allow_advance_collection = True

the extra amount may reduce future outstanding installments.

If false, the service rejects an amount above the permitted collection amount.

This behavior belongs in CollectionService.

138. GuestCustomer Model
Purpose

Represents a person/customer whose finance activity is being tracked by the Guest Workspace.

Customer identity information must remain independent from finance-account information.

139. Customer Fields
id

public_id

workspace

customer_code

full_name

mobile_number

alternate_mobile_number

gender

occupation

address_line

state

district

city

village

postal_code

landmark

latitude

longitude

location_source

notes

status

joined_at

created_at

updated_at
140. Workspace Relationship
GuestWorkspace
      â”‚
      â””â”€â”€ GuestCustomer

Every customer belongs to exactly one workspace.

Every query must be scoped by workspace.

Never:

GuestCustomer.objects.get(public_id=customer_id)

without workspace ownership filtering.

Conceptually:

GuestCustomer.objects.get(
    public_id=customer_id,
    workspace=current_workspace
)

This is a critical SaaS data-isolation requirement.

141. Customer Code

Each workspace should receive human-readable customer codes.

Example:

CUST-0001
CUST-0002
CUST-0003

Uniqueness requirement:

unique(workspace, customer_code)

The code must be generated by the backend.

Frontend should not determine sequential identifiers.

142. Customer Name

Required.

Normalization can remove unnecessary leading/trailing whitespace.

Do not force uniqueness.

Two customers can legitimately have the same name.

143. Mobile Number

Recommended optional in Guest Workspace.

This is important because traditional lenders may have existing customers without reliable mobile details.

However, when provided:

Validate format.
Normalize number.
Allow duplicate handling according to business rules.

Do not blindly enforce global uniqueness.

Different workspaces can obviously contain the same phone number.

Even within one workspace, duplicates may require warning rather than hard rejection because family members may share phones.

144. Customer Address

V1 must support both:

Structured Address
state
district
city
village
postal_code

and:

Free-Text Address
address_line
landmark

This is necessary because geographic master data will never perfectly represent every local collection address.

145. GPS Fields

Optional:

latitude
longitude

These can be captured when:

Use Current Location

is selected.

Location source:

manual
device_gps
map_selection
geocoded

GPS is optional in Guest Workspace V1.

It becomes significantly more important in V2 route management.

146. Why Capture GPS in V1

Even though Guest Workspace does not provide collector routing yet, storing GPS now means upgraded users will not have to revisit every customer to capture their location.

When they upgrade:

Guest Customer GPS
        â†“
ERP Customer
        â†“
Area/Route Assignment

Existing location data becomes immediately useful.

147. Customer Status

Recommended:

active
inactive
archived

Do not use customer status to represent loan status.

A customer can be:

active

while their finance account is:

closed

because they may return for another finance account later.

148. Customer Deletion

Hard deletion should normally be prohibited once financial history exists.

Example:

Customer
   â”‚
   â””â”€â”€ Collections Exist

DELETE should result in:

Archive Customer

rather than database deletion.

A customer with no finance/history may potentially be hard-deleted depending on product policy, but a consistent archive approach is safer.

149. GuestFinanceAccount Model
Purpose

Represents money/finance provided to a customer and the repayment terms attached to it.

Relationship:

GuestCustomer
      â”‚
      â”œâ”€â”€ Finance Account 1
      â”œâ”€â”€ Finance Account 2
      â””â”€â”€ Finance Account 3
150. Finance Account Fields

Recommended:

id

public_id

workspace

customer

account_number

principal_amount

interest_type

interest_rate

interest_amount

total_payable_amount

collection_frequency

installment_amount

tenure_count

tenure_unit

start_date

expected_end_date

actual_end_date

previously_paid_amount

opening_outstanding_amount

current_paid_amount

current_outstanding_amount

grace_days

status

is_existing_account

calculation_mode

notes

created_at

updated_at
151. Why Store Workspace on FinanceAccount

Technically workspace can be reached through:

finance_account.customer.workspace

but storing workspace directly can make high-volume workspace filtering and reporting easier.

If this denormalization is used, the service must guarantee:

finance_account.workspace
==
finance_account.customer.workspace

It must never accept mismatching workspace/customer relationships.

152. Account Number

Example:

FIN-000001

Unique within workspace.

Recommended constraint:

unique(workspace, account_number)

Generated by backend.

153. Principal Amount

Original amount given to customer.

Example:

â‚¹10,000

Must be:

> 0

Use DecimalField.

Never use float for money.

154. Interest Type

References:

masters.InterestType

Examples could include:

flat_percentage
fixed_amount
monthly_percentage

Calculation behavior depends on interest type.

155. Interest Rate

Example:

10%
3% per month

Use decimal representation.

The exact interpretation depends on interest_type.

156. Interest Amount

Store the calculated monetary interest amount.

Example:

Principal = â‚¹10,000
Interest = â‚¹1,000

interest_amount = â‚¹1,000

This should be stored when the account terms are finalized so historical records do not unexpectedly change if calculation rules are updated later.

157. Total Payable Amount

Calculated:

principal_amount
+
interest_amount
+
initial applicable charges

For simple V1 finance accounts:

â‚¹10,000 principal
+
â‚¹1,000 interest
=
â‚¹11,000 payable

Penalties added later should generally not mutate the original contractual amount without a clear accounting record.

158. Collection Frequency

Reference:

daily
weekly
monthly

This determines schedule generation.

159. Tenure

Use:

tenure_count
tenure_unit

Example:

tenure_count = 20
tenure_unit = weeks

Possible units:

days
weeks
months

This is more flexible than storing only tenure = 20.

160. Installment Amount

Expected collection per scheduled installment.

Example:

â‚¹550/week

The calculator service can derive this where applicable.

Manual override may be supported when the lender's real-world arrangement doesn't divide perfectly.

161. Existing Account Support

This is one of the most important V1 requirements.

Users will not only create new finance accounts.

They may already have:

Customer borrowed â‚¹20,000
8 weeks ago

Already paid â‚¹8,000

Current outstanding â‚¹14,000

The platform must allow them to digitize this existing business.

Therefore:

is_existing_account = True

enables historical opening values.

162. Previously Paid Amount

Represents money collected before the account was entered into this application.

Example:

Total payable: â‚¹22,000

Paid before using platform: â‚¹8,000

Then:

opening_outstanding_amount = â‚¹14,000

This amount must not create fake individual collection transactions unless the user explicitly imports historical transactions.

163. Current Paid Amount

This should represent tracked payments after the opening state plus any explicitly imported historical transactions according to the chosen accounting convention.

To avoid ambiguity, reporting should distinguish:

Opening Paid Amount
Platform Recorded Collections
Total Paid

Example:

Previously Paid     â‚¹8,000
Recorded in App     â‚¹3,000
--------------------------------
Total Paid          â‚¹11,000
164. Current Outstanding Amount

Conceptually:

total_payable_amount
-
previously_paid_amount
-
valid recorded collections
+
applicable adjustments

The authoritative calculation must live in FinanceAccountService / CollectionService.

The frontend must never calculate and persist the balance itself.

165. Finance Account Status

Recommended:

draft
active
completed
overdue
defaulted
cancelled
Draft

Terms are being prepared.

Active

Collections are ongoing.

Completed

Outstanding amount reached zero and account is closed normally.

Overdue

Expected schedule has passed with outstanding balance.

Defaulted

Lender manually/operationally identifies the account as defaulted.

Cancelled

Account was cancelled according to permitted business rules.

166. Status Transitions

Do not allow arbitrary frontend changes such as:

active â†’ completed

The service determines whether completion is valid.

Example:

Outstanding = â‚¹0
        â†“
FinanceAccountService
        â†“
status = completed
actual_end_date = today
167. Calculation Mode

Recommended:

automatic
manual
Automatic

System calculates interest, total payable, installment amount and schedule based on supported rules.

Manual

User provides the agreed totals/installment information.

This is useful because traditional finance arrangements may not always fit a mathematically standardized product.

V1 should prioritize accurate record-keeping over forcing every lender into one calculation formula.

168. Finance Account Immutability

Once collections exist, critical original terms should not be casually editable.

Examples:

principal_amount
interest_type
interest_rate
total_payable_amount
start_date

Changing these after payments exist can corrupt financial history.

Therefore updates should be categorized as:

Safe Updates
notes
grace_days
some metadata
Financial-Term Changes

Require:

validation
recalculation
confirmation
possibly adjustment history

V1 can simply prohibit critical-term edits after the first recorded collection if adjustment workflows are not yet implemented.

169. GuestCollectionSchedule Model
Purpose

Represents the expected payment schedule.

Example:

Week 1    â‚¹550    Due 01 Aug
Week 2    â‚¹550    Due 08 Aug
Week 3    â‚¹550    Due 15 Aug
...
170. Schedule Fields
id

finance_account

installment_number

due_date

expected_amount

paid_amount

remaining_amount

status

completed_at

created_at

updated_at
171. Schedule Status

Recommended:

upcoming
due
partial
paid
missed
overdue
waived

The schedule status and collection status are related but are not the same concept.

A collection is an event.

A schedule is an expectation.

172. Example

Expected:

10 July
â‚¹500

No payment occurs.

Schedule:

status = missed/overdue

There may be no successful monetary collection record.

Instead, a collection attempt/status record may capture:

Customer unavailable

depending on how we implement collection events in the next section.

173. Schedule Generation

Handled by:

FinanceAccountService

or dedicated:

ScheduleService

Recommended service:

class FinanceScheduleService:
    ...

Methods:

generate_schedule()

regenerate_draft_schedule()

get_schedule()

update_schedule_statuses()

calculate_next_due()

calculate_remaining_installments()
174. Daily Schedule Example
Start Date: 1 August
Tenure: 30 days

01 Aug
02 Aug
03 Aug
...
30 Aug

Business rules must define whether collection begins:

on start date

or:

one frequency period after start date

This should be configurable/calculation-rule driven rather than assumed inconsistently.

175. Weekly Schedule

Example:

Start: Monday 3 August

10 Aug
17 Aug
24 Aug
31 Aug

The agreed collection day should remain consistent where possible.

176. Monthly Schedule

Monthly schedules need special date handling.

For example:

Start Date: January 31

The next due date cannot always be:

February 31

The schedule service should safely use the final valid day where necessary.

These calculations belong entirely in the backend.

177. Rounding Rules

Money calculations must use:

Decimal

never:

float

Example:

â‚¹10,000 / 3 installments

may not divide perfectly.

Possible schedule:

â‚¹3,333.33
â‚¹3,333.33
â‚¹3,333.34

The final installment should reconcile the rounding difference so:

sum(schedule.expected_amount)
==
total_payable_amount

This is a mandatory financial integrity rule.

178. Existing Customer Onboarding Flow

The V1 onboarding experience should support a fast migration from paper.

Example:

Add Customer
    â†“
Ramesh
    â†“
Add Existing Finance
    â†“
Original Amount
â‚¹10,000
    â†“
Interest
â‚¹1,000
    â†“
Total
â‚¹11,000
    â†“
Already Paid
â‚¹4,000
    â†“
Remaining
â‚¹7,000
    â†“
Frequency
Weekly
    â†“
Expected Weekly Amount
â‚¹500
    â†“
Save

The user does not need to manually recreate every old collection.

179. Historical Entry Modes

V1 should support two conceptual modes.

Opening Balance Mode â€” Primary V1

User enters:

Total payable
Already paid
Remaining balance

Fastest onboarding.

Detailed History Import â€” Optional/Later V1

User provides individual historical collections.

Example:

01 Jun â‚¹500
08 Jun â‚¹500
15 Jun â‚¹300

This can later be supported through Excel import.

Opening Balance Mode should remain the primary V1 workflow.

180. Serializers

Recommended guest_workspace/serializers.py organization can remain one module initially, but if it becomes too large it may be converted into:

serializers/

workspace_serializers.py
customer_serializers.py
finance_account_serializers.py
collection_serializers.py
expense_serializers.py
report_serializers.py

This does not change your five-layer architecture; it only organizes the serializer layer.

181. Workspace Serializers

Required:

GuestWorkspaceSerializer
GuestWorkspaceUpdateSerializer
GuestWorkspaceSettingsSerializer
GuestWorkspaceSettingsUpdateSerializer

The owner field must be read-only.

Workspace status must not be freely editable by the Guest user.

182. Customer Serializers

Required:

GuestCustomerCreateSerializer

GuestCustomerUpdateSerializer

GuestCustomerListSerializer

GuestCustomerDetailSerializer

GuestCustomerSummarySerializer

Separate list/detail serializers prevent unnecessary data from being returned on large customer lists.

183. Customer Create Validation

Validate:

Name required.
Mobile format if supplied.
Valid master location relationships.
Latitude range.
Longitude range.
Postal-code format where applicable.

If:

state = Andhra Pradesh

and:

district = Hyderabad

does not belong to that state, reject the relationship.

The frontend cannot be trusted simply because it used cascading dropdowns.

184. Finance Account Serializers

Required:

GuestFinanceAccountCreateSerializer

GuestExistingFinanceAccountCreateSerializer

GuestFinanceAccountUpdateSerializer

GuestFinanceAccountListSerializer

GuestFinanceAccountDetailSerializer

GuestFinanceAccountSummarySerializer

New finance and existing finance should have separate input serializers because their validation requirements differ significantly.

185. New Finance Account Validation

Validate:

principal_amount > 0

interest_rate >= 0

tenure_count > 0

installment_amount > 0

valid frequency

valid interest type

start_date valid

If automatic calculation mode is used, fields calculated by the backend must not be trusted from frontend input.

186. Existing Finance Account Validation

Additional fields:

previously_paid_amount >= 0

previously_paid_amount <= total_payable_amount

Opening outstanding should be derived where possible.

If the frontend submits:

total_payable = â‚¹10,000
already_paid = â‚¹4,000
outstanding = â‚¹9,000

the backend must reject or ignore the inconsistent calculated value.

The service remains the source of truth.

187. Workspace Service Structure
guest_workspace/services/

workspace_service.py
customer_service.py
finance_account_service.py
schedule_service.py
collection_service.py
expense_service.py
dashboard_service.py
report_service.py
calculator_service.py
import_service.py
export_service.py

Every file contains class-based services.

188. GuestWorkspaceService

Required methods:

create_default_workspace()

get_workspace()

update_workspace()

get_workspace_settings()

update_workspace_settings()

complete_onboarding()

deactivate_workspace()

get_workspace_summary()

validate_workspace_access()
189. CustomerService
class GuestCustomerService:
    ...

Required methods:

create_customer()

update_customer()

get_customer()

get_customers()

archive_customer()

restore_customer()

get_customer_finance_accounts()

get_customer_collection_history()

get_customer_summary()

search_customers()

validate_customer_access()
190. Customer Creation Transaction
Authenticated User
      â†“
Resolve Workspace
      â†“
Validate Customer Data
      â†“
Generate Customer Code
      â†“
Create Customer
      â†“
Audit Event
      â†“
Return Customer

If the frontend creates customer + finance account in a single onboarding request:

Start Transaction
      â†“
Create Customer
      â†“
Create Finance Account
      â†“
Generate Schedule
      â†“
Commit

If finance-account creation fails, the entire combined operation should roll back where the endpoint promises atomic creation.

191. FinanceAccountService

Required methods:

create_finance_account()

create_existing_finance_account()

update_finance_account()

get_finance_account()

get_finance_accounts()

calculate_finance_terms()

activate_finance_account()

complete_finance_account()

cancel_finance_account()

mark_overdue_accounts()

recalculate_balance()

get_account_summary()

validate_financial_term_update()
192. create_finance_account()

Flow:

Validated Input
     â†“
Resolve Workspace
     â†“
Validate Customer Ownership
     â†“
Calculate Interest
     â†“
Calculate Total Payable
     â†“
Calculate Installment
     â†“
Generate Account Number
     â†“
Create Finance Account
     â†“
Generate Schedule
     â†“
Audit
     â†“
Commit

All steps execute inside:

transaction.atomic()
193. Existing Finance Account Creation

Flow:

Customer
   â†“
Original Finance Details
   â†“
Calculate/Validate Total Payable
   â†“
Accept Opening Paid Amount
   â†“
Calculate Opening Outstanding
   â†“
Determine Remaining Tenure
   â†“
Create Account
   â†“
Generate Remaining Schedule
   â†“
Store Opening Position
   â†“
Commit

This flow is one of the major V1 product differentiators because it allows lenders to adopt the application without starting their business records from zero.

194. Calculator Service
class GuestFinanceCalculatorService:
    ...

Methods:

calculate_interest()

calculate_total_payable()

calculate_installment()

calculate_outstanding()

calculate_tenure()

calculate_expected_end_date()

preview_schedule()

The calculator should be usable without creating a FinanceAccount.

Example endpoint:

POST /api/v1/guest/calculator/preview/

Input:

{
  "principal_amount": "10000.00",
  "interest_type": "flat_percentage",
  "interest_rate": "10.00",
  "collection_frequency": "weekly",
  "tenure_count": 20,
  "tenure_unit": "weeks"
}

Output can contain:

Interest
Total Payable
Installment
Expected End Date
Schedule Preview

Nothing is persisted.

195. Customer APIs

Recommended:

GET    /api/v1/guest/customers/

POST   /api/v1/guest/customers/

GET    /api/v1/guest/customers/{public_id}/

PATCH  /api/v1/guest/customers/{public_id}/

DELETE /api/v1/guest/customers/{public_id}/

POST   /api/v1/guest/customers/{public_id}/restore/

GET    /api/v1/guest/customers/{public_id}/summary/

GET    /api/v1/guest/customers/{public_id}/finance-accounts/

GET    /api/v1/guest/customers/{public_id}/collections/
196. Customer List Filters

The view layer should validate and process filters such as:

search
status
area/locality
has_active_finance
collection_frequency
outstanding_min
outstanding_max
created_from
created_to
ordering
page
page_size

Actual database querying belongs to GuestCustomerService.

197. Search

Search should support:

Customer Name
Mobile Number
Customer Code
Finance Account Number

For initial V1 scale, PostgreSQL icontains/indexed approaches may be sufficient.

As volume increases, PostgreSQL full-text/trigram search can be introduced.

Elasticsearch is unnecessary for V1.

198. Finance Account APIs

Recommended:

GET  /api/v1/guest/finance-accounts/

POST /api/v1/guest/finance-accounts/

POST /api/v1/guest/finance-accounts/existing/

GET  /api/v1/guest/finance-accounts/{public_id}/

PATCH /api/v1/guest/finance-accounts/{public_id}/

POST /api/v1/guest/finance-accounts/{public_id}/cancel/

GET /api/v1/guest/finance-accounts/{public_id}/schedule/

GET /api/v1/guest/finance-accounts/{public_id}/collections/

GET /api/v1/guest/finance-accounts/{public_id}/summary/
199. Finance Account List Filters

Support:

status
customer
collection_frequency
start_date_from
start_date_to
expected_end_from
expected_end_to
has_outstanding
overdue
search
ordering
pagination
200. Dashboard-Friendly Customer Summary

Customer detail should expose a calculated summary such as:

Total Finance Accounts
Active Accounts
Completed Accounts
Original Amount
Total Payable
Previously Paid
Collected Through Platform
Outstanding
Last Payment
Next Due

These values should come from a service aggregation rather than being calculated independently by React.

201. Data Isolation Rule

This rule applies to every Guest Workspace endpoint:

request.user
      â†“
GuestWorkspace
      â†“
Requested Resource

The API must never trust:

workspace_id

supplied by the frontend to determine ownership.

For example, if User A requests a customer belonging to User B, the backend should return an appropriate not-found/access response without exposing the other workspace's data.

This becomes the foundation of tenant isolation for the complete ERP.

202. Database Indexes

Important indexes for V1 should include appropriate combinations around:

GuestCustomer:
workspace + status
workspace + customer_code
workspace + mobile_number

GuestFinanceAccount:
workspace + status
workspace + customer
workspace + account_number
workspace + collection_frequency
expected_end_date

GuestCollectionSchedule:
finance_account + due_date
finance_account + status
due_date + status

Index decisions should be validated against actual queries rather than creating indexes for every field.

203. V1 Core Data Flow

At this stage the backend foundation supports:

Register Guest
      â†“
Create Workspace
      â†“
Configure Workspace
      â†“
Add Customer
      â†“
Add Existing/New Finance Account
      â†“
Calculate Finance Terms
      â†“
Generate Collection Schedule
      â†“
Ready for Daily Collection

The next part of Chapter 5 is the most important operational workflow:

GuestCollection and the Digital Collection Register â€” including paid, partial, pending, missed, customer unavailable, promise-to-pay, advance payment, corrections, balance recalculation, schedule allocation, collection history, today's collection book, day closing, and concurrency protection so duplicate clicks cannot accidentally record the same payment twice.


------

Chapter 5 â€” guest_workspace, now with the operational heart of V1: the Digital Collection Register.

204. GuestCollection â€” Digital Collection Register
Purpose

GuestCollection represents an actual collection event or collection attempt against a customer's finance account.

It must support both monetary and non-monetary outcomes.

Examples:

Ramesh â†’ Paid â‚¹500
Suresh â†’ Paid â‚¹300 of â‚¹500
Mahesh â†’ Customer unavailable
Ravi â†’ Promise to pay tomorrow
Krishna â†’ Did not pay â€” business loss today

A collection record is therefore not simply a payment transaction.

It represents:

What happened when a scheduled collection was expected or recorded.

This distinction is important for daily collection-book reporting.

205. Collection Domain Relationships
GuestWorkspace
      â”‚
      â–¼
GuestCustomer
      â”‚
      â–¼
GuestFinanceAccount
      â”‚
      â”œâ”€â”€ GuestCollectionSchedule
      â”‚
      â””â”€â”€ GuestCollection

Where possible:

GuestCollection
      â”‚
      â””â”€â”€ CollectionSchedule

links the actual collection event to the expected installment.

However, the schedule relationship should be nullable because certain payments may not correspond to exactly one scheduled installment.

Examples:

Advance payments.
Opening-balance adjustments.
Bulk historical imports.
Unscheduled payments.
206. GuestCollection Model

Recommended fields:

id

public_id

workspace

customer

finance_account

schedule

collection_date

collection_time

expected_amount

paid_amount

payment_mode

collection_status

reason

remarks

promise_to_pay_date

collection_source

recorded_by

latitude

longitude

opening_outstanding

closing_outstanding

is_adjustment

is_reversed

reversed_at

reversal_reason

created_at

updated_at

Some values are intentionally stored as snapshots even though they can theoretically be derived.

This is necessary for reliable historical financial records.

207. collection_date

Represents the business date on which the collection occurred.

Do not rely only on:

created_at

because a lender may enter yesterday's collection today.

Example:

Collection happened:
22 July

Entered into application:
23 July

Therefore:

collection_date = 2026-07-22
created_at = 2026-07-23 07:30

Both pieces of information matter.

208. collection_time

Optional.

If collection is entered immediately, the backend can default to the current workspace-local time.

If historical data is entered, time may remain null.

209. Expected Amount

Snapshot of what was expected at the moment of collection.

Example:

Expected installment = â‚¹500

Store:

expected_amount = 500

Even if finance terms change later, historical collection reports remain understandable.

210. Paid Amount

Actual amount received.

Examples:

Expected â‚¹500
Paid â‚¹500

or:

Expected â‚¹500
Paid â‚¹300

For non-payment statuses:

paid_amount = 0

Money must use DecimalField.

211. Collection Status

Reference:

masters.CollectionStatus

Core V1 statuses:

paid
partial
pending
customer_unavailable
promise_to_pay
holiday
skipped
defaulted

The backend determines whether a status is compatible with the submitted amount.

212. Status Validation Matrix

Business validation should conceptually follow:

Status	Paid Amount	Reason
Paid	> 0	Optional
Partial	> 0	Optional/Configurable
Pending	0	Recommended
Customer Unavailable	0	Required
Promise to Pay	0	Required
Holiday	0	Optional
Skipped	0	Required
Defaulted	0	Required

Additional rules apply depending on expected amount.

213. Paid Status Rule

If:

expected_amount = â‚¹500
paid_amount = â‚¹500

then:

status = paid

If the frontend sends:

status = partial
paid_amount = â‚¹500

the service should normalize or reject the inconsistency according to API policy.

Prefer backend determination where possible.

214. Partial Payment

Example:

Expected = â‚¹500
Paid = â‚¹300

Then:

Schedule Expected    â‚¹500
Schedule Paid        â‚¹300
Schedule Remaining   â‚¹200
Schedule Status      partial

Finance account:

Previous Outstanding â‚¹7,000
Collection           â‚¹300
New Outstanding      â‚¹6,700

The unpaid â‚¹200 must remain due.

215. Pending Collection

Example:

Expected = â‚¹500
Paid = â‚¹0
Status = pending

No outstanding balance reduction occurs.

The event remains visible in:

Customer history.
Daily collection register.
Pending report.
Today's activity.
216. Customer Unavailable

Example:

Status:
customer_unavailable

Reason:
Shop closed

No financial balance changes.

However, the event is important operationally because the lender can distinguish:

Didn't visit / no record

from:

Visited but customer unavailable

This becomes even more valuable in V2 when employees perform collections.

217. Promise to Pay

When:

status = promise_to_pay

the following should be required:

promise_to_pay_date

Example:

Expected: 23 July
Customer requested: 25 July

The original schedule is not deleted.

Instead, the collection event records the promise.

The customer can appear in a:

Promise to Pay

follow-up list.

218. Holiday

A lender may decide not to collect on a particular date because of:

Local holiday.
Festival.
Business closure.
Personal decision.

A holiday event should not automatically imply customer default.

Future schedule-shifting behavior can be introduced separately.

219. Skipped

skipped means the expected collection was intentionally not collected for a specific reason.

Example:

Customer requested one-week break.

Reason required.

The amount remains outstanding unless an explicit waiver/adjustment occurs.

220. Defaulted

Default should not automatically occur simply because one installment was missed.

It should represent an explicit account/customer operational state.

In V1, default can be manually marked after confirmation.

The system should preserve:

who marked it
when
reason

V2 can introduce configurable default rules.

221. Payment Mode

References:

masters.PaymentMode

Examples:

cash
upi
bank_transfer
cheque
other

Again, the application records the payment mode.

It does not process the payment.

222. Collection Source

Recommended values:

manual
historical_import
adjustment
system

V2 may add:

collector_app
api

This helps identify how a collection entered the system.

223. Recorded By

Relationship:

accounts.User

In Guest Workspace V1:

recorded_by = workspace.owner

In V2:

recorded_by = Collector Employee

Including this field in V1 makes future conversion much easier.

224. GPS Fields

Optional:

latitude
longitude

Guest owners may record a collection from anywhere, so V1 should not force GPS.

V2 can enforce GPS based on business settings.

225. Outstanding Snapshots

Each monetary collection should store:

opening_outstanding
closing_outstanding

Example:

Opening Outstanding = â‚¹6,700

Paid = â‚¹500

Closing Outstanding = â‚¹6,200

This provides a strong audit trail.

226. Why Outstanding Snapshots Matter

Without snapshots, historical screens would constantly calculate balances from all previous transactions.

Snapshots provide:

Easier auditing.
Faster history screens.
Better discrepancy detection.
Clear correction trails.

However, the service must ensure snapshots remain internally consistent.

227. Never Directly Edit Financial Collections

Once a collection has been recorded, arbitrary editing creates audit problems.

For example:

Yesterday:
â‚¹500 collected

Today:
User changes it to â‚¹100

Simply updating the database row destroys the original record.

Therefore financial corrections should use a controlled correction/reversal mechanism.

228. Collection Reversal

If a collection was entered incorrectly:

â‚¹5,000

instead of:

â‚¹500

the system should support:

Reverse Collection

rather than silently overwriting the record.

229. Reversal Fields

Collection contains:

is_reversed
reversed_at
reversal_reason

A supporting model is even better:

GuestCollectionReversal

Recommended fields:

id
collection
reversed_by
reason
opening_balance
restored_balance
created_at

This creates a clear audit trail.

230. Reversal Flow
Original Collection
â‚¹5,000
      â†“
User Requests Correction
      â†“
Validate Ownership
      â†“
Check Already Reversed
      â†“
Lock Finance Account
      â†“
Reverse Balance Effect
      â†“
Restore Schedule Amount
      â†“
Mark Collection Reversed
      â†“
Create Reversal Record
      â†“
Audit
      â†“
Commit

Then the correct â‚¹500 collection can be entered separately.

231. Why Reversal Is Better Than Edit

History becomes:

10:00 AM
â‚¹5,000 recorded

10:05 AM
â‚¹5,000 reversed
Reason: Wrong amount entered

10:06 AM
â‚¹500 recorded

instead of pretending the mistake never occurred.

This becomes especially important when employees are added in V2.

232. Collection Allocation

A payment may need to be allocated against schedule installments.

Example:

Installment 1 outstanding = â‚¹200
Installment 2 due         = â‚¹500

Customer pays             = â‚¹700

The service should allocate:

â‚¹200 â†’ Installment 1
â‚¹500 â†’ Installment 2

rather than randomly assigning payment.

233. Allocation Strategy

Recommended default:

Oldest outstanding installment first.

Flow:

Payment
   â†“
Find oldest unpaid/partial schedules
   â†“
Allocate amount
   â†“
Complete oldest schedule
   â†“
Move remaining amount to next schedule

This creates predictable accounting behavior.

234. GuestCollectionAllocation Model

Because one collection may affect multiple schedules, a dedicated allocation model is recommended.

GuestCollectionAllocation

Fields:

id
collection
schedule
allocated_amount
created_at

Relationship:

GuestCollection
      â”‚
      â”œâ”€â”€ Allocation â†’ Schedule 1
      â””â”€â”€ Allocation â†’ Schedule 2

This is much more reliable than forcing:

collection.schedule = one schedule

for every payment.

Therefore the original nullable schedule field can be omitted if allocation records are used consistently.

235. Example Advance Payment

Schedules:

Week 1 â‚¹500
Week 2 â‚¹500
Week 3 â‚¹500

Customer pays:

â‚¹1,200

Allocation:

Week 1 â†’ â‚¹500
Week 2 â†’ â‚¹500
Week 3 â†’ â‚¹200

Result:

Week 1 paid
Week 2 paid
Week 3 partial â€” â‚¹300 remaining

Finance outstanding decreases by:

â‚¹1,200
236. Overpayment

Suppose finance outstanding is:

â‚¹800

but user enters:

â‚¹1,000

Default V1 behavior should reject it unless:

allow_overpayment = True

If overpayment is eventually supported, the extra â‚¹200 needs an explicit accounting treatment.

Do not silently allow negative outstanding balances.

237. Finance Account Locking

Collection recording is a financial write operation.

Concurrency must be considered.

Example:

Browser Tab A â†’ Record â‚¹500
Browser Tab B â†’ Record â‚¹500

Both requests could read:

Outstanding â‚¹500

and both attempt to complete the account.

Critical collection operations should therefore use:

transaction.atomic()

and, where appropriate:

select_for_update()

on the finance account and affected schedule rows.

238. Collection Transaction Flow

Recommended:

Begin Transaction
      â†“
Lock Finance Account
      â†“
Validate Account Status
      â†“
Validate Amount
      â†“
Determine Expected Amount
      â†“
Create Collection
      â†“
Allocate Payment
      â†“
Update Schedules
      â†“
Update Finance Account Balance
      â†“
Determine Account Status
      â†“
Create Audit Record
      â†“
Commit

If any operation fails:

ROLLBACK EVERYTHING

There must never be a collection record without the corresponding balance update.

239. Duplicate Submission Protection

Mobile networks can be unreliable.

A user may tap:

Save Collection

multiple times.

The frontend disabling the button is not sufficient.

The backend should support idempotency for financial write operations.

240. Idempotency Key

The frontend generates a unique request identifier.

Example header:

Idempotency-Key:
550e8400-e29b-41d4-a716-446655440000

The backend stores or tracks the key for the workspace/action.

If the exact request is repeated:

same idempotency key

the backend returns the existing result instead of recording another payment.

This is strongly recommended for collection creation.

241. CollectionService

Recommended:

class GuestCollectionService:
    ...

Methods:

record_collection()

record_non_payment()

allocate_collection()

calculate_expected_collection()

get_today_register()

get_collection_history()

get_customer_collections()

get_finance_account_collections()

reverse_collection()

get_pending_collections()

get_promises_to_pay()

get_overdue_collections()

validate_collection()

recalculate_account_after_collection()
242. record_collection()

Input conceptually includes:

finance_account
paid_amount
payment_mode
collection_date
remarks

The service determines:

expected amount
collection status
opening outstanding
closing outstanding
allocation

rather than trusting these financial values from frontend input.

243. record_non_payment()

Used for:

pending
customer_unavailable
promise_to_pay
holiday
skipped
defaulted

Input:

finance_account
schedule/due context
status
reason
promise_to_pay_date
collection_date

No balance reduction occurs.

244. Collection Serializers

Recommended:

GuestCollectionCreateSerializer

GuestNonPaymentCreateSerializer

GuestCollectionListSerializer

GuestCollectionDetailSerializer

GuestCollectionReversalSerializer

GuestCollectionRegisterSerializer

GuestPromiseToPaySerializer
245. Collection Create Serializer

Input should be minimal:

finance_account_id
paid_amount
payment_mode_id
collection_date
collection_time (optional)
remarks
idempotency_key

Do not accept:

closing_outstanding

from frontend.

Do not trust:

expected_amount

from frontend.

Do not trust:

status

when it can be safely derived from payment behavior.

246. Non-Payment Serializer

Input:

finance_account_id
schedule_id
collection_status
reason
promise_to_pay_date
collection_date
remarks

Validation:

If:

promise_to_pay

then:

promise_to_pay_date required

If master status has:

requires_reason = True

then reason is required.

247. Today's Collection Register

This is the main V1 operational screen.

Endpoint concept:

GET /api/v1/guest/collection-register/

Default:

date = workspace today

The API should return customers/accounts expected for that day plus their collection state.

248. Collection Register Response

Conceptually:

{
  "date": "2026-07-23",
  "summary": {
    "expected_amount": "15000.00",
    "collected_amount": "10500.00",
    "pending_amount": "4500.00",
    "expenses": "800.00",
    "net_collection": "9700.00"
  },
  "customers": []
}

Each customer row can contain:

Customer ID
Customer Code
Customer Name
Mobile
Area/Locality
Finance Account
Expected Amount
Paid Today
Remaining Today
Account Outstanding
Collection Status
Last Collection
Next Due
249. Collection Register Filters

Support:

date
search
status
collection_frequency
area/locality
payment_status
ordering
page
page_size

For V1, user-defined operational areas may be lightweight; V2 introduces full area management.

250. Digital Card Behavior

The frontend can show each customer as a digital collection card.

Backend should provide enough information for:

Ramesh
Weekly

Expected Today     â‚¹500
Paid Today         â‚¹300
Today's Remaining  â‚¹200

Total Outstanding  â‚¹6,700

[Collect]
[Not Paid]
[History]

The frontend should not need five API calls per card.

The register service should return the necessary summary efficiently.

251. Today's Expected Customers

A customer should appear when:

An active finance account exists.
A schedule is due on the selected date.

Additionally, overdue customers may optionally be included.

The API can support:

include_overdue=true

This is important because a lender may want today's route/register to include yesterday's unpaid customers.

252. Daily Collection History

Endpoint:

GET /api/v1/guest/collections/?date=2026-07-23

Should return actual collection events rather than expected schedule rows.

This distinction must remain clear:

Collection Register
=
Expected + Actual Operational View

Collection History
=
Actual Recorded Events
253. Collection APIs

Recommended:

GET  /api/v1/guest/collection-register/

POST /api/v1/guest/collections/

POST /api/v1/guest/collections/non-payment/

GET  /api/v1/guest/collections/

GET  /api/v1/guest/collections/{public_id}/

POST /api/v1/guest/collections/{public_id}/reverse/

GET /api/v1/guest/collections/pending/

GET /api/v1/guest/collections/promises-to-pay/

GET /api/v1/guest/collections/overdue/
254. Bulk Collection Entry

Because the Guest Workspace acts like a digital notebook, the user may enter many customer results quickly.

A future/late-V1 endpoint can support:

POST /api/v1/guest/collections/bulk/

Example:

Ramesh â‚¹500
Suresh â‚¹300
Mahesh unavailable
Ravi â‚¹500

Each item must still run through the same collection business rules.

Do not create a second simplified accounting implementation for bulk operations.

255. Bulk Transaction Strategy

Do not necessarily rollback 100 customer entries because one row is invalid.

A bulk endpoint can return:

successful
failed

per item.

Example:

50 submitted
48 successful
2 failed

Each individual collection remains atomic.

This is more practical for field/business entry.

256. Collection Schedule Status Updates

Schedule statuses should be refreshed based on:

due_date
paid_amount
remaining_amount
current business date

Example:

remaining = 0
â†’ paid

paid > 0 and remaining > 0
â†’ partial

due_date < today and remaining > 0
â†’ overdue

due_date > today
â†’ upcoming

Avoid storing statuses that can drift without an update mechanism unless necessary for reporting.

A service or scheduled task can reconcile them.

257. No Celery Requirement for V1

Do not introduce Celery merely to change:

due â†’ overdue

at midnight.

The application can initially derive effective status based on date when querying.

Later, Celery can materialize statuses for scale/notifications.

This keeps V1 infrastructure simpler.

258. Day Closing

Guest Workspace should provide a daily summary, but hard accounting day closure should not be mandatory in V1.

A lightweight optional model can be introduced:

GuestDailySummary

or summaries can initially be calculated dynamically.

Recommended V1 approach:

Calculate daily summaries dynamically and add materialized day closing only if performance/business requirements demand it.

This prevents unnecessary complexity.

259. Daily Summary Calculations

For selected business date:

Expected Collection
Actual Collection
Pending Expected Amount
Partial Collection Amount
Number Paid
Number Partial
Number Pending
Number Unavailable
Promises to Pay
Expenses
Net Collection

Net collection:

Actual Monetary Collections
-
Business Expenses

This represents operational cash-flow summary, not formal accounting profit.

The UI should avoid calling it "Profit" unless the business definition truly supports that.

260. Expense Module

Expenses are the second major daily operation.

Example:

Fuel â‚¹300
Food â‚¹150
Parking â‚¹50
Bike Repair â‚¹600
261. GuestExpense Model

Recommended fields:

id

public_id

workspace

expense_date

expense_time

category

amount

payment_mode

description

receipt

recorded_by

latitude

longitude

is_reversed

created_at

updated_at
262. Expense Amount

Must be:

> 0

Use DecimalField.

263. Expense Category

References:

masters.ExpenseCategory

The service must verify that category is either:

system category

or:

category belonging to current workspace

A user cannot submit another workspace's custom category.

264. Expense Receipt

Optional.

Supported examples:

JPG
PNG
PDF

V1 should impose:

Maximum file size.
Allowed MIME types.
Safe generated filenames.
Storage abstraction.

Do not store uploaded file binaries directly in PostgreSQL.

265. Expense Editing

Financial expenses should also preserve auditability.

V1 can allow editing recent expense records with audit logging.

For stronger financial controls, V2 can introduce:

expense correction
approval
reversal

Employee-created expenses will require approval workflows in V2.

266. ExpenseService
class GuestExpenseService:
    ...

Methods:

create_expense()

update_expense()

get_expense()

get_expenses()

delete_or_reverse_expense()

get_daily_expenses()

get_expense_summary()

get_category_breakdown()
267. Expense APIs
GET    /api/v1/guest/expenses/

POST   /api/v1/guest/expenses/

GET    /api/v1/guest/expenses/{public_id}/

PATCH  /api/v1/guest/expenses/{public_id}/

DELETE /api/v1/guest/expenses/{public_id}/

GET /api/v1/guest/expenses/summary/

Filters:

date
date_from
date_to
category
payment_mode
amount_min
amount_max
search
ordering
pagination
268. Dashboard Module

The dashboard should not maintain a separate table containing duplicated totals in V1.

Instead:

GuestDashboardService

aggregates data from:

Finance Accounts
Schedules
Collections
Expenses
Customers
269. GuestDashboardService

Methods:

get_dashboard()

get_today_summary()

get_collection_summary()

get_customer_summary()

get_finance_summary()

get_upcoming_dues()

get_recent_activity()

get_collection_trend()
270. Main Dashboard API
GET /api/v1/guest/dashboard/

Default date context:

workspace local today

Response should provide major dashboard data in one request.

271. Dashboard KPIs

V1 should include:

Today's Expected Collection

Today's Actual Collection

Today's Pending Amount

Today's Expenses

Today's Net Collection

Total Active Customers

Active Finance Accounts

Total Outstanding

Today's Paid Customers

Today's Partial Customers

Today's Pending Customers

Promises to Pay

Upcoming Collections
272. Collection Percentage

Recommended definition:

Actual Due Collections
Ã·
Expected Due Collection
Ã— 100

Example:

Expected â‚¹10,000
Collected â‚¹8,000

Collection % = 80%

If expected collection is zero, avoid division by zero and return an agreed neutral value such as 0 with supporting context.

273. Total Outstanding

Should include outstanding balances from relevant active/overdue finance accounts.

Do not include:

cancelled

accounts.

Completed accounts should normally have zero outstanding.

274. Recent Activity

Can include:

Ramesh paid â‚¹500

Suresh added as customer

Fuel expense â‚¹300

Mahesh marked unavailable

Finance FIN-0004 completed

V1 can derive this from business events/audit data.

Avoid a complicated social-style activity system.

275. Dashboard Date Filtering

Support:

today
yesterday
this_week
this_month
custom

The view validates date inputs.

The service performs aggregations.

276. Reports Module

Guest Workspace reports should remain practical rather than enterprise-heavy.

Core V1 reports:

Daily Collection Report

Weekly Collection Report

Monthly Collection Report

Customer Statement

Finance Account Statement

Outstanding Report

Pending Collection Report

Expense Report

Collection vs Expense Report

Promise-to-Pay Report
277. GuestReportService
class GuestReportService:
    ...

Methods:

daily_collection_report()

weekly_collection_report()

monthly_collection_report()

customer_statement()

finance_account_statement()

outstanding_report()

pending_report()

expense_report()

collection_expense_report()

promise_to_pay_report()
278. Report Filters

Depending on report:

date
date_from
date_to
customer
finance_account
collection_frequency
collection_status
payment_mode
expense_category
minimum_amount
maximum_amount
279. Customer Statement

Should show:

Customer Details

Finance Account

Original Principal

Interest

Total Payable

Previously Paid

Platform Collections

Outstanding

Collection History

Upcoming Schedule

This is useful when a lender wants to show a customer their current position.

280. Finance Account Statement

Example:

FIN-000012

Principal             â‚¹10,000
Interest               â‚¹1,000
Total Payable         â‚¹11,000
Previously Paid        â‚¹3,000
Platform Collections   â‚¹4,500
Outstanding            â‚¹3,500

Then chronological collection history.

281. Outstanding Report

Should support grouping by:

Customer
Collection Frequency
Status
Locality

and display:

Customer
Account Number
Total Payable
Total Paid
Outstanding
Next Due
Days Overdue
282. Export Architecture

Do not place PDF/Excel generation inside views.

Use:

GuestExportService

Methods:

export_collections_csv()

export_collections_excel()

export_expenses_excel()

export_customer_statement_pdf()

export_finance_statement_pdf()

export_outstanding_report()

For large exports in V2:

Celery

can generate files asynchronously.

Small V1 exports can be generated synchronously if performance remains acceptable.

283. Reports APIs

Recommended:

GET /api/v1/guest/reports/daily/

GET /api/v1/guest/reports/weekly/

GET /api/v1/guest/reports/monthly/

GET /api/v1/guest/reports/outstanding/

GET /api/v1/guest/reports/pending/

GET /api/v1/guest/reports/expenses/

GET /api/v1/guest/reports/promises/

GET /api/v1/guest/customers/{id}/statement/

GET /api/v1/guest/finance-accounts/{id}/statement/

Exports:

GET /api/v1/guest/reports/{report}/export/?format=csv

GET /api/v1/guest/reports/{report}/export/?format=xlsx

GET /api/v1/guest/reports/{report}/export/?format=pdf

Only supported formats should be accepted.

284. Guest Workspace V1 Main Flow

At this point, the complete core business flow becomes:

Register
   â†“
Create Guest Workspace
   â†“
Configure Defaults
   â†“
Add Existing Customers
   â†“
Add Existing Finance Accounts
   â†“
Enter Previously Paid Amount
   â†“
Generate Remaining Schedule
   â†“
Open Daily Collection Register
   â†“
Select Customer
   â†“
Paid / Partial / Not Paid
   â†“
Update Schedule
   â†“
Update Outstanding
   â†“
Record Expense
   â†“
View Daily Summary
   â†“
View Reports

This is the actual V1 product, rather than merely a limited demo of the future ERP.

285. One Important V1 Addition â€” Daily Record Without Schedule

Because your original idea is specifically aimed at lenders who may simply want a digital collection card, V1 should not force every user to perfectly configure historical schedules before they can start recording collections.

Therefore Guest Workspace should support a simplified onboarding mode:

Customer
   â†“
Amount Taken
   â†“
Total Payable / Interest
   â†“
Paid Till Date
   â†“
Current Outstanding
   â†“
Frequency
   â†“
Expected Collection Amount

Then they can immediately start entering daily records.

Internally, the backend still uses FinanceAccount, but schedule generation can be simplified or generated only for the remaining tenure.

This preserves the easy user experience you originally wanted while keeping the backend financially structured.

286. V1 Guest Workspace Completion Boundary

For the first production release, the must-have backend is:

Authentication
      +
Guest Workspace
      +
Customers
      +
Existing Finance Entry
      +
New Finance Entry
      +
Daily / Weekly / Monthly Scheduling
      +
Digital Collection Register
      +
Paid / Partial / Non-Payment Recording
      +
Outstanding Tracking
      +
Expenses
      +
Dashboard
      +
Basic Reports
      +
Customer Statements
      +
Import / Export
      +
Auditability

Features such as employees, route optimization, live GPS tracking, payroll, cash handover, advanced analytics, SMS campaigns, and WhatsApp communication remain V2.


-----


287. Existing Business Migration

A major V1 requirement is allowing a lender who already operates using notebooks, Excel sheets, or handwritten records to start using the platform without entering everything manually.

The system should support three onboarding methods:

Manual Customer Entry
        â”‚
        â”œâ”€â”€ Quick Opening Balance
        â”‚
        â””â”€â”€ Detailed Finance Entry

Excel / CSV Import
        â”‚
        â”œâ”€â”€ Customers
        â”œâ”€â”€ Finance Accounts
        â””â”€â”€ Opening Balances

Start Fresh
        â”‚
        â””â”€â”€ New Customers + New Finance

The most important migration principle is:

Existing historical payments do not need to be recreated individually unless the user has that data.

288. Opening Balance Migration

Example existing business record:

Customer: Ramesh

Amount Taken        â‚¹20,000
Interest             â‚¹4,000
Total Payable       â‚¹24,000

Tenure              24 Weeks
Weekly Amount        â‚¹1,000

Started             10 Weeks Ago

Paid Till Date      â‚¹8,000
Outstanding         â‚¹16,000

The user should be able to enter this directly.

The backend creates:

GuestCustomer

        â†“

GuestFinanceAccount

principal_amount = 20,000

interest_amount = 4,000

total_payable = 24,000

previously_paid = 8,000

opening_outstanding = 16,000

Only future/remaining collection activity needs to be tracked normally.

289. Opening Balance Integrity

The backend must validate:

previously_paid_amount >= 0

previously_paid_amount <= total_payable_amount

and calculate:

opening_outstanding =
total_payable_amount
-
previously_paid_amount

The frontend should not be the source of truth for this calculation.

290. Remaining Tenure

For an existing finance account, the user may know:

Original Tenure = 24 weeks

Completed = 8 weeks

Remaining = 16 weeks

or they may only know:

Outstanding = â‚¹16,000

Weekly Collection = â‚¹1,000

The platform should support both entry styles.

The calculator can derive an approximate remaining installment count where appropriate:

Outstanding
Ã·
Installment Amount

with the final installment adjusted for remainder.

291. Import Module

Recommended service:

class GuestImportService:
    ...

Responsibilities:

validate_file()

parse_customer_import()

validate_rows()

preview_import()

import_customers()

import_finance_accounts()

import_opening_balances()

import_historical_collections()

generate_error_report()

Historical collections can remain optional/late V1.

292. Import Job Model

Recommended:

GuestImportJob

Fields:

id
public_id

workspace

import_type

original_file_name

stored_file

status

total_rows
valid_rows
invalid_rows
processed_rows

created_records
failed_records

error_file

created_by

started_at
completed_at

created_at
updated_at
293. Import Status

Recommended:

uploaded
validating
ready
processing
completed
partially_completed
failed
cancelled

Even if imports initially run synchronously, designing the model this way makes future Celery processing straightforward.

294. Supported V1 Import Formats

Recommended:

.xlsx
.csv

Do not support many spreadsheet formats initially.

The platform should provide its own downloadable template.

Example columns:

Customer Name
Mobile Number
Address
Village / Locality
Amount Taken
Interest Type
Interest Rate
Interest Amount
Total Payable
Collection Frequency
Installment Amount
Tenure
Start Date
Paid Till Date
Outstanding
Notes
295. Import Template

Endpoint:

GET /api/v1/guest/imports/template/

The template should contain:

Column names.
Example row.
Instructions where useful.
Allowed values for fields such as frequency.

For example:

collection_frequency

Allowed:
daily
weekly
monthly
296. Import Preview

Never immediately insert a large uploaded spreadsheet.

Recommended flow:

Upload File
    â†“
Parse
    â†“
Validate
    â†“
Preview
    â†“
User Confirms
    â†“
Import

Example preview:

Total Rows       250

Valid            238
Invalid           12

The frontend can show invalid rows before committing.

297. Row-Level Validation

Each row should validate:

Customer name.
Phone format where supplied.
Amounts.
Interest values.
Collection frequency.
Tenure.
Dates.
Previously paid amount.
Outstanding consistency.

Example error:

Row 18

Customer:
Ravi

Error:
Previously paid amount cannot exceed total payable amount.
298. Import Error Report

Users should be able to download rejected rows.

Example:

Row | Customer | Error
18  | Ravi     | Invalid paid amount
24  | Suresh   | Invalid date
41  | Mahesh   | Missing customer name

This is significantly better than returning:

Import failed.
299. Duplicate Detection

Import should attempt to identify likely duplicates using combinations such as:

Customer Code
Mobile Number
Customer Name + Mobile
Finance Account Number

But name alone must not determine duplication.

Example:

Ramesh

could legitimately appear many times.

300. Duplicate Handling Options

Import preview can classify:

New

Possible Duplicate

Invalid

For V1, safest default:

Do not automatically overwrite existing customer/finance data.

The user should explicitly resolve potential duplicates.

301. Historical Collections Import

Optional advanced import:

Customer Code
Finance Account Number
Collection Date
Paid Amount
Payment Mode
Remarks

These collections should use:

collection_source = historical_import

and must pass through the same balance integrity rules.

Do not bypass GuestCollectionService.

302. Export Module

Recommended:

class GuestExportService:
    ...

Exports should support business backup and portability.

Important V1 exports:

Customers

Finance Accounts

Collections

Expenses

Outstanding Accounts

Customer Statement
303. CSV / Excel Export

Recommended endpoints:

GET /api/v1/guest/exports/customers/?format=xlsx

GET /api/v1/guest/exports/finance-accounts/?format=xlsx

GET /api/v1/guest/exports/collections/?format=xlsx

GET /api/v1/guest/exports/expenses/?format=xlsx

Filters should work with exports.

Example:

/collections/?date_from=2026-07-01
&date_to=2026-07-31
&format=xlsx
304. Data Portability

A user should not become trapped inside the platform.

They should be able to export core business records.

This improves:

User trust.
Business continuity.
Migration safety.
Supportability.
305. Free Workspace Limits

Because Guest Workspace is free, the backend should support configurable usage limits even if initial limits are generous.

Do not scatter conditions like:

if customers >= 100:

across services.

Use centralized plan configuration.

306. Plan Model

A lightweight platform-level model can be introduced:

Plan

Fields:

id

code

name

plan_type

price

customer_limit

active_finance_limit

monthly_collection_limit

storage_limit_mb

export_enabled

import_enabled

gps_enabled

is_active

created_at
updated_at

Example:

code = guest_free
307. Feature Entitlement

A separate structure becomes valuable as V2 grows:

Plan
 â”‚
 â””â”€â”€ PlanFeature

Examples:

guest_workspace
customer_import
excel_export
gps_capture
advanced_reports
employees
route_management
sms
whatsapp

This is preferable to hardcoding plan checks throughout the codebase.

308. Workspace Subscription

Even free users can have a subscription/entitlement record.

Recommended future-compatible model:

WorkspaceSubscription

Fields:

workspace
plan

status

started_at
expires_at

trial_started_at
trial_ends_at

created_at
updated_at

For free Guest:

plan = guest_free
status = active
expires_at = NULL

When upgraded later, the same entitlement system can handle paid plans.

309. FeatureAccessService

Recommended shared service:

class FeatureAccessService:
    ...

Methods:

can_use_feature()

check_customer_limit()

check_finance_account_limit()

check_import_access()

check_export_access()

check_storage_limit()

get_workspace_entitlements()

Business services call this before restricted actions.

310. Limit Response

If a user reaches a limit:

{
  "success": false,
  "message": "Customer limit reached for your current plan.",
  "code": "CUSTOMER_LIMIT_REACHED",
  "data": {
    "current": 100,
    "limit": 100
  }
}

Machine-readable codes are important because the frontend can display the correct upgrade UI.

311. Do Not Delete Data When Plan Changes

Suppose a future paid user has:

500 customers

and moves to a plan allowing:

250 customers

Never delete 250 customers.

Instead, restrict appropriate new actions until usage is within plan rules or the user upgrades.

312. Audit Trail

Financial software needs an audit trail even in the lightweight Guest version.

Recommended shared model:

AuditLog

This can live in a small core application.

313. AuditLog Fields
id

public_id

workspace_id

user

action

entity_type

entity_id

description

old_values

new_values

ip_address

user_agent

created_at

JSON fields can hold selected before/after values.

Sensitive fields must be excluded.

314. Auditable Actions

At minimum:

CUSTOMER_CREATED

CUSTOMER_UPDATED

CUSTOMER_ARCHIVED

FINANCE_CREATED

FINANCE_UPDATED

FINANCE_CANCELLED

COLLECTION_RECORDED

COLLECTION_REVERSED

EXPENSE_CREATED

EXPENSE_UPDATED

EXPENSE_DELETED

IMPORT_COMPLETED

WORKSPACE_UPDATED

V2 adds employee, salary, area, route and permission actions.

315. Audit Logging Principle

Business services should generate audit records after successful domain operations.

Example:

GuestCollectionService.record_collection()

          â†“

Collection Saved

          â†“

Balances Updated

          â†“

AuditLogService.create_log()

Audit logic should not be manually repeated inside views.

316. Soft Deletion

Financially relevant entities should generally use archival/status-based deletion.

Examples:

Customer â†’ archived

Finance Account â†’ cancelled

Collection â†’ reversed

Expense â†’ deleted/reversed with audit

Avoid:

Model.objects.filter(...).delete()

for financial history.

317. What Can Be Hard Deleted?

Temporary/non-financial records can be deleted where safe.

Examples:

Expired OTP

Temporary import file

Unused draft configuration

But customer financial history should be retained according to product/legal retention requirements.

318. Database Constraints

Application validation alone is not enough.

PostgreSQL should enforce critical constraints where appropriate.

Examples:

principal_amount > 0

paid_amount >= 0

expected_amount >= 0

expense_amount > 0

tenure_count > 0

Combined with service-layer validation, this provides defense in depth.

319. Financial Decimal Precision

Recommended money fields:

DecimalField(
    max_digits=14,
    decimal_places=2
)

depending on the expected maximum business values.

Interest rates may use higher precision:

decimal_places = 4

Never use Python/DB floating-point types for monetary calculations.

320. Pagination Standard

All potentially large list endpoints should support pagination.

Examples:

customers
finance accounts
collections
expenses
imports
audit logs

Recommended initial default:

page_size = 20

Allow controlled overrides such as:

?page=2&page_size=50

with a maximum.

Example:

MAX_PAGE_SIZE = 100
321. Pagination Response

Use a consistent format:

{
  "success": true,
  "data": {
    "count": 248,
    "next": "...",
    "previous": null,
    "results": []
  }
}

or your own standardized metadata structure.

The important requirement is consistency across applications.

322. Filtering Architecture

Following your five-layer requirement:

View

Handles:

Query parameter extraction
Filter validation
Permission/application validation
Pagination configuration
Service

Handles:

QuerySet construction
Database filtering
Search
Ordering
Business-specific query rules

Example:

GET /customers/?status=active&search=ramesh

View validates:

status = active
search = ramesh

then calls:

GuestCustomerService.get_customers(
    workspace=workspace,
    status=status,
    search=search,
)
323. Standard Ordering

Useful list APIs should support ordering.

Customers:

name
created_at
outstanding
last_collection

Collections:

collection_date
created_at
paid_amount

Expenses:

expense_date
amount
created_at

The service must whitelist ordering fields.

Never pass arbitrary frontend ordering directly into ORM operations.

324. API Response Standard

Use one response structure across the project.

Success:

{
  "success": true,
  "message": "Collection recorded successfully.",
  "data": {}
}

Validation failure:

{
  "success": false,
  "message": "Validation failed.",
  "errors": {
    "paid_amount": [
      "Paid amount cannot exceed outstanding amount."
    ]
  }
}

Business failure:

{
  "success": false,
  "message": "This finance account is already completed.",
  "code": "FINANCE_ACCOUNT_COMPLETED"
}
325. Exception Architecture

Create project-level custom exceptions.

Examples:

BusinessValidationError

ResourceNotFoundError

WorkspaceAccessDenied

FeatureLimitExceeded

InvalidFinancialOperation

DuplicateOperationError

A global DRF exception handler converts them into standardized API responses.

This prevents every view from implementing repetitive:

try:
    ...
except Exception:
    ...
326. Database Transactions

Use transactions around multi-record financial operations.

Mandatory examples:

Guest Registration + Workspace Creation

Finance Account + Schedule Creation

Collection + Allocation + Balance Update

Collection Reversal

Import Row Financial Creation

Guest â†’ Lender Upgrade

Use:

transaction.atomic()

Service layer owns these transaction boundaries.

327. Backup Strategy

Your PostgreSQL production database should have backups independently of application-level exports.

These are different concepts.

User Export
Excel / CSV / PDF

Used by lender.

Database Backup
PostgreSQL backup

Used for disaster recovery.

328. Production Backup Architecture

If PostgreSQL is hosted using a managed provider such as Railway or another production database provider, backup capabilities depend on the selected infrastructure/plan.

Regardless of provider, your architecture should account for:

Production PostgreSQL
        â”‚
        â”œâ”€â”€ Automated Provider Backups
        â”‚
        â””â”€â”€ Periodic Independent Backup

You do not need to maintain a permanently running duplicate PostgreSQL database just to have backups.

329. pg_dump

A periodic backup can use:

pg_dump

Conceptually:

PostgreSQL
     â†“
pg_dump
     â†“
Encrypted Backup File
     â†“
Object Storage

Backups should not simply remain on the same application server.

If the server itself is lost, the backup would also be lost.

330. Backup Requirements

Production planning should include:

Daily automated backups

Retention policy

Encrypted storage

Restore testing

Database credentials protection

Backup monitoring

A backup that has never been tested for restoration should not be assumed to be reliable.

331. Uploaded File Storage

Files such as:

expense receipts
import spreadsheets
generated reports
future customer documents

should not rely on a container's local filesystem in production.

Use object storage.

Conceptually:

Django
   â†“
Storage Backend
   â†“
Object Storage

The application database stores the file reference, not the binary file itself.

332. Redis in V1

Redis is useful but should not be a mandatory architectural dependency for the first Guest Workspace release unless required by your deployment.

V1 can operate with:

Django
DRF
PostgreSQL

Redis can later support:

Caching

Rate Limiting

Django Channels

Celery

Distributed Locks

Temporary Data

WebSocket Channel Layer
333. Django Channels

Guest Workspace V1 does not require WebSockets for its core functionality.

Normal REST APIs are enough for:

Customer creation
Collection entry
Expenses
Dashboard
Reports

When V2 introduces multiple employees working simultaneously, Django Channels may become useful for:

Live collection updates

Collector status

Dashboard refreshes

Notifications

At that point:

Django Channels
       +
Redis Channel Layer

is the recommended production architecture.

334. Guest â†’ Lender Upgrade

This is one of the most important future-proofing requirements.

The Guest Workspace must not become dead data when a user purchases V2.

Everything valuable should migrate or attach to the new business.

335. Upgrade Goal

Before:

User
 â”‚
 â””â”€â”€ GuestWorkspace
       â”‚
       â”œâ”€â”€ Customers
       â”œâ”€â”€ Finance Accounts
       â”œâ”€â”€ Collections
       â””â”€â”€ Expenses

After:

User
 â”‚
 â””â”€â”€ FinanceBusiness
       â”‚
       â”œâ”€â”€ Customers
       â”œâ”€â”€ Finance Accounts
       â”œâ”€â”€ Collections
       â”œâ”€â”€ Expenses
       â”œâ”€â”€ Areas
       â”œâ”€â”€ Employees
       â””â”€â”€ Routes

The user remains the same authenticated identity.

336. Avoid Copying Everything If Possible

A stronger architecture is to make the core financial models reusable between Guest and ERP rather than literally copying millions of rows during upgrade.

Long-term conceptual design:

Workspace
    â”‚
    â”œâ”€â”€ workspace_type = guest
    â”‚
    â””â”€â”€ workspace_type = business

Then:

Customer
FinanceAccount
Collection
Expense

belong to the workspace.

Upgrade becomes largely:

Guest Workspace
      â†“
Convert Workspace Type
      â†“
Attach Business Configuration
      â†“
Enable ERP Features

instead of:

Copy Customers
Copy Accounts
Copy Collections
Copy Expenses
337. Recommended Refinement to Earlier Model Naming

Because we now know Guest â†’ ERP conversion is a major product requirement, I would slightly refine the architecture before coding.

Instead of database models named:

GuestCustomer
GuestFinanceAccount
GuestCollection
GuestExpense

prefer:

Customer
FinanceAccount
Collection
CollectionSchedule
CollectionAllocation
Expense

inside the finance/workspace domain.

They belong to a:

Workspace

whose type determines available functionality.

This avoids duplicate V2 tables.

338. Workspace Model Refinement

Instead of only:

GuestWorkspace

use a generic:

Workspace

with:

workspace_type

Choices:

guest
finance_business

V1 creates:

workspace_type = guest

V2 upgrade changes it to:

workspace_type = finance_business

and creates additional business configuration.

This is a major improvement before implementation begins.

339. Revised Core Architecture

Therefore the recommended final data architecture becomes:

User
 â”‚
 â–¼
Workspace
 â”‚
 â”œâ”€â”€ WorkspaceSettings
 â”‚
 â”œâ”€â”€ Subscription
 â”‚
 â”œâ”€â”€ Customer
 â”‚      â”‚
 â”‚      â””â”€â”€ FinanceAccount
 â”‚             â”‚
 â”‚             â”œâ”€â”€ CollectionSchedule
 â”‚             â”œâ”€â”€ Collection
 â”‚             â”‚      â”‚
 â”‚             â”‚      â””â”€â”€ CollectionAllocation
 â”‚             â”‚
 â”‚             â””â”€â”€ Adjustments
 â”‚
 â”œâ”€â”€ Expense
 â”‚
 â”œâ”€â”€ ImportJob
 â”‚
 â””â”€â”€ AuditLog

V2 adds:

Workspace
 â”‚
 â”œâ”€â”€ Areas
 â”œâ”€â”€ Routes
 â”œâ”€â”€ Employees
 â”œâ”€â”€ Employee Assignments
 â”œâ”€â”€ Salaries
 â”œâ”€â”€ Cash Handovers
 â””â”€â”€ Business Configuration

without recreating the core finance records.

340. UpgradeService

Future:

class WorkspaceUpgradeService:
    ...

Methods:

validate_upgrade()

preview_upgrade()

upgrade_to_business()

create_business_configuration()

create_owner_membership()

activate_subscription()

enable_features()

rollback_upgrade()
341. Upgrade Transaction
Begin Transaction
       â†“
Lock Workspace
       â†“
Validate Guest Workspace
       â†“
Validate Subscription
       â†“
Create Business Configuration
       â†“
Create Owner Membership
       â†“
Convert Workspace Type
       â†“
Enable ERP Features
       â†“
Preserve Customers
       â†“
Preserve Finance Accounts
       â†“
Preserve Collections
       â†“
Preserve Expenses
       â†“
Audit Upgrade
       â†“
Commit

No customer financial records need to move if the generic workspace architecture is adopted.

342. V1 Recommended App Structure

With the refinements above, I recommend keeping the number of Django apps small, as you requested earlier:

backend/
â”‚
â”œâ”€â”€ config/
â”‚
â”œâ”€â”€ core/
â”‚
â”œâ”€â”€ accounts/
â”‚
â”œâ”€â”€ masters/
â”‚
â”œâ”€â”€ finance/
â”‚
â””â”€â”€ integrations/
core

Contains:

Base models
Workspace
Workspace settings
Plans
Subscriptions
Audit logs
Common exceptions
Common pagination
Utilities
Permissions
accounts

Contains:

User
Authentication
OTP
Sessions
Login history
masters

Contains:

Locations
Collection frequencies
Interest types
Payment modes
Statuses
Expense categories
finance

Major V1 application.

Contains:

Customers
Finance accounts
Schedules
Collections
Allocations
Expenses
Dashboard
Reports
Imports
Exports
Calculator
integrations

Contains external provider boundaries:

Google Maps

Storage

SMS â€” future add-on

WhatsApp â€” future add-on

This is cleaner than maintaining separate guest_workspace and business_finance apps with duplicate models.

343. Final V1 Priority

Development priority should therefore be:

Foundation
   â†“
Accounts
   â†“
Workspace
   â†“
Masters
   â†“
Customers
   â†“
Finance Accounts
   â†“
Existing Business Migration
   â†“
Collection Schedule
   â†“
Digital Collection Register
   â†“
Expenses
   â†“
Dashboard
   â†“
Reports
   â†“
Import / Export
   â†“
Audit + Security
   â†“
Production Deployment

V1 ends here from a product-scope perspective.

The database and service architecture, however, is intentionally prepared for the next layer.

---

## 344. Frontend-Backend Architecture & Gap Resolution Appendix

To align backend PRD specifications with the frontend application structure (`Fintech_Frontend`), the following technical contracts and architectural decisions are formalized:

### 1. Customer vs. Loan Entity Decoupling
- While the database maintains strict 1-to-many separation between `Customer` and `FinanceAccount` / `Loan`, guest workspace API serializers provide flattened response helpers (`primary_active_loan`) so single-loan UI screens (such as `mock-data.ts`) can render seamlessly without breaking multi-loan enterprise capability.

### 2. Authentication Policy
- Primary authentication uses Mobile Phone + OTP verification followed by password setup.
- Social OAuth 2.0 endpoints (`/api/v1/accounts/oauth/google/`, `/api/v1/accounts/oauth/microsoft/`) are supported to handle the frontend login interface options.

### 3. PWA Offline Batch Synchronization
- Field collection entries accept client-generated `offline_id` (UUID), `gps_latitude`, `gps_longitude`, and device timestamp to enable offline batch sync via `POST /api/v1/field/sync/`.

### 4. Cash Reconciliation Pipeline
- Cash handovers transition through explicit states (`PENDING_VERIFICATION` ──► `VERIFIED` / `DISCREPANCY_FLAGGED` ──► `RECONCILED_AND_LOCKED`) linking collector shift drawer submissions to branch manager verification.



