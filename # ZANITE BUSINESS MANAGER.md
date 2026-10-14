# ZANITE BUSINESS MANAGER

### Business Management & Analytics System — System Structure and Requirements

## 1. System Overview

Zanite Business Manager is a web-based business management system designed primarily for small and medium-sized businesses (SMEs).

The system will help business owners manage sales, expenses, inventory, customers, debts, payments and business performance from one platform.

The main objective is to replace scattered records such as notebooks, spreadsheets and separate payment records with one centralized system.

### Main objective

> To help business owners record their daily operations and clearly understand the financial and operational performance of their businesses.

# 2. Target Users

The system will primarily target:

* Retail shops
* Mini-supermarkets
* Boutiques
* Electronics shops
* Beauty and cosmetics businesses
* Hardware shops
* Restaurants and small food businesses
* Salons and barbershops
* Small wholesalers
* Online sellers
* Service-based businesses

The system should be flexible enough to accommodate different business types.

# 3. User Roles

### A. Business Owner / Administrator

The administrator has full control over the business account.

They can:

* Manage products
* Record sales
* Record expenses
* Manage customers
* Manage debts
* Manage employees
* View reports
* View financial summaries
* Manage business settings
* Manage users
* Export business data

### B. Employee / Staff

Employees have restricted access depending on permissions.

For example:

* Record sales
* View available products
* Add customers
* Record payments

They should not automatically have access to sensitive financial reports or system settings.

# 4. Main System Modules

The system should contain the following major modules:

```text
ZANITE BUSINESS MANAGER
│
├── Authentication
│
├── Dashboard
│
├── Sales
│   ├── New Sale
│   ├── Sales History
│   └── Receipts
│
├── Products & Inventory
│   ├── Products
│   ├── Categories
│   ├── Stock
│   └── Stock Movements
│
├── Expenses
│
├── Customers
│
├── Debtors / Credit
│
├── Suppliers
│
├── Employees
│
├── Payments
│
├── Reports & Analytics
│
├── Notifications
│
├── Business Settings
│
└── User Profile
```

# 5. Authentication Module

Users should be able to securely access their business accounts.

### Requirements

* User registration
* Login
* Logout
* Password reset
* Email verification
* Session management
* Role-based access
* Business account creation

### Business registration

During registration, collect:

* Business name
* Owner name
* Phone number
* Email
* Business type
* Location
* Currency
* Password

The default currency can be KES, while allowing other currencies later.

# 6. Dashboard

The dashboard should provide a quick overview of the business.

### Key metrics

Display:

Today's Sales

> KSh 25,400

Today's Expenses

> KSh 8,500

Today's Profit

> KSh 16,900

Outstanding Debts

> KSh 42,000

Low Stock Items

> 7

Total Products

> 245

### Dashboard charts

Include:

* Sales trend
* Expense trend
* Profit trend
* Top-selling products
* Sales by payment method
* Expenses by category

Example:

```text
              BUSINESS PERFORMANCE

Sales
│
│          █
│      █   █
│  █   █   █
│  █   █ █ █
└────────────────
 Mon Tue Wed Thu
```

# 7. Sales Management

This is one of the most important modules.

The user should be able to record a sale.

### Sale information

* Sale ID
* Date
* Customer
* Product
* Quantity
* Unit price
* Discount
* Total amount
* Payment method
* Amount paid
* Balance
* Employee who processed sale

### Payment methods

Initially:

* Cash
* M-Pesa
* Airtel Money
* Bank
* Card
* Credit

The system should allow additional payment methods later.

# 8. Point-of-Sale Interface

The system should eventually have a simple POS interface.

Example:

```text
----------------------------------
          NEW SALE
----------------------------------

Search Product
[ Samsung A07             🔍 ]

Product
Samsung A07

Price: KSh 14,500
Quantity: [-] 1 [+]

----------------------------------

Subtotal:       KSh 14,500
Discount:       KSh 0
TOTAL:          KSh 14,500

Payment:
○ Cash
○ M-Pesa
○ Bank
○ Credit

[ COMPLETE SALE ]
----------------------------------
```

After completing the sale:

* Save transaction
* Reduce inventory
* Update revenue
* Update profit calculations
* Generate receipt
* Record payment

# 9. Inventory Management

The inventory module should allow businesses to know exactly what they have in stock.

### Product information

Each product should have:

* Product ID/SKU
* Product name
* Category
* Description
* Buying price
* Selling price
* Current stock
* Minimum stock level
* Supplier
* Date added
* Product image
* Status

## Stock Management

The system should automatically update stock.

### Example

Initial stock:

> Samsung A07 = 20 units

Sale:

> 2 units

New stock:

> 18 units

The system should record this as a stock movement.

### Stock movements

```text
Date       Product       Type       Qty
-----------------------------------------
17/09      Samsung A07   Sale       -2
17/09      Samsung A07   Purchase   +10
18/09      Samsung A07   Sale       -1
```

# 10. Low Stock Alerts

The business owner should define a minimum stock level.

Example:

```text
Samsung A07
Current Stock: 3
Minimum Level: 5

⚠ LOW STOCK
```

The system should notify the owner when stock falls below the threshold.

# 11. Expense Management

Users should be able to record every business expense.

### Expense fields

* Expense ID
* Date
* Category
* Description
* Amount
* Payment method
* Supplier/payee
* Notes
* Recorded by

### Expense categories

Examples:

* Rent
* Electricity
* Water
* Transport
* Salaries
* Stock purchases
* Internet
* Marketing
* Repairs
* Licenses
* Other

# 12. Customer Management

The system should maintain customer records.

### Customer information

* Customer ID
* Name
* Phone
* Email
* Address
* Total purchases
* Outstanding balance
* Transaction history
* Date registered

A customer profile should show their complete transaction history.

# 13. Credit / Debt Management

This is a particularly useful feature for small businesses.

When a customer purchases on credit:

```text
Product value:      KSh 10,000
Amount paid:        KSh 4,000
Outstanding:        KSh 6,000
```

The system records:

> Customer owes KSh 6,000.

When the customer pays:

```text
Previous debt:      KSh 6,000
Payment:            KSh 2,000
Remaining debt:     KSh 4,000
```

### Requirements

* Record credit sale
* Record debt repayment
* View outstanding debts
* Customer debt history
* Payment reminders
* Due dates
* Debt reports

# 14. Supplier Management

Businesses should be able to manage suppliers.

### Supplier information

* Supplier name
* Phone
* Email
* Address
* Products supplied
* Purchase history
* Amount owed
* Payment history

This becomes especially useful when inventory management is expanded.

# 15. Purchasing

The system should allow users to record stock purchases.

Example:

```text
Supplier: ABC Distributors

Product: Cooking Oil
Quantity: 20
Buying Price: KSh 350
Total: KSh 7,000

Payment:
M-Pesa

[ RECORD PURCHASE ]
```

When the purchase is recorded:

Inventory increases automatically.

# 16. Profit & Loss

The system should calculate business performance.

Basic calculation:

> Profit = Revenue − Expenses

However, for inventory businesses, the system should eventually distinguish sales revenue, cost of goods sold (COGS), gross profit and operating expenses rather than simply treating every stock purchase as an immediate expense.

Example:

```text
Sales Revenue             KSh 250,000
Cost of Goods Sold        KSh 150,000
--------------------------------------
Gross Profit              KSh 100,000

Operating Expenses        KSh 40,000
--------------------------------------
Net Profit                KSh 60,000
```

This distinction will make the system much more useful than a simple income/expense tracker.

# 17. Reports & Analytics

The reporting module should provide business insights.

### Reports

#### Sales Report

* Daily sales
* Weekly sales
* Monthly sales
* Sales by product
* Sales by employee
* Sales by customer
* Sales by payment method

#### Expense Report

* Expenses by category
* Expenses by date
* Largest expenses

#### Inventory Report

* Current stock
* Low-stock products
* Stock value
* Fast-moving products
* Slow-moving products

#### Financial Report

* Revenue
* COGS
* Gross profit
* Operating expenses
* Net profit
* Outstanding debts

# 18. Export System

Users should be able to export their information.

Possible formats:

* PDF
* Excel
* CSV

Example:

```text
[ Export PDF ]
[ Export Excel ]
[ Export CSV ]
```

This is also useful for businesses that want to keep offline records.

# 19. Receipt & Invoice System

After a sale, the system should generate a receipt.

Example:

```text
--------------------------------
          BUSINESS NAME
          Phone: 07XXXXXXXX
--------------------------------

Receipt No: #000145
Date: 17/09/2026

Samsung A07       1 × 14,500
Phone Case        2 × 500
--------------------------------
TOTAL             KSh 15,500

Payment: M-Pesa

Thank you for shopping with us.
--------------------------------
```

Later, invoices can include:

* Business logo
* Customer details
* Due date
* Tax information
* Payment instructions

# 20. Notifications

The system should generate important alerts.

Examples:

> 🔔 Samsung A07 is running low.

> 🔔 John Kamau has an outstanding debt of KSh 5,000.

> 🔔 Monthly sales have reached KSh 500,000.

> 🔔 Your subscription expires in 5 days.

Later, notifications can be delivered through:

* In-app notifications
* Email
* SMS
* WhatsApp

# 21. Business Settings

Business owners should be able to configure:

* Business name
* Logo
* Phone number
* Email
* Address
* Currency
* Receipt format
* Tax settings
* Payment methods
* Low-stock thresholds
* User permissions

# 22. Database Structure

A possible relational database structure:

```text
users
│
├── businesses
│
├── employees
│
├── customers
│
├── suppliers
│
├── products
│      │
│      └── categories
│
├── sales
│      │
│      └── sale_items
│
├── expenses
│
├── purchases
│      │
│      └── purchase_items
│
├── payments
│
├── debts
│
├── stock_movements
│
└── notifications
```

### Important relationships

```text
Business
   │
   ├── Users
   ├── Products
   ├── Customers
   ├── Suppliers
   ├── Sales
   ├── Expenses
   └── Purchases
```

Every business's data must be isolated from every other business.

Business A must never be able to access Business B's data.

That becomes extremely important once you turn this into SaaS.

# 23. Security Requirements

Because the system handles financial/business information, security should not be an afterthought.

Requirements:

* Password hashing
* Authentication
* Authorization
* Role-based permissions
* Secure sessions
* Input validation
* SQL injection protection
* CSRF protection
* Secure API endpoints
* Database backups
* Audit logs
* Data isolation between businesses
* No passwords/API secrets inside frontend JavaScript

# 24. Technology Requirements

### Version 1

I'd build the first version with:

Backend

* Python
* Flask

Database

* SQLite initially

Frontend

* HTML
* CSS
* JavaScript

Charts

* Chart.js

Reports

* Python/ReportLab

Data analysis

* Pandas

### Production version

Move toward:

* Flask/FastAPI
* PostgreSQL
* JavaScript frontend
* Cloud hosting
* Object storage for images
* Proper authentication
* Automated backups

# 25. Monetization Requirements

The system should be designed as a multi-tenant SaaS from the beginning, even if Version 1 is small.

Possible structure:

### Free

* Basic sales
* Basic expenses
* Limited products
* Basic dashboard

### Basic — KSh 300/month

* More products
* Customers
* Debts
* Reports
* Receipts

### Business — KSh 700/month

* Inventory
* Employees
* Advanced reports
* PDF/Excel exports
* Multiple payment methods

### Pro — KSh 1,500/month

* Multiple users
* Advanced analytics
* Automated backups
* Integrations
* Custom branding

These prices are testable starting hypotheses, not something you need to lock in before talking to customers.

# 26. Future Integrations

Once the core system works, you can integrate:

M-Pesa

→ Payment confirmation

WhatsApp

→ Receipts and debt reminders

SMS

→ Customer notifications

Online Store

→ Automatically synchronize online orders with inventory.

Accounting

→ Export financial records.

AI

→ Business insights such as:

> "Your sales increased by 18% this month."

> "Product X generated the highest revenue."

> "Your transport expenses increased significantly compared with last month."

# 27. MVP — What You Should Actually Build First

This is important.

Do not build everything above in Version 1.

Your first working product should contain only:

```text
ZANITE BUSINESS MANAGER MVP
│
├── Registration / Login
│
├── Dashboard
│
├── Products
│
├── Inventory
│
├── Sales
│
├── Expenses
│
├── Customers
│
├── Basic Debts
│
├── Profit Calculation
│
└── Basic Reports
```

### MVP workflow

A business owner should be able to:

1. Add product

↓

2. Add stock

↓

3. Sell product

↓

4. Stock automatically decreases

↓

5. Revenue automatically updates

↓

6. Record expenses

↓

7. System calculates business performance

↓

8. Owner sees the results on dashboard

That is the core engine.

Once that works reliably, add suppliers, employees, invoices, notifications, M-Pesa, WhatsApp, advanced analytics, etc.

# 28. The Most Important Requirement

The system should answer one question extremely well:

> "What is happening in my business financially and operationally?"

If a shop owner opens the dashboard and within 10 seconds can understand:

How much I sold → how much I spent → what I earned → what I owe → what customers owe me → what stock I have

zanite-business-manager/
│
├── app.py
├── requirements.txt
├── config.py
│
├── database/
│   └── business.db
│
├── models/
│   ├── user.py
│   ├── product.py
│   ├── sale.py
│   ├── expense.py
│   ├── customer.py
│   └── debt.py
│
├── routes/
│   ├── auth.py
│   ├── dashboard.py
│   ├── sales.py
│   ├── inventory.py
│   ├── expenses.py
│   └── customers.py
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── sales.html
│   ├── inventory.html
│   ├── expenses.html
│   └── customers.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── images/
│
└── reports/

lets skip the monitization for now, lets work on everything else minus monetization