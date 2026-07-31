# External APIs and Credentials Plan

This document lists the external services, credentials, and integration points expected in the Finance ERP backend. It also explains where each service is intended to be used and how it will be used in the system, including frontend-backend gap resolutions.

## 1. Authentication and Security Credentials

| Service / Credential | Required Values | Where It Is Used | How It Is Used |
|---|---|---|---|
| Django Secret Key | DJANGO_SECRET_KEY | Global backend configuration | Used to sign session data, CSRF protection, and secure application state. |
| JWT Authentication | JWT_SIGNING_KEY, JWT_ACCESS_TOKEN_LIFETIME, JWT_REFRESH_TOKEN_LIFETIME | Accounts app | Used for user login, token issuance, token refresh, and protected API access. |
| OAuth 2.0 Social Auth | GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET | Accounts app (`/api/v1/accounts/oauth/`) | Supports social login options displayed on frontend (`login.tsx`), exchanging OAuth tokens for JWT access tokens. |
| Database Credentials | DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT | All apps | Used to connect the backend to PostgreSQL for customer, loan, collection, workspace, and ERP data. |
| Debug / Environment Flags | DEBUG | Global settings | Used to control local development behavior and logging. |

## 2. Communication and Notification Services

| Service / Credential | Required Values | Where It Is Used | How It Is Used |
|---|---|---|---|
| Email Service | EMAIL_BACKEND, EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, DEFAULT_FROM_EMAIL | Accounts, guest_workspace, integrations | Used for OTP delivery, registration emails, password resets, reminders, and business alerts. |
| SMS Gateway | SMS_PROVIDER, SMS_API_KEY, SMS_SENDER_ID, SMS_BASE_URL | Accounts, guest_workspace, finance | Planned for OTP verification, collection reminders, payment reminders, and customer notifications. |
| WhatsApp Business API | WHATSAPP_PROVIDER, WHATSAPP_API_KEY, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN | Guest workspace, finance, integrations | Planned for sending reminders, alerts, payment updates, and business notifications to customers or employees. |

### 2.1 Webhook & Callback Interfaces (Placeholder Specs)
- **WhatsApp Webhook Endpoint**: `POST /api/v1/integrations/webhooks/whatsapp/`
  - Payload: `{ "event": "message_status", "message_id": "...", "status": "delivered|read", "recipient": "+91..." }`
- **SMS Status Webhook Endpoint**: `POST /api/v1/integrations/webhooks/sms/`
  - Payload: `{ "sms_id": "...", "status": "DELIVRD", "delivered_at": "ISO-8601" }`

## 3. Maps and Location Services

| Service / Credential | Required Values | Where It Is Used | How It Is Used |
|---|---|---|---|
| Google Maps API | GOOGLE_MAPS_API_KEY, GOOGLE_MAPS_ENABLED | Finance, integrations, guest_workspace | Used for customer address lookup, geocoding, map directions, route optimization, and location-based collections (`gps_latitude`, `gps_longitude`). |

## 4. File Storage and Media Services

| Service / Credential | Required Values | Where It Is Used | How It Is Used |
|---|---|---|---|
| AWS S3 / Object Storage | AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME | Guest workspace, finance, integrations | Used to store receipts, customer documents, profile photos, logos, and business attachments. |

## 5. Payment and Subscription Services

| Service / Credential | Required Values | Where It Is Used | How It Is Used |
|---|---|---|---|
| Payment Provider | PAYMENT_PROVIDER, PAYMENT_API_KEY, PAYMENT_WEBHOOK_SECRET | Subscriptions, billing | Planned for plan purchases, subscription activation, renewal handling, invoices, and webhook verification. |
| Dynamic UPI QR Code Engine | MERCHANT_UPI_VPA, MERCHANT_NAME | Payments, invoices, subscriptions | Generates dynamic UPI payload string `upi://pay?pa={VPA}&pn={NAME}&am={AMOUNT}&tr={REF_ID}&cu=INR` rendered as a QR code on invoices and billing screens. |

## 6. Background Jobs and Cache Services

| Service / Credential | Required Values | Where It Is Used | How It Is Used |
|---|---|---|---|
| Redis | REDIS_URL | Cache layer, sessions, queues | Used for caching, session storage, rate limiting, and fast access to frequently used data. |
| Celery | CELERY_BROKER_URL, CELERY_RESULT_BACKEND | Background tasks | Used for async tasks such as report generation, notification dispatch, syncing, and scheduled jobs. |

## 7. OTP and Security Controls

| Service / Credential | Required Values | Where It Is Used | How It Is Used |
|---|---|---|---|
| OTP Configuration | OTP_TTL_MINUTES, OTP_MAX_ATTEMPTS, OTP_RATE_LIMIT | Accounts, guest_workspace | Used for initial account verification through OTP. After verification, regular access uses the password-based login flow. |

## 8. Summary of Integration Purpose

The system is expected to integrate with:
- Authentication and account security (including JWT & Social OAuth)
- SMS and email communication
- WhatsApp notifications
- Google Maps for route and address operations
- Cloud object storage for documents and media
- Dynamic UPI QR Code payment engine & automated payment gateways
- Redis and Celery for performance and background processing

These integrations support the transition from the Guest Workspace to the full Finance ERP without changing the core backend architecture.

## 9. Implementation Checklist

Use this checklist to track what is already available, what is planned, and what still needs to be implemented.

- [ ] Django secret key configured
- [ ] JWT signing key configured
- [ ] Google & Microsoft OAuth Social Auth keys configured
- [ ] PostgreSQL database credentials configured
- [ ] Email service configured for OTP and notifications
- [ ] SMS gateway configured (placeholder endpoints defined)
- [ ] WhatsApp Business API configured (placeholder endpoints defined)
- [ ] Google Maps API key configured
- [ ] AWS S3 / object storage configured
- [ ] Dynamic UPI QR code generator prepared for invoice payment screens
- [ ] Payment gateway configured for enterprise subscriptions
- [ ] Redis configured for cache/session support
- [ ] Celery configured for background jobs
- [ ] OTP settings configured for expiry and retry limits
- [ ] System Health & Telemetry diagnostics endpoint verified
- [ ] PWA Offline Batch Synchronization engine and conflict resolution tested
- [ ] Promo Coupon validation and redemption tracking verified
- [ ] Environment variables documented for development and production
- [ ] Integration testing completed for each enabled service
- [ ] Production credentials secured and stored safely
