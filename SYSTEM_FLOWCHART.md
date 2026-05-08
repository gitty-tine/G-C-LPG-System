# G and C LPG Trading System Flowchart

This flowchart is based on the current Python code in this project. The app uses a PySide6 MVC-style structure:

- `views/` builds screens and handles user interaction.
- `controllers/` validate requests and coordinate view/model updates.
- `models/` read and write MySQL data through `database/connection.py`.
- Stored procedures and database views do much of the business/data work.

## 1. Whole System Entry Flow

```mermaid
flowchart TD
    A["Start app<br/>main.py"] --> B["Install error logging hooks<br/>utils.error_logger"]
    B --> C["Open LoginView<br/>views/login_view.py"]

    C --> D{"User action"}
    D --> E["Enter username/password"]
    D --> F["Forgot password"]

    E --> G["LoginController.handle_login()"]
    G --> H["LoginModel.authenticate()"]
    H --> I["Query users table<br/>verify bcrypt password"]
    I --> J{"Valid credentials?"}

    J -- "No" --> K["Show login error"]
    K --> C

    J -- "Yes" --> L["Store current user<br/>LoginController._current_user"]
    L --> M{"Role"}

    M -- "admin" --> N["Build Admin Dashboard<br/>AdminDashboardController + DashboardView"]
    M -- "owner or other" --> O["Build Owner Dashboard<br/>OwnerDashboardController + OwnerDashboardView"]

    F --> P["ForgotPasswordModal"]
    P --> Q["Find account by email<br/>LoginModel.get_user_by_email()"]
    Q --> R["Generate reset code<br/>send email"]
    R --> S["Verify code"]
    S --> T["Reset password<br/>sp_change_user_password"]
    T --> C
```

## 2. Role-Based Navigation Flow

```mermaid
flowchart LR
    U["Signed-in user"] --> R{"User role"}

    R -- "Admin" --> A0["Admin DashboardView"]
    A0 --> A1["Dashboard<br/>today KPIs, today's deliveries, unpaid delivered"]
    A0 --> A2["Deliveries<br/>create, edit pending, update status, view items"]
    A0 --> A3["Customers<br/>add, edit, archive, restore, delete when allowed"]
    A0 --> A4["LPG Products<br/>read/search product catalog"]
    A0 --> A5["Transactions<br/>view/filter, mark unpaid as paid"]
    A0 --> A6["Delivery Logs<br/>view delivery status history"]
    A0 --> A7["Audit Logs<br/>view system record changes"]

    R -- "Owner" --> O0["Owner DashboardView"]
    O0 --> O1["Dashboard<br/>sales KPIs, delivery counts, weekly chart, top customers"]
    O0 --> O2["LPG Products<br/>add, edit, archive, restore, delete when allowed"]
    O0 --> O3["Transactions<br/>read-only transaction view"]
    O0 --> O4["Reports<br/>daily, weekly, monthly, export PDF/Excel"]
    O0 --> O5["Delivery Logs<br/>view delivery status history"]
    O0 --> O6["Audit Logs<br/>view system record changes"]

    A0 --> S1["Shared topbar tools"]
    O0 --> S1
    S1 --> S2["Notifications<br/>summary alerts + audit activity"]
    S1 --> S3["Internal messages<br/>admin/owner conversations"]
    S1 --> S4["Profile menu<br/>edit profile, change password, sign out"]
```

## 3. Admin Operational Workflow

```mermaid
flowchart TD
    AD["Admin Dashboard"] --> DB["AdminDashboardController"]
    DB --> DM["AdminDashboardModel"]
    DM --> DV["vw_dashboard_today<br/>vw_delivery_details<br/>transactions"]
    DV --> DBD["Show today's KPIs, deliveries, unpaid delivered records"]

    AD --> DEL["Deliveries page"]
    DEL --> DC["DeliveryController"]
    DC --> DList["list_deliveries()<br/>DeliveryModel.get_all()"]
    DList --> VDD["vw_delivery_details + delivery_items + lpg_products + transactions"]
    VDD --> DEL

    DEL --> NewD["New delivery"]
    NewD --> Drop["Load active customers/products"]
    Drop --> CreateD["create_delivery(customer, date, notes, items)"]
    CreateD --> SPD["sp_create_delivery"]
    SPD --> DI["Insert delivery_items"]
    DI --> RefreshD["Reload delivery list"]

    DEL --> EditD["Edit delivery"]
    EditD --> CanEdit{"Status is Pending?"}
    CanEdit -- "No" --> EditBlocked["Show only pending deliveries can be edited"]
    CanEdit -- "Yes" --> UpdD["update_delivery()"]
    UpdD --> SPUD["sp_update_pending_delivery<br/>update delivery_items if changed"]
    SPUD --> AuditEdit["Insert audit_logs row for delivery edit"]
    AuditEdit --> RefreshD

    DEL --> StatusD["Update delivery status"]
    StatusD --> SPStatus["sp_update_delivery_status"]
    SPStatus --> RefreshD

    AD --> CUS["Customers page"]
    CUS --> CC["CustomerController"]
    CC --> CM["CustomerModel"]
    CM --> CVS["vw_customer_summary"]
    CUS --> CAct["Add/Edit/Archive/Restore/Delete"]
    CAct --> CSP["sp_add_customer<br/>sp_update_customer<br/>sp_archive_customer<br/>sp_restore_customer<br/>sp_delete_customer"]

    AD --> PROD["LPG Products page"]
    PROD --> PC["ProductController"]
    PC --> PM["ProductModel"]
    PM --> PT["lpg_products + delivery_items"]
    PT --> PROD

    AD --> TRX["Transactions page"]
    TRX --> TC["AdminTransactionController"]
    TC --> TM["TransactionModel"]
    TM --> TV["vw_transaction_summary + transactions"]
    TRX --> Pay["Mark as paid"]
    Pay --> SPPay["sp_mark_payment"]

    AD --> LOGS["Delivery Logs / Audit Logs"]
    LOGS --> LC["DeliveryLogsController / AuditLogsController"]
    LC --> LM["delivery_logs / audit_logs"]

    CSP --> Notify["notify_notifications_changed()"]
    CreateD --> Notify
    UpdD --> Notify
    SPStatus --> Notify
    SPPay --> Notify
```

## 4. Owner Management and Reporting Workflow

```mermaid
flowchart TD
    OD["Owner Dashboard"] --> ODC["OwnerDashboardController"]
    ODC --> ODM["OwnerDashboardModel"]
    ODM --> OViews["vw_owner_dashboard_daily<br/>vw_report_delivery_financials<br/>vw_transaction_summary"]
    OViews --> OKPI["Show sales KPIs, delivery counts, weekly chart, top customers, recent transactions"]

    OD --> OP["Owner LPG Products page"]
    OP --> OPC["OwnerProductController"]
    OPC --> OPM["OwnerProductModel"]
    OPM --> OPData["lpg_products + delivery_items + audit_logs"]
    OP --> ProductActions["Add/Edit/Archive/Restore/Delete product"]
    ProductActions --> ProductSP["sp_add_product<br/>sp_update_product<br/>sp_archive_product<br/>sp_restore_product<br/>sp_delete_product"]

    OD --> OT["Owner Transactions page"]
    OT --> OTC["AdminTransactionController<br/>read-only view"]
    OTC --> OTM["TransactionModel.get_all()"]
    OTM --> OTV["vw_transaction_summary"]

    OD --> REP["Reports page"]
    REP --> RC["ReportController.load_period()"]
    RC --> RLive["ReportModel.get_summary()<br/>sp_get_report_summary"]
    RC --> RSnap{"Completed period?"}
    RSnap -- "Yes" --> SnapSP["Snapshot procedures<br/>daily/weekly/monthly"]
    RSnap -- "No" --> SkipSnap["Use live summary only"]
    SnapSP --> Merge["Merge snapshot totals into live summary"]
    SkipSnap --> Merge
    Merge --> Insights["sp_get_report_insights"]
    Insights --> Lines["sp_get_report_lines"]
    Lines --> RView["Display report rows and metrics"]
    RView --> Export["Export PDF or Excel"]

    OD --> OLogs["Delivery Logs / Audit Logs"]
    OLogs --> OLogC["DeliveryLogsController / AuditLogsController"]
    OLogC --> OLogM["delivery_logs / audit_logs"]

    ProductSP --> Notify["notify_notifications_changed()"]
```

## 5. Shared Services and Data Layer

```mermaid
flowchart TD
    AnyView["Any dashboard/view"] --> Controllers["Controllers"]
    Controllers --> Models["Models"]
    Models --> Conn["database.connection.get_connection()"]
    Conn --> DB["MySQL database<br/>gnc_lpg_db"]

    DB --> Tables["Main tables<br/>users, customers, lpg_products, deliveries, delivery_items, transactions"]
    DB --> LogTables["Log/support tables<br/>delivery_logs, audit_logs, internal_messages, notification_reads, error_logs"]
    DB --> Views["Database views<br/>vw_customer_summary<br/>vw_delivery_details<br/>vw_delivery_items_details<br/>vw_transaction_summary<br/>vw_dashboard_today<br/>vw_owner_dashboard_daily<br/>vw_report_delivery_financials<br/>vw_error_logs"]
    DB --> Procs["Stored procedures<br/>customer/product CRUD<br/>delivery creation/status/edit<br/>payment marking<br/>reports/snapshots<br/>profile/password/reset<br/>messaging"]

    Controllers --> EventBus["Notification event bus<br/>notify_notifications_changed()"]
    EventBus --> NotifViews["Dashboard notification panels refresh"]
    NotifViews --> NotifController["NotificationController"]
    NotifController --> NotifModel["NotificationModel"]
    NotifModel --> NotifSources["Overdue deliveries<br/>today open deliveries<br/>unpaid delivered transactions<br/>recent audit activity"]
    NotifModel --> Reads["notification_reads"]

    AnyView --> MessagePanel["Messaging panel"]
    MessagePanel --> MsgController["MessageController"]
    MsgController --> MsgModel["MessageModel"]
    MsgModel --> InternalMessages["internal_messages<br/>sp_send_internal_message<br/>sp_mark_internal_thread_read"]

    BkgErr["Unhandled errors / logged exceptions"] --> ErrLogger["utils.error_logger"]
    ErrLogger --> ErrorLogs["error_logs + vw_error_logs"]

    AnyView --> Profile["Profile actions"]
    Profile --> AccountController["AccountController"]
    AccountController --> AccountModel["AccountModel"]
    AccountModel --> UserSP["sp_update_user_profile<br/>sp_change_user_password"]
    UserSP --> Users["users table"]
```

## Important Accuracy Notes

- The app starts at `main.py`, then `views/login_view.py`.
- Login is role-based: `admin` opens `DashboardView`; every other role path currently opens `OwnerDashboardView`.
- Admin can manage deliveries and customers. Admin product screen is currently read/search only.
- Owner can manage LPG products. Owner transaction screen is read-only.
- Transactions are read from `vw_transaction_summary`; marking payment uses `sp_mark_payment`.
- Reports use live stored procedure totals, then merge snapshot totals only for completed daily/weekly/monthly periods.
- Several side effects are handled in the database through stored procedures and likely database triggers/views. The Python code calls the procedures and then reloads the relevant views/tables.
