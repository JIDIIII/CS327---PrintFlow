# PrintFlow System Requirements

## 1. System Overview

PrintFlow is a web-based order management system for a single printing shop. It centralizes customer records, printing order details, deadlines, production status, and payment records. Its purpose is to reduce forgotten jobs, incorrect order details, missed deadlines, and difficulty prioritizing work.

The initial version is intended to be designed, implemented, and tested within one academic semester.

## 2. Objectives

PrintFlow shall:

1. Allow authorized users to register, sign in, manage their profile, and securely sign out.
2. Allow users to create, view, edit, and update customer printing orders.
3. Track each order from submission through completion or cancellation.
4. Present a dashboard summarizing current shop activity.
5. Identify orders that are due soon or overdue.
6. Record payments and show the paid amount, remaining balance, and payment status for every order.
7. Support search and filtering by customer, order status, deadline, and service type.
8. Preserve completed and cancelled orders as transaction history.
9. Produce simple order, completed-transaction, and payment summaries for a selected period.

## 3. Users and Access

### 3.1 Authorized User

An authorized user is a printing-shop owner or employee who may:

- Create an account.
- Sign in and sign out.
- View and update their own account information.
- Manage customers, orders, services, statuses, and payments.
- View dashboard information, search results, order history, and reports.

### 3.2 Access Rules

- All operational pages shall require authentication.
- Passwords shall be handled by Django's authentication system and shall never be stored as plain text.
- A user shall only be allowed to update their own profile unless administrator permissions are added later.
- Django administrator access shall be limited to staff or superuser accounts.

## 4. Functional Requirements

### FR-01: Account Registration

- The system shall allow a new authorized user to register with a first name, last name, username, email address, and password.
- The system shall reject duplicate usernames and invalid account information.
- The system shall apply Django's configured password-validation rules.

### FR-02: Authentication

- The system shall allow a registered user to sign in using valid credentials.
- The system shall reject invalid credentials without revealing sensitive account information.
- The system shall allow a signed-in user to securely sign out and end the session.

### FR-03: Profile Management

- The system shall display the signed-in user's account information.
- The user shall be able to update permitted profile information such as name and email address.

### FR-04: Customer Management

- The system shall allow a user to create, view, and update customer records.
- A customer record shall contain a name and may contain a contact number, email address, address, and notes.
- The system shall retain customer records referenced by historical orders.

### FR-05: Printing Service Management

- The system shall allow authorized users to define available printing products or services.
- A service record shall contain a unique name and may contain a description and active/inactive state.
- Inactive services shall remain visible on historical orders but shall not be selectable for new orders.

### FR-06: Order Management

- The system shall allow a user to create an order for an existing customer.
- An order shall include a unique order number, customer, printing service, size or dimensions, quantity, total price, deadline, special instructions, status, creator, and creation/update timestamps.
- The system shall allow users to view and edit an existing order.
- Order values shall be validated before they are saved.
- Quantity shall be greater than zero.
- Total price shall not be negative.
- Completed and cancelled orders shall be retained for history and reporting instead of being automatically deleted.

### FR-07: Order Status Tracking

- An order shall have exactly one current status from the following values:
  - Pending
  - In Progress
  - Ready for Pickup
  - Completed
  - Cancelled
- The system shall allow an authorized user to change an order's status.
- The system shall record each status change with the previous status, new status, user, timestamp, and optional note.

### FR-08: Deadline Monitoring

- The system shall display the deadline of each active order.
- The system shall identify an order as overdue when its deadline has passed and its status is not Completed or Cancelled.
- The system shall identify upcoming deadlines using a configurable period, with seven days as the initial default.
- Due-soon and overdue values shall be calculated from the deadline and current status rather than stored as permanent database flags.

### FR-09: Payment Tracking

- The system shall allow a user to record one or more payments for an order.
- Each payment shall include the order, amount, payment date and time, user who recorded it, and an optional note or reference.
- A payment amount shall be greater than zero.
- The total amount paid shall be the sum of valid payment records for the order.
- The remaining balance shall equal the order total minus the total amount paid, with a minimum displayed balance of zero.
- Payment status shall be derived as Unpaid, Partially Paid, or Paid.
- Online payment processing and bank or electronic-wallet integration are not required.

### FR-10: Dashboard

- The dashboard shall display:
  - Total number of orders
  - Pending orders
  - Ongoing orders
  - Completed orders
  - Overdue orders
  - Upcoming deadlines
  - Recent orders
- For the initial version, ongoing orders shall include In Progress and Ready for Pickup orders.
- Dashboard totals shall be calculated from current order data and shall not require a separate dashboard database model.

### FR-11: Search and Filtering

- The system shall allow users to search orders by customer name.
- The system shall allow users to filter orders by status, deadline or date range, and printing service.
- Search and filters shall be usable together.
- The results shall clearly show when no matching orders are found.

### FR-12: Order History

- The system shall provide a history view for completed and cancelled orders.
- Historical records shall remain searchable and filterable.

### FR-13: Reports and Summaries

- The system shall provide simple summaries for a user-selected date range.
- Summaries shall include orders created, completed transactions, total order value, payments received, and outstanding balances.
- Reports shall be generated from order and payment data; a separate report model is not required for the initial version.

## 5. Recommended Django Application Structure

The setup guide explains that `startapp` creates a self-contained module for one business feature. The guide's `students` app is an example only. For PrintFlow, run the following commands from the directory containing `manage.py`:

```bash
python3 manage.py startapp accounts
python3 manage.py startapp customers
python3 manage.py startapp orders
python3 manage.py startapp payments
python3 manage.py startapp dashboard
```

Register all five apps in `INSTALLED_APPS`. The `dashboard` app contains views, URLs, templates, and report queries but does not need its own database model for the initial version.

## 6. Required Data Models

### 6.1 Django `User` (built in)

Use Django's built-in authentication user for the initial version.

Key data:

- Username
- First name
- Last name
- Email address
- Password hash
- Active/staff status
- Date joined and last login

No separate profile model is required unless the project later needs fields not supported by the built-in user model.

### 6.2 `Customer` (`customers/models.py`)

| Field | Suggested Django type | Rules |
| --- | --- | --- |
| `name` | `CharField(max_length=150)` | Required |
| `contact_number` | `CharField(max_length=30)` | Optional |
| `email` | `EmailField()` | Optional |
| `address` | `TextField()` | Optional |
| `notes` | `TextField()` | Optional |
| `created_at` | `DateTimeField(auto_now_add=True)` | Automatic |
| `updated_at` | `DateTimeField(auto_now=True)` | Automatic |

### 6.3 `PrintService` (`orders/models.py`)

| Field | Suggested Django type | Rules |
| --- | --- | --- |
| `name` | `CharField(max_length=100, unique=True)` | Required and unique |
| `description` | `TextField()` | Optional |
| `is_active` | `BooleanField(default=True)` | Required |
| `created_at` | `DateTimeField(auto_now_add=True)` | Automatic |
| `updated_at` | `DateTimeField(auto_now=True)` | Automatic |

Examples include document printing, tarpaulin, stickers, business cards, and sublimation. These examples are configuration data, not hard-coded status choices.

### 6.4 `Order` (`orders/models.py`)

| Field | Suggested Django type | Rules |
| --- | --- | --- |
| `order_number` | `CharField(max_length=30, unique=True)` | Required and unique |
| `customer` | `ForeignKey(Customer, on_delete=PROTECT)` | Required |
| `service` | `ForeignKey(PrintService, on_delete=PROTECT)` | Required |
| `size` | `CharField(max_length=100)` | Required |
| `quantity` | `PositiveIntegerField()` | Required; greater than zero |
| `total_price` | `DecimalField(max_digits=12, decimal_places=2)` | Required; non-negative |
| `deadline` | `DateTimeField()` | Required |
| `special_instructions` | `TextField()` | Optional |
| `status` | `CharField` with `TextChoices` | Required; default Pending |
| `created_by` | `ForeignKey(User, on_delete=PROTECT)` | Required |
| `created_at` | `DateTimeField(auto_now_add=True)` | Automatic |
| `updated_at` | `DateTimeField(auto_now=True)` | Automatic |
| `completed_at` | `DateTimeField(null=True, blank=True)` | Set when completed |

The `status` choices shall be `PENDING`, `IN_PROGRESS`, `READY_FOR_PICKUP`, `COMPLETED`, and `CANCELLED` with user-friendly labels.

### 6.5 `OrderStatusHistory` (`orders/models.py`)

| Field | Suggested Django type | Rules |
| --- | --- | --- |
| `order` | `ForeignKey(Order, on_delete=CASCADE)` | Required |
| `from_status` | `CharField` using order choices | Blank only for initial entry |
| `to_status` | `CharField` using order choices | Required |
| `changed_by` | `ForeignKey(User, on_delete=PROTECT)` | Required |
| `changed_at` | `DateTimeField(auto_now_add=True)` | Automatic |
| `note` | `TextField()` | Optional |

### 6.6 `Payment` (`payments/models.py`)

| Field | Suggested Django type | Rules |
| --- | --- | --- |
| `order` | `ForeignKey(Order, on_delete=PROTECT)` | Required |
| `amount` | `DecimalField(max_digits=12, decimal_places=2)` | Required; greater than zero |
| `paid_at` | `DateTimeField()` | Required; default to current date/time |
| `recorded_by` | `ForeignKey(User, on_delete=PROTECT)` | Required |
| `reference` | `CharField(max_length=100)` | Optional manual reference |
| `note` | `TextField()` | Optional |
| `created_at` | `DateTimeField(auto_now_add=True)` | Automatic |

## 7. Model Relationships

```text
Django User 1 ---- many Order
Django User 1 ---- many OrderStatusHistory
Django User 1 ---- many Payment

Customer 1 ---- many Order
PrintService 1 ---- many Order
Order 1 ---- many OrderStatusHistory
Order 1 ---- many Payment
```

## 8. Business Rules

1. Customer, service, user, order, and payment references used by historical transactions shall be protected from accidental deletion where specified.
2. An overdue order is an order with a deadline earlier than the current time whose status is neither Completed nor Cancelled.
3. An order's amount paid is the sum of its related payment amounts.
4. An order is Unpaid when the amount paid is zero, Partially Paid when it is greater than zero but less than the total price, and Paid when it is equal to or greater than the total price.
5. Changing an order to Completed shall record its completion time. Moving it away from Completed shall clear that time unless a later audit requirement says otherwise.
6. Every order status change shall create a corresponding status-history record.
7. Monetary calculations shall use decimal values and shall not use floating-point fields.
8. Date and time values shall be timezone-aware. The application shall display dates and times using the printing shop's configured local timezone.

## 9. Non-Functional Requirements

### 9.1 Usability

- Navigation and forms shall use clear labels and consistent layouts.
- Validation errors shall appear near the affected fields and preserve valid entered data.
- Status, deadline, balance, and important actions shall be easy to identify.

### 9.2 Security

- The system shall use Django authentication, sessions, CSRF protection, and password hashing.
- Operational pages shall require authentication.
- Server-side validation shall be applied even when client-side validation is present.
- Secrets and production database credentials shall be stored outside source code.

### 9.3 Data Integrity

- Required fields and allowed choices shall be enforced by forms and models.
- Database migrations shall be created and applied whenever models change.
- Historical completed, cancelled, status-change, and payment records shall be preserved.

### 9.4 Performance

- Common order-list, dashboard, and report queries shall use appropriate relationships and database indexes.
- The system shall paginate long order and history lists.
- The semester version shall support the normal workload of one printing shop.

### 9.5 Reliability and Maintainability

- The system shall display understandable error messages and avoid losing submitted form values after validation errors.
- Core business logic shall have automated tests.
- Apps shall remain focused on their named business responsibilities.
- Dependencies shall be recorded in `requirements.txt`.

## 10. Technical Requirements

- Python 3
- Django
- HTML and CSS templates, with JavaScript only where needed
- SQLite for initial local development, as supported by the setup guide
- Django ORM and migrations for database management
- Django admin for development-time record inspection and administration
- A modern web browser

The database may later be migrated to PostgreSQL if deployment requirements demand it, but that change is outside the initial local setup.

## 11. Testing and Acceptance Criteria

The initial release is acceptable when:

1. A user can register, sign in, update account information, and sign out.
2. An authenticated user can create and update customers, services, orders, and payments.
3. An order can move through every required status and each change is recorded.
4. Dashboard totals agree with the stored order data.
5. Due-soon and overdue lists correctly follow the configured date rules.
6. Amount paid, balance, and payment status are calculated correctly from payment records.
7. Search and combined filters return the correct orders.
8. Completed and cancelled orders remain available in history.
9. Date-range summaries return correct order and payment totals.
10. Invalid required fields, non-positive quantities, negative prices, and non-positive payments are rejected.
11. Data remains available after the server is restarted.
12. Automated tests for the major functions pass, and manual browser testing confirms the primary workflows.

## 12. Scope Limitations

The initial version shall not include:

- Advanced accounting, payroll, or full financial management.
- Direct communication with printers, cutters, sublimation machines, or other equipment.
- Online payment processing or bank/e-wallet integration.
- Automatic verification of manually entered customer, order, and payment information.
- Advanced material inventory for ink, paper, tarpaulin, vinyl, or similar supplies.
- Multiple shops or business branches.
- Guaranteed SMS or email notifications; these are optional only if semester time and resources permit.
- Features that cannot reasonably be designed, developed, and tested within the semester.

## 13. Recommended Implementation Order

1. Register the Django apps in `INSTALLED_APPS`.
2. Implement and migrate `Customer` and `PrintService`.
3. Implement and migrate `Order` and `OrderStatusHistory`.
4. Implement and migrate `Payment`.
5. Configure Django authentication views and account forms.
6. Build customer, service, order, status, and payment workflows.
7. Build dashboard, deadline monitoring, search, history, and reports from the stored data.
8. Register core models in Django admin.
9. Create automated tests and complete end-to-end manual testing.

