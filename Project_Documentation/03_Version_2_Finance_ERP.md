# Version 2 – Finance ERP / Lender Platform (Full Documentation)

This file contains the full Version 2 ERP and lender-platform specification from the original source document.

--- BEGIN VERSION 2 SECTION ---

Chapter 6 â€” Finance ERP / Lender V2
344. Purpose

Version 2 converts the lightweight Guest Workspace into a complete finance-business management platform.

The main V2 roles are:

Admin
Lender / Owner
Employee / Collector

The lender owns and controls the finance business.

Employees work under the lender and are primarily responsible for field collections.

Admin manages the overall SaaS platform.

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
345. V1 â†’ V2 Upgrade

The architecture defined previously becomes important here.

Before upgrade:

User
 â”‚
 â–¼
Workspace
 â”‚
 â”œâ”€â”€ Customers
 â”œâ”€â”€ Finance Accounts
 â”œâ”€â”€ Collections
 â””â”€â”€ Expenses

workspace_type = guest

After upgrade:

Same User
 â”‚
 â–¼
Same Workspace
 â”‚
 â”œâ”€â”€ Existing Customers
 â”œâ”€â”€ Existing Finance Accounts
 â”œâ”€â”€ Existing Collections
 â”œâ”€â”€ Existing Expenses
 â”‚
 â”œâ”€â”€ Business Profile
 â”œâ”€â”€ Areas
 â”œâ”€â”€ Routes
 â”œâ”€â”€ Employees
 â”œâ”€â”€ Assignments
 â”œâ”€â”€ Salaries
 â””â”€â”€ Cash Reconciliation

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
Suspensions.
Support operations.
Platform analytics.
Lender

Controls:

Only their Workspace

Can manage:

Their employees.
Their customers.
Their finance accounts.
Their areas.
Their routes.
Their collections.
Their expenses.
Their salaries.
Their business settings.

A Lender must never be able to access another lender's workspace.

348. Employee / Collector Role

Employees belong to a finance workspace.

Their primary responsibilities are:

View Assigned Area

View Assigned Customers

Follow Collection Route

Open Customer Details

Record Collection

Record Non-Payment Reason

Capture Collection Time

Capture GPS where enabled

Record Expense

View Personal Daily Summary

View Collection History

View Salary Information where permitted

Employees should not automatically receive access to:

Entire Business Revenue
Other Employees' Collections
Business-wide Reports
Subscription
Finance Settings
Other Areas
Employee Salaries

unless the lender grants those permissions.

349. V2 Domain Architecture

V2 extends the existing system:

Workspace
â”‚
â”œâ”€â”€ BusinessProfile
â”‚
â”œâ”€â”€ WorkspaceMembership
â”‚
â”œâ”€â”€ Area
â”‚    â”‚
â”‚    â”œâ”€â”€ EmployeeAreaAssignment
â”‚    â”œâ”€â”€ Customers
â”‚    â””â”€â”€ CollectionRoute
â”‚
â”œâ”€â”€ Employees
â”‚
â”œâ”€â”€ Customers
â”‚    â”‚
â”‚    â””â”€â”€ FinanceAccount
â”‚          â”‚
â”‚          â”œâ”€â”€ Schedule
â”‚          â””â”€â”€ Collections
â”‚
â”œâ”€â”€ EmployeeExpense
â”‚
â”œâ”€â”€ Salary
â”‚
â”œâ”€â”€ CashHandover
â”‚
â””â”€â”€ Reports
350. WorkspaceMembership

Do not identify employees merely through:

User.account_type = employee

A relationship should exist between the user and workspace.

Recommended:

WorkspaceMembership

Fields:

id

public_id

workspace

user

role

status

joined_at

terminated_at

created_by

created_at
updated_at
351. Membership Roles

Initial:

owner
collector

Future:

manager
accountant
supervisor

This enables a single authentication architecture while business roles remain workspace-specific.

352. Membership Status

Recommended:

invited
active
suspended
terminated

An employee's User account does not need to be deleted when employment ends.

Instead:

WorkspaceMembership.status = terminated

Their historical collection records remain linked to the same person.

353. BusinessProfile

When Guest upgrades or a new Lender directly registers for ERP, create:

BusinessProfile

One-to-one with Workspace.

Fields:

id

workspace

business_name

owner_name

business_mobile

alternate_mobile

email

business_category

address

state
district
city
village
postal_code

latitude
longitude

registration_number
tax_identifier

logo

business_start_date

created_at
updated_at

Registration/tax fields can remain optional depending on product requirements.

354. Business Settings

Recommended separate model:

FinanceBusinessSettings

Fields may include:

workspace

default_interest_type

default_interest_rate

default_collection_frequency

default_grace_period

allow_partial_collection

allow_advance_collection

allow_overpayment

allow_employee_expenses

require_collection_gps

require_customer_gps

require_expense_receipt

employee_area_limit

max_collectors_per_area

penalty_enabled

route_management_enabled

created_at
updated_at
355. Maximum Collectors Per Area

Your requirement was:

A lender can assign up to two collectors per area.

Do not hardcode:

if collectors >= 2:

Use:

max_collectors_per_area

Default:

2

Then:

Area A
 â”œâ”€â”€ Collector 1
 â””â”€â”€ Collector 2

A third assignment is rejected unless configuration/plan permits it.

356. Area Model

An Area represents the lender's operational collection area.

It is not the same as geographic master data.

Examples:

Anaparthi Main Market

Railway Station Route

Area 1

East Side

Monday Route

Recommended:

Area
357. Area Fields
id

public_id

workspace

area_code

name

description

state
district
city
village

postal_code

center_latitude
center_longitude

status

created_by

created_at
updated_at

Optional future fields:

boundary_polygon
map_metadata
358. Area Code

Generated per workspace.

Example:

AREA-001
AREA-002

Constraint:

unique(workspace, area_code)
359. Area Status

Recommended:

active
inactive
archived

Areas containing financial history should not be physically deleted.

360. Customer â†’ Area Assignment

Customers should have an operational area relationship.

Recommended:

Customer.area

nullable initially.

Example:

Ramesh
   â†“
Anaparthi Main Market

During Guest â†’ Lender upgrade, existing customers may initially have:

area = NULL

The lender can assign them later.

361. Bulk Customer Area Assignment

Because upgraded lenders may already have hundreds of customers, V2 must support:

Select Customers
       â†“
Assign Area

Endpoint concept:

POST /api/v2/areas/{area_id}/customers/assign/

Input:

customer_ids[]

Service validates that every customer belongs to the same workspace.

362. Customer Area Transfer

Customers may move.

Do not simply overwrite area without history.

Recommended model:

CustomerAreaHistory

Fields:

customer

from_area

to_area

changed_by

reason

effective_date

created_at

Then:

Area A
 â†“
Customer Transfer
 â†“
Area B

remains auditable.

363. Employee Model

Authentication information remains in:

accounts.User

Employment information should be separate.

Recommended:

EmployeeProfile
364. EmployeeProfile Fields
id

public_id

workspace

user

employee_code

full_name

mobile_number

alternate_mobile

email

address

state
district
city
village
postal_code

joining_date

employment_type

salary_type

base_salary

status

emergency_contact_name

emergency_contact_number

profile_photo

created_by

created_at
updated_at

Sensitive future fields should be stored only when genuinely necessary.

365. Employee Code

Generated:

EMP-0001
EMP-0002

Unique per workspace.

366. Employee Status

Recommended:

active
on_leave
suspended
terminated

Terminated employees remain available in historical reports.

367. Employee Creation Flow

Lender:

Add Employee
      â†“
Enter Employee Details
      â†“
Create/Find User Identity
      â†“
Create Workspace Membership
      â†“
Create Employee Profile
      â†“
Assign Role
      â†“
Optional Area Assignment
      â†“
Send Account Setup Instructions

All related database operations should be transactional.

368. Existing User Scenario

Suppose the employee's mobile number already belongs to an existing platform user.

Do not create another User.

Instead:

Existing User
     â†“
New WorkspaceMembership
     â†“
EmployeeProfile

This architecture supports future multi-workspace participation if the business permits it.

369. EmployeeAreaAssignment

Do not rely only on:

employee.area

because:

One area may have two collectors.
A collector may be moved.
Assignment history matters.

Recommended model:

EmployeeAreaAssignment
370. Assignment Fields
id

workspace

employee

area

assigned_from

assigned_until

status

assigned_by

transfer_reason

created_at
updated_at

Statuses:

active
completed
cancelled
371. Collector Area Limit

Your original requirement implied collectors are assigned specifically to areas.

V1/V2 default can enforce:

One active primary area per collector

while:

Maximum 2 active collectors per area

These should be configurable business rules.

372. Employee Transfer

Example:

Collector Ravi

Area A
  â†“
Transfer
  â†“
Area B

Flow:

Validate Employee
      â†“
Validate Destination Area
      â†“
Check Collector Capacity
      â†“
Close Previous Assignment
      â†“
Create New Assignment
      â†“
Recalculate Collection Access
      â†“
Audit

Historical collections remain associated with the collector and original customer/area context.

373. AreaService

Recommended:

class AreaService:
    ...

Methods:

create_area()

update_area()

get_area()

get_areas()

archive_area()

assign_customers()

transfer_customer()

get_area_customers()

get_area_summary()

validate_area_capacity()
374. EmployeeService
class EmployeeService:
    ...

Methods:

create_employee()

update_employee()

get_employee()

get_employees()

activate_employee()

suspend_employee()

terminate_employee()

assign_area()

transfer_area()

remove_area_assignment()

get_employee_summary()

get_employee_collection_summary()
375. Collector Access Rule

When a collector requests customers:

Authenticated Employee
       â†“
Workspace Membership
       â†“
Active Area Assignment
       â†“
Customers in Assigned Area

The collector should not be able to change:

?area_id=another_area

and access customers outside their assignment.

Authorization must come from the server.

376. Collection Ownership in V2

Existing Collection.recorded_by becomes extremely useful.

Example:

Customer: Ramesh

Amount: â‚¹500

Collected By:
Ravi

Collection Time:
09:42 AM

Payment Mode:
Cash

The lender can now see exactly who recorded each collection.

377. Collection Snapshot Additions

For stronger historical reporting, V2 collection records should also capture or relate to:

area_at_collection

collector

customer_location

collection_location

Do not depend only on the customer's current area because the customer may later move.

378. Collection GPS

If:

require_collection_gps = True

the employee's device captures:

latitude
longitude
accuracy

when collection is recorded.

The frontend uses the device's native geolocation capability.

The backend stores coordinates.

Google does not need to be called simply to obtain GPS coordinates.

379. GPS Validation

The backend validates:

-90 <= latitude <= 90

-180 <= longitude <= 180

Optional metadata:

gps_accuracy
captured_at

This provides more context than coordinates alone.

380. Collection Location Verification

A future feature can compare:

Customer GPS
       vs
Collector Collection GPS

to calculate approximate distance.

Example:

Customer registered location:
17.123...

Collection recorded:
17.124...

Then:

Distance = 85 metres

This can flag suspicious remote collection entries.

This should be optional rather than blocking V2's initial release.

381. Route Management

Each area may have a preferred customer collection order.

Example:

Area A

1. Ramesh
2. Suresh
3. Mahesh
4. Ravi
5. Krishna

The lender or authorized collector can modify the route order.

382. CollectionRoute Model

Recommended:

CollectionRoute

Fields:

id

public_id

workspace

area

name

collection_frequency

collection_day

status

created_by

created_at
updated_at

An area can eventually have different routes for:

Daily customers
Weekly customers
Monthly customers
383. RouteStop Model

Recommended:

RouteStop

Fields:

id

route

customer

sequence_number

latitude

longitude

estimated_distance

estimated_duration

is_active

created_at
updated_at

Constraint:

unique(route, customer)

and preferably:

unique(route, sequence_number)
384. Why Store Route Order

Google can suggest an efficient route, but the lender may know local realities better.

Example:

Road blocked in morning

Market opens after 10 AM

Customer only available after lunch

Therefore:

Google Suggested Route
        â†“
Lender Edits
        â†“
Saved Business Route

The platform must preserve the lender's chosen order.

385. Customer GPS Capture

When adding a new customer:

Add Customer
      â†“
Enter Details
      â†“
Capture Current Location
      â†“
Device GPS
      â†“
latitude + longitude
      â†“
Optional Reverse Geocoding
      â†“
Save Customer

Alternatively:

Search Address
      â†“
Google Places
      â†“
Select Location
      â†“
Save Coordinates

Both methods should be supported.

386. Route Generation Flow
Select Area
      â†“
Get Customers Due
      â†“
Read Customer GPS
      â†“
Send Stops to Routing Provider
      â†“
Receive Route
      â†“
Display Inside Application
      â†“
Lender Reorders if Needed
      â†“
Save Route Order
387. In-App Navigation

Your earlier requirement was:

Do not redirect the collector to another application.

Therefore maps should be embedded inside your frontend.

The collector stays inside your application.

Conceptually:

Collector App
     â”‚
     â”œâ”€â”€ Customer List
     â”‚
     â””â”€â”€ Embedded Map
            â”‚
            â”œâ”€â”€ Current Position
            â”œâ”€â”€ Route
            â”œâ”€â”€ Customer Markers
            â””â”€â”€ Next Stop
388. Google Maps Integration

The external integration boundary can support Google Maps Platform services such as:

Maps JavaScript API

Places API

Geocoding API

Routes API

Use only the services required by each flow.

For example, device GPS should come from the browser/mobile device rather than paying an external provider unnecessarily.

389. GoogleMapsService

Inside:

integrations/services/google_maps_service.py

Recommended:

class GoogleMapsService:
    ...

Methods conceptually:

geocode_address()

reverse_geocode()

search_places()

get_place_details()

calculate_route()

calculate_route_matrix()

optimize_stops()

The finance service should not directly contain HTTP requests to Google.

390. RouteService
class RouteService:
    ...

Methods:

create_route()

generate_route()

optimize_route()

reorder_route()

get_route()

get_employee_route()

get_today_route()

add_route_stop()

remove_route_stop()

resequence_stops()

calculate_route_summary()
391. Route Editing

Frontend can submit:

Customer A â†’ 1
Customer C â†’ 2
Customer B â†’ 3
Customer D â†’ 4

Backend validates:

All customers belong to workspace.
All belong to appropriate area.
No duplicate sequence numbers.
No duplicate customers.
Employee has permission to edit route.

Then update atomically.

392. Today's Collector Route

Endpoint concept:

GET /api/v2/employee/today-route/

Response should provide:

Area

Collector

Expected Customers

Route Stops

Customer Coordinates

Expected Amount

Collection Status

Total Route Distance

Estimated Duration

This allows one API call to initialize the employee's field screen.

393. Collector Dashboard

Employee dashboard should focus on operational information.

KPIs:

Today's Assigned Customers

Today's Expected Collection

Today's Collected Amount

Today's Pending Amount

Customers Completed

Customers Remaining

Partial Payments

Unavailable Customers

Today's Expenses

Route Progress

Do not expose lender-level profitability by default.

394. Collector Customer Card

Example:

Ramesh

FIN-00123

Weekly

Expected Today        â‚¹500
Total Outstanding   â‚¹6,500

Address:
Main Road, Anaparthi

[Directions]

[Collect]

[Not Paid]

[History]

Directions remain inside the application map.

395. Collector Collection Flow
Open Customer
      â†“
Review Amount Due
      â†“
Enter Amount
      â†“
Select Payment Mode
      â†“
Optional Notes
      â†“
Capture GPS
      â†“
Submit
      â†“
CollectionService
      â†“
Update Account
      â†“
Update Route Stop
      â†“
Update Employee Summary
      â†“
Update Lender Dashboard

The same core CollectionService from V1 should be reused.

396. Employee Expense

Collectors may spend money during the day.

Examples:

Fuel
Parking
Food
Vehicle Repair
Other Approved Expense

Employee expense should be distinguished from owner-entered general business expense.

Recommended:

EmployeeExpense
397. EmployeeExpense Fields
id

public_id

workspace

employee

area

expense_date

expense_time

category

amount

payment_mode

description

receipt

latitude

longitude

approval_status

approved_by

approved_at

rejection_reason

created_at
updated_at
398. Expense Approval

Recommended statuses:

pending
approved
rejected
cancelled

Collector creates:

Fuel â‚¹300

Lender sees:

Pending Expense
Ravi
Fuel
â‚¹300

and can approve/reject.

399. Why Expense Approval Matters

If employee expenses immediately reduce business cash totals without lender approval, employees could incorrectly affect reporting.

Therefore lender dashboards can distinguish:

Submitted Expenses

Approved Expenses

Rejected Expenses

Only approved expenses should normally affect official business expense summaries.

400. Cash vs Digital Collections

Payment mode matters significantly in V2.

Example:

Ravi collected:

Cash           â‚¹12,000
UPI             â‚¹5,000
Bank Transfer   â‚¹2,000

Cash requires physical handover.

Digital payments may not.

Therefore cash reconciliation should primarily track physical cash.

401. Cash Handover

At the end of the collection period/day:

Collector
   â†“
Cash Collected
   â†“
Approved Cash Expenses
   â†“
Expected Cash in Hand
   â†“
Cash Handed to Lender
   â†“
Difference

This is a major V2 feature.

402. CashHandover Model

Recommended:

CashHandover

Fields:

id

public_id

workspace

employee

handover_date

collection_cash_amount

approved_cash_expenses

expected_handover_amount

actual_handover_amount

difference_amount

status

submitted_by

verified_by

submitted_at

verified_at

remarks

created_at
updated_at
403. Cash Calculation

Conceptually:

Cash Collections
-
Approved Cash Expenses
=
Expected Cash Handover

Example:

Cash Collected        â‚¹15,000

Fuel Expense             â‚¹300
Parking                    â‚¹50

Expected Handover      â‚¹14,650

Collector hands over:

â‚¹14,650

Difference:

â‚¹0
404. Cash Difference

If:

Expected = â‚¹14,650
Actual   = â‚¹14,500

then:

Shortage = â‚¹150

If actual is higher:

Excess

The lender should provide/record remarks when verifying discrepancies.

405. Cash Handover Status

Recommended:

draft
submitted
verified
disputed
cancelled

Once verified, modification should be heavily restricted.

Corrections should use audit/adjustment mechanisms.

406. CashReconciliationService
class CashReconciliationService:
    ...

Methods:

calculate_expected_cash()

create_handover()

submit_handover()

verify_handover()

dispute_handover()

get_employee_daily_cash()

get_pending_handovers()

get_handover_history()
407. Employee Salary

Lender defines salary for employees.

Do not store only:

employee.salary

because salaries change over time.

Use salary history.

Recommended:

EmployeeSalaryStructure
408. Salary Structure Fields
id

workspace

employee

salary_type

base_amount

effective_from

effective_until

status

created_by

created_at
updated_at

Salary types initially:

monthly
daily

Future:

collection_based
commission
mixed
409. Salary Payment

Separate model:

SalaryPayment

Fields:

id

workspace

employee

salary_period_start

salary_period_end

base_salary

allowances

deductions

expense_adjustments

net_salary

payment_date

payment_mode

status

remarks

created_by

created_at
updated_at
410. Salary Status

Recommended:

draft
approved
paid
cancelled

Payroll should remain relatively simple in initial V2.

The platform does not need to become a complete HR/payroll product immediately.

411. Penalty / Extra Charge

Your original requirement included:

If tenure exceeds, some extra charges may be added optionally depending on the customer's payment progress.

This should be handled as an explicit adjustment rather than silently changing interest.

Recommended:

FinanceAdjustment
412. FinanceAdjustment Fields
id

public_id

workspace

finance_account

adjustment_type

amount

reason

effective_date

status

created_by

approved_by

created_at
updated_at

Types:

penalty
late_charge
waiver
discount
correction
other
413. Penalty Rule

The system may suggest:

Account overdue

but V2 should initially allow the lender to decide whether a charge applies.

Example:

Ramesh

Expected End:
01 July

Outstanding:
â‚¹2,000

Payment History:
Good

Suggested:
Overdue

Lender:
Waive Charge

Another customer:

Repeatedly missed payments

Lender:
Add â‚¹300 late charge

This matches your original real-world business requirement better than automatically penalizing every overdue account.

414. Finance Adjustment Accounting

If:

Outstanding = â‚¹2,000

and lender adds:

Late Charge = â‚¹300

then:

Adjusted Outstanding = â‚¹2,300

The original:

principal
interest
original total payable

must remain historically visible.

Do not rewrite original interest to manufacture the new total.

415. Lender Dashboard

The lender dashboard becomes much richer than the Guest dashboard.

Core KPIs:

Total Customers

Active Finance Accounts

Total Principal Deployed

Total Expected Receivable

Total Outstanding

Today's Expected Collection

Today's Actual Collection

Today's Collection %

Today's Cash Collection

Today's Digital Collection

Today's Expenses

Pending Employee Expenses

Expected Cash Handovers

Pending Cash Handovers

Overdue Accounts

Employees Active Today
416. Area Analytics

For each area:

Customers

Active Accounts

Amount Deployed

Outstanding

Today's Expected

Today's Collected

Collection %

Pending Customers

Overdue Customers

Assigned Collectors

Expenses

This allows the lender to compare business performance geographically.

417. Collector Analytics

For each collector:

Assigned Customers

Expected Collection

Collected Amount

Collection %

Paid Customers

Partial Customers

Missed Customers

Unavailable Customers

Cash Collected

Digital Collected

Expenses

Cash Pending Handover

Avoid simplistic "performance scores" until the business has clear, fair scoring rules.

418. Employee APIs

Recommended:

GET    /api/v2/employees/

POST   /api/v2/employees/

GET    /api/v2/employees/{id}/

PATCH  /api/v2/employees/{id}/

POST /api/v2/employees/{id}/suspend/

POST /api/v2/employees/{id}/activate/

POST /api/v2/employees/{id}/terminate/

POST /api/v2/employees/{id}/assign-area/

POST /api/v2/employees/{id}/transfer-area/

GET /api/v2/employees/{id}/collections/

GET /api/v2/employees/{id}/expenses/

GET /api/v2/employees/{id}/summary/
419. Area APIs
GET    /api/v2/areas/

POST   /api/v2/areas/

GET    /api/v2/areas/{id}/

PATCH  /api/v2/areas/{id}/

DELETE /api/v2/areas/{id}/

GET  /api/v2/areas/{id}/customers/

POST /api/v2/areas/{id}/customers/assign/

GET /api/v2/areas/{id}/employees/

GET /api/v2/areas/{id}/summary/

DELETE should generally archive rather than physically remove.

420. Route APIs
GET  /api/v2/routes/

POST /api/v2/routes/

GET /api/v2/routes/{id}/

PATCH /api/v2/routes/{id}/

POST /api/v2/routes/{id}/generate/

POST /api/v2/routes/{id}/optimize/

POST /api/v2/routes/{id}/reorder/

GET /api/v2/routes/{id}/stops/

GET /api/v2/employee/today-route/
421. Expense APIs

Employee:

POST /api/v2/employee/expenses/

GET /api/v2/employee/expenses/

Lender:

GET /api/v2/expenses/employee/

POST /api/v2/expenses/{id}/approve/

POST /api/v2/expenses/{id}/reject/

All access must be workspace-scoped.

422. Cash Handover APIs
GET /api/v2/cash-handovers/

POST /api/v2/cash-handovers/

GET /api/v2/cash-handovers/{id}/

POST /api/v2/cash-handovers/{id}/submit/

POST /api/v2/cash-handovers/{id}/verify/

POST /api/v2/cash-handovers/{id}/dispute/
423. Salary APIs
GET  /api/v2/employees/{id}/salary/

POST /api/v2/employees/{id}/salary/

GET /api/v2/salary-payments/

POST /api/v2/salary-payments/

POST /api/v2/salary-payments/{id}/approve/

POST /api/v2/salary-payments/{id}/mark-paid/
424. LenderService

Recommended:

class LenderService:
    ...

Methods:

get_business_profile()

update_business_profile()

get_business_settings()

update_business_settings()

get_business_summary()

get_lender_dashboard()

get_area_performance()

get_employee_performance()

get_cash_position()
425. V2 App Organization

You previously wanted fewer Django apps.

Do not create separate apps for:

employees
areas
routes
salaries
cash
expenses

unless the codebase eventually becomes large enough to justify it.

Recommended V2 structure remains:

accounts/
core/
masters/
finance/
integrations/

Inside finance/services/:

customer_service.py
finance_account_service.py
schedule_service.py
collection_service.py
expense_service.py

area_service.py
employee_service.py
route_service.py

cash_reconciliation_service.py
salary_service.py

adjustment_service.py

dashboard_service.py
report_service.py

This keeps the application count manageable while preserving domain separation through service classes.

426. V2 finance/models.py

Even if stored in one Django app, models can eventually be split into a Python package:

finance/
â”‚
â”œâ”€â”€ models/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ customer.py
â”‚   â”œâ”€â”€ finance_account.py
â”‚   â”œâ”€â”€ collection.py
â”‚   â”œâ”€â”€ expense.py
â”‚   â”œâ”€â”€ area.py
â”‚   â”œâ”€â”€ employee.py
â”‚   â”œâ”€â”€ route.py
â”‚   â”œâ”€â”€ cash.py
â”‚   â””â”€â”€ salary.py
â”‚
â”œâ”€â”€ serializers/
â”‚
â”œâ”€â”€ services/
â”‚
â”œâ”€â”€ views/
â”‚
â””â”€â”€ urls.py

This still follows your architecture:

Models
   â†“
Serializers
   â†“
Services
   â†“
Views
   â†“
URLs

Splitting files is only code organization, not additional Django applications.

427. V2 Authorization Architecture

Authentication answers:

Who are you?

Authorization answers:

What are you allowed to do?

For every request:

JWT
 â†“
User
 â†“
Workspace Membership
 â†“
Role
 â†“
Permission
 â†“
Resource Ownership

All must be validated server-side.

428. Role Permissions

Initial permission examples:

CUSTOMER_VIEW
CUSTOMER_CREATE
CUSTOMER_UPDATE

COLLECTION_VIEW
COLLECTION_CREATE
COLLECTION_REVERSE

EXPENSE_CREATE
EXPENSE_APPROVE

EMPLOYEE_VIEW
EMPLOYEE_MANAGE

AREA_VIEW
AREA_MANAGE

ROUTE_VIEW
ROUTE_MANAGE

REPORT_VIEW

SALARY_VIEW
SALARY_MANAGE

CASH_HANDOVER_CREATE
CASH_HANDOVER_VERIFY

BUSINESS_SETTINGS_MANAGE
429. Owner Permissions

Owner gets all workspace permissions by default.

Collector receives only necessary operational permissions.

Example:

CUSTOMER_VIEW_ASSIGNED

COLLECTION_VIEW_ASSIGNED

COLLECTION_CREATE

EXPENSE_CREATE

ROUTE_VIEW_ASSIGNED

CASH_HANDOVER_CREATE
430. Add-On Architecture

You specified that:

SMS Gateway

WhatsApp Business API

should be feature-version add-ons.

They should therefore not be tightly coupled to core finance functionality.

Conceptually:

Core ERP
   â”‚
   â”œâ”€â”€ SMS Add-On
   â”‚
   â””â”€â”€ WhatsApp Add-On

If the customer does not purchase them, the ERP continues working normally.

431. Communication Use Cases

Future SMS/WhatsApp functionality could support:

Payment Reminder

Payment Confirmation

Upcoming Due Reminder

Overdue Reminder

Finance Completion Message

Account Statement

Promise-to-Pay Reminder

The lender should control which communication types are enabled.

432. NotificationService

Core code should call an abstraction:

class NotificationService:
    ...

rather than directly calling an SMS vendor.

Conceptually:

Collection Recorded
      â†“
NotificationService
      â†“
Check Feature Access
      â†“
Check Business Preference
      â†“
SMS / WhatsApp Provider

This lets providers change without rewriting finance logic.

433. Add-On Cost Protection

Communication APIs can create variable costs.

Therefore V2 should track:

messages sent
message type
provider
delivery status
provider reference
estimated/actual cost

and enforce plan/add-on quotas where required.

Do not provide unlimited provider calls merely because a lender repeatedly clicks a button.

434. Complete V2 Daily Flow

The operational business flow becomes:

Lender
   â†“
Creates Areas
   â†“
Adds Employees
   â†“
Assigns Collectors to Areas
   â†“
Adds / Assigns Customers
   â†“
Captures Customer GPS
   â†“
Creates Finance Accounts
   â†“
Schedules Generated
   â†“
Routes Generated
   â†“
Collector Starts Day
   â†“
Opens Assigned Route
   â†“
Visits Customer
   â†“
Records Collection / Non-Payment
   â†“
GPS + Time + Collector Recorded
   â†“
Lender Dashboard Updates
   â†“
Collector Records Expenses
   â†“
Completes Route
   â†“
Cash Reconciliation
   â†“
Cash Handover
   â†“
Lender Verifies
   â†“
Daily Reports
435. Critical V2 Principle

The biggest architectural requirement across both versions is:

V1 Guest Workspace
        â†“
        â†“ upgrade
        â†“
V2 Finance ERP

and not:

Guest System
     X
Separate ERP System

Customers, finance accounts, schedules, collections and expenses should remain the same core domain records.

V2 simply adds people, areas, routes, controls, reconciliation and analytics around them.

This gives you a much cleaner Django/PostgreSQL architecture and avoids a costly V1â†’V2 data migration later.


-----

Chapter 7 â€” Platform Admin
436. Platform Admin Purpose

The Platform Admin is responsible for operating the complete SaaS platform.

Platform
â”‚
â”œâ”€â”€ Guest Workspaces
â”œâ”€â”€ Finance Businesses
â”‚   â”œâ”€â”€ Lenders
â”‚   â”œâ”€â”€ Employees
â”‚   â”œâ”€â”€ Customers
â”‚   â””â”€â”€ Business Activity
â”œâ”€â”€ Plans
â”œâ”€â”€ Subscriptions
â”œâ”€â”€ Add-ons
â”œâ”€â”€ Master Data
â”œâ”€â”€ Integrations
â”œâ”€â”€ Support
â”œâ”€â”€ Security
â””â”€â”€ Platform Analytics

Admin should have visibility into platform operations without becoming part of a lender's normal collection workflow.

437. Admin Role Architecture

Do not represent platform administrators as workspace members.

Recommended distinction:

User
â”‚
â”œâ”€â”€ Platform Role
â”‚     â””â”€â”€ ADMIN
â”‚
â””â”€â”€ WorkspaceMembership
      â”œâ”€â”€ OWNER
      â””â”€â”€ COLLECTOR

This prevents confusion between:

Platform Administrator

and:

Finance Business Owner
438. Admin Permission Levels

Initially, one admin role is enough.

However, design permissions so future roles can be introduced:

super_admin
support_admin
operations_admin
finance_admin

V1 does not need all these roles.

The permission architecture should simply avoid assuming every future admin must have unrestricted access.

439. Admin Dashboard

Endpoint:

GET /api/v1/admin/dashboard/

Admin dashboard should provide platform-level KPIs.

440. User Statistics

Show:

Total Registered Users

Active Users

Inactive Users

New Users Today

New Users This Week

New Users This Month

Also:

Guest Users

Lender / Owner Users

Employee Users
441. Workspace Statistics

Admin should see:

Total Workspaces

Guest Workspaces

Finance Business Workspaces

Active Workspaces

Suspended Workspaces

Converted Guest â†’ Business Workspaces

This is important for understanding V1-to-V2 conversion.

442. Business Statistics

Admin can view:

Total Finance Businesses

Active Businesses

Trial Businesses

Paid Businesses

Suspended Businesses

Recently Created Businesses

Admin should not need to calculate these on the frontend.

443. Platform Usage Analytics

Useful operational statistics:

Total Customers Created

Total Finance Accounts

Total Collections Recorded

Collections Recorded Today

Total Expenses Recorded

Active Employees

Active Areas

These values describe platform usage.

Be careful about displaying lender financial totals to ordinary admin/support roles unless operationally required.

444. Financial Privacy

The Platform Admin technically operates the infrastructure, but the application should still follow least-privilege principles.

For example, a support employee may need:

Workspace Name
Owner
Plan
Account Status
Feature Usage
Error Information

without automatically needing:

Every Customer Balance
Every Collection Amount
Customer Personal Details

Future admin permissions should support this separation.

445. Admin User Management

Admin endpoint family:

GET /api/v1/admin/users/

GET /api/v1/admin/users/{id}/

POST /api/v1/admin/users/{id}/activate/

POST /api/v1/admin/users/{id}/suspend/

POST /api/v1/admin/users/{id}/restore/

Avoid normal hard deletion.

446. Admin User List

Filters:

search

status

registration_date

workspace_type

role

plan

is_verified

ordering

Search can support:

Name
Mobile
Email
User ID
Workspace Name
447. User Detail

Admin can view appropriate account metadata:

User ID

Name

Mobile

Email

Verification Status

Account Status

Registration Date

Last Login

Workspace

Workspace Type

Plan

Subscription Status

Usage Summary

Sensitive authentication information must never be exposed.

Never return:

Password Hash
OTP
Refresh Token
Reset Token
API Secrets
448. User Suspension

Admin may suspend an account for:

Abuse.
Security issues.
Subscription problems.
Fraud investigation.
Terms violations.
Support intervention.

Recommended:

active
suspended
blocked
closed
449. Suspension Reason

Store:

status
reason
changed_by
changed_at

Prefer a history model for significant status changes.

Recommended:

UserStatusHistory
450. Workspace Management

Admin APIs:

GET /api/v1/admin/workspaces/

GET /api/v1/admin/workspaces/{id}/

POST /api/v1/admin/workspaces/{id}/suspend/

POST /api/v1/admin/workspaces/{id}/activate/

Workspace suspension is different from user suspension.

451. Why Separate User and Workspace Suspension?

Suppose:

Lender User
    â”‚
    â”œâ”€â”€ Workspace A
    â””â”€â”€ Future Workspace B

A problem with Workspace A does not necessarily mean the entire identity should be disabled.

Therefore:

User Status

and:

Workspace Status

should remain independent.

452. Workspace Detail

Admin can see:

Workspace ID

Workspace Name

Workspace Type

Owner

Created Date

Status

Plan

Subscription

Customer Count

Finance Account Count

Employee Count

Storage Usage

Feature Usage

For Guest:

guest

For full ERP:

finance_business
453. Workspace Usage Metrics

Create a service method such as:

AdminWorkspaceService.get_usage_summary()

Possible response:

Customers             82 / 100
Active Finance        57 / 100
Collections This Month 2,410
Storage               34 MB / 100 MB
Employees              2 / 5
Areas                  2

This becomes important for subscription enforcement.

454. Plan Management

Admin must configure product plans without code changes.

Recommended existing:

Plan

Admin CRUD:

GET    /api/v1/admin/plans/

POST   /api/v1/admin/plans/

GET    /api/v1/admin/plans/{id}/

PATCH  /api/v1/admin/plans/{id}/

POST /api/v1/admin/plans/{id}/activate/

POST /api/v1/admin/plans/{id}/deactivate/
455. Plan Configuration

Fields can include:

Name

Code

Description

Workspace Type

Billing Period

Price

Customer Limit

Finance Account Limit

Employee Limit

Area Limit

Storage Limit

Monthly Collection Limit

Import Enabled

Export Enabled

Reports Enabled

GPS Enabled

Route Management Enabled

Advanced Analytics Enabled

Status
456. Never Delete Active Plans

If 500 businesses use:

business_basic

and Admin no longer wants to sell it, set:

is_active = False

Existing subscribers may continue according to business policy.

Do not physically delete the plan.

457. Plan Features

Recommended:

Feature

Fields:

id
code
name
description
category
is_active

Examples:

GUEST_WORKSPACE

CUSTOMER_IMPORT

EXCEL_EXPORT

ADVANCED_REPORTS

EMPLOYEE_MANAGEMENT

AREA_MANAGEMENT

GPS_CAPTURE

ROUTE_MANAGEMENT

CASH_RECONCILIATION

SALARY_MANAGEMENT

SMS

WHATSAPP
458. PlanFeature

Relationship:

Plan
 â”‚
 â””â”€â”€ PlanFeature
       â”‚
       â””â”€â”€ Feature

Fields:

plan
feature
is_enabled
limit_value
configuration

This allows flexible feature packaging.

459. Add-On Management

Some capabilities should be purchasable independently.

Your explicitly identified add-ons are:

SMS Gateway
WhatsApp Business API

Future examples:

Additional Employees
Additional Storage
Advanced Reports
Additional Areas

Recommended:

AddOn
460. AddOn Model

Fields:

id

code

name

description

price

billing_type

feature

usage_limit

configuration

is_active

created_at
updated_at
461. Workspace Add-On

Recommended:

WorkspaceAddOn

Fields:

workspace

addon

status

activated_at

expires_at

usage_count

usage_reset_at

created_at
updated_at
462. SMS Add-On

Example:

SMS Add-On

â‚¹X / month

Included:
1,000 SMS

Usage:

723 / 1000

When limit reached:

SMS_LIMIT_REACHED

Core collection functionality must continue working.

463. WhatsApp Add-On

Similar architecture:

Workspace
   â†“
WhatsApp Add-On
   â†“
Provider Configuration
   â†“
Message Template
   â†“
Message
   â†“
Delivery Status

Actual provider implementation belongs in integrations.

464. Subscription Management

Recommended existing:

WorkspaceSubscription

Admin should see:

Workspace

Plan

Status

Billing Period

Start Date

Renewal Date

Expiry Date

Trial Information

Add-Ons
465. Subscription Status

Recommended:

trial

active

past_due

expired

cancelled

suspended

Do not mix subscription state with workspace state.

For example:

subscription = expired
workspace = active

may mean the workspace can still log in but has restricted functionality.

466. SubscriptionService
class SubscriptionService:
    ...

Methods:

create_subscription()

activate_subscription()

change_plan()

cancel_subscription()

expire_subscription()

renew_subscription()

get_entitlements()

check_usage_limit()

reset_usage()

get_subscription_summary()
467. Upgrade/Downgrade

Example:

Guest Free
    â†“
Business Basic
    â†“
Business Pro

or:

Business Pro
    â†“
Business Basic

Before downgrade, service checks:

Employees
Customers
Areas
Storage
Features in use

The downgrade should not delete existing business data.

468. Subscription Billing

Do not tightly couple the product architecture to one payment provider.

Use:

PaymentProviderService

Future integrations might use a payment gateway suitable for your market.

The domain should care about:

Payment Requested
Payment Successful
Payment Failed
Refunded

rather than provider-specific response structures.

469. Subscription Payment Model

Recommended:

SubscriptionPayment

Fields:

id
public_id

workspace
subscription

amount
currency

provider

provider_payment_id
provider_order_id

payment_status

payment_method

paid_at

failure_reason

created_at
updated_at
470. Payment Status

Recommended:

created
pending
successful
failed
refunded
partially_refunded

Subscription payment webhooks must be idempotent.

471. Admin Subscription APIs
GET /api/v1/admin/subscriptions/

GET /api/v1/admin/subscriptions/{id}/

POST /api/v1/admin/subscriptions/{id}/activate/

POST /api/v1/admin/subscriptions/{id}/extend/

POST /api/v1/admin/subscriptions/{id}/cancel/

POST /api/v1/admin/subscriptions/{id}/change-plan/

Every manual admin modification should be audited.

472. Master Data Administration

Admin manages platform-wide master data.

Examples:

Interest Types

Collection Frequencies

Payment Modes

Collection Statuses

Expense Categories

Finance Statuses

Employment Types

Salary Types
473. Master Data Principle

Do not hardcode business dropdowns throughout frontend/backend.

For example, avoid repeatedly writing:

Cash
UPI
Bank Transfer
Cheque

inside frontend components.

Instead:

GET /api/v1/masters/payment-modes/

Frontend receives active options.

474. System vs Workspace Masters

Some masters are platform-wide:

Payment Mode
Collection Frequency
Interest Type

Some may allow lender-specific additions:

Expense Category
Non-Payment Reason

Recommended fields:

workspace = NULL

means:

System Master

while:

workspace = Workspace

means:

Custom Workspace Master
475. Geographic Master Data

For:

State
District
City
Village

I would not make the runtime finance application dependent on an external API for every dropdown.

Instead:

Reliable Geographic Dataset/API
        â†“
Import / Sync
        â†“
Your PostgreSQL
        â†“
Application

This gives you control over availability, relationships, search and future corrections.

Google Places should primarily help with addresses/GPS, not act as your canonical administrative hierarchy database.

476. Geographic Models

Possible:

State

District

City

Village

Relationships:

Country
   â†“
State
   â†“
District
   â†“
City / Mandal
   â†“
Village

Exact administrative hierarchy should match the geographic dataset you select rather than forcing every location into an incorrect hierarchy.

477. MasterDataService
class MasterDataService:
    ...

Methods:

get_states()

get_districts()

get_cities()

get_villages()

get_payment_modes()

get_interest_types()

get_collection_frequencies()

get_collection_statuses()

get_expense_categories()

Admin-specific service:

class AdminMasterDataService:
    ...

for create/update/activation operations.

478. Platform Configuration

Some system behaviour should be configurable without deployment.

Recommended:

PlatformSetting

Examples:

guest_registration_enabled

guest_customer_limit

maintenance_mode

minimum_supported_app_version

default_currency

default_timezone

default_country

import_file_size_limit

receipt_file_size_limit

Sensitive secrets should not be stored casually here.

API keys remain in secure environment/secret management.

479. Admin Audit Logs

Admin should be able to inspect platform audit activity.

Endpoint:

GET /api/v1/admin/audit-logs/

Filters:

user

workspace

action

entity_type

date_from

date_to
480. Admin Action Logging

Especially audit:

USER_SUSPENDED

USER_ACTIVATED

WORKSPACE_SUSPENDED

WORKSPACE_ACTIVATED

PLAN_CREATED

PLAN_UPDATED

SUBSCRIPTION_CHANGED

ADDON_ACTIVATED

MASTER_UPDATED

ADMIN_DATA_ACCESS

Sensitive administrative access should itself be observable.

481. Support Notes

Admin/support may need to record internal notes.

Recommended:

SupportNote

Fields:

workspace

user

note

visibility

created_by

created_at

These notes must never appear to collectors/customers accidentally.

482. Impersonation

Avoid implementing unrestricted:

Login as Lender

early.

If support impersonation is eventually required, it needs:

Explicit permission.
Strong audit logs.
Visible impersonation state.
Time limitation.
Restrictions on sensitive financial operations.

For V1/V2 initial releases, support can inspect metadata without impersonation.

483. Admin Dashboard Service

Recommended:

class AdminDashboardService:
    ...

Methods:

get_overview()

get_user_statistics()

get_workspace_statistics()

get_subscription_statistics()

get_usage_statistics()

get_conversion_statistics()

get_recent_registrations()
484. Guest â†’ Paid Conversion Analytics

Because Guest Workspace is your acquisition mechanism, Admin should specifically track:

Guest Registrations

Active Guest Workspaces

Guests Recording Collections

Guest â†’ Lender Conversions

Conversion Rate

Average Days Before Conversion

This tells you whether the free product is actually helping paid adoption.

485. Admin Search

A global admin search can eventually search:

User

Workspace

Business

Subscription

by:

Name
Mobile
Email
Public ID
Business Name

Avoid exposing full customer search platform-wide unless support genuinely requires it.

486. AdminService Structure

Inside services:

core/services/
â”‚
â”œâ”€â”€ workspace_service.py
â”œâ”€â”€ subscription_service.py
â”œâ”€â”€ feature_access_service.py
â””â”€â”€ audit_service.py

accounts/services/
â”‚
â”œâ”€â”€ authentication_service.py
â”œâ”€â”€ user_service.py
â””â”€â”€ admin_user_service.py

masters/services/
â”‚
â”œâ”€â”€ master_data_service.py
â””â”€â”€ admin_master_service.py

finance/services/
â”‚
â”œâ”€â”€ admin_finance_service.py
â””â”€â”€ admin_dashboard_service.py

We continue following your requirement:

CRUD
+
Business Logic
=
Service Classes

Views should not become service implementations.

487. Admin Views

Example:

class AdminWorkspaceListView(APIView):
    def get(self, request):
        # permissions
        # query parameter validation
        # filters
        # pagination

        data = AdminWorkspaceService.get_workspaces(...)
        return Response(...)

Not:

class AdminWorkspaceListView(APIView):
    def get(self, request):
        # 200 lines of ORM queries
        # calculations
        # subscription logic
        # status logic

The latter violates the architecture we selected.

488. Admin Security

Admin endpoints require stronger protection.

At minimum:

Authenticated
+
Platform Admin
+
Required Admin Permission

For sensitive future actions, consider:

Recent Authentication

or step-up verification.

Examples:

Subscription manual modification
User suspension
Workspace suspension
High-privilege configuration changes
489. Admin Rate Limiting

Admin endpoints should also be rate limited, especially:

Search

Exports

Bulk operations

Authentication

Sensitive actions

Admin status does not mean unlimited requests.

490. Admin Data Exports

Admin may need operational exports such as:

Registered Businesses

Subscriptions

Plan Usage

Platform Usage

Revenue Records

But avoid providing convenient bulk exports of lender/customer financial data unless necessary.

491. Platform Health

Admin dashboard can eventually expose application health:

API Status

Database Status

Redis Status

Celery Status

Failed Background Jobs

SMS Provider Status

WhatsApp Provider Status

Do not expose infrastructure credentials or sensitive diagnostic details.

492. Admin Notifications

Admin-level alerts could include:

Payment Provider Failures

High API Error Rate

Import Failures

SMS Provider Failure

WhatsApp Provider Failure

Backup Failure

Storage Threshold

Suspicious Login Activity

This becomes more important as the platform grows.

493. Platform Admin Scope Summary

The Platform Admin now controls:

Users
   +
Workspaces
   +
Lenders
   +
Plans
   +
Subscriptions
   +
Features
   +
Add-Ons
   +
Master Data
   +
Platform Settings
   +
Audit Logs
   +
Support Operations
   +
Platform Analytics

But does not participate in daily customer collection operations.

Chapter 8 â€” Finance Calculation Engine

This is one of the most important backend components because incorrect calculations can corrupt every dashboard and report.

494. Finance Engine Principle

There must be one authoritative calculation engine.

Do not calculate finance independently in:

React
Serializer
View
Dashboard
Report
Collection API

Instead:

FinanceCalculationService

becomes the source of truth.

Frontend may show estimates for UX, but backend calculations determine stored financial values.

495. FinanceCalculationService

Recommended:

class FinanceCalculationService:
    ...

Core methods:

calculate_interest()

calculate_total_payable()

calculate_installment_amount()

calculate_tenure()

generate_schedule()

calculate_outstanding()

calculate_payment_allocation()

calculate_overdue()

calculate_adjustment()

calculate_account_summary()

validate_finance_terms()

All calculations use Decimal.

496. Basic Finance Equation

At its simplest:

Principal
+
Interest
+
Approved Charges
-
Waivers
=
Total Receivable

Then:

Total Receivable
-
Valid Collections
=
Outstanding

Historical values must remain distinguishable.

497. Flat Interest

Example:

Principal = â‚¹10,000
Interest Rate = 10%

Interest:

â‚¹10,000 Ã— 10%
=
â‚¹1,000

Total payable:

â‚¹10,000 + â‚¹1,000
=
â‚¹11,000
498. Fixed Interest Amount

Some lenders may simply say:

Give â‚¹10,000

Take â‚¹12,000 total

Instead of entering an interest percentage, allow:

Interest Type:
Fixed Amount

Interest:
â‚¹2,000

Then:

Total Payable = â‚¹12,000

This is useful for real-world informal finance workflows.

499. Monthly Percentage Interest

Another supported model may be:

Principal = â‚¹1,00,000

Interest = 3% per month

If the finance term is three months and the agreed calculation is simple monthly interest:

Monthly Interest
=
â‚¹3,000

3 Months
=
â‚¹9,000

Then:

Total Payable
=
â‚¹1,09,000

However, the exact product behaviour must distinguish this from a model where the borrower pays interest periodically while principal remains outstanding.

500. Interest-Only Collection Model

Your original finance examples included:

â‚¹1,00,000
3% monthly

Customer pays:
â‚¹3,000 interest every month

Principal repaid later

This should not be forced into the same schedule as normal principal+interest installments.

Recommended future finance mode:

repayment_structure

Choices:

installment
interest_only
custom
501. Installment Repayment

Example:

Principal       â‚¹10,000
Interest         â‚¹1,000

Total           â‚¹11,000

Tenure:
22 days

Installment:

â‚¹11,000 / 22
=
â‚¹500/day

Schedule:

Day 1   â‚¹500
Day 2   â‚¹500
...
Day 22  â‚¹500
502. Uneven Installment Rounding

Example:

Total Payable = â‚¹10,000

Tenure = 21 weeks

Exact:

â‚¹476.190476...

Do not lose money through repeated rounding.

One strategy:

First 20 installments = â‚¹476.19

Final installment =
remaining exact amount

The engine should guarantee:

SUM(schedule.expected_amount)
=
total_payable

exactly to supported currency precision.

503. Collection Frequencies

Core:

daily
weekly
monthly

Architecture should permit future:

biweekly
custom

Do not build three completely separate finance systems.

Frequency should influence schedule generation.

504. Weekly Scheduling

Example:

Start:
Monday 27 July

Frequency:
Weekly

Tenure:
10 weeks

Schedule:

27 Jul
03 Aug
10 Aug
17 Aug
...

The system should maintain the agreed collection weekday.

505. Monthly Scheduling

Monthly schedules require care.

Example:

Start:
31 January

The next month does not have 31 days.

The business needs a deterministic rule.

Recommended:

If the target day does not exist, use the month's last valid day.

Therefore:

31 Jan
28 Feb / 29 Feb
31 Mar
30 Apr

according to the agreed recurrence logic.

This should be covered by tests.

506. Daily Scheduling

Daily does not automatically mean:

every calendar day

Some businesses may skip:

Sunday
Public Holiday
Business Holiday

Therefore workspace settings can eventually contain:

collection_days

Example:

Monday-Saturday

V1 can start with calendar-day schedules if that matches the selected business rule, but the schedule engine should be extendable.

507. Grace Period

Example:

Due:
Monday

Grace Period:
2 days

Then the installment is not treated according to the lender's overdue policy until the grace period ends.

Store/configure:

grace_period_days

rather than modifying original due dates.

508. Partial Payment

Expected:

â‚¹500

Paid:

â‚¹300

Result:

Expected     â‚¹500
Paid         â‚¹300
Remaining    â‚¹200
Status       Partial

The â‚¹200 remains outstanding.

509. Next Collection After Partial Payment

The business rule should be explicit.

Recommended default:

Oldest unpaid amount remains due and future scheduled installments remain unchanged.

Example:

Week 1 remaining â‚¹200
Week 2 expected  â‚¹500

Next due exposure:

Overdue â‚¹200
+
Current â‚¹500

rather than silently spreading â‚¹200 across all future installments.

510. Advance Payment

Expected today:

â‚¹500

Customer pays:

â‚¹1,500

Allocation:

Oldest Due        â‚¹500
Next Installment  â‚¹500
Next Installment  â‚¹500

using oldest-outstanding-first allocation.

511. Payment Allocation

Never merely calculate:

outstanding -= payment

and ignore schedules.

Use:

Collection
   â†“
CollectionAllocation
   â†“
Schedule 1
Schedule 2
Schedule 3

This allows the system to explain exactly what the payment covered.

512. Overdue Amount

Conceptually:

SUM(
    remaining amounts
    where due_date < effective_date
)

taking grace rules into account.

Do not classify the entire account outstanding as overdue if much of it belongs to future installments.

513. Account Outstanding

Account-level outstanding:

Total Receivable
-
Valid Allocated/Recognized Payments

subject to approved adjustments.

The service should be able to reconcile this against remaining schedules.

514. Adjustment Engine

Suppose:

Original Receivable â‚¹12,000
Paid                 â‚¹8,000
Outstanding          â‚¹4,000

Lender adds:

Late Charge â‚¹500

Then:

Adjusted Receivable â‚¹12,500
Outstanding          â‚¹4,500

Original finance terms remain unchanged.

515. Waiver

Suppose:

Outstanding â‚¹1,000

Lender waives:

â‚¹200

Then:

Outstanding â‚¹800

Store an explicit:

WAIVER â‚¹200

Do not create a fake â‚¹200 payment.

Payments and waivers are financially different events.

516. Discount

A discount can similarly reduce receivable without pretending cash was collected.

Reports should distinguish:

Cash Collected

Waived Amount

Discount Amount

Penalties Added
517. Account Completion

Finance account becomes:

completed

when its recognized outstanding reaches:

â‚¹0.00

subject to any unresolved adjustments.

Completion should record:

completed_at

The original account should not disappear.

518. Early Completion

If customer pays all remaining balance before scheduled end:

Outstanding â‚¹5,000

Customer pays â‚¹5,000

allocate across remaining schedules and complete the account.

Future schedule rows become fully covered rather than deleted.

519. Finance Cancellation

Cancellation is different from completion.

Possible scenario:

Finance created accidentally
No money actually issued

Then:

status = cancelled

Once collections exist, cancellation should normally be restricted and require controlled corrections.

520. Calculation Snapshots

FinanceAccount should store agreed values:

principal_amount

interest_type

interest_rate

interest_amount

original_total_payable

adjustment_total

effective_total_receivable

paid_amount

outstanding_amount

Some are stored snapshots; some can be recalculated for reconciliation.

The service remains authoritative.

521. Reconciliation Check

Provide an internal method such as:

reconcile_finance_account()

It verifies relationships such as:

Collections
+
Waivers
+
Outstanding

against:

Original Receivable
+
Charges
-
Discounts

according to your final accounting rules.

Any mismatch should be detectable.

522. Finance Calculation Test Matrix

This service needs particularly strong automated tests.

At minimum:

Daily exact installments

Daily uneven installments

Weekly schedules

Monthly schedules

Leap year

31st-day monthly schedule

Partial payment

Advance payment

Multiple schedule allocation

Opening balance

Late charge

Waiver

Collection reversal

Early completion

Zero outstanding

Overpayment rejection

Duplicate collection submission

Finance calculation tests should be written before relying on dashboard/report totals.

523. Finance Preview API

Before creating finance, frontend can call:

POST /api/v1/finance/calculate/

Input:

principal
interest_type
interest_rate / interest_amount
frequency
tenure
start_date

Response:

Interest

Total Payable

Installment Amount

First Due Date

Last Due Date

Schedule Preview

This endpoint does not create the finance account.

524. Finance Creation

Actual creation:

POST /api/v1/finance-accounts/

The backend recalculates everything again.

Never trust the totals returned earlier by the preview endpoint and sent back by the frontend.

Flow:

Frontend Preview
       â†“
User Confirms
       â†“
Creation Request
       â†“
Backend Recalculates
       â†“
Validate
       â†“
Create Account
       â†“
Create Schedule
       â†“
Commit
525. Why This Chapter Matters

This engine becomes shared by:

Guest Workspace

Lender ERP

Collection Register

Customer Statement

Lender Dashboard

Admin Analytics

Reports

Imports

Account Adjustments

So financial formulas must not be duplicated elsewhere.

526. Current PRD Status

At this point we have covered the major business domains:

V1 Guest Workspace
        âœ“

V2 Lender / Owner
        âœ“

V2 Employee / Collector
        âœ“

Platform Admin
        âœ“

Customers
        âœ“

Finance Accounts
        âœ“

Daily / Weekly / Monthly Collections
        âœ“

Existing Business Migration
        âœ“

Expenses
        âœ“

Areas
        âœ“

GPS
        âœ“

Routes
        âœ“

Employee Management
        âœ“

Cash Handover
        âœ“

Salary
        âœ“

Penalties / Waivers
        âœ“

Plans / Subscriptions
        âœ“

SMS / WhatsApp Add-On Architecture
        âœ“

Finance Calculation Engine
        âœ“

The remaining work is now mostly technical architecture rather than missing product functionality: authentication/security, notification/background-job architecture, complete PostgreSQL relationships/indexes, API standards, performance/caching, deployment/backups/monitoring, testing, and finally the exact Django folder structure and recommended implementation order.

----

Chapter 9 â€” Authentication, Authorization & Security Architecture
527. Security Objective

The application contains sensitive business and financial information:

Customer Details
Finance Accounts
Outstanding Amounts
Collection History
Employee Information
GPS Locations
Expenses
Cash Handovers
Salary Information
Business Analytics

Security therefore needs to exist at several levels:

Authentication
      â†“
Platform Role
      â†“
Workspace Membership
      â†“
Permission
      â†“
Resource Ownership
      â†“
Business Rule Validation

Authentication alone is never sufficient.

528. Authentication Technology

Recommended stack:

Django
Django REST Framework
SimpleJWT
PostgreSQL

Use JWT authentication for the React/frontend application.

Primary tokens:

Access Token
Refresh Token
529. Access Token

Access tokens should be short-lived.

Example:

15â€“30 minutes

They authenticate API requests.

Conceptually:

Authorization:
Bearer <access_token>

The exact lifetime should remain configurable through environment/settings rather than business code.

530. Refresh Token

Refresh tokens live longer.

Example:

7â€“30 days

Their purpose is obtaining new access tokens without asking the user to log in repeatedly.

Recommended security features:

Refresh Token Rotation
+
Blacklist After Rotation
531. Login Flow
Mobile / Email
      +
Password
      â†“
AuthenticationService
      â†“
Validate Credentials
      â†“
Validate User Status
      â†“
Generate Access Token
      â†“
Generate Refresh Token
      â†“
Create Login/Session Record
      â†“
Return User Context

The response can also return:

User
Workspace
Role
Permissions
Workspace Type
Subscription
Feature Entitlements

so the frontend can initialize correctly.

532. AuthenticationService

Recommended:

class AuthenticationService:
    ...

Methods:

register()

login()

logout()

refresh_token()

change_password()

request_password_reset()

verify_password_reset()

verify_mobile()

verify_email()

get_authenticated_context()

Authentication business logic should not live inside DRF views.

533. Registration Flow

For Guest V1:

User Registration
      â†“
Validate Mobile / Email
      â†“
Create User
      â†“
Verify Identity if required
      â†“
Create Workspace
      â†“
workspace_type = guest
      â†“
Create Owner Membership
      â†“
Assign Guest Free Plan
      â†“
Create Workspace Settings
      â†“
Return Authentication Context

This should run transactionally where appropriate.

534. User Model

Use a custom Django user model from the beginning.

Recommended conceptual fields:

id
public_id

full_name

mobile_number
email

password

is_mobile_verified
is_email_verified

status

is_staff
is_superuser

last_login

created_at
updated_at

Do not use mobile/email values as public API identifiers.

535. Public IDs

Expose:

UUID

or equivalent non-sequential public IDs.

Example:

customer:
2a47a3f2-...

instead of:

/customer/12/

where practical.

Internally PostgreSQL can still use efficient integer/bigint primary keys if desired.

536. Password Storage

Never store:

Plain Password
Encrypted Recoverable Password

Use Django's built-in password hashing infrastructure.

Passwords should never be returned through serializers.

537. Password Validation

Use Django password validators and additional reasonable rules.

Avoid forcing unnecessarily complicated rules that cause users to reuse predictable passwords.

Support:

Minimum Length
Common Password Detection
Similarity Checks
Compromised-password checks if introduced later
538. OTP Architecture

OTP may be required for:

Mobile Verification
Password Reset
Sensitive Account Recovery

Recommended model:

OTPRequest

Fields conceptually:

user/mobile
purpose
hashed_otp
expires_at
attempt_count
status
created_at
verified_at

Do not store OTP values as plain text when avoidable.

539. OTP Expiry

Example:

5 minutes

OTP must become invalid after:

Successful Verification
Expiry
Maximum Attempts
New OTP replacing old OTP
540. OTP Rate Limiting

Protect:

Send OTP
Verify OTP

against abuse.

Example rules:

Maximum requests per phone/IP window

Resend cooldown

Maximum verification attempts

SMS APIs cost money, making this both a security and cost-control requirement.

541. Login Attempt Protection

Track repeated failures.

Possible protections:

Rate Limit by IP

Rate Limit by Account

Temporary Cooldown

Suspicious Login Logging

Avoid permanently locking legitimate users due to a small number of mistakes.

542. Session / Device Tracking

Recommended:

UserSession

Fields:

id
user

device_identifier
device_name

ip_address
user_agent

last_activity_at

created_at
revoked_at

status

This allows:

View Active Sessions
Logout Current Session
Logout Other Devices
Logout All Devices
543. Logout

Logout should invalidate/revoke the refresh token where applicable.

Flow:

Logout Request
      â†“
Validate Refresh Token
      â†“
Blacklist / Revoke
      â†“
Close Session Record

Deleting frontend local storage alone is not sufficient server-side logout protection.

544. Authentication Context Endpoint

Recommended:

GET /api/v1/auth/me/

Response conceptually:

{
  "user": {},
  "workspace": {},
  "membership": {},
  "permissions": [],
  "plan": {},
  "features": []
}

The frontend can use this after refresh/reload.

545. Workspace Context

Most authenticated finance requests operate inside a workspace.

Every service query should be scoped using the authenticated workspace.

Bad:

Customer.objects.get(public_id=customer_id)

Better conceptually:

Customer.objects.get(
    public_id=customer_id,
    workspace=workspace,
)

This is one of the most important security rules in the application.

546. Multi-Tenant Isolation

The system is effectively multi-tenant.

Example:

Lender A
   â†“
Workspace A
   â†“
Customers A

Lender B
   â†“
Workspace B
   â†“
Customers B

There must never be:

Workspace A user
      â†“
Customer from Workspace B

even if the user manually changes IDs in the URL.

547. Workspace Isolation Rule

Every workspace-owned model should include:

workspace

directly or have an unambiguous ownership path.

Examples:

Customer.workspace

FinanceAccount.workspace

Collection.workspace

Expense.workspace

Area.workspace

EmployeeProfile.workspace

Route.workspace

CashHandover.workspace

Direct workspace references can simplify secure filtering and indexing.

548. Object-Level Authorization

Suppose collector calls:

GET /api/v2/customers/{customer_id}/

Validation is not merely:

Customer belongs to workspace

It also needs:

Customer belongs to collector's assigned area

when the requester is a collector.

Therefore authorization can be:

User
 â†“
Workspace
 â†“
Membership
 â†“
Role
 â†“
Permission
 â†“
Area Assignment
 â†“
Customer
549. PermissionService

Recommended shared service:

class PermissionService:
    ...

Methods:

has_permission()

require_permission()

can_access_customer()

can_access_finance_account()

can_access_area()

can_access_employee()

can_manage_collection()

can_reverse_collection()

can_approve_expense()

can_verify_cash_handover()
550. DRF Permissions

Use DRF permission classes for coarse request authorization.

Examples:

IsAuthenticated

IsPlatformAdmin

IsWorkspaceMember

IsWorkspaceOwner

HasWorkspacePermission

Detailed domain authorization can still be handled by service/permission helpers.

551. Never Trust Frontend Roles

Frontend may hide:

Delete
Reverse
Approve
Salary
Settings

buttons.

That is only UI behavior.

A collector could still manually call an endpoint.

Backend must independently verify permissions.

552. Workspace Owner Access

Owner generally receives:

ALL WORKSPACE PERMISSIONS

but still only for their workspace.

Being an owner does not grant access to other businesses.

553. Collector Access

Collector access should normally be restricted to:

Assigned Area
Assigned Customers
Assigned Routes
Own Collections
Own Expenses
Own Cash Handovers
Allowed Salary Information

This restriction belongs in backend services/querysets.

554. Admin Access

Platform Admin operates outside normal workspace membership.

Admin endpoints should live separately:

/api/v1/admin/...

Do not make admin access happen by bypassing every workspace check inside ordinary lender endpoints.

Separate APIs produce cleaner security boundaries.

555. Sensitive Operations

Operations requiring stronger permission include:

Collection Reversal

Finance Adjustment

Customer Archival

Employee Termination

Expense Approval

Cash Handover Verification

Salary Modification

Workspace Suspension

Subscription Modification

All should create audit records.

556. Request Audit Metadata

For significant actions capture where appropriate:

User

Workspace

IP Address

User Agent

Timestamp

Entity

Action

For employee field actions also potentially:

GPS
Device Context
557. GPS Privacy

Customer and employee GPS information is sensitive.

Only collect it when required for a legitimate application feature.

Do not continuously track collectors merely because location permission exists.

For initial V2:

Capture location when explicitly required

such as:

Customer Location Registration
Collection Recording
Route Navigation

rather than maintaining unnecessary continuous location history.

558. API Rate Limiting

Apply throttling to expensive/sensitive endpoints.

Examples:

Login

OTP Send

OTP Verify

Password Reset

Google Places Search

Route Generation

Exports

Imports

SMS Send

WhatsApp Send

General API endpoints can have broader rate limits.

559. File Upload Security

Uploads include:

Expense Receipts
Import Files
Business Logo
Profile Images

Validate:

File Size
Extension
MIME Type
Allowed Content Type
Filename

Generate server-controlled storage names.

Never trust the original filename as a storage path.

560. Secrets

Keep secrets outside source code.

Examples:

SECRET_KEY

DATABASE_URL

Google Maps API Key

SMS Provider Credentials

WhatsApp Credentials

Object Storage Credentials

Payment Gateway Secrets

Use environment variables/secret management.

Never commit them to Git.

561. CORS

Configure allowed frontend origins explicitly.

Production should not casually use:

CORS_ALLOW_ALL_ORIGINS = True

Allow only trusted frontend domains.

562. HTTPS

Production authentication and financial APIs should operate over HTTPS.

Never intentionally send:

Passwords
JWTs
Customer Data
GPS

over plaintext HTTP.

563. Security Headers

Production should configure appropriate Django/browser security controls such as:

Secure Cookies where applicable
HSTS
Content-Type protection
Frame protection
Referrer policy

exact settings depend on deployment architecture.

Chapter 10 â€” Notifications & Background Processing
564. Notification Categories

There are two different concepts:

Internal Notifications

and:

External Communications

Internal notifications are part of the application.

External communication includes optional:

SMS
WhatsApp
565. Notification Model

Recommended:

Notification

Fields:

id
public_id

workspace

recipient

notification_type

title

message

entity_type
entity_id

is_read

read_at

created_at
566. Notification Examples

Lender:

Employee submitted expense

Cash handover awaiting verification

Finance account completed

Large collection reversal

Collector:

Area assignment changed

New route assigned

Expense approved

Expense rejected
567. NotificationService
class NotificationService:
    ...

Methods:

create_notification()

get_notifications()

mark_as_read()

mark_all_as_read()

send_business_event_notification()
568. Background Jobs

Some work should not block API requests.

Examples:

Large Excel Import

Large Excel/PDF Export

SMS Sending

WhatsApp Sending

Scheduled Reminders

Heavy Report Generation

Data Reconciliation

Periodic Cleanup

V1 Guest does not require background infrastructure immediately.

V2 can introduce it.

569. Celery

Recommended V2 architecture:

Django API
    â”‚
    â”œâ”€â”€ PostgreSQL
    â”‚
    â””â”€â”€ Redis
          â”‚
          â–¼
        Celery
          â”‚
          â”œâ”€â”€ Import Worker
          â”œâ”€â”€ Report Worker
          â”œâ”€â”€ Notification Worker
          â””â”€â”€ Maintenance Worker

Redis can act as the Celery broker/cache depending on deployment decisions.

570. Celery Beat

For scheduled operations:

Celery Beat

can trigger:

Due Reminders

Promise-to-Pay Reminders

Subscription Expiry Checks

Usage Resets

Cleanup Jobs

Periodic Reconciliation

Do not use Celery Beat for calculations that can simply be derived at query time.

571. Job Idempotency

Background tasks can be retried.

Therefore jobs such as:

Send Payment Confirmation
Generate Statement
Process Subscription Webhook

must account for duplicate execution.

Use unique event/job identifiers where necessary.

572. Retry Strategy

External integrations fail.

Example:

SMS Provider Timeout

should not necessarily cause immediate permanent failure.

Use controlled retry:

Attempt 1
   â†“ fail
Wait
   â†“
Attempt 2
   â†“ fail
Wait Longer
   â†“
Attempt 3

with maximum retry limits.

573. Failed Job Handling

Do not retry forever.

Track:

Pending
Processing
Completed
Failed
Retrying

and retain enough failure information for debugging without exposing secrets.

574. SMS Architecture
Finance Event
     â†“
NotificationService
     â†“
FeatureAccessService
     â†“
CommunicationPreference
     â†“
SMSService
     â†“
Provider Adapter

This prevents finance code from depending on one SMS company.

575. WhatsApp Architecture

Similarly:

Finance Event
     â†“
WhatsAppService
     â†“
Template
     â†“
Provider Adapter
     â†“
WhatsApp Business API

Template-based communication requirements should be handled by the integration layer.

576. Communication Log

Recommended:

CommunicationLog

Fields:

workspace

customer

channel

message_type

template

destination

provider

provider_reference

status

sent_at

delivered_at

failed_at

failure_reason

created_at
577. Communication Status

Recommended:

queued
sent
delivered
failed
cancelled

Actual provider capabilities may add statuses later.

Chapter 11 â€” PostgreSQL Database Architecture
578. Database Choice

PostgreSQL is a strong fit because the application needs:

Transactions

Relational Integrity

Financial Data

Indexes

Aggregations

JSON Metadata

Concurrency Controls

Reporting
579. Main Relationship Structure

The final high-level structure is:

User
â”‚
â”œâ”€â”€ UserSession
â”‚
â””â”€â”€ WorkspaceMembership
          â”‚
          â–¼
      Workspace
          â”‚
          â”œâ”€â”€ WorkspaceSettings
          â”œâ”€â”€ BusinessProfile
          â”œâ”€â”€ Subscription
          â”‚
          â”œâ”€â”€ Customer
          â”‚      â”‚
          â”‚      â””â”€â”€ FinanceAccount
          â”‚             â”‚
          â”‚             â”œâ”€â”€ CollectionSchedule
          â”‚             â”‚
          â”‚             â”œâ”€â”€ Collection
          â”‚             â”‚      â”‚
          â”‚             â”‚      â””â”€â”€ CollectionAllocation
          â”‚             â”‚
          â”‚             â””â”€â”€ FinanceAdjustment
          â”‚
          â”œâ”€â”€ Expense
          â”‚
          â”œâ”€â”€ Area
          â”‚      â”‚
          â”‚      â”œâ”€â”€ Customer
          â”‚      â”œâ”€â”€ EmployeeAreaAssignment
          â”‚      â””â”€â”€ CollectionRoute
          â”‚               â”‚
          â”‚               â””â”€â”€ RouteStop
          â”‚
          â”œâ”€â”€ EmployeeProfile
          â”‚
          â”œâ”€â”€ EmployeeExpense
          â”‚
          â”œâ”€â”€ CashHandover
          â”‚
          â”œâ”€â”€ EmployeeSalaryStructure
          â”‚
          â”œâ”€â”€ SalaryPayment
          â”‚
          â”œâ”€â”€ ImportJob
          â”‚
          â””â”€â”€ AuditLog
580. Foreign-Key Deletion Strategy

Do not casually use:

on_delete=models.CASCADE

everywhere.

Financial history requires deliberate deletion behavior.

581. Recommended Deletion Philosophy

For critical relationships:

Workspace â†’ Financial Records

prefer preventing accidental deletion.

For example:

on_delete=models.PROTECT

may be appropriate in several historical relationships.

Business-level deletion should generally be:

archive
suspend
cancel
reverse

rather than physical deletion.

582. Customer Deletion

Customer with financial history:

DO NOT HARD DELETE

Use:

status = archived

Their:

Finance Accounts
Collections
Statements

remain intact.

583. Finance Account Deletion

Do not delete.

Use statuses:

active
completed
overdue
cancelled

depending on domain rules.

584. Collection Deletion

Never normal-delete valid financial collections.

Use:

reversal

with audit history.

585. Employee Deletion

Employee who has recorded collections must remain historically identifiable.

Use:

terminated

instead of deleting the EmployeeProfile/User relationship.

586. Indexing Strategy

Indexes should match common queries.

For Customer:

workspace + status

workspace + mobile_number

workspace + area

workspace + customer_code
587. Finance Account Indexes

Useful:

workspace + status

workspace + customer

workspace + account_number

workspace + next_due_date

Exact indexes should follow actual query patterns once implementation begins.

588. Collection Indexes

Collections will eventually become one of the largest tables.

Important candidates:

workspace + collection_date

workspace + customer + collection_date

workspace + finance_account + collection_date

workspace + recorded_by + collection_date

workspace + area + collection_date
589. Schedule Indexes

Important:

workspace + due_date

finance_account + due_date

workspace + status + due_date

This supports daily collection-register queries.

590. Expense Indexes

Useful:

workspace + expense_date

workspace + category + expense_date

workspace + employee + expense_date
591. Unique Constraints

Examples:

unique(workspace, customer_code)

unique(workspace, finance_account_number)

unique(workspace, employee_code)

unique(workspace, area_code)

unique(route, customer)

unique(route, sequence_number)

Use database constraints in addition to service validation.

592. Check Constraints

Useful examples:

principal_amount > 0

paid_amount >= 0

expense_amount > 0

tenure > 0

latitude BETWEEN -90 AND 90

longitude BETWEEN -180 AND 180

Do not rely solely on serializers.

593. Database Transaction Boundaries

Critical:

Finance Creation
Collection Recording
Collection Reversal
Adjustment
Cash Verification
Guest â†’ Business Upgrade
Subscription Changes

should use database transactions.

594. Row Locking

Use:

select_for_update()

where concurrent financial updates could conflict.

Example:

Collector A records â‚¹500
Collector B records â‚¹500

against the same account simultaneously.

Locking prevents inconsistent outstanding calculations.

Chapter 12 â€” API Standards
595. API Versioning

Recommended:

/api/v1/

for initial APIs.

Do not necessarily create /v2/ simply because the product is called "Version 2".

API version and product version are different concepts.

If V2 ERP functionality can be added without breaking the API contract, it can still exist under:

/api/v1/

This is an important refinement.

Use /api/v2/ only when introducing breaking API changes.

596. Endpoint Naming

Use plural resources:

/customers/
/finance-accounts/
/collections/
/expenses/
/areas/
/employees/

Prefer predictable REST naming.

597. Actions

Domain operations that are not CRUD can use explicit action endpoints:

/collections/{id}/reverse/

/employees/{id}/suspend/

/cash-handovers/{id}/verify/

/finance-accounts/{id}/complete/
598. HTTP Methods

Generally:

GET     Read

POST    Create / Domain Action

PATCH   Partial Update

PUT     Full Replacement where genuinely needed

DELETE  Delete/Archive where semantics allow

Financial reversal should normally be:

POST /collections/{id}/reverse/

not DELETE.

599. Standard Success Response

Recommended:

{
  "success": true,
  "message": "Collection recorded successfully.",
  "data": {}
}
600. Standard Error Response

Recommended:

{
  "success": false,
  "message": "Unable to record collection.",
  "code": "INVALID_COLLECTION_AMOUNT",
  "errors": {
    "paid_amount": [
      "Amount exceeds the remaining outstanding."
    ]
  }
}
601. Error Codes

Create stable machine-readable codes.

Examples:

AUTHENTICATION_REQUIRED

PERMISSION_DENIED

WORKSPACE_ACCESS_DENIED

CUSTOMER_NOT_FOUND

FINANCE_ACCOUNT_COMPLETED

INVALID_COLLECTION_AMOUNT

COLLECTION_ALREADY_REVERSED

AREA_COLLECTOR_LIMIT_REACHED

FEATURE_NOT_AVAILABLE

PLAN_LIMIT_REACHED

Frontend can use these safely instead of parsing English messages.

602. Filtering

Example:

GET /api/v1/collections/
    ?date_from=2026-07-01
    &date_to=2026-07-31
    &status=paid
    &area=...

View:

validates parameters

Service:

builds business query

following your architecture.

603. Search

Use:

?search=ramesh

Services decide which fields are searchable.

For customers:

Name
Mobile
Customer Code

Do not allow arbitrary database-field searching.

604. Ordering

Example:

?ordering=-collection_date

Whitelist supported ordering fields.

Never directly trust arbitrary field names supplied by frontend.

605. Pagination

Default:

20

Maximum example:

100

For very large event tables later, cursor pagination may become useful.

Initially standard page-based pagination is sufficient.

606. Idempotency

Financial create operations should support idempotency.

Particularly:

Collection Recording

Subscription Webhooks

Cash Handover Submission

External Payment Confirmation

This protects against retries and duplicate taps.

607. API Documentation

Use OpenAPI documentation.

For DRF, an OpenAPI-compatible documentation package can generate:

Endpoints

Parameters

Request Schemas

Responses

Authentication Requirements

Maintain meaningful serializer schemas rather than treating documentation as an afterthought.

Chapter 13 â€” Performance & Caching
608. Performance Principle

Do not add Redis everywhere before performance problems exist.

First optimize:

Database Queries
Indexes
Query Relationships
Aggregations
Pagination

Then cache where it provides measurable value.

609. select_related

Use for single-valued relationships.

Example collection listing may need:

customer
finance_account
recorded_by
payment_mode
area

Without optimization, 100 collections can trigger many additional queries.

610. prefetch_related

Use for collections of related records.

Examples:

Area â†’ Collectors

Route â†’ Route Stops

Finance Account â†’ Schedule

when actually needed.

611. Avoid N+1 Queries

Dashboard/report APIs must be reviewed for N+1 patterns.

Bad conceptually:

Fetch 100 customers

For each customer:
    query finance
    query collections
    query outstanding

Prefer database aggregation or carefully preloaded data.

612. Dashboard Optimization

Dashboard totals should usually be calculated using database aggregation:

SUM
COUNT
AVG
CASE
FILTER

rather than loading thousands of rows into Python.

613. Redis Caching

Later Redis can cache:

Master Data

Plan Configuration

Feature Entitlements

Expensive Dashboard Aggregations

Frequently Used Workspace Settings

Do not cache rapidly changing financial balances without a clear invalidation strategy.

614. Cache Invalidation

Example:

Collection Recorded
      â†“
Today's Dashboard Cache
      â†“
Invalidate

Incorrect cached finance totals are worse than slightly slower queries.

615. Google API Caching

Where provider terms permit and data is suitable, avoid unnecessary repeated external calls.

For example, once a customer address has been converted to coordinates and confirmed, store the resulting coordinates in your database.

Do not geocode the same customer every time their card opens.

Chapter 14 â€” Deployment & Production Architecture
616. Initial V1 Architecture

For Guest Workspace, keep deployment relatively simple:

React Frontend
      â†“
Django + DRF
      â†“
PostgreSQL
      â†“
Object Storage

No need to introduce ten infrastructure services on day one.

617. Expanded V2 Architecture

When required:

Frontend
    â†“
Reverse Proxy / Platform
    â†“
Django + Gunicorn
    â”‚
    â”œâ”€â”€ PostgreSQL
    â”‚
    â”œâ”€â”€ Redis
    â”‚
    â”œâ”€â”€ Object Storage
    â”‚
    â””â”€â”€ Celery Workers
             â”‚
             â”œâ”€â”€ Imports
             â”œâ”€â”€ Reports
             â””â”€â”€ Notifications
618. Environment Separation

At minimum:

Development

Production

Prefer:

Development

Staging

Production

as the product matures.

Never test risky migrations directly against production.

619. Environment Variables

Examples:

DJANGO_SECRET_KEY

DATABASE_URL

DEBUG

ALLOWED_HOSTS

CORS_ALLOWED_ORIGINS

REDIS_URL

GOOGLE_MAPS_API_KEY

STORAGE_*

SMS_*

WHATSAPP_*

PAYMENT_*

Different environments use different credentials.

620. Production Debugging

Production:

DEBUG = False

Errors should go to structured logging/error monitoring rather than exposing stack traces to users.

621. Health Endpoint

Recommended:

GET /health/

Can verify basic application availability.

A deeper internal health check can monitor:

Database

Redis

Storage

Workers

without exposing credentials or sensitive infrastructure details.

622. Logging

Use structured application logs for:

Request Errors

Integration Failures

Background Jobs

Authentication Events

Unexpected Business Exceptions

Do not log:

Passwords

JWTs

OTP Codes

API Secrets

Full Sensitive Customer Data
623. Error Monitoring

Production should have an error-monitoring mechanism so failures such as:

500 errors
Celery task failures
Google integration errors
Database exceptions

are visible without manually reading server logs all day.

624. Database Backups

Production PostgreSQL should have:

Automated Backup
+
Retention
+
Off-System Copy where appropriate
+
Restore Testing

Again:

Backup â‰  Second Running Database

A standby/replica is a different availability feature.

625. Backup Frequency

For this type of financial-recording application, daily backups are a baseline, but recovery objectives should determine whether you need more frequent snapshots or point-in-time recovery.

As the platform grows, define:

RPO

maximum acceptable data loss,

and:

RTO

maximum acceptable restoration time.

626. Database Migrations

Production deployment flow:

Code Reviewed
      â†“
Backup / Recovery Confidence
      â†“
Deploy
      â†“
Run Django Migrations
      â†“
Health Check
      â†“
Monitor

Large destructive migrations need special planning.

Chapter 15 â€” Testing Strategy
627. Testing Priority

This product should not rely mainly on frontend/manual testing.

Highest priority automated tests should cover:

Financial Calculations

Workspace Isolation

Permissions

Collection Recording

Reversals

Adjustments

Cash Reconciliation
628. Service Tests

Because your business logic lives in service classes, service tests become especially important.

Example:

FinanceCalculationServiceTest

CollectionServiceTest

FinanceAccountServiceTest

ExpenseServiceTest

EmployeeServiceTest

RouteServiceTest

CashReconciliationServiceTest
629. Workspace Isolation Tests

Explicitly test:

Lender A cannot read Lender B customer

Collector A cannot read another area

Collector cannot approve own expense

Collector cannot modify salary

Lender cannot access another workspace

These are security tests, not optional UI tests.

630. Collection Tests

Test:

Full payment

Partial payment

Advance payment

Non-payment

Promise to pay

Overpayment

Duplicate request

Reversal

Completed account

Concurrent collection
631. Finance Tests

Test:

Flat interest

Fixed interest

Daily tenure

Weekly tenure

Monthly tenure

Rounding

Leap years

Opening balances

Charges

Waivers

Early closure
632. Import Tests

Test:

Valid spreadsheet

Missing columns

Invalid amounts

Duplicate customers

Mixed valid/invalid rows

Large imports

Invalid file type
633. Route Tests

Test:

Customer without GPS

Duplicate stop

Wrong area customer

Collector without assignment

Manual reorder

Route provider failure

External provider calls should be mocked in automated tests.

634. Cash Tests

Test:

Exact handover

Short cash

Excess cash

Unapproved expense

Digital payment exclusion

Already verified handover
Chapter 16 â€” Final Django Project Structure

Your requirement is:

Five layers: models â†’ serializers â†’ services â†’ views â†’ URLs.

CRUD and business logic belong in services.

Views handle request/application concerns, filters, permissions and validations.

Services use class-based methods rather than scattered standalone functions.

The final structure can therefore be:

backend/
â”‚
â”œâ”€â”€ manage.py
â”‚
â”œâ”€â”€ requirements.txt
â”‚
â”œâ”€â”€ .env.example
â”‚
â”œâ”€â”€ .gitignore
â”‚
â”‚
â”œâ”€â”€ config/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ settings/
â”‚   â”‚   â”œâ”€â”€ base.py
â”‚   â”‚   â”œâ”€â”€ development.py
â”‚   â”‚   â””â”€â”€ production.py
â”‚   â”œâ”€â”€ urls.py
â”‚   â”œâ”€â”€ wsgi.py
â”‚   â””â”€â”€ asgi.py
â”‚
â”œâ”€â”€ core/
â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â”œâ”€â”€ base.py
â”‚   â”‚   â”œâ”€â”€ workspace.py
â”‚   â”‚   â”œâ”€â”€ subscription.py
â”‚   â”‚   â”œâ”€â”€ audit.py
â”‚   â”‚   â””â”€â”€ notification.py
â”‚   â”‚
â”‚   â”œâ”€â”€ serializers/
â”‚   â”œâ”€â”€ services/
â”‚   â”‚   â”œâ”€â”€ workspace_service.py
â”‚   â”‚   â”œâ”€â”€ feature_access_service.py
â”‚   â”‚   â”œâ”€â”€ subscription_service.py
â”‚   â”‚   â”œâ”€â”€ permission_service.py
â”‚   â”‚   â”œâ”€â”€ audit_service.py
â”‚   â”‚   â””â”€â”€ notification_service.py
â”‚   â”‚
â”‚   â”œâ”€â”€ views/
â”‚   â”œâ”€â”€ permissions.py
â”‚   â”œâ”€â”€ pagination.py
â”‚   â”œâ”€â”€ exceptions.py
â”‚   â”œâ”€â”€ exception_handler.py
â”‚   â””â”€â”€ urls.py
â”‚
â”œâ”€â”€ accounts/
â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â”œâ”€â”€ user.py
â”‚   â”‚   â”œâ”€â”€ session.py
â”‚   â”‚   â””â”€â”€ otp.py
â”‚   â”‚
â”‚   â”œâ”€â”€ serializers/
â”‚   â”‚   â”œâ”€â”€ auth_serializer.py
â”‚   â”‚   â””â”€â”€ user_serializer.py
â”‚   â”‚
â”‚   â”œâ”€â”€ services/
â”‚   â”‚   â”œâ”€â”€ authentication_service.py
â”‚   â”‚   â”œâ”€â”€ user_service.py
â”‚   â”‚   â””â”€â”€ admin_user_service.py
â”‚   â”‚
â”‚   â”œâ”€â”€ views/
â”‚   â”‚   â”œâ”€â”€ auth_views.py
â”‚   â”‚   â””â”€â”€ admin_user_views.py
â”‚   â”‚
â”‚   â””â”€â”€ urls.py
â”‚
â”œâ”€â”€ masters/
â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â”œâ”€â”€ location.py
â”‚   â”‚   â”œâ”€â”€ finance_master.py
â”‚   â”‚   â””â”€â”€ expense_master.py
â”‚   â”‚
â”‚   â”œâ”€â”€ serializers/
â”‚   â”œâ”€â”€ services/
â”‚   â”‚   â”œâ”€â”€ master_data_service.py
â”‚   â”‚   â””â”€â”€ admin_master_service.py
â”‚   â”œâ”€â”€ views/
â”‚   â””â”€â”€ urls.py
â”‚
â”œâ”€â”€ finance/
â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â”œâ”€â”€ customer.py
â”‚   â”‚   â”œâ”€â”€ finance_account.py
â”‚   â”‚   â”œâ”€â”€ collection.py
â”‚   â”‚   â”œâ”€â”€ expense.py
â”‚   â”‚   â”œâ”€â”€ area.py
â”‚   â”‚   â”œâ”€â”€ employee.py
â”‚   â”‚   â”œâ”€â”€ route.py
â”‚   â”‚   â”œâ”€â”€ cash_handover.py
â”‚   â”‚   â”œâ”€â”€ salary.py
â”‚   â”‚   â”œâ”€â”€ adjustment.py
â”‚   â”‚   â””â”€â”€ import_job.py
â”‚   â”‚
â”‚   â”œâ”€â”€ serializers/
â”‚   â”‚   â”œâ”€â”€ customer_serializer.py
â”‚   â”‚   â”œâ”€â”€ finance_account_serializer.py
â”‚   â”‚   â”œâ”€â”€ collection_serializer.py
â”‚   â”‚   â”œâ”€â”€ expense_serializer.py
â”‚   â”‚   â”œâ”€â”€ area_serializer.py
â”‚   â”‚   â”œâ”€â”€ employee_serializer.py
â”‚   â”‚   â”œâ”€â”€ route_serializer.py
â”‚   â”‚   â”œâ”€â”€ cash_serializer.py
â”‚   â”‚   â””â”€â”€ salary_serializer.py
â”‚   â”‚
â”‚   â”œâ”€â”€ services/
â”‚   â”‚   â”œâ”€â”€ customer_service.py
â”‚   â”‚   â”œâ”€â”€ finance_calculation_service.py
â”‚   â”‚   â”œâ”€â”€ finance_account_service.py
â”‚   â”‚   â”œâ”€â”€ schedule_service.py
â”‚   â”‚   â”œâ”€â”€ collection_service.py
â”‚   â”‚   â”œâ”€â”€ expense_service.py
â”‚   â”‚   â”œâ”€â”€ dashboard_service.py
â”‚   â”‚   â”œâ”€â”€ report_service.py
â”‚   â”‚   â”œâ”€â”€ import_service.py
â”‚   â”‚   â”œâ”€â”€ export_service.py
â”‚   â”‚   â”œâ”€â”€ area_service.py
â”‚   â”‚   â”œâ”€â”€ employee_service.py
â”‚   â”‚   â”œâ”€â”€ route_service.py
â”‚   â”‚   â”œâ”€â”€ cash_reconciliation_service.py
â”‚   â”‚   â”œâ”€â”€ salary_service.py
â”‚   â”‚   â””â”€â”€ adjustment_service.py
â”‚   â”‚
â”‚   â”œâ”€â”€ views/
â”‚   â”‚   â”œâ”€â”€ customer_views.py
â”‚   â”‚   â”œâ”€â”€ finance_account_views.py
â”‚   â”‚   â”œâ”€â”€ collection_views.py
â”‚   â”‚   â”œâ”€â”€ expense_views.py
â”‚   â”‚   â”œâ”€â”€ dashboard_views.py
â”‚   â”‚   â”œâ”€â”€ report_views.py
â”‚   â”‚   â”œâ”€â”€ area_views.py
â”‚   â”‚   â”œâ”€â”€ employee_views.py
â”‚   â”‚   â”œâ”€â”€ route_views.py
â”‚   â”‚   â”œâ”€â”€ cash_views.py
â”‚   â”‚   â””â”€â”€ salary_views.py
â”‚   â”‚
â”‚   â””â”€â”€ urls.py
â”‚
â””â”€â”€ integrations/
    â”œâ”€â”€ services/
    â”‚   â”œâ”€â”€ google_maps_service.py
    â”‚   â”œâ”€â”€ storage_service.py
    â”‚   â”œâ”€â”€ sms_service.py
    â”‚   â”œâ”€â”€ whatsapp_service.py
    â”‚   â””â”€â”€ payment_provider_service.py
    â”‚
    â””â”€â”€ providers/
        â”œâ”€â”€ maps/
        â”œâ”€â”€ sms/
        â”œâ”€â”€ whatsapp/
        â””â”€â”€ payments/
635. Final Layer Responsibility

The rule throughout the backend should remain:

MODEL
â”‚
â”‚ Database structure
â”‚ relationships
â”‚ constraints
â–¼
SERIALIZER
â”‚
â”‚ Input/output structure
â”‚ field-level validation
â–¼
SERVICE
â”‚
â”‚ CRUD
â”‚ business rules
â”‚ calculations
â”‚ transactions
â”‚ ORM queries
â”‚ domain authorization
â–¼
VIEW
â”‚
â”‚ Authentication
â”‚ request parsing
â”‚ query parameters
â”‚ filtering input validation
â”‚ pagination
â”‚ HTTP handling
â–¼
URL
â”‚
â”‚ Endpoint routing
â–¼
CLIENT

One refinement: views can validate filter/query parameters, but the actual ORM filtering should remain inside the service, which matches the architecture you requested.

636. V1 Implementation Boundary

Although the architecture contains V2 models/services, do not build all of them for the first release.

Your first implementation milestone should be:

Accounts
   â†“
Workspace
   â†“
Masters
   â†“
Customers
   â†“
Finance Calculation
   â†“
Finance Accounts
   â†“
Schedules
   â†“
Collections
   â†“
Expenses
   â†“
Dashboard
   â†“
Reports
   â†“
Import / Export

Meaning V1 is:

Guest Workspace â€” a free digital finance collection book.

Do not delay that release for:

Employees
Routes
Payroll
Cash Handover
SMS
WhatsApp
Advanced Admin Analytics
637. Recommended V1 Development Phases
Phase 1
Project + PostgreSQL + Authentication
        â†“
Phase 2
Workspace + Masters
        â†“
Phase 3
Customers
        â†“
Phase 4
Finance Calculation + Finance Accounts
        â†“
Phase 5
Schedule Engine
        â†“
Phase 6
Digital Collection Register
        â†“
Phase 7
Expenses
        â†“
Phase 8
Dashboard
        â†“
Phase 9
Reports
        â†“
Phase 10
Existing Business Import
        â†“
Phase 11
Export + Audit
        â†“
Phase 12
Testing + Security
        â†“
Production
638. V2 Development Phases

After V1 receives real usage:

Guest â†’ Business Upgrade
        â†“
Business Profile
        â†“
Areas
        â†“
Employees
        â†“
Employee Area Assignment
        â†“
Customer GPS
        â†“
Route Management
        â†“
Collector Application
        â†“
Employee Expenses
        â†“
Cash Handover
        â†“
Salary
        â†“
Advanced Analytics
        â†“
SMS Add-On
        â†“
WhatsApp Add-On
639. Architecture Completion Status

At this stage, the backend PRD covers the full system:

Guest Workspace V1             âœ“

Customer Management            âœ“
Finance Accounts               âœ“
Existing Finance Migration     âœ“
Daily/Weekly/Monthly Finance    âœ“
Collection Register            âœ“
Partial/Advance Collections     âœ“
Expenses                       âœ“
Dashboard                      âœ“
Reports                        âœ“
Import/Export                  âœ“

Lender / Owner V2              âœ“
Employee / Collector V2        âœ“
Areas                          âœ“
GPS                            âœ“
Routes                         âœ“
Employee Expenses              âœ“
Cash Handover                  âœ“
Salary                         âœ“
Penalties/Waivers              âœ“

Platform Admin                 âœ“
Plans                          âœ“
Subscriptions                  âœ“
Feature Entitlements           âœ“
SMS/WhatsApp Add-ons           âœ“

Finance Calculation Engine     âœ“
Authentication                 âœ“
Authorization                  âœ“
Workspace Isolation            âœ“
Security                       âœ“
Notifications                  âœ“
Background Jobs                âœ“
PostgreSQL Architecture        âœ“
API Standards                  âœ“
Performance                    âœ“
Redis Strategy                 âœ“
Deployment                     âœ“
Backups                        âœ“
Testing                        âœ“
Final Project Structure        âœ“

So from the backend PRD/architecture perspective, the major specification is now complete.

The next useful step is no longer adding more PRD chapters. It is turning this into an implementation blueprint: exact V1 models and their fields/relationships first, then serializers, service-class method contracts, views, URLs, and the exact order of Django migrations.


-----------------------

Chapter 17 â€” V1 Implementation Blueprint
640. V1 Scope

The first production release is centered on:

Guest Workspace â€” Digital Finance Collection Book

A lender should be able to create a free workspace without onboarding their employees or entire business.

The V1 user can:

Register / Login
        â†“
Create Guest Workspace
        â†“
Add Existing Customers
        â†“
Add Existing / New Finance
        â†“
Record Previous Paid Amount
        â†“
Record Daily / Weekly / Monthly Collections
        â†“
Record Non-Payment
        â†“
Record Expenses
        â†“
See Daily Summary
        â†“
See Customer History
        â†“
See Outstanding
        â†“
View Reports
        â†“
Export Data
Explicitly not required for initial V1
Employees
Collector Management
Areas
Routes
Google Maps Navigation
Salary
Cash Handover
SMS
WhatsApp

The database architecture should remain compatible with those V2 additions.

641. V1 Django Apps

Keep the initial project compact:

accounts
core
masters
finance
integrations

integrations may contain very little in the first release.

Do not create separate Django apps for:

customers
collections
expenses
reports
dashboard

They belong inside finance.

642. Core V1 Models

The primary V1 data graph becomes:

User
 â”‚
 â–¼
WorkspaceMembership
 â”‚
 â–¼
Workspace
 â”‚
 â”œâ”€â”€ WorkspaceSettings
 â”‚
 â”œâ”€â”€ Customer
 â”‚     â”‚
 â”‚     â””â”€â”€ FinanceAccount
 â”‚             â”‚
 â”‚             â”œâ”€â”€ CollectionSchedule
 â”‚             â”‚
 â”‚             â”œâ”€â”€ Collection
 â”‚             â”‚      â”‚
 â”‚             â”‚      â””â”€â”€ CollectionAllocation
 â”‚             â”‚
 â”‚             â””â”€â”€ FinanceAdjustment
 â”‚
 â”œâ”€â”€ Expense
 â”‚
 â”œâ”€â”€ ImportJob
 â”‚
 â””â”€â”€ AuditLog
Chapter 18 â€” Accounts Models
643. User

Use a custom user model immediately.

Conceptually:

class User(AbstractBaseUser, PermissionsMixin):
    id
    public_id

    full_name

    mobile_number
    email

    password

    is_mobile_verified
    is_email_verified

    status

    is_staff
    is_superuser

    last_login

    created_at
    updated_at

Recommended public identifier:

UUID

Internal primary key:

BigAutoField
644. User Identity

For India-first V1, mobile-number login can be the primary path while email remains optional.

Recommended:

mobile_number = unique
email = nullable

Normalize mobile numbers before storage.

Eventually store them consistently in international format.

Example:

+919876543210

rather than mixing:

9876543210
+91 9876543210
91-9876543210
645. User Status

Use choices:

active
suspended
blocked
closed

Default:

active

AuthenticationService checks this before generating tokens.

646. UserManager

Because this is a custom user model, create:

class UserManager(BaseUserManager):

with methods such as:

create_user()

create_superuser()

This is one of the few framework-required cases where a model manager is appropriate.

Business operations still belong in services.

647. UserSession

Recommended for production:

class UserSession:
    id
    public_id

    user

    refresh_token_jti

    device_identifier
    device_name

    ip_address
    user_agent

    last_activity_at

    status

    created_at
    revoked_at

Statuses:

active
revoked
expired
Chapter 19 â€” Workspace Models
648. Workspace

This is one of the most important models in the architecture.

class Workspace:
    id
    public_id

    name

    workspace_type

    status

    owner

    created_at
    updated_at

For V1:

workspace_type = guest

Later:

finance_business
649. Why Workspace Exists in V1

Even though Guest initially has only one user, do not attach customers directly only to User.

Avoid:

User
 â””â”€â”€ Customers

Use:

User
   â†“
Workspace
   â†“
Customers

because V2 introduces employees into the same business.

650. Workspace Status

Recommended:

active
suspended
archived

Subscription status remains separate.

651. WorkspaceMembership
class WorkspaceMembership:
    id
    public_id

    workspace
    user

    role
    status

    joined_at
    terminated_at

    created_at
    updated_at

V1 role:

owner

V2 adds:

collector

and potentially others.

652. Membership Constraint

Prevent duplicate membership:

unique(workspace, user)
653. WorkspaceSettings

Do not fill Workspace with every configuration field.

Use:

class WorkspaceSettings:
    workspace

    currency

    timezone

    default_collection_frequency

    default_interest_type

    allow_partial_payment

    allow_advance_payment

    created_at
    updated_at

Defaults:

currency = INR

timezone = Asia/Kolkata

allow_partial_payment = True

allow_advance_payment = True
Chapter 20 â€” Customer Model
654. Customer

Recommended:

class Customer:
    id
    public_id

    workspace

    customer_code

    full_name

    mobile_number
    alternate_mobile

    address_line

    state
    district
    city
    village
    postal_code

    latitude
    longitude

    notes

    status

    created_by

    created_at
    updated_at

GPS remains nullable in V1.

This means V2 can begin capturing location without migrating to a different customer structure.

655. Customer Code

Generate automatically per workspace.

Example:

CUS-000001
CUS-000002
CUS-000003

Do not make the frontend responsible for generating it.

656. Customer Mobile Number

Do not make:

mobile_number

globally unique.

Two lenders could finance the same person.

Potential workspace-level duplicate detection:

workspace + mobile_number

can warn the lender.

However, don't automatically assume two people sharing a number are the same customer.

657. Customer Status
active
inactive
archived

Customers with finance history should be archived rather than deleted.

658. Minimal Guest Customer Creation

Your original Guest Workspace concept was intentionally quick.

Therefore customer creation should not require every field.

Minimum:

Name

Recommended:

Name
Mobile

Optional:

Address
Notes
GPS

Do not make the free digital card tedious to use.

659. CustomerService
class CustomerService:

Methods:

create_customer()

update_customer()

get_customer()

get_customers()

archive_customer()

restore_customer()

search_customers()

get_customer_summary()

get_customer_finance_history()

check_possible_duplicate()

All queries require workspace context.

Chapter 21 â€” FinanceAccount
660. Purpose

One customer can borrow multiple times.

Therefore:

Customer
   â”‚
   â”œâ”€â”€ Finance #1
   â”œâ”€â”€ Finance #2
   â””â”€â”€ Finance #3

Do not store:

loan_amount
interest
outstanding

directly as the customer's only finance state.

661. FinanceAccount Model

Recommended:

class FinanceAccount:
    id
    public_id

    workspace
    customer

    account_number

    principal_amount

    interest_type
    interest_rate
    interest_amount

    collection_frequency

    tenure_count
    tenure_unit

    start_date
    first_due_date
    expected_end_date

    original_total_payable

    adjustment_total
    effective_total_receivable

    paid_amount
    outstanding_amount

    repayment_structure

    status

    is_opening_balance

    created_by

    completed_at

    created_at
    updated_at
662. Money Fields

Every financial value should use:

DecimalField

not:

FloatField

Example:

max_digits = 14
decimal_places = 2

Exact limits can be finalized based on the maximum finance amount you want the platform to support.

663. Interest Types

V1 can support:

percentage_flat
fixed_amount

Potential later:

monthly_percentage

Do not implement complex reducing-balance lending unless it is genuinely part of your target business.

664. Collection Frequency
daily
weekly
monthly

These are essential V1 requirements.

665. Tenure

Store:

tenure_count
tenure_unit

Examples:

35 days

10 weeks

6 months

Rather than only storing:

tenure = 35

without knowing the unit.

666. Repayment Structure

V1:

installment

Later:

interest_only
custom

The field can exist before every mode is supported.

667. Finance Status

Recommended:

draft
active
completed
overdue
cancelled

Do not permanently mark overdue merely because one installment was late if you need richer state later.

You can alternatively derive overdue status while keeping the account active.

This should be finalized during implementation.

668. Account Number

Generate:

FIN-000001
FIN-000002

per workspace.

Constraint:

unique(workspace, account_number)
669. FinanceAccountService
class FinanceAccountService:

Methods:

preview_finance()

create_finance_account()

create_existing_finance_account()

update_finance_account()

get_finance_account()

get_finance_accounts()

cancel_finance_account()

complete_finance_account()

get_account_summary()

get_account_statement()

recalculate_account()

reconcile_account()
Chapter 22 â€” Existing Finance Onboarding
670. Why This Is Critical

Your Guest Workspace is primarily useful because an existing lender can start using it today.

Example:

Ramesh borrowed â‚¹10,000

Total payable â‚¹12,000

Already paid â‚¹7,000

Outstanding â‚¹5,000

The lender should not have to enter every historical collection individually.

671. Existing Finance Flow

Frontend:

Add Existing Customer
       â†“
Add Existing Finance
       â†“
Principal
       â†“
Interest / Total Payable
       â†“
Frequency
       â†“
Original Tenure
       â†“
Start Date
       â†“
Amount Paid Till Date
       â†“
Current Outstanding
       â†“
Save
672. Opening Balance

Store:

is_opening_balance = True

The service calculates:

original_total_payable
-
paid_before_platform
=
opening_outstanding
673. Opening Collection

Do not create 20 fake historical payment records if the lender only knows:

Paid Till Date = â‚¹7,000

Recommended model concept:

OpeningBalance

or a specially classified opening transaction.

This keeps:

Actual collections recorded in our app

separate from:

Historical amount entered during onboarding
674. OpeningBalance Model

Recommended:

class FinanceOpeningBalance:
    id

    workspace
    finance_account

    amount_paid_before_platform
    opening_outstanding

    as_of_date

    notes

    created_by

    created_at

One per FinanceAccount.

Constraint:

unique(finance_account)
675. Why Separate Opening Balance

Suppose dashboard says:

Collections Today = â‚¹20,000

Historical â‚¹7,000 must never accidentally appear as today's collection.

Separate opening balances prevent this accounting mistake.

Chapter 23 â€” Collection Schedule
676. CollectionSchedule Model
class CollectionSchedule:
    id
    public_id

    workspace
    finance_account

    installment_number

    due_date

    expected_amount

    allocated_amount

    remaining_amount

    status

    created_at
    updated_at
677. Schedule Status

Recommended:

upcoming
due
partial
paid
overdue
waived

Some statuses can be derived rather than constantly updated.

Avoid unnecessary scheduled jobs purely for changing:

upcoming â†’ due â†’ overdue

when date comparison can determine it.

678. Schedule Constraint
unique(finance_account, installment_number)

and ensure:

expected_amount > 0
679. ScheduleService
class ScheduleService:

Methods:

generate_schedule()

regenerate_schedule()

get_schedule()

get_due_installments()

get_overdue_installments()

allocate_payment()

reverse_allocation()

calculate_next_due()

get_schedule_summary()

regenerate_schedule() should be heavily restricted after collections exist.

Chapter 24 â€” Collection Model
680. Collection

This becomes the heart of the daily digital collection card.

class Collection:
    id
    public_id

    workspace

    customer
    finance_account

    amount

    collection_date
    collection_time

    payment_mode

    status

    notes

    recorded_by

    latitude
    longitude
    gps_accuracy

    idempotency_key

    reversed_at
    reversed_by
    reversal_reason

    created_at
    updated_at
681. Payment Modes

V1:

cash
upi
bank_transfer
other

Payment mode means:

How the lender/collector says they received the money.

The application itself does not process the customer payment.

This preserves your original requirement.

682. Collection Status

Recommended:

recorded
reversed

Avoid using:

paid
partial

as Collection statuses.

Those describe the payment's effect on the schedule/account, not whether the Collection transaction itself is valid.

683. Collection Allocation

Recommended:

class CollectionAllocation:
    id

    workspace

    collection
    schedule

    allocated_amount

    created_at

Example:

Collection â‚¹1,000
     â”‚
     â”œâ”€â”€ Schedule #4 â‚¹500
     â””â”€â”€ Schedule #5 â‚¹500
684. Collection Recording Transaction

The entire operation should occur inside:

transaction.atomic()

Flow:

Validate Request
      â†“
Lock Finance Account
      â†“
Check Outstanding
      â†“
Create Collection
      â†“
Find Oldest Outstanding Schedules
      â†“
Allocate Payment
      â†“
Update Schedules
      â†“
Update Finance Account
      â†“
Check Completion
      â†“
Audit
      â†“
Commit
685. CollectionService
class CollectionService:

Methods:

record_collection()

reverse_collection()

get_collection()

get_collections()

get_today_collections()

get_customer_collections()

get_finance_collections()

get_daily_summary()

validate_collection_amount()

allocate_collection()

recalculate_after_reversal()
686. Duplicate Tap Protection

Imagine the lender taps:

SAVE

twice because the network is slow.

Without protection:

â‚¹500
+
â‚¹500
=
â‚¹1,000 incorrectly recorded

Use:

idempotency_key

for collection creation.

Same key:

same operation

not another payment.

Chapter 25 â€” Non-Payment Records
687. Requirement

Your Guest digital card must record not only payments but:

If they didn't pay, why?

Do not create â‚¹0 Collection transactions.

Create a separate business event.

688. CollectionAttempt

Recommended:

class CollectionAttempt:
    id
    public_id

    workspace

    customer
    finance_account

    attempt_date
    attempt_time

    outcome

    reason

    promise_to_pay_date

    notes

    recorded_by

    created_at
689. Outcome

Recommended:

not_paid
customer_unavailable
promised_later
business_closed
other

The exact reasons can later come from master data.

690. Why Separate CollectionAttempt

Then the daily report can correctly say:

Customers Due            40

Paid                     31

Partial                   3

Not Paid                  4

Unavailable               2

without pretending non-payment is a financial transaction.

Chapter 26 â€” Expenses
691. Expense Model

Guest lender can record daily expenses.

class Expense:
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

    created_by

    created_at
    updated_at
692. Expense Categories

Examples:

Fuel
Food
Travel
Phone
Maintenance
Other

Allow custom categories later.

693. ExpenseService
class ExpenseService:

Methods:

create_expense()

update_expense()

get_expense()

get_expenses()

delete_or_cancel_expense()

get_daily_expenses()

get_expense_summary()

Whether an expense can be physically deleted should depend on your audit policy.

Chapter 27 â€” Guest Daily Collection Screen Backend
694. Core Requirement

This is probably the most important screen in V1.

The lender should open the workspace and immediately see today's customers.

Endpoint:

GET /api/v1/collection-register/today/
695. Today Register Response

Conceptually:

Date

Customers Due

Expected Collection

Collected

Pending

Expenses

Net Collection

Then customer rows:

Customer

Finance Account

Frequency

Expected Today

Previous Pending

Total Due

Paid Today

Outstanding

Today's Status
696. Daily Register Calculation

Conceptually:

Due Today
+
Previous Overdue
=
Current Collectable Exposure

But this does not mean the customer is required to pay the entire outstanding finance balance.

Example:

Previous Pending     â‚¹200
Today Installment    â‚¹500

Current Due          â‚¹700

Total Account
Outstanding        â‚¹6,200

The UI should distinguish these clearly.

697. Quick Collection

The frontend can show:

Ramesh
â‚¹500 Due

[ â‚¹500 ] [Paid]

The API still uses normal:

POST /collections/

There is no need for separate business logic for "quick collection."

698. Custom Amount

User can enter:

â‚¹300

instead of expected:

â‚¹500

CollectionService determines:

Partial

through allocation results.

699. Not Paid

Frontend:

[Not Paid]

opens:

Reason

Promise Date

Notes

and creates:

CollectionAttempt

not Collection.

Chapter 28 â€” DashboardService
700. Guest Dashboard

V1 dashboard should stay useful but simple.

Total Customers

Active Finance Accounts

Total Principal

Total Receivable

Total Outstanding

Today's Expected

Today's Collected

Today's Pending

Today's Expenses

Today's Net Collection

Overdue Amount

Completed Finance Accounts
701. Net Collection

For Guest:

Today's Collections
-
Today's Expenses
=
Today's Net Collection

This is operational cash-flow information, not accounting profit.

Name it carefully in the UI.

Do not call it:

Profit

because principal repayments and expenses do not by themselves calculate true business profit.

702. DashboardService
class DashboardService:

Methods:

get_guest_dashboard()

get_collection_summary()

get_finance_summary()

get_expense_summary()

get_overdue_summary()

get_recent_activity()

Use database aggregation rather than Python loops over all records.

Chapter 29 â€” Reports
703. V1 Reports

Initial reports:

Daily Collection Report

Date Range Collection Report

Customer Statement

Finance Account Statement

Outstanding Report

Overdue Report

Expense Report

Daily Summary
704. ReportService
class ReportService:

Methods:

get_daily_collection_report()

get_collection_report()

get_customer_statement()

get_finance_statement()

get_outstanding_report()

get_overdue_report()

get_expense_report()

get_daily_business_summary()
705. Customer Statement

Statement should clearly separate:

Finance Created

Opening Paid Amount

Collections

Adjustments

Waivers

Current Outstanding

This gives the lender an understandable financial history.

Chapter 30 â€” Audit Architecture
706. AuditLog

Recommended:

class AuditLog:
    id

    workspace
    user

    action

    entity_type
    entity_id

    old_values
    new_values

    ip_address
    user_agent

    created_at

JSON fields can store selected change metadata.

707. Important V1 Audit Actions

Record at least:

CUSTOMER_CREATED

CUSTOMER_UPDATED

FINANCE_CREATED

FINANCE_CANCELLED

COLLECTION_RECORDED

COLLECTION_REVERSED

EXPENSE_CREATED

EXPENSE_UPDATED

OPENING_BALANCE_CREATED

FINANCE_ADJUSTMENT_CREATED
Chapter 31 â€” V1 Endpoint Map
708. Authentication
POST /api/v1/auth/register/

POST /api/v1/auth/login/

POST /api/v1/auth/refresh/

POST /api/v1/auth/logout/

GET  /api/v1/auth/me/

POST /api/v1/auth/change-password/

POST /api/v1/auth/forgot-password/

POST /api/v1/auth/reset-password/
709. Workspace
GET   /api/v1/workspace/

PATCH /api/v1/workspace/

GET   /api/v1/workspace/settings/

PATCH /api/v1/workspace/settings/

Since Guest has one workspace, the frontend doesn't initially need complicated workspace switching.

710. Customers
GET    /api/v1/customers/

POST   /api/v1/customers/

GET    /api/v1/customers/{public_id}/

PATCH  /api/v1/customers/{public_id}/

POST /api/v1/customers/{public_id}/archive/

POST /api/v1/customers/{public_id}/restore/

GET /api/v1/customers/{public_id}/summary/

GET /api/v1/customers/{public_id}/statement/
711. Finance
POST /api/v1/finance-accounts/preview/

GET  /api/v1/finance-accounts/

POST /api/v1/finance-accounts/

GET   /api/v1/finance-accounts/{id}/

PATCH /api/v1/finance-accounts/{id}/

POST /api/v1/finance-accounts/{id}/cancel/

GET /api/v1/finance-accounts/{id}/schedule/

GET /api/v1/finance-accounts/{id}/statement/

Existing finance:

POST /api/v1/finance-accounts/existing/
712. Collection Register
GET /api/v1/collection-register/today/

GET /api/v1/collection-register/
    ?date=...

This should be optimized because it is the primary V1 screen.

713. Collections
GET  /api/v1/collections/

POST /api/v1/collections/

GET /api/v1/collections/{id}/

POST /api/v1/collections/{id}/reverse/

Filters:

date_from
date_to
customer
finance_account
payment_mode
search
714. Collection Attempts
POST /api/v1/collection-attempts/

GET /api/v1/collection-attempts/

Filters:

date
customer
outcome
715. Expenses
GET    /api/v1/expenses/

POST   /api/v1/expenses/

GET    /api/v1/expenses/{id}/

PATCH  /api/v1/expenses/{id}/

If you allow removal:

DELETE /api/v1/expenses/{id}/

or preferably controlled cancellation depending on audit requirements.

716. Dashboard
GET /api/v1/dashboard/

Optional filters later:

date_from
date_to

But the primary response should represent current business status.

717. Reports
GET /api/v1/reports/daily/

GET /api/v1/reports/collections/

GET /api/v1/reports/outstanding/

GET /api/v1/reports/overdue/

GET /api/v1/reports/expenses/

GET /api/v1/reports/customer/{id}/

GET /api/v1/reports/finance/{id}/
Chapter 32 â€” Serializer Structure
718. Avoid One Serializer Per Model

Different operations have different requirements.

For Customer:

CustomerCreateSerializer

CustomerUpdateSerializer

CustomerListSerializer

CustomerDetailSerializer

This is cleaner than exposing every database field through one giant serializer.

719. Finance Serializers

Recommended:

FinancePreviewSerializer

FinanceCreateSerializer

ExistingFinanceCreateSerializer

FinanceUpdateSerializer

FinanceListSerializer

FinanceDetailSerializer

FinanceScheduleSerializer

The create serializer accepts finance terms.

It should not accept authoritative calculated totals from the client.

720. Collection Serializers
CollectionCreateSerializer

CollectionListSerializer

CollectionDetailSerializer

CollectionReverseSerializer

Create accepts:

finance_account

amount

payment_mode

collection_date

notes

idempotency_key

Backend determines allocations.

Chapter 33 â€” View Responsibilities
721. Example Customer Create Flow
POST /customers/
       â†“
CustomerCreateView
       â†“
Authentication
       â†“
Workspace Context
       â†“
Serializer Validation
       â†“
CustomerService.create_customer()
       â†“
Response Serializer
       â†“
201 Created
722. Views Must Stay Thin

Example:

class CustomerCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CustomerCreateSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        customer = CustomerService.create_customer(
            user=request.user,
            data=serializer.validated_data,
        )

        return Response(
            CustomerDetailSerializer(customer).data,
            status=201,
        )

Conceptually, this is the level of responsibility you want.

723. Service Responsibility

CustomerService.create_customer() handles:

Resolve Workspace

Check Workspace Status

Check Plan Limit

Check Duplicate

Generate Customer Code

Create Customer

Create Audit Log

The view does not reproduce these rules.

Chapter 34 â€” Implementation Order
724. Step 1 â€” Project Foundation

Build:

Django project

DRF

PostgreSQL

Environment settings

Custom User

JWT

Common BaseModel

Exception handler

Response conventions

Pagination

Do migrations immediately.

725. Step 2 â€” Workspace

Build:

Workspace

WorkspaceMembership

WorkspaceSettings

Registration should automatically create all three.

Test:

Register
   â†“
User
   â†“
Guest Workspace
   â†“
Owner Membership
   â†“
Settings

before proceeding.

726. Step 3 â€” Customers

Implement completely:

Model
Serializer
Service
View
URL
Tests

before finance.

Test workspace isolation from this stage.

727. Step 4 â€” Finance Calculation Engine

Implement and heavily unit test:

Flat Percentage

Fixed Interest

Daily

Weekly

Monthly

Rounding

Schedule Generation

Do not build collection logic until these tests are reliable.

728. Step 5 â€” Finance Accounts

Implement:

Preview

New Finance

Existing Finance

Opening Balance

Finance Detail

Schedule
729. Step 6 â€” Collection Engine

Implement:

Collection

Allocation

Partial Payment

Advance Payment

Overpayment Validation

Reversal

Account Completion

This is the most sensitive implementation stage.

730. Step 7 â€” Daily Digital Card

Now combine:

Schedule
+
Collection
+
Attempt

into:

Today's Collection Register

This produces your main V1 product experience.

731. Step 8 â€” Expenses

Implement expense recording and daily totals.

Then:

Collection
-
Expense
=
Operational Net Collection

can appear in the daily summary.

732. Step 9 â€” Dashboard & Reports

Only after the transaction data is stable should you implement:

Dashboard

Reports

Statements

because these depend on trustworthy finance and collection data.

733. Step 10 â€” Existing Business Import

After manual flows work correctly, add bulk onboarding.

Do not build Excel import before the underlying:

CustomerService
FinanceAccountService
FinanceCalculationService

are stable.

The ImportService should call those existing services instead of duplicating their logic.

734. Critical Architecture Rule

For the whole project:

API View
   â†“
Serializer
   â†“
Service
   â†“
Models

But service-to-service calls are allowed:

CollectionService
       â†“
ScheduleService
       â†“
FinanceCalculationService
       â†“
AuditService

This is necessary and healthy.

What we want to prevent is:

View
 â†“
Huge Business Logic
 â†“
Direct ORM Everywhere
735. V1 Definition of Done

V1 is ready when a lender can:

Create Free Account
        â†“
Add Existing Customers
        â†“
Enter Their Existing Finance
        â†“
System Calculates Current Position
        â†“
Open Today's Digital Collection Card
        â†“
Select Customer
        â†“
Enter Only Paid Amount
        â†“
Record Payment Mode
        â†“
Or Record Why They Didn't Pay
        â†“
Continue Through Customers
        â†“
Record Daily Expenses
        â†“
See:
   Expected
   Collected
   Pending
   Expenses
   Net Collection
        â†“
Open Any Customer
        â†“
See:
   Borrowed Amount
   Interest
   Tenure
   Paid Till Date
   Collections Recorded
   Outstanding
        â†“
View Daily / Date-Range Reports

That gives you a small but genuinely usable V1 rather than attempting to ship the complete lender ERP immediately.

The next implementation level is the actual Django model specificationâ€”field types, ForeignKey relationships, related_names, constraints, indexes, abstract base models and which values should be stored versus calculated.


------------

Continuing with the next implementation layer: **exact V1 Django model/database specification**. This defines what should be stored in PostgreSQL, the relationships, constraints, indexes, and what should remain calculated by services.

# Chapter 35 â€” Django Model Standards

## 736. Base Model Strategy

Most business models should inherit from a common abstract model.

```python
class BaseModel(models.Model):
    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

This gives every major resource:

```text
Internal ID
Public UUID
Created Timestamp
Updated Timestamp
```

---

# 737. Internal ID vs Public ID

Use PostgreSQL/Django internal primary keys for joins:

```text
id = BigAutoField
```

Expose:

```text
public_id = UUID
```

through APIs.

Example:

```text
Database:

id = 182
public_id = 59c9a4d8-...
```

API:

```text
/api/v1/customers/59c9a4d8-.../
```

Do not expose internal sequential IDs unnecessarily.

---

# 738. Financial Field Standard

Create a consistent money convention.

Recommended:

```python
models.DecimalField(
    max_digits=14,
    decimal_places=2
)
```

This supports values up to roughly:

```text
â‚¹999,999,999,999.99
```

which is far beyond your initial requirement.

Never use:

```text
FloatField
```

for money.

---

# 739. Percentage Field

Interest rates should also use Decimal.

Example:

```python
interest_rate = models.DecimalField(
    max_digits=7,
    decimal_places=4,
    null=True,
    blank=True,
)
```

This permits rates such as:

```text
3
3.5
10.25
```

without floating-point problems.

---

# 740. Date vs DateTime

Use:

```text
DateField
```

for business dates such as:

```text
Finance Start Date
Due Date
Collection Business Date
Expense Date
Opening Balance Date
```

Use:

```text
DateTimeField
```

for system events:

```text
created_at
updated_at
reversed_at
completed_at
login_at
```

These concepts should not be mixed.

---

# 741. Historical Business Date

Suppose a lender records today's collection tomorrow morning.

The system should preserve:

```text
collection_date = actual business collection date
created_at = when record entered system
```

These can be different.

That distinction matters for reports.

---

# 742. Timezone

Store timestamps using Django timezone-aware datetimes.

Application timezone:

```text
Asia/Kolkata
```

for the initial India-focused product.

Do not manually add `+05:30` throughout business code.

---

# Chapter 36 â€” User Model Specification

## 743. User Model

Recommended implementation:

```python
class User(AbstractBaseUser, PermissionsMixin):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        BLOCKED = "blocked", "Blocked"
        CLOSED = "closed", "Closed"

    id = models.BigAutoField(primary_key=True)

    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    full_name = models.CharField(max_length=150)

    mobile_number = models.CharField(
        max_length=20,
        unique=True,
    )

    email = models.EmailField(
        null=True,
        blank=True,
    )

    is_mobile_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "mobile_number"
```

---

# 744. `status` vs `is_active`

These serve different purposes.

Django:

```text
is_active
```

controls whether authentication is generally permitted.

Your domain:

```text
status
```

explains business state.

For example:

```text
status = suspended
is_active = False
```

AuthenticationService should coordinate them.

---

# 745. Email Uniqueness

If email is optional, decide carefully whether it should be globally unique.

Recommended once email authentication/recovery is supported:

```text
non-null email must be unique
```

This can be enforced using a conditional database constraint.

For early V1, mobile number remains the primary identity.

---

# 746. UserManager

```python
class UserManager(BaseUserManager):

    def create_user(self, mobile_number, password=None, **extra_fields):
        ...

    def create_superuser(self, mobile_number, password=None, **extra_fields):
        ...
```

The manager handles Django user creation mechanics.

Application registration remains:

```text
AuthenticationService.register()
```

because registration also creates Workspace, Membership and Settings.

---

# Chapter 37 â€” Workspace Model Specification

## 747. Workspace

```python
class Workspace(BaseModel):

    class WorkspaceType(models.TextChoices):
        GUEST = "guest", "Guest"
        BUSINESS = "business", "Business"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        ARCHIVED = "archived", "Archived"

    name = models.CharField(max_length=150)

    workspace_type = models.CharField(
        max_length=20,
        choices=WorkspaceType.choices,
        default=WorkspaceType.GUEST,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_workspaces",
    )
```

---

# 748. Why `PROTECT` Owner?

If a User owns a workspace containing financial history, deleting that User should not cascade-delete the business.

Therefore:

```text
User deletion
     â†“
PROTECT
     â†“
Workspace remains safe
```

Account closure should be a status operation.

---

# 749. WorkspaceMembership & 3 Official User Roles

The system strictly supports **3 Official User Roles**:
1. **`ADMIN` (Super Admin)**: SaaS platform management via `is_superuser=True` / `is_staff=True`.
2. **`LENDER_OWNER` (Lender Owner)**: Workspace owner managing business, customers, loans, routes, staff, reports, and settings.
3. **`FIELD_COLLECTOR` (Field Collector / Agent)**: On-ground collector executing routes, recording payments, geo-attendance, and cash handover.

```python
class WorkspaceMembership(BaseModel):

    class Role(models.TextChoices):
        LENDER_OWNER = "LENDER_OWNER", "Lender Owner"
        FIELD_COLLECTOR = "FIELD_COLLECTOR", "Field Collector / Agent"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        TERMINATED = "terminated", "Terminated"

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="memberships",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="workspace_memberships",
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    terminated_at = models.DateTimeField(
        null=True,
        blank=True,
    )
```

Constraint:

```python
models.UniqueConstraint(
    fields=["workspace", "user"],
    name="unique_workspace_user_membership",
)
```

---

# 750. WorkspaceSettings

```python
class WorkspaceSettings(BaseModel):

    workspace = models.OneToOneField(
        Workspace,
        on_delete=models.PROTECT,
        related_name="settings",
    )

    currency = models.CharField(
        max_length=3,
        default="INR",
    )

    timezone = models.CharField(
        max_length=50,
        default="Asia/Kolkata",
    )

    default_collection_frequency = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )

    default_interest_type = models.CharField(
        max_length=30,
        null=True,
        blank=True,
    )

    allow_partial_payment = models.BooleanField(default=True)

    allow_advance_payment = models.BooleanField(default=True)
```

---

# Chapter 38 â€” Customer Model Specification

## 751. Customer

```python
class Customer(BaseModel):

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        ARCHIVED = "archived", "Archived"

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="customers",
    )

    customer_code = models.CharField(
        max_length=30,
    )

    full_name = models.CharField(
        max_length=150,
    )

    mobile_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )

    alternate_mobile = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )

    address_line = models.TextField(
        null=True,
        blank=True,
    )

    state = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    district = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    village = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    postal_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    notes = models.TextField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_customers",
    )
```

---

# 752. Customer Constraints

```python
models.UniqueConstraint(
    fields=["workspace", "customer_code"],
    name="unique_customer_code_per_workspace",
)
```

Do not make name unique.

Do not make mobile globally unique.

---

# 753. Customer Indexes

Recommended:

```python
models.Index(
    fields=["workspace", "status"]
)

models.Index(
    fields=["workspace", "mobile_number"]
)

models.Index(
    fields=["workspace", "full_name"]
)
```

Later V2:

```text
workspace + area
```

can be added.

---

# 754. Customer Code Generation

Do not generate codes using:

```text
Customer.objects.count() + 1
```

because concurrent requests can produce duplicates.

A safer architecture is a workspace-scoped sequence/counter.

Recommended:

```text
WorkspaceSequence
```

---

# 755. WorkspaceSequence

```python
class WorkspaceSequence(models.Model):

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="sequences",
    )

    sequence_type = models.CharField(max_length=30)

    current_value = models.PositiveBigIntegerField(default=0)
```

Constraint:

```text
unique(workspace, sequence_type)
```

Types:

```text
customer
finance_account
employee
area
```

---

# 756. SequenceService

```python
class SequenceService:

    @classmethod
    def get_next_number(cls, workspace, sequence_type):
        ...
```

Use:

```text
transaction.atomic()
+
select_for_update()
```

so concurrent creation remains safe.

Then generate:

```text
CUS-000001
FIN-000001
```

---

# Chapter 39 â€” Finance Account Model Specification

## 757. FinanceAccount Choices

```python
class FinanceAccount(BaseModel):

    class InterestType(models.TextChoices):
        FLAT_PERCENTAGE = "flat_percentage", "Flat Percentage"
        FIXED_AMOUNT = "fixed_amount", "Fixed Amount"

    class Frequency(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"

    class RepaymentStructure(models.TextChoices):
        INSTALLMENT = "installment", "Installment"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
```

For V1, I recommend deriving overdue rather than storing it as an account status.

---

# 758. Why Derive Overdue?

An account can simultaneously be:

```text
Active
+
â‚¹500 overdue
+
â‚¹5,000 future scheduled
```

Calling the entire account:

```text
status = overdue
```

loses useful information.

Better:

```text
status = active
```

and calculate:

```text
is_overdue = true
overdue_amount = â‚¹500
```

---

# 759. FinanceAccount Fields

```python
workspace = models.ForeignKey(
    Workspace,
    on_delete=models.PROTECT,
    related_name="finance_accounts",
)

customer = models.ForeignKey(
    Customer,
    on_delete=models.PROTECT,
    related_name="finance_accounts",
)

account_number = models.CharField(
    max_length=30,
)

principal_amount = models.DecimalField(
    max_digits=14,
    decimal_places=2,
)

interest_type = models.CharField(
    max_length=30,
    choices=InterestType.choices,
)

interest_rate = models.DecimalField(
    max_digits=7,
    decimal_places=4,
    null=True,
    blank=True,
)

interest_amount = models.DecimalField(
    max_digits=14,
    decimal_places=2,
)

collection_frequency = models.CharField(
    max_length=20,
    choices=Frequency.choices,
)

tenure_count = models.PositiveIntegerField()

start_date = models.DateField()

first_due_date = models.DateField()

expected_end_date = models.DateField()

original_total_payable = models.DecimalField(
    max_digits=14,
    decimal_places=2,
)

adjustment_total = models.DecimalField(
    max_digits=14,
    decimal_places=2,
    default=0,
)

effective_total_receivable = models.DecimalField(
    max_digits=14,
    decimal_places=2,
)

paid_amount = models.DecimalField(
    max_digits=14,
    decimal_places=2,
    default=0,
)

outstanding_amount = models.DecimalField(
    max_digits=14,
    decimal_places=2,
)

repayment_structure = models.CharField(
    max_length=30,
    choices=RepaymentStructure.choices,
    default=RepaymentStructure.INSTALLMENT,
)

status = models.CharField(
    max_length=20,
    choices=Status.choices,
    default=Status.ACTIVE,
)

is_opening_balance = models.BooleanField(default=False)

created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.PROTECT,
    related_name="created_finance_accounts",
)

completed_at = models.DateTimeField(
    null=True,
    blank=True,
)
```

---

# 760. Remove `tenure_unit`

Earlier we considered:

```text
tenure_count
tenure_unit
```

But because:

```text
collection_frequency
```

already represents daily/weekly/monthly installments, V1 can use:

```text
tenure_count = number of installments
```

Example:

```text
frequency = weekly
tenure_count = 20
```

means:

```text
20 weekly installments
```

This is simpler and avoids contradictory combinations such as:

```text
frequency = weekly
tenure_unit = months
```

---

# 761. Finance Constraints

Database constraints:

```text
principal_amount > 0

interest_amount >= 0

original_total_payable >= principal_amount

paid_amount >= 0

outstanding_amount >= 0

tenure_count > 0
```

Also:

```text
customer.workspace == finance.workspace
```

cannot easily be guaranteed with a simple PostgreSQL FK constraint using this schema.

Therefore Service validation must enforce it.

---

# 762. Finance Indexes

Recommended:

```text
workspace + status

workspace + customer

workspace + account_number

workspace + expected_end_date
```

Unique:

```text
workspace + account_number
```

---

# Chapter 40 â€” Opening Balance Model

## 763. FinanceOpeningBalance

```python
class FinanceOpeningBalance(BaseModel):

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="finance_opening_balances",
    )

    finance_account = models.OneToOneField(
        FinanceAccount,
        on_delete=models.PROTECT,
        related_name="opening_balance",
    )

    amount_paid_before_platform = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    opening_outstanding = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    as_of_date = models.DateField()

    notes = models.TextField(
        null=True,
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_opening_balances",
    )
```

---

# 764. Existing Finance Validation

Service verifies:

```text
amount_paid_before_platform
<=
original_total_payable
```

and:

```text
opening_outstanding
=
original_total_payable
-
amount_paid_before_platform
```

Do not accept `opening_outstanding` from frontend as authoritative.

Calculate it.

---

# Chapter 41 â€” Schedule Model Specification

## 765. CollectionSchedule

```python
class CollectionSchedule(BaseModel):

    finance_account = models.ForeignKey(
        FinanceAccount,
        on_delete=models.PROTECT,
        related_name="schedules",
    )

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="collection_schedules",
    )

    installment_number = models.PositiveIntegerField()

    due_date = models.DateField()

    expected_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    allocated_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    remaining_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
```

---

# 766. Do We Need Schedule Status Stored?

For V1, I recommend **not storing status**.

Derive:

```text
allocated = 0
remaining > 0
due_date > today
â†’ upcoming

allocated = 0
due_date = today
â†’ due

allocated > 0
remaining > 0
â†’ partial

remaining = 0
â†’ paid

remaining > 0
due_date < today
â†’ overdue
```

This avoids stale statuses.

---

# 767. Schedule Constraints

```text
unique(finance_account, installment_number)

expected_amount > 0

allocated_amount >= 0

remaining_amount >= 0

allocated_amount <= expected_amount
```

Also:

```text
remaining_amount
=
expected_amount - allocated_amount
```

is maintained by service logic.

---

# 768. Schedule Indexes

```text
workspace + due_date

finance_account + due_date

workspace + due_date + remaining_amount
```

The last pattern helps collection-register queries.

---

# Chapter 42 â€” Collection Model Specification

## 769. Collection

```python
class Collection(BaseModel):

    class PaymentMode(models.TextChoices):
        CASH = "cash", "Cash"
        UPI = "upi", "UPI"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        RECORDED = "recorded", "Recorded"
        REVERSED = "reversed", "Reversed"

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="collections",
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="collections",
    )

    finance_account = models.ForeignKey(
        FinanceAccount,
        on_delete=models.PROTECT,
        related_name="collections",
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    collection_date = models.DateField()

    payment_mode = models.CharField(
        max_length=30,
        choices=PaymentMode.choices,
    )

    notes = models.TextField(
        null=True,
        blank=True,
    )

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recorded_collections",
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    gps_accuracy = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    idempotency_key = models.UUIDField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RECORDED,
    )

    reversed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    reversed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reversed_collections",
        null=True,
        blank=True,
    )

    reversal_reason = models.TextField(
        null=True,
        blank=True,
    )
```

---

# 770. Collection Time

We previously considered separate:

```text
collection_time
```

but it is not necessary if:

```text
collection_date
```

represents business date and:

```text
created_at
```

records actual system submission time.

If the lender needs to manually specify the historical time later, we can add it.

For V1, avoid unnecessary fields.

---

# 771. Collection Idempotency Constraint

Use:

```text
unique(workspace, idempotency_key)
```

not globally unique if you want keys scoped by workspace.

---

# 772. Collection Indexes

Important:

```text
workspace + collection_date

workspace + customer + collection_date

workspace + finance_account + collection_date

workspace + recorded_by + collection_date

workspace + status + collection_date
```

This table will grow quickly, so indexes matter.

---

# Chapter 43 â€” Collection Allocation

## 773. CollectionAllocation

```python
class CollectionAllocation(BaseModel):

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="collection_allocations",
    )

    collection = models.ForeignKey(
        Collection,
        on_delete=models.PROTECT,
        related_name="allocations",
    )

    schedule = models.ForeignKey(
        CollectionSchedule,
        on_delete=models.PROTECT,
        related_name="allocations",
    )

    allocated_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
```

Constraint:

```text
unique(collection, schedule)
```

and:

```text
allocated_amount > 0
```

---

# 774. Why Allocation Is Essential

Without allocation:

```text
Finance â‚¹12,000
Paid â‚¹5,000
```

tells you total payment but not:

```text
Which installments were covered?
What is overdue?
What was paid in advance?
```

With allocation:

```text
Collection #1 â‚¹1,500
   â†“
Installment 1 â‚¹500
Installment 2 â‚¹500
Installment 3 â‚¹500
```

you can reconstruct the account correctly.

---

# Chapter 44 â€” Collection Attempt

## 775. CollectionAttempt

```python
class CollectionAttempt(BaseModel):

    class Outcome(models.TextChoices):
        NOT_PAID = "not_paid", "Not Paid"
        CUSTOMER_UNAVAILABLE = (
            "customer_unavailable",
            "Customer Unavailable",
        )
        PROMISED_LATER = "promised_later", "Promised Later"
        BUSINESS_CLOSED = "business_closed", "Business Closed"
        OTHER = "other", "Other"

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="collection_attempts",
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="collection_attempts",
    )

    finance_account = models.ForeignKey(
        FinanceAccount,
        on_delete=models.PROTECT,
        related_name="collection_attempts",
    )

    attempt_date = models.DateField()

    outcome = models.CharField(
        max_length=30,
        choices=Outcome.choices,
    )

    reason = models.TextField(
        null=True,
        blank=True,
    )

    promise_to_pay_date = models.DateField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        null=True,
        blank=True,
    )

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="collection_attempts",
    )
```

---

# 776. Promise Validation

If:

```text
outcome = promised_later
```

require:

```text
promise_to_pay_date
```

and preferably:

```text
promise_to_pay_date >= attempt_date
```

This belongs primarily in serializer/service validation.

---

# Chapter 45 â€” Expense Model

## 777. ExpenseCategory

Instead of hardcoding categories permanently, use:

```python
class ExpenseCategory(BaseModel):

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="expense_categories",
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=100)

    code = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)
```

Meaning:

```text
workspace = NULL
â†’ System Category

workspace = specific workspace
â†’ Custom Category
```

---

# 778. Expense

```python
class Expense(BaseModel):

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="expenses",
    )

    expense_date = models.DateField()

    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name="expenses",
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    payment_mode = models.CharField(
        max_length=30,
    )

    description = models.TextField(
        null=True,
        blank=True,
    )

    receipt = models.FileField(
        upload_to="expense_receipts/",
        null=True,
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_expenses",
    )
```

---

# 779. Expense Constraints

```text
amount > 0
```

and Service validates:

```text
category.workspace
```

must either be:

```text
NULL
```

or:

```text
same workspace
```

---

# Chapter 46 â€” Finance Adjustment

## 780. FinanceAdjustment

Even if V1 uses this lightly, include the architecture.

```python
class FinanceAdjustment(BaseModel):

    class AdjustmentType(models.TextChoices):
        CHARGE = "charge", "Charge"
        WAIVER = "waiver", "Waiver"
        DISCOUNT = "discount", "Discount"

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="finance_adjustments",
    )

    finance_account = models.ForeignKey(
        FinanceAccount,
        on_delete=models.PROTECT,
        related_name="adjustments",
    )

    adjustment_type = models.CharField(
        max_length=20,
        choices=AdjustmentType.choices,
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    reason = models.TextField()

    effective_date = models.DateField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_finance_adjustments",
    )
```

---

# 781. Adjustment Sign

Store:

```text
amount = positive value
```

regardless of type.

Example:

```text
CHARGE â‚¹500

WAIVER â‚¹200
```

FinanceCalculationService determines effect:

```text
Charge
â†’ +â‚¹500

Waiver
â†’ -â‚¹200
```

This is easier to understand than storing negative values inconsistently.

---

# Chapter 47 â€” Audit Log

## 782. AuditLog

```python
class AuditLog(models.Model):

    id = models.BigAutoField(primary_key=True)

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="audit_logs",
        null=True,
        blank=True,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="audit_logs",
        null=True,
        blank=True,
    )

    action = models.CharField(max_length=100)

    entity_type = models.CharField(max_length=100)

    entity_id = models.CharField(max_length=100)

    old_values = models.JSONField(
        null=True,
        blank=True,
    )

    new_values = models.JSONField(
        null=True,
        blank=True,
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    user_agent = models.TextField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
```

Audit logs should generally be append-only.

---

# Chapter 48 â€” What Should Be Stored vs Calculated?

## 783. Important Rule

Do not store every value just because the frontend displays it.

There are three categories:

```text
Authoritative Stored Values

Cached / Snapshot Values

Calculated Values
```

---

# 784. Authoritative Stored Values

Examples:

```text
Principal

Interest Terms

Finance Start Date

Schedule Expected Amount

Collection Amount

Collection Date

Expense Amount

Opening Balance

Adjustment

Customer Details
```

These represent actual business events or agreements.

---

# 785. Snapshot Values

FinanceAccount stores:

```text
paid_amount

outstanding_amount

effective_total_receivable
```

even though they can theoretically be calculated.

Why?

Because these values are requested constantly.

Instead of:

```text
SUM 50,000 collections
+
adjustments
+
opening balance
```

every time an account appears, maintain an authoritative cached summary.

But it must be reconcilable from transaction records.

---

# 786. Calculated Values

Do not necessarily store:

```text
is_overdue

overdue_amount

today_due

today_collected

today_pending

customer_total_outstanding

dashboard_total_collected

daily_net_collection
```

These should generally come from service queries/aggregations.

---

# 787. Source of Truth Hierarchy

For financial reconciliation:

```text
Finance Terms
       +
Opening Balance
       +
Schedules
       +
Collections
       +
Allocations
       +
Adjustments
       â†“
Authoritative History
       â†“
FinanceAccount Summary Fields
```

If summary values become inconsistent, history allows them to be rebuilt.

---

# Chapter 49 â€” Collection Transaction Algorithm

## 788. Record Collection

`CollectionService.record_collection()` should roughly perform:

```text
1. Resolve workspace

2. Validate workspace active

3. Validate finance account belongs to workspace

4. Validate finance active

5. Validate customer/account relationship

6. Validate amount > 0

7. Check idempotency key

8. Begin transaction

9. Lock FinanceAccount

10. Lock relevant schedules

11. Recheck outstanding

12. Reject invalid overpayment

13. Create Collection

14. Allocate oldest remaining schedule first

15. Update schedule allocated/remaining values

16. Update FinanceAccount paid/outstanding

17. Complete account if outstanding = 0

18. Create AuditLog

19. Commit

20. Return updated account summary
```

---

# 789. Oldest-Due-First Allocation

Example:

```text
Schedule 1
Remaining â‚¹200

Schedule 2
Remaining â‚¹500

Schedule 3
Remaining â‚¹500
```

Customer pays:

```text
â‚¹900
```

Allocation:

```text
Schedule 1 â†’ â‚¹200
Schedule 2 â†’ â‚¹500
Schedule 3 â†’ â‚¹200
```

Remaining:

```text
Schedule 3 â†’ â‚¹300
```

This algorithm should be deterministic.

---

# 790. Overpayment

Suppose:

```text
Outstanding = â‚¹700
```

and user enters:

```text
â‚¹1,000
```

V1 should reject:

```text
COLLECTION_EXCEEDS_OUTSTANDING
```

rather than silently accepting â‚¹300 extra.

Future versions could support customer credit balances if required.

---

# 791. Collection Reversal Algorithm

Never:

```text
DELETE Collection
```

Instead:

```text
Lock Account
     â†“
Lock Collection
     â†“
Validate not already reversed
     â†“
Reverse Allocations
     â†“
Restore Schedule Remaining
     â†“
Decrease Account Paid
     â†“
Increase Outstanding
     â†“
Reopen Account if previously completed
     â†“
Mark Collection REVERSED
     â†“
Store Reason/User/Time
     â†“
Audit
```

All inside one transaction.

---

# Chapter 50 â€” Existing Finance Schedule Strategy

## 792. Important Scenario

Suppose lender starts using your app today.

Existing customer:

```text
Original Finance       â‚¹10,000

Total Payable          â‚¹12,000

Weekly Installment       â‚¹600

Original Tenure       20 weeks

Already Paid          â‚¹7,200

Current Outstanding   â‚¹4,800
```

The platform may not know exactly which historical dates the â‚¹7,200 was paid.

---

# 793. Do Not Fabricate History

Do not generate fake records like:

```text
Week 1 paid â‚¹600
Week 2 paid â‚¹600
...
Week 12 paid â‚¹600
```

unless the lender actually supplies that history.

Instead store:

```text
Opening Paid â‚¹7,200
```

---

# 794. Remaining Schedule

Generate schedule only for the remaining obligation from the onboarding point according to the selected continuation rule.

For example:

```text
Outstanding â‚¹4,800
Weekly â‚¹600
```

Remaining:

```text
8 installments
```

starting from the selected:

```text
Next Collection Date
```

This is much cleaner for the Guest Workspace.

---

# 795. Existing Finance Input

Therefore existing finance creation should request:

```text
Customer

Original Principal

Interest Type

Interest Rate / Interest Amount

Original Total Payable

Frequency

Original Tenure

Original Start Date

Paid Till Date

Next Collection Date

Expected Installment Amount
```

Backend calculates:

```text
Current Outstanding
Remaining Installments
Expected End Date
```

---

# 796. Existing Irregular Finance

Sometimes:

```text
Outstanding â‚¹5,000

Weekly expected â‚¹700
```

doesn't divide evenly.

Generate:

```text
â‚¹700
â‚¹700
â‚¹700
â‚¹700
â‚¹700
â‚¹700
â‚¹700
â‚¹100
```

so:

```text
SUM(schedule) = â‚¹5,000
```

---

# Chapter 51 â€” Daily Register Query Design

## 797. Main Query

Today's register should identify finance accounts having:

```text
remaining schedule due today
```

OR:

```text
remaining schedule overdue from earlier
```

Then group appropriately by customer/account.

---

# 798. Register Customer State

For every finance account calculate:

```text
today_expected

previous_pending

total_due

paid_today

remaining_due

account_outstanding

latest_attempt
```

---

# 799. Status Logic

Possible UI status:

```text
PAID

PARTIAL

PENDING

NOT_PAID

PROMISED_LATER

UNAVAILABLE
```

These are presentation/business-register statuses.

Do not necessarily create a database column for them.

---

# 800. Paid Today Example

Expected:

```text
â‚¹500
```

Customer pays:

```text
â‚¹500
```

Register:

```text
Expected       â‚¹500
Collected      â‚¹500
Pending          â‚¹0
Status          PAID
```

---

# 801. Partial Example

Expected:

```text
â‚¹500
```

Paid:

```text
â‚¹300
```

Register:

```text
Expected       â‚¹500
Collected      â‚¹300
Pending        â‚¹200
Status       PARTIAL
```

---

# 802. No Payment Example

Expected:

```text
â‚¹500
```

Attempt:

```text
Customer unavailable
```

Register:

```text
Expected       â‚¹500
Collected        â‚¹0
Pending        â‚¹500
Status   UNAVAILABLE
```

---

# Chapter 52 â€” Service Class Standards

## 803. Your Required Service Pattern

You specifically requested class-based services.

Use:

```python
class CustomerService:

    @classmethod
    def create_customer(cls, *, workspace, user, data):
        ...

    @classmethod
    def update_customer(cls, *, workspace, customer, user, data):
        ...
```

or:

```python
@staticmethod
```

where class state/helper dispatch isn't needed.

Both remain class-based.

---

# 804. Avoid Service Instantiation Without Need

Do not unnecessarily do:

```python
service = CustomerService()
service.create_customer(...)
```

if the service carries no state.

Prefer:

```python
CustomerService.create_customer(...)
```

This keeps service usage simple.

---

# 805. Service-to-Service Calls

Allowed:

```text
FinanceAccountService
    â†“
FinanceCalculationService

CollectionService
    â†“
ScheduleService

CollectionService
    â†“
AuditService

AuthenticationService
    â†“
WorkspaceService
```

But avoid circular service dependencies.

---

# 806. Service Return Values

Services should preferably return domain objects/data rather than DRF `Response`.

Bad:

```python
return Response(...)
```

inside service.

Good:

```python
return collection
```

Then View determines HTTP response.

Services should not depend heavily on DRF.

---

# 807. Service Exceptions

Define domain exceptions:

```text
WorkspaceSuspendedError

FinanceAccountCompletedError

CollectionExceedsOutstandingError

DuplicateCollectionError

CustomerNotFoundError

PlanLimitReachedError
```

Global exception handler converts them into API responses.

---

# Chapter 53 â€” Serializer Validation Boundary

## 808. Serializer Handles Structural Validation

Serializer should handle things such as:

```text
Required field

String length

Date format

Decimal format

Choice validation

Basic field relationships
```

---

# 809. Service Handles Business Validation

Service handles:

```text
Customer belongs to workspace

Finance is active

Collection doesn't exceed outstanding

Workspace plan permits action

Account can be cancelled

Collection can be reversed

Existing finance values are financially consistent
```

This separation is important.

---

# Chapter 54 â€” View Filtering Pattern

## 810. Example

Request:

```text
GET /collections/
?date_from=2026-07-01
&date_to=2026-07-23
&payment_mode=cash
&search=ramesh
```

View validates parameters.

Then:

```python
collections = CollectionService.get_collections(
    workspace=workspace,
    filters=validated_filters,
)
```

Service builds ORM query.

---

# 811. Why Filters Belong in Service Query

Your rule says Views handle filtering/application concerns.

That means View decides:

```text
which filters were requested
whether values are valid
```

while Service performs:

```text
queryset.filter(...)
select_related(...)
ordering
business restrictions
```

This prevents ORM/business queries from spreading into views.

---

# Chapter 55 â€” V1 Migration Order

## 812. Initial Migration Sequence

Recommended development sequence:

```text
1. accounts.User

2. core.Workspace

3. core.WorkspaceMembership

4. core.WorkspaceSettings

5. core.WorkspaceSequence

6. finance.Customer

7. finance.FinanceAccount

8. finance.FinanceOpeningBalance

9. finance.CollectionSchedule

10. finance.Collection

11. finance.CollectionAllocation

12. finance.CollectionAttempt

13. finance.ExpenseCategory

14. finance.Expense

15. finance.FinanceAdjustment

16. core.AuditLog
```

Django will resolve actual migration dependencies.

The point is to build domains in this conceptual order rather than creating all 40 future models immediately.

---

# 813. Seed Data

After migrations, seed only necessary system masters.

For example:

```text
Expense Categories

Fuel
Food
Travel
Phone
Maintenance
Other
```

Potential future master records can wait.

Use a data migration or controlled management command rather than manually adding production master records through Django shell.

---

# Chapter 56 â€” First V1 API Development Order

## 814. API Milestone 1

Build:

```text
POST /auth/register/
POST /auth/login/
POST /auth/refresh/
GET  /auth/me/
POST /auth/logout/
```

Definition of done:

> A new user registers and automatically owns a Guest Workspace.

---

# 815. API Milestone 2

Build customer APIs.

Definition of done:

> User can create, list, search, update and archive customers without accessing another workspace's data.

---

# 816. API Milestone 3

Build:

```text
POST /finance-accounts/preview/
```

before finance creation.

Definition of done:

> Daily, weekly and monthly calculations produce correct schedules and exact totals.

---

# 817. API Milestone 4

Build new and existing finance creation.

Definition of done:

> A lender can enter both a brand-new finance and an already-running finance.

---

# 818. API Milestone 5

Build collection APIs.

Definition of done:

> Full, partial and advance collections allocate correctly and update outstanding atomically.

---

# 819. API Milestone 6

Build:

```text
POST /collection-attempts/
```

Definition of done:

> User can record why a due customer didn't pay.

---

# 820. API Milestone 7

Build daily register.

This becomes the first point where the V1 feels like the intended product.

```text
GET /collection-register/today/
```

---

# 821. API Milestone 8

Build expenses.

Then daily summary can show:

```text
Collected â‚¹25,000

Expenses   â‚¹1,500

Net       â‚¹23,500
```

---

# 822. API Milestone 9

Build:

```text
Dashboard
Customer Statement
Finance Statement
Outstanding Report
Collection Report
Expense Report
```

---

# 823. API Milestone 10

Only after everything above works:

```text
Excel Import
Excel Export
```

Then a lender with hundreds of existing customers can migrate efficiently.

---

# Chapter 57 â€” V1 Database Relationship Summary

The resulting V1 PostgreSQL architecture is:

```text
USER
 â”‚
 â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
 â”‚                          â”‚
 â–¼                          â–¼
WORKSPACE MEMBERSHIP     USER SESSION
 â”‚
 â–¼
WORKSPACE
 â”‚
 â”œâ”€â”€ WORKSPACE SETTINGS
 â”‚
 â”œâ”€â”€ WORKSPACE SEQUENCE
 â”‚
 â”œâ”€â”€ EXPENSE CATEGORY
 â”‚
 â”œâ”€â”€ EXPENSE
 â”‚
 â”œâ”€â”€ AUDIT LOG
 â”‚
 â””â”€â”€ CUSTOMER
       â”‚
       â””â”€â”€ FINANCE ACCOUNT
              â”‚
              â”œâ”€â”€ OPENING BALANCE
              â”‚
              â”œâ”€â”€ FINANCE ADJUSTMENT
              â”‚
              â”œâ”€â”€ COLLECTION ATTEMPT
              â”‚
              â”œâ”€â”€ COLLECTION SCHEDULE
              â”‚        â–²
              â”‚        â”‚
              â”‚   COLLECTION ALLOCATION
              â”‚        â–²
              â”‚        â”‚
              â””â”€â”€ COLLECTION
```

This is compact enough for V1 while leaving a clean extension path for:

```text
Areas
Employees
Routes
GPS
Cash Handover
Salary
Subscriptions
SMS
WhatsApp
```

without redesigning the finance core.

---

# Chapter 58 â€” Next Backend Layer

The **model/database specification is now sufficiently defined to begin coding**.

The next layer should be the exact **service contract specification**, because your architecture intentionally puts most of the application intelligence there.

That means defining each method, its inputs, validation rules, transaction boundary and output for:

```text
AuthenticationService
WorkspaceService
SequenceService
CustomerService
FinanceCalculationService
FinanceAccountService
ScheduleService
CollectionService
CollectionAttemptService
ExpenseService
DashboardService
ReportService
AuditService
ImportService
ExportService
```

The most important of those is `FinanceCalculationService â†’ FinanceAccountService â†’ ScheduleService â†’ CollectionService`, because that chain becomes the financial core of the entire application.



--------------------------

Continuing with the **Service Layer Contract Specification**. This is the most important architectural layer for your backend because CRUD, ORM operations, calculations, transactions, and business rules are centralized here.

# Chapter 59 â€” Service Layer Architecture

## 824. Service Layer Responsibility

Your final request flow should be:

```text
URL
 â†“
View
 â†“
Serializer
 â†“
Service
 â†“
Model / PostgreSQL
```

Views handle HTTP/application concerns.

Services handle:

```text
CRUD operations
ORM queries
Business rules
Financial calculations
Transactions
Cross-model operations
Authorization of resources
Audit creation
External integration coordination
```

---

# 825. Service Class Standard

Use class-based services.

Preferred:

```python
class CustomerService:

    @classmethod
    def create_customer(cls, *, workspace, user, data):
        ...

    @classmethod
    def update_customer(cls, *, workspace, user, customer_id, data):
        ...
```

`@staticmethod` is also acceptable when the method doesn't use other class methods.

Avoid standalone business functions scattered throughout the application.

---

# 826. Service Input Rule

Prefer explicit keyword arguments.

Good:

```python
CollectionService.record_collection(
    workspace=workspace,
    user=request.user,
    finance_account_id=finance_id,
    data=serializer.validated_data,
)
```

instead of passing the entire request:

```python
CollectionService.record_collection(request)
```

Services should generally not depend on DRF's `Request`.

---

# 827. Service Output Rule

Services return:

```text
Model Instance
QuerySet
Domain Result Object
Dictionary of calculated values
```

They should not normally return:

```python
Response(...)
```

HTTP handling belongs to Views.

---

# Chapter 60 â€” AuthenticationService

## 828. Responsibility

```python
class AuthenticationService:
```

handles:

```text
Registration
Login
Logout
Refresh-token related session handling
Password changes
Password recovery
User verification
Authentication context
```

---

# 829. `register()`

Contract:

```python
AuthenticationService.register(
    *,
    validated_data,
    request_metadata=None,
)
```

Input:

```text
full_name
mobile_number
password
email (optional)
```

Flow:

```text
Normalize Mobile
      â†“
Check Existing User
      â†“
Validate Registration Rules
      â†“
transaction.atomic()
      â†“
Create User
      â†“
Create Guest Workspace
      â†“
Create Owner Membership
      â†“
Create Workspace Settings
      â†“
Initialize Workspace Sequences
      â†“
Assign Free Guest Plan when plans exist
      â†“
Create Audit/Event
      â†“
Generate Authentication Tokens
      â†“
Create UserSession
      â†“
Commit
```

Return:

```text
user
workspace
membership
access_token
refresh_token
```

---

# 830. Registration Transaction

Registration creates several related records.

Therefore:

```python
@transaction.atomic
```

should cover:

```text
User
Workspace
Membership
Settings
Initial configuration
```

If Workspace creation fails, you don't want a half-created registration.

---

# 831. `login()`

```python
AuthenticationService.login(
    *,
    mobile_number,
    password,
    device_info=None,
)
```

Flow:

```text
Normalize Mobile
      â†“
Find User
      â†“
Verify Password
      â†“
Check is_active
      â†“
Check status
      â†“
Generate Tokens
      â†“
Create/Update UserSession
      â†“
Return Authentication Context
```

---

# 832. Login Failure

Do not return:

```text
Mobile exists but password is wrong.
```

versus:

```text
Mobile does not exist.
```

to anonymous callers.

Prefer a generic message:

```text
Invalid mobile number or password.
```

This reduces account enumeration.

---

# 833. `get_authenticated_context()`

```python
AuthenticationService.get_authenticated_context(
    *,
    user,
)
```

Returns:

```text
User
Workspace
Membership
Role
Workspace Type
Settings
Plan
Features
```

For V1 Guest:

```text
role = owner
workspace_type = guest
```

---

# Chapter 61 â€” WorkspaceService

## 834. Responsibility

```python
class WorkspaceService:
```

Methods:

```text
create_guest_workspace()

get_user_workspace()

get_workspace()

update_workspace()

get_workspace_settings()

update_workspace_settings()

validate_workspace_access()

upgrade_workspace()
```

`upgrade_workspace()` becomes important in V2.

---

# 835. `get_user_workspace()`

V1 assumes one active workspace.

```python
WorkspaceService.get_user_workspace(
    *,
    user,
)
```

Query through:

```text
WorkspaceMembership
```

rather than trusting a workspace ID supplied by the frontend.

---

# 836. Future Workspace Switching

V2 may eventually support:

```text
One user
   â†“
Multiple finance businesses
```

If required, the architecture can later accept:

```text
X-Workspace-ID
```

or another explicit workspace context.

Do not build this complexity into Guest V1 unless required.

---

# 837. Workspace Access Validation

```python
WorkspaceService.validate_workspace_access(
    *,
    workspace,
    user,
)
```

Checks:

```text
Membership exists
Membership active
Workspace active
User active
```

Returns membership or raises a domain exception.

---

# Chapter 62 â€” SequenceService

## 838. Responsibility

Generates workspace-scoped identifiers.

```python
class SequenceService:
```

Methods:

```text
get_next_number()

generate_customer_code()

generate_finance_account_number()

generate_employee_code()

generate_area_code()
```

V1 uses the first three relevant methods.

---

# 839. Sequence Transaction

Example:

```python
SequenceService.generate_customer_code(
    workspace=workspace
)
```

Internally:

```text
BEGIN TRANSACTION
      â†“
SELECT WorkspaceSequence
FOR UPDATE
      â†“
current_value += 1
      â†“
SAVE
      â†“
CUS-000123
      â†“
COMMIT
```

This prevents duplicates under concurrent requests.

---

# Chapter 63 â€” CustomerService

## 840. Responsibility

```python
class CustomerService:
```

Methods:

```text
create_customer()

update_customer()

get_customer()

get_customers()

archive_customer()

restore_customer()

search_customers()

check_possible_duplicate()

get_customer_summary()

get_customer_finance_history()
```

---

# 841. `create_customer()`

```python
CustomerService.create_customer(
    *,
    workspace,
    user,
    data,
)
```

Flow:

```text
Validate Workspace
      â†“
Check Plan Limit
      â†“
Normalize Mobile
      â†“
Check Possible Duplicate
      â†“
Generate Customer Code
      â†“
Create Customer
      â†“
Audit
      â†“
Return Customer
```

---

# 842. Duplicate Handling

Suppose same workspace already has:

```text
Ramesh
9876543210
```

and lender adds:

```text
Ramesh Kumar
9876543210
```

Do not necessarily reject it automatically.

Return/raise a duplicate warning workflow if desired.

There are legitimate cases where people share phone numbers.

---

# 843. `get_customer()`

Never:

```python
Customer.objects.get(public_id=customer_id)
```

Use:

```python
Customer.objects.get(
    public_id=customer_id,
    workspace=workspace,
)
```

Every service follows this principle.

---

# 844. `get_customers()`

Inputs:

```text
workspace
filters
search
ordering
```

Possible filters:

```text
status
has_active_finance
created_from
created_to
```

Search:

```text
full_name
mobile_number
customer_code
```

---

# 845. `archive_customer()`

Rules:

```text
Customer exists in workspace
      â†“
Already archived?
      â†“
Check active finance
```

If active finance exists, recommended V1 behavior:

```text
Reject archive
```

unless product requirements explicitly allow hidden customers with active debt.

---

# Chapter 64 â€” FinanceCalculationService

## 846. Responsibility

This service must remain as pure and deterministic as possible.

```python
class FinanceCalculationService:
```

It should generally not perform database writes.

Methods:

```text
calculate_interest()

calculate_total_payable()

calculate_installment_amount()

calculate_schedule()

calculate_expected_end_date()

calculate_remaining_finance()

apply_adjustments()

calculate_outstanding()

validate_finance_terms()
```

This makes financial calculations easy to unit test.

---

# 847. Flat Percentage Interest

Example:

```text
Principal = â‚¹10,000
Interest = 20%
```

Calculation:

```text
Interest
= 10,000 Ã— 20 / 100
= â‚¹2,000

Total Payable
= â‚¹12,000
```

---

# 848. Fixed Interest

Example:

```text
Principal = â‚¹10,000
Fixed Interest = â‚¹2,000
```

Then:

```text
Total Payable = â‚¹12,000
```

---

# 849. Installment Calculation

Suppose:

```text
Total Payable = â‚¹12,000
Tenure = 35 days
```

Raw installment:

```text
â‚¹342.857...
```

Money requires deterministic rounding.

You cannot simply create:

```text
35 Ã— â‚¹342.86
```

and assume it exactly equals â‚¹12,000.

---

# 850. Rounding Strategy

Recommended:

```text
Calculate standard installment
      â†“
Round to 2 decimal places
      â†“
Generate N - 1 installments
      â†“
Final installment =
Total Payable - previous installment total
```

Therefore:

```text
SUM(schedule.expected_amount)
=
total payable
```

always.

---

# 851. Example

If:

```text
Total = â‚¹1,000
Tenure = 3
```

schedule could be:

```text
â‚¹333.33
â‚¹333.33
â‚¹333.34
```

Never:

```text
â‚¹333.33 Ã— 3 = â‚¹999.99
```

with â‚¹0.01 disappearing.

---

# 852. Decimal Rounding

Use Python:

```python
Decimal
```

with an explicitly chosen rounding strategy.

Do not mix:

```text
float
+
Decimal
```

in financial calculations.

---

# 853. `calculate_schedule()`

Input concept:

```python
FinanceCalculationService.calculate_schedule(
    total_payable=Decimal("12000.00"),
    tenure_count=35,
    frequency="daily",
    first_due_date=date(...),
)
```

Return:

```python
[
    {
        "installment_number": 1,
        "due_date": ...,
        "expected_amount": Decimal("342.86"),
    },
    ...
]
```

No database writes.

---

# 854. Daily Schedule

For:

```text
frequency = daily
```

increment:

```text
1 calendar day
```

per installment.

Later, if lenders need:

```text
Skip Sundays
Skip holidays
Custom collection days
```

introduce collection-calendar rules separately.

Do not silently assume those rules now.

---

# 855. Weekly Schedule

For:

```text
frequency = weekly
```

increment:

```text
7 days
```

---

# 856. Monthly Schedule

Monthly date handling requires care.

Example:

```text
First Due Date = January 31
```

There is no February 31.

Use calendar-aware month arithmetic rather than adding 30 days.

A sensible rule is:

> Use the same day where available; otherwise use the last valid day of the target month.

This rule should be explicitly tested.

---

# 857. Finance Preview

The frontend should not calculate authoritative finance totals.

Endpoint:

```text
POST /finance-accounts/preview/
```

calls:

```text
FinanceCalculationService
```

and returns:

```text
Principal
Interest
Total Payable
Installment
First Due
Expected End
Schedule Preview
```

Then the user confirms.

---

# Chapter 65 â€” FinanceAccountService

## 858. Responsibility

```python
class FinanceAccountService:
```

Methods:

```text
preview_finance()

create_finance_account()

create_existing_finance_account()

update_finance_account()

get_finance_account()

get_finance_accounts()

cancel_finance_account()

complete_finance_account()

get_account_summary()

get_account_statement()

recalculate_account()

reconcile_account()
```

---

# 859. `preview_finance()`

This can delegate almost entirely to:

```text
FinanceCalculationService
```

No records created.

---

# 860. `create_finance_account()`

Flow:

```text
Resolve Customer
      â†“
Validate Same Workspace
      â†“
Validate Finance Terms
      â†“
Calculate Interest
      â†“
Calculate Total Payable
      â†“
Generate Schedule
      â†“
BEGIN TRANSACTION
      â†“
Generate Account Number
      â†“
Create FinanceAccount
      â†“
Create CollectionSchedule rows
      â†“
Audit
      â†“
COMMIT
```

---

# 861. Initial Finance Summary

For a new finance:

```text
paid_amount = 0

outstanding_amount =
effective_total_receivable
```

Example:

```text
Principal              â‚¹10,000
Interest                â‚¹2,000

Effective Receivable   â‚¹12,000

Paid                         â‚¹0

Outstanding            â‚¹12,000
```

---

# 862. Existing Finance Creation

```python
FinanceAccountService.create_existing_finance_account(
    *,
    workspace,
    user,
    customer,
    data,
)
```

Flow:

```text
Validate Original Finance
      â†“
Calculate Original Total
      â†“
Validate Paid Till Date
      â†“
Calculate Outstanding
      â†“
Validate Next Collection Date
      â†“
Generate Remaining Schedule
      â†“
BEGIN TRANSACTION
      â†“
Create FinanceAccount
      â†“
Create OpeningBalance
      â†“
Create Remaining Schedule
      â†“
Audit
      â†“
COMMIT
```

---

# 863. Existing Finance Paid Amount

Suppose:

```text
Original Total = â‚¹12,000
Paid Before Platform = â‚¹7,000
```

FinanceAccount can store:

```text
paid_amount = â‚¹7,000
outstanding = â‚¹5,000
```

But reporting must distinguish:

```text
Total Paid = â‚¹7,000

Platform Collections = â‚¹0

Opening Paid = â‚¹7,000
```

This distinction is critical.

---

# 864. Finance Editing

Not every finance field should remain editable forever.

Before first collection:

```text
Principal
Interest
Frequency
Tenure
Dates
```

may be editable.

After collections exist:

```text
Do not freely rewrite original terms
```

because doing so changes historical meaning.

Use controlled:

```text
Adjustments
Waivers
Charges
```

instead.

---

# 865. `cancel_finance_account()`

Recommended rule:

If:

```text
No collections
```

allow cancellation.

If collections already exist:

```text
Require stronger controlled process
```

rather than casually cancelling the account.

V1 can simply reject cancellation after valid collections exist.

---

# Chapter 66 â€” ScheduleService

## 866. Responsibility

```python
class ScheduleService:
```

Methods:

```text
create_schedule()

get_account_schedule()

get_due_schedules()

get_overdue_schedules()

get_collectable_schedules()

allocate_amount()

reverse_allocation()

calculate_due_summary()
```

---

# 867. Collectable Schedule Query

For a given date:

```text
remaining_amount > 0

AND

due_date <= selected_date
```

ordered by:

```text
due_date ASC
installment_number ASC
```

This implements oldest-due-first allocation.

---

# 868. Schedule Summary

For an account:

```text
Upcoming Amount
Due Today
Overdue Amount
Total Due
Paid Schedule Amount
Remaining Schedule Amount
Next Due Date
```

---

# Chapter 67 â€” CollectionService

## 869. Responsibility

```python
class CollectionService:
```

This is the most transaction-sensitive service.

Methods:

```text
record_collection()

reverse_collection()

get_collection()

get_collections()

get_customer_collections()

get_finance_collections()

validate_collection()

allocate_collection()

get_collection_summary()

get_today_collection_total()
```

---

# 870. `record_collection()`

Signature:

```python
CollectionService.record_collection(
    *,
    workspace,
    user,
    finance_account_id,
    data,
)
```

Input:

```text
amount
payment_mode
collection_date
notes
idempotency_key

optional GPS
```

---

# 871. Validation Order

Perform cheap validation first:

```text
Amount valid?
Date valid?
Payment mode valid?
```

Then database/business validation:

```text
Finance belongs to workspace?
Customer belongs to finance?
Account active?
Outstanding available?
Duplicate request?
```

Then transaction.

---

# 872. Future-Dated Collections

V1 should normally reject:

```text
collection_date > today
```

because a collection represents money already received.

If scheduled/future payments are needed later, that is a different concept.

---

# 873. Backdated Collections

Allowing backdated entries is useful because lenders may enter records later.

Example:

```text
Collected yesterday
Recorded today
```

Allow it.

But preserve:

```text
collection_date = yesterday
created_at = today
```

Audit records make this visible.

---

# 874. Collection Allocation

After creating Collection:

```text
remaining_to_allocate = collection.amount
```

Iterate oldest outstanding schedules.

Example:

```text
for schedule in schedules:

    amount =
        min(
            schedule.remaining_amount,
            remaining_to_allocate
        )

    create allocation

    update schedule

    remaining_to_allocate -= amount

    if remaining_to_allocate == 0:
        break
```

All within the transaction.

---

# 875. Advance Payment

Suppose today only â‚¹500 is due but account outstanding is â‚¹5,000.

Customer pays:

```text
â‚¹2,000
```

If:

```text
allow_advance_payment = True
```

allocation can continue into future schedules.

Therefore:

```text
â‚¹500 current
+
â‚¹1,500 future
```

becomes allocated.

---

# 876. Partial Payment

Suppose due:

```text
â‚¹500
```

customer pays:

```text
â‚¹200
```

Schedule becomes:

```text
expected        â‚¹500
allocated       â‚¹200
remaining       â‚¹300
```

No special partial-payment transaction type is required.

The state emerges naturally from allocation.

---

# 877. Account Completion

After collection:

```text
outstanding_amount == 0
```

then:

```text
status = completed
completed_at = timezone.now()
```

---

# 878. Reversal Permission

For Guest V1:

```text
Owner can reverse
```

Later V2:

```text
Collector records
Owner may control reversal
```

This is why the reversal operation should already use PermissionService hooks.

---

# 879. Reversal Audit

Audit should record:

```text
Collection ID
Amount
Reason
Reversed By
Time
Affected Finance
```

Do not hide reversed collections from history.

Display them appropriately.

---

# Chapter 68 â€” CollectionAttemptService

## 880. Responsibility

```python
class CollectionAttemptService:
```

Methods:

```text
create_attempt()

update_attempt()

get_attempts()

get_latest_attempt()

get_customer_attempts()
```

---

# 881. Attempt Creation

Validate:

```text
Customer belongs to workspace

Finance belongs to customer

Finance active

Attempt date valid

Outcome valid
```

If promised later:

```text
promise_to_pay_date required
```

---

# 882. Multiple Attempts

Do not force only one attempt per customer per day.

Example:

```text
10:00 AM
Customer unavailable

5:00 PM
Promised tomorrow
```

Both can be useful later for collectors.

V1 UI may choose to display only the latest attempt.

---

# Chapter 69 â€” ExpenseService

## 883. Responsibility

```python
class ExpenseService:
```

Methods:

```text
create_expense()

update_expense()

get_expense()

get_expenses()

cancel_expense()

get_daily_total()

get_expense_summary()
```

---

# 884. Expense Creation

Flow:

```text
Validate Workspace
      â†“
Validate Category
      â†“
Validate Amount
      â†“
Validate Date
      â†“
Validate Receipt
      â†“
Create Expense
      â†“
Audit
```

---

# 885. Expense Date

As with collections:

```text
expense_date
```

is the business date.

```text
created_at
```

is system entry time.

Backdated expenses can be allowed.

Future expenses should generally not be recorded as actual expenses.

---

# Chapter 70 â€” FinanceAdjustmentService

## 886. Responsibility

```python
class FinanceAdjustmentService:
```

Methods:

```text
create_charge()

create_waiver()

create_discount()

get_adjustments()

reverse_adjustment()
```

Do not let frontend directly manipulate:

```text
outstanding_amount
```

to "correct" an account.

Use an adjustment.

---

# 887. Example

Current:

```text
Outstanding â‚¹5,000
```

Lender waives:

```text
â‚¹500
```

Do not:

```text
PATCH outstanding = 4500
```

Create:

```text
WAIVER â‚¹500
```

Then:

```text
Effective Receivable decreases â‚¹500
Outstanding becomes â‚¹4,500
```

and history remains explainable.

---

# Chapter 71 â€” DashboardService

## 888. Responsibility

```python
class DashboardService:
```

Methods:

```text
get_guest_dashboard()

get_daily_summary()

get_finance_summary()

get_collection_summary()

get_expense_summary()

get_overdue_summary()

get_recent_activity()
```

---

# 889. Dashboard Date

Dashboard should receive an optional business date.

Default:

```text
today in workspace timezone
```

Do not rely blindly on server UTC date.

---

# 890. Today's Expected

Calculate from schedules due on selected date.

Be careful not to confuse:

```text
Expected Today
```

with:

```text
Total Due including previous overdue
```

Show both if useful.

---

# 891. Today's Collection

Use valid:

```text
Collection.status = recorded
```

where:

```text
collection_date = selected_date
```

Opening balances must never enter this calculation.

---

# 892. Today's Expenses

```text
SUM(expenses.amount)
```

for selected business date.

---

# 893. Net Collection

```text
Valid Collections
-
Expenses
```

Label:

```text
Net Collection
```

or:

```text
Net Cash Position
```

not accounting profit.

---

# 894. Outstanding

Workspace outstanding:

```text
SUM(
    active FinanceAccount.outstanding_amount
)
```

depending on whether completed/cancelled records should contribute.

Usually:

```text
completed â†’ 0
cancelled â†’ excluded
```

---

# Chapter 72 â€” ReportService

## 895. Responsibility

```python
class ReportService:
```

Methods:

```text
get_daily_report()

get_collection_report()

get_customer_statement()

get_finance_statement()

get_outstanding_report()

get_overdue_report()

get_expense_report()

get_business_summary()
```

---

# 896. Customer Statement

Return chronological events:

```text
Opening Finance

Opening Balance

Collection

Collection

Adjustment

Collection Reversal

Waiver

...
```

A statement should explain how the current balance was reached.

---

# 897. Finance Statement

Header:

```text
Account Number
Customer
Principal
Interest
Total Receivable
Opening Paid
Platform Collected
Adjustments
Outstanding
Status
```

Then transaction history.

---

# 898. Outstanding Report

Columns:

```text
Customer
Finance Account
Principal
Total Receivable
Total Paid
Outstanding
Overdue
Next Due Date
Frequency
```

---

# 899. Overdue Report

Calculate from schedules:

```text
due_date < selected_date

AND

remaining_amount > 0
```

Do not simply filter FinanceAccount status.

---

# Chapter 73 â€” AuditService

## 900. Responsibility

```python
class AuditService:
```

Methods:

```text
log_create()

log_update()

log_action()

log_financial_event()
```

Audit failures require deliberate handling.

For critical financial actions, the audit record should preferably be part of the same transaction.

---

# 901. Audit Payload

Do not dump complete model objects blindly.

Store relevant changed fields.

Example:

```json
{
  "amount": "500.00",
  "payment_mode": "cash",
  "finance_account": "FIN-000123"
}
```

Avoid:

```text
Passwords
Tokens
Sensitive secrets
```

---

# Chapter 74 â€” ImportService

## 902. V1 Import Purpose

Existing lenders may have:

```text
20
100
500
1000+
```

customers.

Manual onboarding would become painful.

Support spreadsheet import after core workflows are stable.

---

# 903. ImportService

```python
class ImportService:
```

Methods:

```text
validate_file()

parse_file()

validate_headers()

validate_row()

preview_import()

execute_import()

get_import_status()

get_import_errors()
```

---

# 904. Import Architecture

Never make ImportService independently create raw database records using duplicated rules.

Bad:

```text
ImportService
  â†“
Customer.objects.create()
FinanceAccount.objects.create()
```

Preferred:

```text
ImportService
   â†“
CustomerService
   â†“
FinanceAccountService
```

so manual and imported records follow the same rules.

---

# 905. Import Preview

Recommended flow:

```text
Upload Excel
      â†“
Parse
      â†“
Validate
      â†“
Show:

450 valid
23 warnings
7 errors
      â†“
User Confirms
      â†“
Import Valid Rows
```

This is much safer than importing immediately.

---

# 906. Import Row Example

Potential columns:

```text
Customer Name

Mobile

Address

Principal

Interest Type

Interest Rate / Amount

Frequency

Original Tenure

Start Date

Paid Till Date

Next Collection Date
```

---

# 907. Import Errors

Return row-level errors:

```text
Row 18
Invalid mobile number

Row 42
Paid amount exceeds total payable

Row 78
Unsupported frequency
```

Do not return only:

```text
Import failed.
```

---

# Chapter 75 â€” ExportService

## 908. Responsibility

```python
class ExportService:
```

Methods:

```text
export_customers()

export_collections()

export_outstanding()

export_expenses()

export_customer_statement()

export_finance_statement()
```

---

# 909. Export Security

Every export query must still be:

```text
workspace scoped
```

Exports are particularly sensitive because one authorization bug can expose large amounts of customer data.

---

# Chapter 76 â€” PermissionService

## 910. Add It Now Even Though V1 Has One Role

Create:

```python
class PermissionService:
```

even if Guest V1 only has Owner.

Methods:

```text
can_manage_customer()

can_manage_finance()

can_record_collection()

can_reverse_collection()

can_manage_expense()

can_view_report()
```

V1 implementation may simply confirm:

```text
active owner membership
```

V2 can expand it without rewriting finance services.

---

# Chapter 77 â€” Service Dependency Map

## 911. Recommended Dependency Direction

```text
AuthenticationService
      â”‚
      â””â”€â”€ WorkspaceService

CustomerService
      â”‚
      â”œâ”€â”€ SequenceService
      â”œâ”€â”€ PermissionService
      â””â”€â”€ AuditService

FinanceAccountService
      â”‚
      â”œâ”€â”€ FinanceCalculationService
      â”œâ”€â”€ ScheduleService
      â”œâ”€â”€ SequenceService
      â”œâ”€â”€ PermissionService
      â””â”€â”€ AuditService

CollectionService
      â”‚
      â”œâ”€â”€ ScheduleService
      â”œâ”€â”€ PermissionService
      â””â”€â”€ AuditService

ExpenseService
      â”‚
      â”œâ”€â”€ PermissionService
      â””â”€â”€ AuditService

DashboardService
      â”‚
      â””â”€â”€ Read Queries

ReportService
      â”‚
      â””â”€â”€ Read Queries

ImportService
      â”‚
      â”œâ”€â”€ CustomerService
      â””â”€â”€ FinanceAccountService
```

Avoid:

```text
FinanceCalculationService
      â†“
FinanceAccountService
```

because that would create circular dependencies.

Calculation service should remain low-level/pure.

---

# Chapter 78 â€” Transaction Ownership

## 912. One Service Owns the Transaction

Suppose:

```text
FinanceAccountService
    â†“
ScheduleService
```

`FinanceAccountService` should normally own the outer transaction.

Avoid many unrelated nested transaction boundaries.

Critical transaction owners:

```text
AuthenticationService.register()

FinanceAccountService.create_finance_account()

FinanceAccountService.create_existing_finance_account()

CollectionService.record_collection()

CollectionService.reverse_collection()

FinanceAdjustmentService.create_*

Import row/batch operations
```

---

# Chapter 79 â€” Exception Architecture

## 913. Base Exception

Create:

```python
class BusinessException(Exception):
    code = "BUSINESS_ERROR"
    message = "Unable to complete operation."
    status_code = 400
```

Then domain exceptions inherit from it.

---

# 914. Example Exceptions

```text
WorkspaceNotFoundError

WorkspaceSuspendedError

PermissionDeniedError

CustomerNotFoundError

FinanceAccountNotFoundError

FinanceAccountCompletedError

FinanceAccountCancelledError

InvalidFinanceTermsError

CollectionExceedsOutstandingError

CollectionAlreadyReversedError

DuplicateCollectionError

InvalidOpeningBalanceError

PlanLimitReachedError
```

---

# 915. Global Exception Handler

DRF handler converts:

```text
BusinessException
```

into:

```json
{
  "success": false,
  "code": "COLLECTION_EXCEEDS_OUTSTANDING",
  "message": "Collection amount exceeds the account outstanding balance.",
  "errors": {}
}
```

This keeps Views clean.

---

# Chapter 80 â€” Serializer Contract Map

## 916. Authentication

```text
RegisterSerializer
LoginSerializer
ChangePasswordSerializer
ForgotPasswordSerializer
ResetPasswordSerializer
UserSerializer
AuthContextSerializer
```

---

# 917. Customer

```text
CustomerCreateSerializer
CustomerUpdateSerializer
CustomerListSerializer
CustomerDetailSerializer
CustomerSummarySerializer
```

---

# 918. Finance

```text
FinancePreviewSerializer

FinanceCreateSerializer

ExistingFinanceCreateSerializer

FinanceUpdateSerializer

FinanceListSerializer

FinanceDetailSerializer

FinanceSummarySerializer

ScheduleSerializer
```

---

# 919. Collection

```text
CollectionCreateSerializer

CollectionListSerializer

CollectionDetailSerializer

CollectionReverseSerializer

CollectionAttemptCreateSerializer

CollectionAttemptSerializer
```

---

# 920. Expense

```text
ExpenseCreateSerializer

ExpenseUpdateSerializer

ExpenseListSerializer

ExpenseDetailSerializer

ExpenseCategorySerializer
```

---

# 921. Reports

Reports do not necessarily need model serializers.

Use dedicated output serializers where useful:

```text
DailyReportSerializer

OutstandingReportSerializer

CustomerStatementSerializer

FinanceStatementSerializer
```

This also improves OpenAPI documentation.

---

# Chapter 81 â€” Views

## 922. View Structure

You can use DRF:

```text
APIView
GenericAPIView
```

and selected generic views.

Because your business logic lives in services, I would avoid relying heavily on `ModelViewSet` behavior that encourages ORM operations directly in Views.

Explicit APIs make the domain clearer.

---

# 923. Customer Views

```text
CustomerListCreateView

CustomerDetailView

CustomerArchiveView

CustomerRestoreView

CustomerSummaryView

CustomerStatementView
```

---

# 924. Finance Views

```text
FinancePreviewView

FinanceAccountListCreateView

ExistingFinanceCreateView

FinanceAccountDetailView

FinanceCancelView

FinanceScheduleView

FinanceStatementView
```

---

# 925. Collection Views

```text
CollectionListCreateView

CollectionDetailView

CollectionReverseView

CollectionAttemptListCreateView

DailyCollectionRegisterView
```

---

# 926. Expense Views

```text
ExpenseListCreateView

ExpenseDetailView

ExpenseCategoryListView
```

---

# 927. Dashboard / Reports

```text
GuestDashboardView

DailyReportView

CollectionReportView

OutstandingReportView

OverdueReportView

ExpenseReportView
```

---

# Chapter 82 â€” URL Structure

## 928. Root URLs

```text
/api/v1/auth/

/api/v1/workspace/

/api/v1/customers/

/api/v1/finance-accounts/

/api/v1/collections/

/api/v1/collection-attempts/

/api/v1/collection-register/

/api/v1/expenses/

/api/v1/dashboard/

/api/v1/reports/
```

Keep API naming consistent.

---

# Chapter 83 â€” Recommended Service Folder

## 929. Final V1 `finance/services`

```text
finance/
â””â”€â”€ services/
    â”‚
    â”œâ”€â”€ customer_service.py
    â”‚
    â”œâ”€â”€ finance_calculation_service.py
    â”‚
    â”œâ”€â”€ finance_account_service.py
    â”‚
    â”œâ”€â”€ schedule_service.py
    â”‚
    â”œâ”€â”€ collection_service.py
    â”‚
    â”œâ”€â”€ collection_attempt_service.py
    â”‚
    â”œâ”€â”€ finance_adjustment_service.py
    â”‚
    â”œâ”€â”€ expense_service.py
    â”‚
    â”œâ”€â”€ dashboard_service.py
    â”‚
    â”œâ”€â”€ report_service.py
    â”‚
    â”œâ”€â”€ import_service.py
    â”‚
    â””â”€â”€ export_service.py
```

Core:

```text
core/
â””â”€â”€ services/
    â”œâ”€â”€ workspace_service.py
    â”œâ”€â”€ sequence_service.py
    â”œâ”€â”€ permission_service.py
    â”œâ”€â”€ audit_service.py
    â””â”€â”€ feature_access_service.py
```

Accounts:

```text
accounts/
â””â”€â”€ services/
    â”œâ”€â”€ authentication_service.py
    â””â”€â”€ user_service.py
```

---

# Chapter 84 â€” Critical Finance Invariants

## 930. Database Must Always Satisfy

For every active finance:

```text
paid_amount
+
outstanding_amount
=
effective_total_receivable
```

subject to your opening-balance and adjustment representation.

---

# 931. Schedule Invariant

```text
SUM(schedule.expected_amount)
=
remaining scheduled obligation represented by those schedules
```

For new finance this generally starts as:

```text
SUM(schedule.expected_amount)
=
effective_total_receivable
```

For imported existing finance, schedules may intentionally represent only the remaining obligation.

---

# 932. Allocation Invariant

For every valid collection:

```text
SUM(collection.allocations)
=
collection.amount
```

---

# 933. Schedule Allocation Invariant

For every schedule:

```text
allocated_amount
+
remaining_amount
=
expected_amount
```

---

# 934. Reversal Invariant

Reversing a collection must restore the exact financial state that existed immediately before that collection, except for later valid transactions that remain in history.

This is why allocation records are important.

---

# 935. Opening Balance Invariant

```text
opening_paid
+
opening_outstanding
=
original_total_payable
```

for imported finance before subsequent platform events and adjustments.

---

# Chapter 85 â€” Concurrency Example

## 936. Why Locking Matters

Finance outstanding:

```text
â‚¹500
```

Two requests arrive simultaneously:

```text
Request A â†’ collect â‚¹500
Request B â†’ collect â‚¹500
```

Without locking, both might read:

```text
outstanding = â‚¹500
```

and both succeed.

Result:

```text
â‚¹1,000 collected against â‚¹500
```

---

# 937. Correct Handling

Inside:

```text
CollectionService.record_collection()
```

use:

```text
transaction.atomic()
       â†“
FinanceAccount.objects.select_for_update()
```

Request A obtains lock.

Request B waits.

After A commits:

```text
outstanding = â‚¹0
```

B reads the updated state and fails.

This is essential for production finance software.

---

# Chapter 86 â€” V1 Backend Completion Map

At this stage, the backend design has progressed through:

```text
Product Requirements             âœ“

Roles                            âœ“

Guest Workspace                  âœ“

V1 / V2 Separation               âœ“

Django App Architecture          âœ“

5-Layer Architecture             âœ“

PostgreSQL Architecture          âœ“

Model Specification              âœ“

Relationships                    âœ“

Indexes                          âœ“

Constraints                      âœ“

Financial Data Model             âœ“

Existing Finance Migration       âœ“

Schedule Architecture            âœ“

Collection Allocation            âœ“

Partial Payment                  âœ“

Advance Payment                  âœ“

Non-Payment Records              âœ“

Expenses                         âœ“

Adjustments                      âœ“

Authentication                   âœ“

Workspace Isolation              âœ“

Authorization                    âœ“

Service Layer Contracts          âœ“

Transactions                     âœ“

Concurrency                      âœ“

Exceptions                       âœ“

Serializer Structure             âœ“

View Structure                   âœ“

URL Structure                    âœ“

Reports                          âœ“

Dashboard                        âœ“

Import / Export Architecture     âœ“

Audit Architecture               âœ“
```

The architecture/specification portion is therefore effectively complete enough to start implementation.

The next practical chapter is **actual implementation planning**: exact Django package/files to create first, dependencies for `requirements.txt`, settings organization, PostgreSQL configuration, custom User setup, BaseModel, exception handler, JWT configuration, and the first migration. After that, implementation can proceed feature-by-feature instead of adding more architectural abstraction.



-----------------------------

Continuing into the **actual Django backend implementation plan**. The architecture is now fixed enough that development should proceed in a controlled order.

# Chapter 87 â€” Backend Bootstrap & Foundation

## 938. Technology Stack

For V1:

```text
Python
Django
Django REST Framework
PostgreSQL
SimpleJWT
django-cors-headers
django-filter
drf-spectacular
Pillow
python-dotenv / django-environ
psycopg
```

Later V2 can add:

```text
Redis
Celery
Celery Beat
Django Channels â€” only if genuine real-time features require it
Google Maps Platform
SMS Provider
WhatsApp Business API
Object Storage
Payment Gateway
```

**Do not add Redis, Celery or Channels to V1 simply because they may be useful later.**

---

# 939. Initial Project Creation

Conceptual setup:

```text
backend/
â”‚
â”œâ”€â”€ manage.py
â”‚
â”œâ”€â”€ requirements.txt
â”‚
â”œâ”€â”€ .env
â”‚
â”œâ”€â”€ .env.example
â”‚
â”œâ”€â”€ .gitignore
â”‚
â”‚
â”œâ”€â”€ config/
â”œâ”€â”€ accounts/
â”œâ”€â”€ core/
â”œâ”€â”€ masters/
â”œâ”€â”€ finance/
â””â”€â”€ integrations/
```

Apps:

```text
accounts
core
masters
finance
integrations
```

`integrations` does not necessarily need database models.

---

# 940. Final V1 Folder Structure

```text
backend/
â”‚
â”œâ”€â”€ manage.py
â”œâ”€â”€ requirements.txt
â”œâ”€â”€ .env
â”œâ”€â”€ .env.example
â”œâ”€â”€ .gitignore
â”‚
â”œâ”€â”€ config/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ urls.py
â”‚   â”œâ”€â”€ asgi.py
â”‚   â”œâ”€â”€ wsgi.py
â”‚   â”‚
â”‚   â””â”€â”€ settings/
â”‚       â”œâ”€â”€ __init__.py
â”‚       â”œâ”€â”€ base.py
â”‚       â”œâ”€â”€ development.py
â”‚       â””â”€â”€ production.py
â”‚
â”œâ”€â”€ accounts/
â”‚   â”œâ”€â”€ migrations/
â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ user.py
â”‚   â”‚   â”œâ”€â”€ user_session.py
â”‚   â”‚   â””â”€â”€ otp.py
â”‚   â”‚
â”‚   â”œâ”€â”€ serializers/
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ auth_serializer.py
â”‚   â”‚   â””â”€â”€ user_serializer.py
â”‚   â”‚
â”‚   â”œâ”€â”€ services/
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ authentication_service.py
â”‚   â”‚   â””â”€â”€ user_service.py
â”‚   â”‚
â”‚   â”œâ”€â”€ views/
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â””â”€â”€ auth_views.py
â”‚   â”‚
â”‚   â”œâ”€â”€ managers.py
â”‚   â”œâ”€â”€ urls.py
â”‚   â””â”€â”€ apps.py
â”‚
â”œâ”€â”€ core/
â”‚   â”œâ”€â”€ migrations/
â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ base.py
â”‚   â”‚   â”œâ”€â”€ workspace.py
â”‚   â”‚   â”œâ”€â”€ workspace_sequence.py
â”‚   â”‚   â””â”€â”€ audit.py
â”‚   â”‚
â”‚   â”œâ”€â”€ serializers/
â”‚   â”‚   â”œâ”€â”€ workspace_serializer.py
â”‚   â”‚   â””â”€â”€ common_serializer.py
â”‚   â”‚
â”‚   â”œâ”€â”€ services/
â”‚   â”‚   â”œâ”€â”€ workspace_service.py
â”‚   â”‚   â”œâ”€â”€ sequence_service.py
â”‚   â”‚   â”œâ”€â”€ permission_service.py
â”‚   â”‚   â””â”€â”€ audit_service.py
â”‚   â”‚
â”‚   â”œâ”€â”€ views/
â”‚   â”‚   â””â”€â”€ workspace_views.py
â”‚   â”‚
â”‚   â”œâ”€â”€ exceptions/
â”‚   â”‚   â”œâ”€â”€ base.py
â”‚   â”‚   â”œâ”€â”€ auth.py
â”‚   â”‚   â”œâ”€â”€ workspace.py
â”‚   â”‚   â””â”€â”€ finance.py
â”‚   â”‚
â”‚   â”œâ”€â”€ exception_handler.py
â”‚   â”œâ”€â”€ permissions.py
â”‚   â”œâ”€â”€ pagination.py
â”‚   â”œâ”€â”€ utils.py
â”‚   â””â”€â”€ urls.py
â”‚
â”œâ”€â”€ masters/
â”‚   â”œâ”€â”€ migrations/
â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â”œâ”€â”€ location.py
â”‚   â”‚   â””â”€â”€ expense_category.py
â”‚   â”œâ”€â”€ serializers/
â”‚   â”œâ”€â”€ services/
â”‚   â”œâ”€â”€ views/
â”‚   â””â”€â”€ urls.py
â”‚
â”œâ”€â”€ finance/
â”‚   â”œâ”€â”€ migrations/
â”‚   â”‚
â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ customer.py
â”‚   â”‚   â”œâ”€â”€ finance_account.py
â”‚   â”‚   â”œâ”€â”€ opening_balance.py
â”‚   â”‚   â”œâ”€â”€ collection_schedule.py
â”‚   â”‚   â”œâ”€â”€ collection.py
â”‚   â”‚   â”œâ”€â”€ collection_attempt.py
â”‚   â”‚   â”œâ”€â”€ finance_adjustment.py
â”‚   â”‚   â””â”€â”€ expense.py
â”‚   â”‚
â”‚   â”œâ”€â”€ serializers/
â”‚   â”‚   â”œâ”€â”€ customer_serializer.py
â”‚   â”‚   â”œâ”€â”€ finance_serializer.py
â”‚   â”‚   â”œâ”€â”€ collection_serializer.py
â”‚   â”‚   â”œâ”€â”€ collection_attempt_serializer.py
â”‚   â”‚   â”œâ”€â”€ expense_serializer.py
â”‚   â”‚   â”œâ”€â”€ dashboard_serializer.py
â”‚   â”‚   â””â”€â”€ report_serializer.py
â”‚   â”‚
â”‚   â”œâ”€â”€ services/
â”‚   â”‚   â”œâ”€â”€ customer_service.py
â”‚   â”‚   â”œâ”€â”€ finance_calculation_service.py
â”‚   â”‚   â”œâ”€â”€ finance_account_service.py
â”‚   â”‚   â”œâ”€â”€ schedule_service.py
â”‚   â”‚   â”œâ”€â”€ collection_service.py
â”‚   â”‚   â”œâ”€â”€ collection_attempt_service.py
â”‚   â”‚   â”œâ”€â”€ finance_adjustment_service.py
â”‚   â”‚   â”œâ”€â”€ expense_service.py
â”‚   â”‚   â”œâ”€â”€ dashboard_service.py
â”‚   â”‚   â”œâ”€â”€ report_service.py
â”‚   â”‚   â”œâ”€â”€ import_service.py
â”‚   â”‚   â””â”€â”€ export_service.py
â”‚   â”‚
â”‚   â”œâ”€â”€ views/
â”‚   â”‚   â”œâ”€â”€ customer_views.py
â”‚   â”‚   â”œâ”€â”€ finance_views.py
â”‚   â”‚   â”œâ”€â”€ collection_views.py
â”‚   â”‚   â”œâ”€â”€ expense_views.py
â”‚   â”‚   â”œâ”€â”€ dashboard_views.py
â”‚   â”‚   â””â”€â”€ report_views.py
â”‚   â”‚
â”‚   â”œâ”€â”€ urls.py
â”‚   â””â”€â”€ apps.py
â”‚
â”œâ”€â”€ integrations/
â”‚   â”œâ”€â”€ services/
â”‚   â”‚   â”œâ”€â”€ storage_service.py
â”‚   â”‚   â”œâ”€â”€ google_maps_service.py
â”‚   â”‚   â”œâ”€â”€ sms_service.py
â”‚   â”‚   â””â”€â”€ whatsapp_service.py
â”‚   â””â”€â”€ providers/
â”‚
â””â”€â”€ tests/
```

---

# Chapter 88 â€” Requirements

## 941. Core V1 Dependencies

Conceptually:

```text
Django
djangorestframework
djangorestframework-simplejwt
psycopg
django-cors-headers
django-filter
drf-spectacular
Pillow
```

Use pinned/controlled dependency versions in production rather than installing arbitrary latest versions on every deployment.

---

# 942. Don't Install Yet

V1 does not immediately require:

```text
channels
channels-redis
redis
celery
django-celery-beat
```

They belong to later infrastructure requirements.

This keeps:

```text
Development
Deployment
Debugging
Hosting Cost
```

simpler.

---

# Chapter 89 â€” Settings Architecture

## 943. Base Settings

`config/settings/base.py`

contains settings shared by all environments:

```text
INSTALLED_APPS
MIDDLEWARE
AUTH_USER_MODEL
REST_FRAMEWORK
JWT
LANGUAGE
TIMEZONE
STATIC
MEDIA
API documentation
Password validators
```

---

# 944. Development Settings

`development.py`

contains:

```text
DEBUG = True

Development database

Local CORS origins

Development email backend

Verbose logging
```

---

# 945. Production Settings

`production.py`

contains:

```text
DEBUG = False

Production PostgreSQL

Production domains

HTTPS security

Restricted CORS

Production storage

Production logging
```

---

# 946. Environment Selection

Use an environment variable such as:

```text
DJANGO_SETTINGS_MODULE=config.settings.development
```

locally.

Production:

```text
DJANGO_SETTINGS_MODULE=config.settings.production
```

---

# Chapter 90 â€” Environment Variables

## 947. `.env.example`

Keep an example such as:

```text
DJANGO_SECRET_KEY=

DEBUG=

DATABASE_URL=

ALLOWED_HOSTS=

CORS_ALLOWED_ORIGINS=

ACCESS_TOKEN_MINUTES=

REFRESH_TOKEN_DAYS=
```

Later:

```text
REDIS_URL=

GOOGLE_MAPS_API_KEY=

SMS_API_KEY=

WHATSAPP_ACCESS_TOKEN=

STORAGE_ACCESS_KEY=
STORAGE_SECRET_KEY=
```

---

# 948. `.env`

Never commit:

```text
.env
```

to Git.

`.gitignore` should include at minimum:

```text
.env
venv/
.venv/
__pycache__/
*.pyc
media/
.pytest_cache/
.coverage
```

---

# Chapter 91 â€” PostgreSQL Configuration

## 949. Development Database

Create a dedicated database/user.

Conceptually:

```text
Database:
finance_platform

User:
finance_app
```

Do not run the application using the PostgreSQL superuser in production.

---

# 950. Connection Configuration

The application should consume database credentials from environment configuration.

Conceptually:

```text
DATABASE_URL
    â†“
Django
    â†“
PostgreSQL
```

Do not hardcode:

```text
database password
host
production URL
```

inside source files.

---

# 951. Database Connection Lifecycle

Request:

```text
React
 â†“
Django API
 â†“
Django ORM
 â†“
PostgreSQL
```

Django manages database connections.

Your services simply use ORM operations.

You do not manually open a new PostgreSQL connection inside every service.

---

# Chapter 92 â€” Custom User Must Come First

## 952. Critical Django Rule

Create the custom User model **before initial migrations**.

Set:

```text
AUTH_USER_MODEL = "accounts.User"
```

before running your first real migration.

Changing the user model after the project already contains many migrations is much more painful.

---

# 953. User Manager

Structure:

```text
accounts/
â”œâ”€â”€ managers.py
â””â”€â”€ models/
    â””â”€â”€ user.py
```

Manager handles:

```text
create_user
create_superuser
```

AuthenticationService handles actual application registration.

---

# Chapter 93 â€” BaseModel

## 954. BaseModel Location

```text
core/models/base.py
```

Contains:

```text
public_id
created_at
updated_at
```

Potential future common field:

```text
metadata
```

should only be added if actually needed.

Do not turn BaseModel into a dumping ground.

---

# Chapter 94 â€” Model Imports

## 955. `models/__init__.py`

Because models are split across files, import them explicitly.

Conceptually:

```text
User
UserSession
```

inside accounts.

Finance exposes:

```text
Customer
FinanceAccount
FinanceOpeningBalance
CollectionSchedule
Collection
CollectionAllocation
CollectionAttempt
FinanceAdjustment
Expense
```

Django must discover the models properly.

---

# Chapter 95 â€” API Response Architecture

## 956. Success Responses

Keep API output predictable.

Example:

```json
{
  "success": true,
  "message": "Customer created successfully.",
  "data": {
    "public_id": "...",
    "customer_code": "CUS-000001",
    "full_name": "Ramesh"
  }
}
```

---

# 957. Paginated Response

Recommended:

```json
{
  "success": true,
  "message": "Customers fetched successfully.",
  "data": {
    "count": 120,
    "next": "...",
    "previous": null,
    "results": []
  }
}
```

---

# 958. Error Response

```json
{
  "success": false,
  "code": "INVALID_COLLECTION_AMOUNT",
  "message": "Unable to record collection.",
  "errors": {
    "amount": [
      "Amount must be greater than zero."
    ]
  }
}
```

Frontend gets one predictable contract.

---

# Chapter 96 â€” Global Exception Handling

## 959. Why Global Handling

Without a global handler, different endpoints often return:

```text
{"detail": "..."}
{"error": "..."}
{"message": "..."}
{"amount": ["..."]}
```

which makes frontend handling unnecessarily difficult.

Normalize them.

---

# 960. Exception Flow

```text
Service
   â†“
raises BusinessException
   â†“
View / DRF
   â†“
custom_exception_handler
   â†“
Standard Error Response
```

---

# 961. Validation Errors

Serializer validation should also be transformed into the common response shape.

Example:

```json
{
  "success": false,
  "code": "VALIDATION_ERROR",
  "message": "Please correct the highlighted fields.",
  "errors": {
    "mobile_number": [
      "Enter a valid mobile number."
    ]
  }
}
```

---

# Chapter 97 â€” Pagination

## 962. Default Pagination

Recommended starting point:

```text
page_size = 20
```

Optional:

```text
?page=2
&page_size=50
```

Set a maximum such as:

```text
100
```

to prevent requests like:

```text
?page_size=1000000
```

---

# 963. Services and Pagination

Following your architecture:

```text
View
 â†“
validates pagination/filter parameters
 â†“
Service
 â†“
returns scoped QuerySet
 â†“
View/DRF paginator
 â†“
serializer
```

Pagination itself can remain an API-layer concern.

---

# Chapter 98 â€” Search & Filtering

## 964. Customer Search

Support:

```text
?search=ramesh
```

Service searches:

```text
full_name
mobile_number
customer_code
```

---

# 965. Finance Filters

Possible:

```text
?status=active

?customer=<uuid>

?frequency=weekly

?created_from=...

?created_to=...
```

---

# 966. Collection Filters

```text
?date_from=

?date_to=

?customer=

?finance_account=

?payment_mode=

?search=
```

---

# 967. Expense Filters

```text
?date_from=

?date_to=

?category=

?payment_mode=
```

---

# Chapter 99 â€” JWT Configuration

## 968. Token Strategy

Recommended initial configuration:

```text
Access Token:
15â€“30 minutes

Refresh Token:
7â€“30 days
```

Use refresh-token rotation if practical.

---

# 969. Token Payload

Keep JWT claims minimal.

Potential claims:

```text
user_id
token_type
exp
jti
```

Do not stuff:

```text
customer lists
workspace settings
permissions for every object
```

inside tokens.

Those values can change before the token expires.

---

# 970. Workspace in JWT?

For Guest V1, you don't actually need to trust a workspace ID from JWT.

You can resolve:

```text
request.user
     â†“
active membership
     â†“
workspace
```

This is safer and keeps authorization centralized.

---

# Chapter 100 â€” Authentication Endpoints

## 971. Register

```text
POST /api/v1/auth/register/
```

Request:

```json
{
  "full_name": "Ramesh Kumar",
  "mobile_number": "9876543210",
  "password": "********"
}
```

Backend:

```text
Normalize number
 â†“
Create User
 â†“
Create Guest Workspace
 â†“
Create Membership
 â†“
Create Settings
 â†“
Generate JWT
```

---

# 972. Login

```text
POST /api/v1/auth/login/
```

Request:

```json
{
  "mobile_number": "9876543210",
  "password": "********"
}
```

Response conceptually:

```json
{
  "success": true,
  "data": {
    "access": "...",
    "refresh": "...",
    "user": {},
    "workspace": {}
  }
}
```

---

# 973. Refresh

```text
POST /api/v1/auth/refresh/
```

Returns new access credentials according to the selected rotation policy.

---

# 974. Me

```text
GET /api/v1/auth/me/
```

Returns:

```text
User

Workspace

Membership

Settings

Feature access
```

This should be the frontend's primary authentication initialization endpoint.

---

# Chapter 101 â€” Frontend Authentication Flow

## 975. Application Start

Frontend:

```text
Application Loads
      â†“
Access Token Available?
      â”‚
      â”œâ”€â”€ NO â†’ Login
      â”‚
      â””â”€â”€ YES
             â†“
         GET /auth/me/
             â†“
         Valid?
          â”‚
          â”œâ”€â”€ YES â†’ Dashboard
          â”‚
          â””â”€â”€ 401
                â†“
           Try Refresh
                â†“
           Retry /auth/me/
```

---

# 976. Expired Access Token

Frontend API client can:

```text
API Request
    â†“
401
    â†“
Refresh Token
    â†“
New Access Token
    â†“
Retry Original Request
```

Avoid multiple simultaneous refresh calls when several requests receive 401 together.

Use a refresh-lock/queue strategy in the frontend.

---

# Chapter 102 â€” First Registration Transaction

## 977. What Happens in PostgreSQL

When Vinay registers, conceptually:

### `accounts_user`

```text
id             1
public_id      UUID
full_name      Vinay
mobile         ...
status         active
```

### `core_workspace`

```text
id             1
name           Vinay's Workspace
type           guest
owner_id       1
status         active
```

### `workspace_membership`

```text
workspace_id   1
user_id        1
role           owner
status         active
```

### `workspace_settings`

```text
workspace_id   1
currency       INR
timezone       Asia/Kolkata
partial        true
advance        true
```

The user can now begin using the free Guest Workspace.

---

# Chapter 103 â€” Customer API Implementation

## 978. Create Customer

```text
POST /api/v1/customers/
```

Minimum:

```json
{
  "full_name": "Ramesh"
}
```

Better:

```json
{
  "full_name": "Ramesh",
  "mobile_number": "9876543210",
  "address_line": "Main Road"
}
```

---

# 979. Request Flow

```text
CustomerListCreateView
        â†“
CustomerCreateSerializer
        â†“
WorkspaceService.get_user_workspace()
        â†“
CustomerService.create_customer()
        â†“
SequenceService.generate_customer_code()
        â†“
Customer.objects.create()
        â†“
AuditService
        â†“
CustomerDetailSerializer
        â†“
201
```

---

# 980. Customer List

```text
GET /api/v1/customers/
```

Service query begins:

```text
Customer.objects.filter(
    workspace=workspace
)
```

Then applies:

```text
search
status
ordering
```

Never:

```text
Customer.objects.all()
```

for normal workspace APIs.

---

# Chapter 104 â€” Finance Preview Implementation

## 981. Preview Endpoint

Before creating finance:

```text
POST /api/v1/finance-accounts/preview/
```

Example:

```json
{
  "principal_amount": "10000.00",
  "interest_type": "flat_percentage",
  "interest_rate": "20.00",
  "collection_frequency": "daily",
  "tenure_count": 35,
  "first_due_date": "2026-07-24"
}
```

---

# 982. Backend Calculation

```text
Principal
â‚¹10,000
   â†“
20%
   â†“
Interest
â‚¹2,000
   â†“
Total
â‚¹12,000
   â†“
35 installments
```

Returns:

```text
Total Payable
Interest
Installment Approximation
Expected End Date
Full Schedule
```

Nothing is saved.

---

# 983. Why Preview API Matters

The frontend should not independently decide financial calculations.

Otherwise you could eventually have:

```text
React calculation = â‚¹11,999.99

Backend calculation = â‚¹12,000

Database = something else
```

One authoritative calculation engine prevents this.

---

# Chapter 105 â€” Finance Creation

## 984. Confirm

After preview, user clicks:

```text
Create Finance
```

Frontend submits original terms.

Do **not** trust the preview totals sent back from frontend.

Backend recalculates everything.

---

# 985. Transaction

```text
BEGIN

Lock/generate sequence
      â†“
FIN-000001
      â†“
Create FinanceAccount
      â†“
Create 35 schedules
      â†“
Audit

COMMIT
```

If schedule creation fails:

```text
ROLLBACK
```

No half-created finance remains.

---

# Chapter 106 â€” Existing Finance API

## 986. Endpoint

```text
POST /api/v1/finance-accounts/existing/
```

Example:

```json
{
  "customer": "...",

  "principal_amount": "10000.00",

  "interest_type": "flat_percentage",

  "interest_rate": "20",

  "collection_frequency": "weekly",

  "tenure_count": 20,

  "start_date": "2026-04-01",

  "paid_till_date": "7200.00",

  "next_collection_date": "2026-07-27"
}
```

Backend determines remaining obligation.

---

# 987. Important UX Improvement

For existing finance, support **two entry modes**.

### Calculate From Terms

User provides:

```text
Principal
Interest
Tenure
Paid Till Date
```

Backend calculates outstanding.

### Enter Known Current Balance

Some lenders may only know:

```text
Original Taken â‚¹10,000
Current Pending â‚¹4,800
Weekly Amount â‚¹600
```

They may not have perfect historical details.

A migration tool should not prevent them from adopting the platform merely because old paper records are incomplete.

Mark such accounts appropriately, for example:

```text
opening_data_quality = estimated
```

versus:

```text
opening_data_quality = verified
```

This is a useful addition to the V1 design.

---

# Chapter 107 â€” Collection API Implementation

## 988. Endpoint

```text
POST /api/v1/collections/
```

Example:

```json
{
  "finance_account": "...",
  "amount": "500.00",
  "payment_mode": "cash",
  "collection_date": "2026-07-23",
  "idempotency_key": "UUID"
}
```

---

# 989. Transaction Flow

```text
Request
 â†“
Serializer
 â†“
Resolve Workspace
 â†“
CollectionService
 â†“
BEGIN
 â†“
SELECT FinanceAccount FOR UPDATE
 â†“
Validate Outstanding
 â†“
SELECT schedules FOR UPDATE
 â†“
Create Collection
 â†“
Create Allocations
 â†“
Update Schedules
 â†“
Update Account
 â†“
Audit
 â†“
COMMIT
```

This is the central financial write operation.

---

# Chapter 108 â€” Daily Register Implementation

## 990. Endpoint

```text
GET /api/v1/collection-register/today/
```

or:

```text
GET /api/v1/collection-register/?date=2026-07-23
```

I prefer supporting both through one resource:

```text
GET /api/v1/collection-register/
```

with default:

```text
date = today
```

This avoids creating a special endpoint solely for today.

---

# 991. Register Summary

Return:

```json
{
  "date": "2026-07-23",
  "summary": {
    "customers_due": 32,
    "expected_today": "16000.00",
    "previous_pending": "3500.00",
    "collected_today": "14200.00",
    "remaining_due": "5300.00",
    "expenses": "800.00",
    "net_collection": "13400.00"
  },
  "customers": []
}
```

---

# 992. Customer Row

Conceptually:

```json
{
  "customer": {
    "public_id": "...",
    "customer_code": "CUS-000023",
    "full_name": "Ramesh",
    "mobile_number": "..."
  },
  "finance_account": {
    "public_id": "...",
    "account_number": "FIN-000031"
  },
  "expected_today": "500.00",
  "previous_pending": "200.00",
  "total_due": "700.00",
  "paid_today": "300.00",
  "remaining_due": "400.00",
  "account_outstanding": "5600.00",
  "status": "partial"
}
```

This gives the frontend almost everything it needs for the digital collection card without making several API calls per customer.

---

# Chapter 109 â€” Database Query Optimization

## 993. Avoid This

Daily register:

```text
Fetch 50 accounts
      â†“
For each:
   Query customer
   Query schedules
   Query collections
   Query attempts
```

That could become hundreds of queries.

---

# 994. Prefer

Use:

```text
select_related()
prefetch_related()
annotate()
Sum()
Case()
When()
Q()
```

to construct an efficient service query.

Target:

```text
few well-designed SQL queries
```

rather than one query per card.

---

# Chapter 110 â€” Test Structure

## 995. Tests by Domain

Recommended:

```text
tests/
â”‚
â”œâ”€â”€ accounts/
â”‚   â”œâ”€â”€ test_registration.py
â”‚   â”œâ”€â”€ test_login.py
â”‚   â””â”€â”€ test_workspace_creation.py
â”‚
â”œâ”€â”€ customers/
â”‚   â”œâ”€â”€ test_customer_service.py
â”‚   â””â”€â”€ test_customer_api.py
â”‚
â”œâ”€â”€ finance/
â”‚   â”œâ”€â”€ test_calculations.py
â”‚   â”œâ”€â”€ test_schedule.py
â”‚   â”œâ”€â”€ test_finance_creation.py
â”‚   â””â”€â”€ test_existing_finance.py
â”‚
â”œâ”€â”€ collections/
â”‚   â”œâ”€â”€ test_full_payment.py
â”‚   â”œâ”€â”€ test_partial_payment.py
â”‚   â”œâ”€â”€ test_advance_payment.py
â”‚   â”œâ”€â”€ test_reversal.py
â”‚   â”œâ”€â”€ test_idempotency.py
â”‚   â””â”€â”€ test_concurrency.py
â”‚
â””â”€â”€ security/
    â”œâ”€â”€ test_workspace_isolation.py
    â””â”€â”€ test_permissions.py
```

---

# 996. Most Important Tests

Before production, these should absolutely pass:

```text
â‚¹500 outstanding + â‚¹500 collection
â†’ outstanding â‚¹0

â‚¹500 outstanding + â‚¹600 collection
â†’ rejected

â‚¹500 due + â‚¹200 collection
â†’ â‚¹300 remaining

â‚¹500 due + â‚¹1000 collection
â†’ future schedules allocated if allowed

Duplicate idempotency key
â†’ no duplicate collection

Reversal
â†’ exact balance restored

Workspace A customer requested by Workspace B
â†’ inaccessible

Two concurrent final collections
â†’ only valid amount accepted
```

---

# Chapter 111 â€” Development Milestones

## 997. Milestone A â€” Foundation

Implement:

```text
Project setup
PostgreSQL
Settings
Custom User
BaseModel
Exceptions
JWT
CORS
OpenAPI
```

Then stop and test.

---

# 998. Milestone B â€” Registration

Implement:

```text
Workspace
Membership
Settings
Sequence

AuthenticationService

Register
Login
Refresh
Logout
Me
```

At this point you have a functioning SaaS account foundation.

---

# 999. Milestone C â€” Customer Book

Implement:

```text
Customer Model
Customer Serializers
CustomerService
Customer Views
Customer URLs
Customer Tests
```

At this point users can build their digital customer book.

---

# 1000. Milestone D â€” Finance Engine

Implement:

```text
FinanceCalculationService
Schedule calculations
Finance preview
Finance Account
Opening Balance
Existing Finance
```

This is where the application becomes finance-specific.

---

# 1001. Milestone E â€” Collection Engine

Implement:

```text
Collection
Allocation
Partial payment
Advance payment
Reversal
Non-payment attempts
Idempotency
Transactions
Concurrency protection
```

This is the most critical backend milestone.

---

# 1002. Milestone F â€” Digital Collection Card

Implement:

```text
Collection Register
Today's customers
Quick collection
Not paid
Promise date
Daily totals
```

At this stage, **the core V1 product is usable**.

---

# 1003. Milestone G â€” Business Records

Implement:

```text
Expenses
Dashboard
Statements
Outstanding
Overdue
Reports
```

---

# 1004. Milestone H â€” Migration & Export

Implement:

```text
Excel import
Import preview
Row validation
Import execution

Excel export
Customer export
Collection export
Outstanding export
```

Now existing lenders can migrate larger books.

---

# 1005. Milestone I â€” Production Hardening

Implement:

```text
Rate limiting

Security review

Query optimization

Database indexes

Audit review

File upload restrictions

Backup configuration

Logging

Error monitoring

API documentation

Load testing
```

Then deploy V1.

---

# Chapter 112 â€” What NOT to Build Before V1

## 1006. Avoid Scope Expansion

Do not delay Guest Workspace because of:

```text
Collector App

Employee Salary

Area Assignment

Google Maps Routes

Real-Time WebSockets

Redis

Celery

SMS

WhatsApp

Payment Gateway

Complex Subscription Billing

Advanced Admin Analytics

Mobile App

AI Features
```

Those features may be valuable, but they do not validate your first hypothesis.

The V1 hypothesis is much simpler:

> **Will local lenders use a simple digital collection book instead of paper/manual records?**

That is what Guest Workspace should prove.

---

# Chapter 113 â€” V1 Product Flow

## 1007. Final User Journey

The complete first-release journey becomes:

```text
LANDING PAGE
      â†“
Try Free Digital Collection Book
      â†“
REGISTER
      â†“
GUEST WORKSPACE CREATED
      â†“
ADD CUSTOMER
      â”‚
      â”œâ”€â”€ New Finance
      â”‚
      â””â”€â”€ Existing Finance
               â†“
       Enter Existing Position
               â†“
        Current Balance Created
               â†“
DAILY COLLECTION REGISTER
      â†“
Ramesh      â‚¹500
Suresh      â‚¹350
Mahesh      â‚¹700
      â†“
Select Customer
      â”‚
      â”œâ”€â”€ Paid
      â”‚     â†“
      â”‚   Enter Amount
      â”‚     â†“
      â”‚   Payment Mode
      â”‚
      â””â”€â”€ Not Paid
            â†“
          Reason
            â†“
       Promise Date
      â†“
END OF DAY
      â†“
Collections
â‚¹18,500
      â†“
Expenses
â‚¹1,200
      â†“
Net Collection
â‚¹17,300
      â†“
REPORTS
      â†“
Customer / Finance History
```

That is a clear, focused product.

---

# Chapter 114 â€” V2 Upgrade Path

Once Guest users trust the application, the natural conversion becomes:

```text
Guest Workspace
       â†“
"Manage your complete finance business"
       â†“
Upgrade Workspace
       â†“
Business Workspace
       â†“
Create Areas
       â†“
Add Employees
       â†“
Assign Collectors
       â†“
Capture Customer GPS
       â†“
Create Collection Routes
       â†“
Collector Login
       â†“
Field Collections
       â†“
Expenses
       â†“
Cash Handover
       â†“
Salary
       â†“
Owner Analytics
       â†“
SMS / WhatsApp Add-ons
```

Most importantly, **the user does not create a new business or migrate their V1 data**.

Their existing:

```text
Customers
Finance Accounts
Schedules
Collections
Expenses
History
```

remain in the same workspace.

Only:

```text
workspace_type
plan
features
```

and additional business configuration expand.

This makes the Guest Workspace more than a demoâ€”it becomes the entry point into the complete finance-management platform.

---

# Chapter 115 â€” Backend PRD Status

At this point we have covered the backend from **product concept all the way down to implementation sequencing**:

```text
Business requirements
        â†“
Roles
        â†“
V1 / V2
        â†“
Guest Workspace
        â†“
Django Apps
        â†“
5-Layer Architecture
        â†“
PostgreSQL Data Model
        â†“
Models & Relationships
        â†“
Financial Engine
        â†“
Schedules
        â†“
Existing Finance
        â†“
Collections
        â†“
Allocation
        â†“
Expenses
        â†“
Non-Payments
        â†“
Services
        â†“
Serializers
        â†“
Views
        â†“
URLs
        â†“
Authentication
        â†“
Authorization
        â†“
Transactions
        â†“
Concurrency
        â†“
Audit
        â†“
Reports
        â†“
Import / Export
        â†“
Security
        â†“
Testing
        â†“
Deployment Architecture
        â†“
Implementation Milestones
```

The specification is now beyond the point where more architecture chapters would add much value. **The next step should be actual code**, beginning with `config`, `accounts`, `core`, PostgreSQL settings, the custom `User`, `BaseModel`, `Workspace`, `WorkspaceMembership`, and `AuthenticationService`, then building each V1 module in the milestone order above.


---

# Chapter 48 — Coupon & Discount Management Specification

## 950. Coupon Model
```python
class Coupon(BaseModel):
    class DiscountType(models.TextChoices):
        PERCENTAGE = "PERCENTAGE", "Percentage"
        FIXED_AMOUNT = "FIXED_AMOUNT", "Fixed Amount"

    code = models.CharField(max_length=30, unique=True, db_index=True)
    description = models.CharField(max_length=255, blank=True)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices, default=DiscountType.PERCENTAGE)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2) # e.g. 20.00 for 20% or flat 500.00
    max_redemptions = models.PositiveIntegerField(null=True, blank=True)
    redemptions_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True, db_index=True)

class CouponRedemption(BaseModel):
    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT, related_name="redemptions")
    workspace = models.ForeignKey("workspace.Workspace", on_delete=models.CASCADE, related_name="coupon_redemptions")
    applied_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2)
    redeemed_at = models.DateTimeField(auto_now_add=True)
```

## 951. CouponService Business Rules
- `validate_coupon(code, workspace)`: Checks active state, valid date windows, redemption limits, and returns calculated discount amount.
- `apply_coupon(code, workspace, total_amount)`: Atomically increments `redemptions_count`, creates a `CouponRedemption` record, and returns net billable amount.

## 952. Coupon API Endpoints
- `POST /api/v1/admin/coupons/` — Create new promo code (Super Admin only).
- `GET /api/v1/admin/coupons/` — List all active and expired promo codes.
- `POST /api/v1/subscriptions/apply-coupon/` — Validate and apply coupon code during subscription checkout.

---

# Chapter 49 — Platform System Health & Telemetry

## 953. HealthCheckService Strategy
Provides deep platform operational diagnostics for Super Admin console (`/admin/system-health`).

```python
class HealthCheckService:
    @staticmethod
    def get_system_health() -> dict:
        # 1. Check PostgreSQL Database connection
        # 2. Ping Redis cache connection
        # 3. Inspect Celery worker active status via ping
        # 4. Check API response time metric (p95 latency)
        return {
            "database": {"status": "HEALTHY", "latency_ms": 1.2},
            "redis": {"status": "HEALTHY", "latency_ms": 0.5},
            "celery": {"status": "HEALTHY", "active_workers": 4},
            "system_uptime": "99.98%",
            "overall_status": "OK"
        }
```

## 954. System Health Endpoints
- `GET /api/v1/admin/system-health/` — Returns real-time health telemetry status (Super Admin only).

---

# Chapter 50 — PWA Offline Synchronization Engine

## 955. OfflineSyncService Architecture
Handles batch synchronization of collection transactions queued on field devices during offline operations (`/field/offline`).

```python
class OfflineSyncService:
    @staticmethod
    def process_batch_sync(collector_user, sync_payload: list) -> dict:
        """
        sync_payload format:
        [
          {
            "client_tx_id": "uuid-v4",
            "customer_id": "uuid",
            "loan_account_id": "uuid",
            "amount": "250.00",
            "payment_mode": "CASH",
            "captured_at": "ISO-TIMESTAMP",
            "latitude": 12.9716,
            "longitude": 77.5946
          }
        ]
        """
        processed = []
        conflicts = []
        
        for item in sync_payload:
            # 1. Idempotency Check using client_tx_id
            if Collection.objects.filter(client_tx_id=item['client_tx_id']).exists():
                processed.append({"client_tx_id": item['client_tx_id'], "status": "ALREADY_PROCESSED"})
                continue
            
            # 2. Record Collection atomically inside transaction.atomic()
            # 3. If loan is already closed or disputed, flag for conflict review
            try:
                col = CollectionService.record_collection(collector=collector_user, **item)
                processed.append({"client_tx_id": item['client_tx_id'], "server_id": str(col.id), "status": "SUCCESS"})
            except Exception as e:
                conflicts.append({"client_tx_id": item['client_tx_id'], "error": str(e), "status": "FLAGGED_FOR_REVIEW"})
                
        return {"processed_count": len(processed), "processed": processed, "conflicts": conflicts}
```

## 956. Offline Sync Endpoints
- `POST /api/v1/field/sync/` — Submit queued offline collection transactions (Field Collector PWA).

---

# Chapter 51 — Collector Performance & Gamification

## 957. CollectorPerformanceService
Computes collector metrics for `/field/performance` surface.

```python
class CollectorPerformanceService:
    @staticmethod
    def get_collector_kpis(collector_user, date=None) -> dict:
        # Calculates:
        # 1. Today's target collection amount vs actual collected
        # 2. On-time collection percentage (%)
        # 3. Collection streak (consecutive days target met)
        # 4. Branch leaderboard rank
        return {
            "target_amount": 15000.00,
            "collected_amount": 14200.00,
            "completion_percentage": 94.67,
            "current_streak_days": 12,
            "branch_rank": 2,
            "total_collectors_in_branch": 8
        }
```

## 958. Performance Endpoints
- `GET /api/v1/field/performance/` — Retrieve individual field agent KPIs, streaks, and branch rankings.

---

# Chapter 52 — Public Marketing & Support Desk

## 959. Public Marketing & Contact Models
```python
class ContactInquiry(BaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    business_name = models.CharField(max_length=150, blank=True)
    message = models.TextField()
    is_processed = models.BooleanField(default=False)

class SupportTicket(BaseModel):
    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        URGENT = "URGENT", "Urgent"

    ticket_number = models.CharField(max_length=30, unique=True)
    workspace = models.ForeignKey("workspace.Workspace", on_delete=models.CASCADE, related_name="support_tickets")
    created_by = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, default="OPEN")

class SupportTicketMessage(BaseModel):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    message = models.TextField()
    attachment = models.FileField(upload_to="support_attachments/", null=True, blank=True)
```

## 960. Public & Support API Endpoints
- `POST /api/v1/public/contact/` — Submit inquiry from public marketing landing page.
- `GET /api/v1/public/faqs/` — List categorized public FAQs.
- `GET /api/v1/public/addons/` — Fetch available SaaS add-on package catalog.
- `POST /api/v1/field/help/tickets/` — Submit support ticket from Field PWA or ERP workspace.
- `GET /api/v1/erp/support/tickets/` — List support ticket history.

---

# Chapter 53 — User Consent & Legal Compliance Specification

## 961. ConsentService Architecture
Manages legal consent records and compliance verification across all authentication and onboarding surfaces.

```python
class ConsentService:
    @staticmethod
    def record_consent(user, consent_type: str, version: str, ip_address: str = None, user_agent: str = "", metadata: dict = None) -> UserConsent:
        """
        Appends an immutable consent entry for the user.
        """
        return UserConsent.objects.create(
            user=user,
            consent_type=consent_type,
            version=version,
            is_agreed=True,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {}
        )

    @staticmethod
    def has_accepted_latest(user, consent_type: str, latest_version: str) -> bool:
        """
        Verifies if the user has accepted the latest version of a specific legal policy.
        """
        return UserConsent.objects.filter(
            user=user,
            consent_type=consent_type,
            version=latest_version,
            is_agreed=True
        ).exists()

    @staticmethod
    def get_consent_history(user) -> QuerySet:
        """
        Returns full audit trail of all consents accepted by the user.
        """
        return UserConsent.objects.filter(user=user).order_by("-accepted_at")
```

## 962. User Consent Endpoints
- `POST /api/v1/auth/consent/` — Explicitly submit policy/terms acceptance (includes client IP & User-Agent).
- `GET /api/v1/auth/consent/history/` — Retrieve user's historical consent audit trail.

---

# Chapter 54 — Workspace Quota Override Specification

## 963. WorkspaceQuotaOverride Model
Stores per-workspace custom limit overrides configured by Super Admin.

```python
class WorkspaceQuotaOverride(BaseModel):
    workspace = models.OneToOneField(
        "workspace.Workspace",
        on_delete=models.CASCADE,
        related_name="quota_override"
    )
    custom_max_collection_days_per_week = models.PositiveIntegerField(null=True, blank=True)
    custom_max_customers_per_week = models.PositiveIntegerField(null=True, blank=True)
    override_reason = models.CharField(max_length=255, blank=True) # e.g. "Promotional trial grant"
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="granted_quota_overrides"
    )
    expires_at = models.DateTimeField(null=True, blank=True)

    def is_valid(self) -> bool:
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True
```

---

# Chapter 55 — Field PWA Synchronization & EOD Cash Reconciliation Extensions

## 964. PWA Offline Batch Synchronization Engine
To support field agents operating in low-connectivity areas (as seen in `/field/offline`), the backend implements a resilient batch synchronization pipeline.

### Offline Queue Lifecycle & Contracts
1. **Frontend Queueing**: When offline, the PWA stores collection logs in local IndexedDB with a generated client UUID (`offline_id`) and device timestamp.
2. **Batch Payload Dispatch**: When connectivity is restored, the PWA dispatches `POST /api/v1/field/sync/` containing up to 100 queued items.
3. **Idempotent Processing**: The server checks `offline_id` against `Collection.offline_id` index:
   - If `offline_id` exists: Returns existing server collection ID without duplicating payment.
   - If new: Creates collection entry, updates `FinanceAccount.paid_amount` and `outstanding_amount`, and records `gps_latitude`/`gps_longitude`.
4. **Server ACK**: Server returns confirmation map containing `{ offline_id, server_collection_id, status }`, allowing client IndexedDB items to be cleared.

## 965. EOD Cash Reconciliation State Machine
Manages end-of-day cash drawer handovers between collectors and branch managers (aligning `/field/handover` with `/erp/reconciliation`).

```
[Collector Handover] ──► PENDING_VERIFICATION
                                │
               ┌────────────────┴────────────────┐
               ▼                                 ▼
      [Manager Verifies Cash]          [Variance Discrepancy]
               │                                 │
               ▼                                 ▼
           VERIFIED                     DISCREPANCY_FLAGGED
               │                                 │
               └────────────────┬────────────────┘
                                ▼
                       RECONCILED_AND_LOCKED
```

### State Definitions
- `PENDING_VERIFICATION`: Field agent has submitted shift total (`submitted_cash`).
- `VERIFIED`: Branch manager counted cash and confirmed match with system expected total.
- `DISCREPANCY_FLAGGED`: Variance detected between system total and physical cash drawer; requires discrepancy reason category (`fuel_expense_offset`, `unrecorded_expense`, `cash_shortage`, `cash_excess`) and manager note.
- `RECONCILED_AND_LOCKED`: Cash ledger entry finalized. Collection records for the shift become immutable.





