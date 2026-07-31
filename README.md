# FinRoute Backend — Django REST API Engine

FinRoute Backend is a high-performance Python / Django REST Framework API engine powering daily money lending businesses, microfinance operators, field collection agents, and enterprise finance management.

---

## 🌟 Key Architecture & Modules

### 1. `apps/accounts` (Authentication & Security)
- **Custom User Model**: Mobile number primary authentication with OTP verification.
- **Role-Based Access Control**: Supports `guest` (lenders), `admin` (super admins), `field_agent`, and `branch_manager`.
- **JWT Security**: Token-based authentication using `djangorestframework-simplejwt`.
- **Management Command**: Quick creation of super admin credentials via `python manage.py create_admin`.

### 2. `apps/guest_workspace` (Single-Lender Workspace Suite)
- **Borrower & Loan Lifecycle**: Register borrowers with custom principal, interest rates, frequencies, and automated sequence numbers.
- **Collections & Batch Passbooks**: Record single or multi-borrower batch collections with receipts and status tracking (`paid`, `skipped`).
- **Atomic Route Auto-Remapping**: Allows lenders to re-configure operational collection days at any time. Automatically re-maps active borrower schedules inside a Django `@transaction.atomic` block while preserving historical receipts.
- **Plan Upgrade Requests**: Endpoint (`POST /api/v1/app/upgrade/request/`) allowing lenders to request collection day plan upgrades.

### 3. `apps/administration` (Super Admin Console APIs)
- **Platform Analytics**: Dashboard metrics, system health status, and active workspace tracking.
- **Plan Upgrade Requests Moderation**: View pending upgrade requests with 1-click **Approve & Activate** or **Reject** actions.
- **Customer Review Moderation**: Moderate landing page user reviews before public display.
- **Workspace & Quota Overrides**: Override customer limits or collection days capacity per workspace.
- **Audit Logs**: Platform-wide security and operational activity tracking.

### 4. `apps/masters` (Master Data Catalog)
- Centralized management for Business Categories, Collection Frequencies (Daily, Weekly, Monthly), Payment Modes, Expense Categories, and Public Customer Reviews.

---

## 💾 Flexible Database Support

The backend supports seamless switching between local SQLite (for fast testing/staging) and production PostgreSQL via an environment toggle:

- **Local Testing / Staging (SQLite)**: Set `USE_SQLITE=True` in `.env`.
- **Production (Cloud PostgreSQL)**: Set `USE_SQLITE=False` and supply `DATABASE_URL` or standard DB variables.

---

## 🛠️ Environment Configuration

Create a `.env` file in the root directory:

```env
# Environment Settings
DJANGO_SECRET_KEY=your-django-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
USE_SQLITE=True
DATABASE_URL=postgresql://postgres:123456@localhost:5432/Fintech
DB_NAME=Fintech
DB_USER=postgres
DB_PASSWORD=123456
DB_HOST=localhost
DB_PORT=5432

# JWT Security
JWT_ACCESS_TOKEN_LIFETIME=30
JWT_REFRESH_TOKEN_LIFETIME=7

# OTP Configuration
OTP_TTL_MINUTES=5
OTP_MAX_ATTEMPTS=5
OTP_SECRET_SALT=fintech-otp-secret-salt-key-2026
```

---

## 🚀 Setup & Execution

### 1. Install Dependencies
```bash
# Create and activate virtual environment
python -m venv venv
# On Windows: venv\Scripts\activate
# On Linux/macOS: source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Run Database Migrations
```bash
python manage.py migrate
```

### 3. Create Super Admin User
```bash
python manage.py create_admin --mobile "+919999999999" --password "Admin@123456" --name "Super Admin"
```

### 4. Start Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```

The REST API will be available at `http://localhost:8000/api/v1/`.
Interactive OpenAPI Swagger docs available at `http://localhost:8000/api/docs/`.

---

## 📄 License

This project is licensed under the MIT License.
