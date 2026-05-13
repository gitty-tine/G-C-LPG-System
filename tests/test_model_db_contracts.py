import datetime as dt
import unittest
from unittest import mock

from tests.helpers import (
    FakeConnection,
    FakeCursor,
    FakeStoredResult,
    install_dependency_stubs,
    patch_connection,
)


install_dependency_stubs()


class LoginAndAccountModelDbTest(unittest.TestCase):
    def test_login_model_queries_and_reset_code_procedures(self):
        import models.login_model as login_model

        cursor = FakeCursor(fetchone_rows=[{"id": 1, "password": "secret"}])
        conn = FakeConnection([cursor])
        patch_connection(self, login_model, conn)

        self.assertEqual(login_model.LoginModel.get_user_by_username("admin")["id"], 1)
        self.assertEqual(conn.cursor_calls[0], {"dictionary": True})
        self.assertIn("BINARY username", cursor.executed[0][0])
        self.assertEqual(cursor.executed[0][1], ("admin",))
        self.assertTrue(cursor.closed)
        self.assertTrue(conn.closed)

        with mock.patch.object(login_model.LoginModel, "get_user_by_username", return_value={"password": "pw"}):
            with mock.patch.object(login_model.LoginModel, "verify_password", return_value=True):
                self.assertEqual(login_model.LoginModel.authenticate("admin", "pw"), {"password": "pw"})
        with mock.patch.object(login_model.LoginModel, "get_user_by_username", return_value=None):
            self.assertIsNone(login_model.LoginModel.authenticate("missing", "pw"))

        code = login_model.LoginModel.generate_reset_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())

        cursor = FakeCursor()
        conn = FakeConnection([cursor])
        with mock.patch.object(login_model, "get_connection", return_value=conn):
            login_model.LoginModel.save_reset_code(5, "123456")
        self.assertEqual(cursor.callprocs, [("sp_save_reset_code", [5, "123456"])])
        self.assertEqual(conn.commits, 1)

        cursor = FakeCursor(fetchone_rows=[{"id": 5}])
        conn = FakeConnection([cursor])
        with mock.patch.object(login_model, "get_connection", return_value=conn):
            self.assertEqual(login_model.LoginModel.verify_reset_code(" user@example.com ", " 123456 ")["id"], 5)
        self.assertEqual(cursor.executed[0][1], ("user@example.com", "123456"))

        cursor = FakeCursor()
        conn = FakeConnection([cursor])
        with mock.patch.object(login_model, "get_connection", return_value=conn):
            login_model.LoginModel.reset_password(5, "NewStrong1!")
        self.assertEqual(cursor.callprocs[0][0], "sp_change_user_password")
        self.assertEqual(cursor.callprocs[0][1][0], 5)
        self.assertTrue(str(cursor.callprocs[0][1][1]).startswith("hashed:"))

    def test_account_model_profile_and_password_updates(self):
        import models.account_model as account_model

        cursor = FakeCursor(fetchone_rows=[{"id": 7, "username": "admin"}])
        conn = FakeConnection([cursor])
        patch_connection(self, account_model, conn)
        self.assertEqual(account_model.AccountModel.get_user_by_id(7)["username"], "admin")
        self.assertEqual(cursor.executed[0][1], (7,))

        cursor = FakeCursor()
        conn = FakeConnection([cursor])
        with mock.patch.object(account_model, "get_connection", return_value=conn):
            with mock.patch.object(
                account_model.AccountModel,
                "get_user_by_id",
                return_value={"id": 7, "username": "new"},
            ):
                self.assertEqual(
                    account_model.AccountModel.update_profile(7, "Admin", "admin", None),
                    {"id": 7, "username": "new"},
                )
        self.assertEqual(cursor.callprocs, [("sp_update_user_profile", [7, "Admin", "admin", None])])
        self.assertEqual(conn.commits, 1)

        cursor = FakeCursor()
        conn = FakeConnection([cursor])
        with mock.patch.object(account_model, "get_connection", return_value=conn):
            with mock.patch.object(
                account_model.AccountModel,
                "get_user_by_id",
                return_value={"id": 7, "password": "Current1!"},
            ):
                self.assertTrue(
                    account_model.AccountModel.update_password(7, "Current1!", "NewStrong1!")
                )
        self.assertEqual(cursor.callprocs[0][0], "sp_change_user_password")
        self.assertEqual(conn.commits, 1)

        with mock.patch.object(
            account_model.AccountModel,
            "get_user_by_id",
            return_value={"id": 7, "password": "different"},
        ):
            with self.assertRaisesRegex(ValueError, "Current password is incorrect"):
                account_model.AccountModel.update_password(7, "Current1!", "NewStrong1!")


class CustomerAndProductModelDbTest(unittest.TestCase):
    def test_customer_read_methods_use_fake_connection(self):
        import models.customer_model as customer_model

        read_cases = [
            ("get_all", (False,), [{"id": 1}]),
            ("get_by_id", (1,), {"id": 1}),
            ("search", ("ana",), [{"id": 2}]),
            ("get_active", (), [{"id": 3}]),
            ("get_dropdown_list", (), [{"id": 4}]),
        ]
        for method_name, args, expected in read_cases:
            with self.subTest(method_name=method_name):
                if isinstance(expected, list):
                    cursor = FakeCursor(fetchall_rows=[expected])
                else:
                    cursor = FakeCursor(fetchone_rows=[expected])
                conn = FakeConnection([cursor])
                with mock.patch.object(customer_model, "get_connection", return_value=conn):
                    result = getattr(customer_model.CustomerModel, method_name)(*args)
                self.assertEqual(result, expected)
                self.assertTrue(cursor.closed)
                self.assertTrue(conn.closed)

    def test_customer_mutation_methods_commit_or_surface_sp_validation(self):
        import models.customer_model as customer_model

        cursor = FakeCursor(stored_results=[FakeStoredResult([(55,)])])
        conn = FakeConnection([cursor])
        with mock.patch.object(customer_model, "get_connection", return_value=conn):
            self.assertEqual(customer_model.CustomerModel.add("Ana", "Manila", "0917", "", user_id=9), 55)
        self.assertEqual(cursor.callprocs[0][0], "sp_add_customer")
        self.assertEqual(conn.commits, 1)

        for method_name, args, proc_name in [
            ("update", (55, "Ana", "Makati", "0917", "", 9), "sp_update_customer"),
            ("archive", (55, 9), "sp_archive_customer"),
            ("restore", (55, 9), "sp_restore_customer"),
            ("delete", (55, 9), "sp_delete_customer"),
        ]:
            with self.subTest(method_name=method_name):
                cursor = FakeCursor()
                conn = FakeConnection([cursor])
                with mock.patch.object(customer_model, "get_connection", return_value=conn):
                    self.assertTrue(getattr(customer_model.CustomerModel, method_name)(*args))
                self.assertEqual(cursor.callprocs[0][0], proc_name)
                self.assertEqual(conn.commits, 1)

        cursor = FakeCursor(callproc_side_effect=Exception("1644 (45000): Bad customer"))
        conn = FakeConnection([cursor])
        with mock.patch.object(customer_model, "get_connection", return_value=conn):
            with self.assertRaisesRegex(ValueError, "Bad customer"):
                customer_model.CustomerModel.archive(55, 9)
        self.assertEqual(conn.rollbacks, 1)

    def test_product_read_and_write_methods(self):
        import models.product_model as product_model

        read_cases = [
            ("get_all", (), [{"id": 1}]),
            ("get_by_id", (1,), {"id": 1}),
            ("search", ("gas",), [{"id": 2}]),
            ("get_summary", (), [{"id": 3}]),
            ("get_by_delivery", (10,), [{"id": 4}]),
            ("get_dropdown_list", (), [{"id": 5}]),
        ]
        for method_name, args, expected in read_cases:
            with self.subTest(method_name=method_name):
                cursor = FakeCursor(
                    fetchall_rows=[expected] if isinstance(expected, list) else None,
                    fetchone_rows=[expected] if isinstance(expected, dict) else None,
                )
                conn = FakeConnection([cursor])
                with mock.patch.object(product_model, "get_connection", return_value=conn):
                    self.assertEqual(getattr(product_model.ProductModel, method_name)(*args), expected)
                self.assertTrue(conn.closed)

        cursor = FakeCursor(fetchone_rows=[{"total": 4}])
        conn = FakeConnection([cursor])
        with mock.patch.object(product_model, "get_connection", return_value=conn):
            self.assertEqual(product_model.ProductModel.get_count(), 4)

        for row, expected in [({"id": 1}, True), (None, False)]:
            cursor = FakeCursor(fetchone_rows=[row])
            conn = FakeConnection([cursor])
            with mock.patch.object(product_model, "get_connection", return_value=conn):
                self.assertEqual(product_model.ProductModel.exists("Solane", "11kg"), expected)

        cursor = FakeCursor(stored_results=[FakeStoredResult([(22,)])])
        conn = FakeConnection([cursor])
        with mock.patch.object(product_model, "get_connection", return_value=conn):
            self.assertEqual(product_model.ProductModel.add("Solane", "11kg", "940", "2200"), 22)
        self.assertEqual(cursor.callprocs[0][0], "sp_add_product")

        for method_name, args, proc_name in [
            ("update", (22, "Solane", "11kg", "950", "2300"), "sp_update_product"),
            ("delete", (22,), "sp_delete_product"),
        ]:
            cursor = FakeCursor()
            conn = FakeConnection([cursor])
            with mock.patch.object(product_model, "get_connection", return_value=conn):
                self.assertTrue(getattr(product_model.ProductModel, method_name)(*args))
            self.assertEqual(cursor.callprocs[0][0], proc_name)

    def test_owner_product_read_write_archive_restore_and_count(self):
        import models.owner_product_model as owner_product_model

        read_cases = [
            ("get_all", (), [{"id": 1}]),
            ("get_by_id", (1,), {"id": 1}),
            ("search", ("gas",), [{"id": 2}]),
            ("get_price_history", (1,), [{"id": 3}]),
            ("get_revenue_summary", (), [{"id": 4}]),
        ]
        for method_name, args, expected in read_cases:
            cursor = FakeCursor(
                fetchall_rows=[expected] if isinstance(expected, list) else None,
                fetchone_rows=[expected] if isinstance(expected, dict) else None,
            )
            conn = FakeConnection([cursor])
            with mock.patch.object(owner_product_model, "get_connection", return_value=conn):
                self.assertEqual(getattr(owner_product_model.OwnerProductModel, method_name)(*args), expected)

        for method_name, args, proc_name in [
            ("add", ("Solane", "11kg", "940", "2200", 8), "sp_add_product"),
            ("update", (1, "Solane", "11kg", "950", "2300", 8), "sp_update_product"),
            ("archive", (1, 8), "sp_archive_product"),
            ("delete", (1, 8), "sp_delete_product"),
            ("restore", (1, 8), "sp_restore_product"),
        ]:
            cursor = FakeCursor(stored_results=[FakeStoredResult([(1,)])])
            conn = FakeConnection([cursor])
            with mock.patch.object(owner_product_model, "get_connection", return_value=conn):
                result = getattr(owner_product_model.OwnerProductModel, method_name)(*args)
            self.assertIn(result, (1, True))
            self.assertEqual(cursor.callprocs[0][0], proc_name)
            self.assertEqual(conn.commits, 1)

        cursor = FakeCursor(fetchone_rows=[{"total": 6}])
        conn = FakeConnection([cursor])
        with mock.patch.object(owner_product_model, "get_connection", return_value=conn):
            self.assertEqual(owner_product_model.OwnerProductModel.get_count(archived=True), 6)


class DeliveryAndTransactionModelDbTest(unittest.TestCase):
    def test_delivery_read_methods_and_status_update(self):
        import models.delivery_model as delivery_model

        for method_name, args in [
            ("get_all", ()),
            ("get_items", (1,)),
            ("get_customer_dropdown", ()),
            ("get_product_dropdown", ()),
        ]:
            cursor = FakeCursor(fetchall_rows=[[{"id": 1}]])
            conn = FakeConnection([cursor])
            with mock.patch.object(delivery_model, "get_connection", return_value=conn):
                self.assertEqual(getattr(delivery_model.DeliveryModel, method_name)(*args), [{"id": 1}])
            self.assertTrue(cursor.closed)
            self.assertTrue(conn.closed)

        cursor = FakeCursor()
        conn = FakeConnection([cursor])
        with mock.patch.object(delivery_model, "get_connection", return_value=conn):
            self.assertTrue(delivery_model.DeliveryModel.update_status(1, "delivered", 7))
        self.assertEqual(cursor.callprocs, [("sp_update_delivery_status", [1, "delivered", 7])])
        self.assertEqual(conn.commits, 1)

    def test_delivery_create_validates_active_customer_and_products(self):
        import models.delivery_model as delivery_model

        cursor = FakeCursor(
            fetchone_rows=[{"id": 1}],
            fetchall_rows=[[{"id": 2}]],
            stored_results=[FakeStoredResult([{"new_delivery_id": 99}])],
        )
        conn = FakeConnection([cursor])
        with mock.patch.object(delivery_model, "get_connection", return_value=conn):
            new_id = delivery_model.DeliveryModel.create(
                1,
                7,
                dt.date(2026, 5, 13),
                "",
                [{"product_id": 2, "quantity": 3, "type": "New Tank", "unit_price": "2200"}],
            )

        self.assertEqual(new_id, 99)
        self.assertEqual(conn.transactions, 1)
        self.assertEqual(conn.commits, 1)
        self.assertEqual(cursor.callprocs[0][0], "sp_create_delivery")

    def test_transaction_queries_and_mark_paid(self):
        import models.admin_transaction_model as transaction_model

        cursor = FakeCursor(fetchall_rows=[[{"transaction_id": 1}]])
        conn = FakeConnection([cursor])
        with mock.patch.object(transaction_model, "get_connection", return_value=conn):
            self.assertEqual(transaction_model.TransactionModel.get_all(), [{"transaction_id": 1}])

        cursor = FakeCursor(fetchone_rows=[{"total_paid": 100}])
        conn = FakeConnection([cursor])
        with mock.patch.object(transaction_model, "get_connection", return_value=conn):
            self.assertEqual(transaction_model.TransactionModel.get_totals(), {"total_paid": 100})

        cursor = FakeCursor(fetchall_rows=[[{"sale_date": dt.date(2026, 5, 13)}]])
        conn = FakeConnection([cursor])
        with mock.patch.object(transaction_model, "get_connection", return_value=conn):
            self.assertEqual(
                transaction_model.TransactionModel.get_daily_summary(
                    dt.date(2026, 5, 1),
                    dt.date(2026, 5, 13),
                ),
                [{"sale_date": dt.date(2026, 5, 13)}],
            )

        for method_name, args in [
            ("get_by_delivery_id", (9,)),
            ("is_paid", (9,)),
        ]:
            cursor = FakeCursor(fetchone_rows=[{"payment_status": "paid"}])
            conn = FakeConnection([cursor])
            with mock.patch.object(transaction_model, "get_connection", return_value=conn):
                result = getattr(transaction_model.TransactionModel, method_name)(*args)
            self.assertIn(result, ({"payment_status": "paid"}, True))

        for method_name in ["get_running_totals", "get_overdue_unpaid"]:
            cursor = FakeCursor(fetchall_rows=[[{"id": 1}]])
            conn = FakeConnection([cursor])
            with mock.patch.object(transaction_model, "get_connection", return_value=conn):
                if method_name == "get_running_totals":
                    result = transaction_model.TransactionModel.get_running_totals(
                        dt.date(2026, 5, 1),
                        dt.date(2026, 5, 13),
                    )
                else:
                    result = transaction_model.TransactionModel.get_overdue_unpaid()
            self.assertEqual(result, [{"id": 1}])

        cursor = FakeCursor()
        conn = FakeConnection([cursor])
        with mock.patch.object(transaction_model, "get_connection", return_value=conn):
            self.assertTrue(transaction_model.TransactionModel.mark_paid(9, user_id=7))
        self.assertEqual(cursor.callprocs, [("sp_mark_payment", [9])])
        self.assertEqual(conn.commits, 1)


class DashboardAuditLogsAndMessagesDbTest(unittest.TestCase):
    def test_admin_dashboard_aggregates_sections_with_one_connection(self):
        import models.admin_dashboard_model as admin_dashboard_model

        cursor = FakeCursor(
            fetchone_rows=[{"total_today": 1}, {"unpaid_count": 2}],
            fetchall_rows=[[{"delivery_id": 3}], [{"delivery_id": 4}]],
        )
        conn = FakeConnection([cursor])
        with mock.patch.object(admin_dashboard_model, "get_connection", return_value=conn):
            payload = admin_dashboard_model.AdminDashboardModel.get_all_dashboard_data()

        self.assertEqual(payload["kpi_counts"]["unpaid_count"], 2)
        self.assertEqual(payload["todays_deliveries"], [{"delivery_id": 3}])
        self.assertEqual(payload["unpaid_deliveries"], [{"delivery_id": 4}])
        self.assertEqual(len(conn.cursor_calls), 1)

    def test_owner_dashboard_aggregates_sections_with_fixed_today(self):
        import models.owner_dashboard_model as owner_dashboard_model

        cursor = FakeCursor(
            fetchone_rows=[
                {"total_sales_today": 100},
                {"total_today": 3},
            ],
            fetchall_rows=[
                [{"day_label": "Mon"}],
                [{"customer_id": 1}],
                [{"transaction_id": 1}],
            ],
        )
        conn = FakeConnection([cursor])
        with mock.patch.object(owner_dashboard_model, "get_connection", return_value=conn):
            with mock.patch.object(
                owner_dashboard_model.OwnerDashboardModel,
                "_today",
                return_value=dt.date(2026, 5, 13),
            ):
                payload = owner_dashboard_model.OwnerDashboardModel.get_all_dashboard_data()

        self.assertEqual(payload["sales_kpis"]["total_sales_today"], 100)
        self.assertEqual(payload["delivery_counts"]["total_today"], 3)
        self.assertEqual(payload["weekly_chart"], [{"day_label": "Mon"}])

    def test_audit_and_delivery_log_models_transform_rows(self):
        import models.audit_logs_model as audit_logs_model
        import models.delivery_logs_model as delivery_logs_model

        audit_row = {
            "id": 1,
            "raw_action": "UPDATE",
            "old_value": "Name: Old",
            "new_value": "Name: New",
        }
        cursor = FakeCursor(fetchall_rows=[[audit_row]])
        conn = FakeConnection([cursor])
        with mock.patch.object(audit_logs_model, "get_connection", return_value=conn):
            rows = audit_logs_model.AuditLogModel.get_logs(action="Updated", section="Customers")
        self.assertEqual(rows[0]["description"], "Name changed")
        self.assertEqual(cursor.executed[0][1], ("UPDATE", "customers"))

        raw_log = {
            "delivery_id": 1,
            "customer_name": "ana",
            "old_status": "pending",
            "new_status": "in transit",
        }
        cursor = FakeCursor(fetchall_rows=[[raw_log]])
        conn = FakeConnection([cursor])
        with mock.patch.object(delivery_logs_model, "get_connection", return_value=conn):
            logs = delivery_logs_model.DeliveryLogsModel().get_all_logs()
        self.assertEqual(logs[0]["customer_name"], "Ana")
        self.assertEqual(logs[0]["new_status"], "In Transit")

    def test_message_model_read_and_write_methods(self):
        import models.message_model as message_model

        cursor = FakeCursor(fetchone_rows=[{"total": 5}])
        conn = FakeConnection([cursor])
        with mock.patch.object(message_model, "get_connection", return_value=conn):
            self.assertEqual(message_model.MessageModel.get_unread_count(7), 5)

        cursor = FakeCursor(fetchall_rows=[[{"user_id": 8, "role": "owner", "latest_sender_id": 7}]])
        conn = FakeConnection([cursor])
        with mock.patch.object(message_model, "get_connection", return_value=conn):
            conversations = message_model.MessageModel.list_conversations(7)
        self.assertTrue(conversations[0]["latest_from_me"])

        cursor = FakeCursor(fetchall_rows=[[{"id": 1, "sender_id": 8, "receiver_id": 7, "body": "hi"}]])
        conn = FakeConnection([cursor])
        with mock.patch.object(message_model, "get_connection", return_value=conn):
            thread = message_model.MessageModel.get_thread(7, 8, limit=999)
        self.assertFalse(thread[0]["is_from_me"])
        self.assertIn("LIMIT 200", cursor.executed[0][0])

        cursor = FakeCursor(stored_results=[FakeStoredResult([{"new_message_id": 12}])])
        conn = FakeConnection([cursor])
        with mock.patch.object(message_model, "get_connection", return_value=conn):
            self.assertEqual(message_model.MessageModel.send_message(7, 8, " hello "), 12)
        self.assertEqual(cursor.callprocs, [("sp_send_internal_message", [7, 8, "hello"])])
        self.assertEqual(conn.commits, 1)

        cursor = FakeCursor()
        conn = FakeConnection([cursor])
        with mock.patch.object(message_model, "get_connection", return_value=conn):
            self.assertTrue(message_model.MessageModel.mark_thread_read(7, 8))
        self.assertEqual(cursor.callprocs[0][0], "sp_mark_internal_thread_read")


class NotificationAndReportModelDbTest(unittest.TestCase):
    def test_notification_mark_read_methods_and_read_map(self):
        import models.notification_model as notification_model

        cursor = FakeCursor()
        conn = FakeConnection([cursor])
        with mock.patch.object(notification_model, "get_connection", return_value=conn):
            self.assertTrue(notification_model.NotificationModel.mark_read(7, "key"))
        self.assertEqual(conn.commits, 1)
        self.assertEqual(cursor.executed[0][1], (7, "key"))

        cursor = FakeCursor()
        conn = FakeConnection([cursor])
        with mock.patch.object(notification_model, "get_connection", return_value=conn):
            self.assertTrue(notification_model.NotificationModel.mark_many_read(7, ["a", "", "b"]))
        self.assertEqual(cursor.executemany_calls[0][1], [(7, "a"), (7, "b")])

        keys = [f"k{i}" for i in range(401)]
        cursor = FakeCursor(
            fetchall_rows=[
                [{"notification_key": "k0", "read_at": "now"}],
                [{"notification_key": "k400", "read_at": "later"}],
            ]
        )
        read_map = notification_model.NotificationModel._read_map(cursor, 7, keys)
        self.assertEqual(set(read_map), {"k0", "k400"})
        self.assertEqual(len(cursor.executed), 2)

    def test_notification_get_for_user_composes_summaries_audit_and_read_state(self):
        import models.notification_model as notification_model

        cursor = FakeCursor()
        conn = FakeConnection([cursor])
        summary = {"key": "summary", "severity": "high", "source": "summary", "created_at": dt.date(2026, 5, 13)}
        audit = {"key": "audit:1", "severity": "normal", "source": "audit", "created_at": dt.date(2026, 5, 12)}

        with mock.patch.object(notification_model, "get_connection", return_value=conn):
            with mock.patch.object(
                notification_model.NotificationModel,
                "_evaluation_stamp",
                return_value=("now", "May 13"),
            ):
                with mock.patch.object(
                    notification_model.NotificationModel,
                    "_fetch_overdue_delivery_alert",
                    return_value=summary,
                ):
                    with mock.patch.object(
                        notification_model.NotificationModel,
                        "_fetch_today_delivery_alert",
                        return_value=None,
                    ):
                        with mock.patch.object(
                            notification_model.NotificationModel,
                            "_fetch_unpaid_transaction_alert",
                            return_value=None,
                        ):
                            with mock.patch.object(
                                notification_model.NotificationModel,
                                "_fetch_recent_activity",
                                return_value=[audit],
                            ):
                                with mock.patch.object(
                                    notification_model.NotificationModel,
                                    "_read_map",
                                    return_value={"audit:1": {"read_at": "later", "read_at_fmt": "Later"}},
                                ):
                                    result = notification_model.NotificationModel.get_for_user(
                                        7,
                                        role="owner",
                                    )

        self.assertFalse(result[0]["is_read"])
        self.assertTrue(result[1]["is_read"])

    def test_report_model_stored_procedure_methods(self):
        import models.report_model as report_model

        proc_cases = [
            ("get_daily_snapshot_summary", ("sp_get_daily_snapshot_summary", "one")),
            ("get_weekly_snapshot_summary", ("sp_get_weekly_snapshot_summary", "one")),
            ("get_monthly_snapshot_summary", ("sp_get_monthly_snapshot_summary", "one")),
            ("get_summary", ("sp_get_report_summary", "one")),
            ("get_breakdown", ("sp_get_delivery_report", "many")),
            ("get_detailed_breakdown", ("sp_get_report_lines", "many")),
            ("get_daily_reports", ("sp_get_daily_reports", "many")),
            ("get_weekly_reports", ("sp_get_weekly_reports", "many")),
            ("get_monthly_reports", ("sp_get_monthly_reports", "many")),
            ("get_sales_by_product", ("sp_get_sales_by_product", "many")),
            ("get_period_comparison", ("sp_get_period_comparison", "many")),
        ]
        for method_name, (proc_name, mode) in proc_cases:
            with self.subTest(method_name=method_name):
                rows = [{"value": method_name}]
                cursor = FakeCursor(stored_results=[FakeStoredResult(rows)])
                conn = FakeConnection([cursor])
                with mock.patch.object(report_model, "get_connection", return_value=conn):
                    result = getattr(report_model.ReportModel, method_name)(
                        dt.date(2026, 5, 1),
                        dt.date(2026, 5, 13),
                    )
                self.assertEqual(result, rows[0] if mode == "one" else rows)
                self.assertEqual(cursor.callprocs[0][0], proc_name)

        cursor = FakeCursor(stored_results=[FakeStoredResult([{"customer_id": 1}])])
        conn = FakeConnection([cursor])
        with mock.patch.object(report_model, "get_connection", return_value=conn):
            self.assertEqual(
                report_model.ReportModel.get_top_customers(
                    dt.date(2026, 5, 1),
                    dt.date(2026, 5, 13),
                    limit=3,
                ),
                [{"customer_id": 1}],
            )
        self.assertEqual(cursor.callprocs[0], ("sp_get_top_customers", [dt.date(2026, 5, 1), dt.date(2026, 5, 13), 3]))

        cursor = FakeCursor(stored_results=[FakeStoredResult([{"peak_sales_day": "May 13"}])])
        conn = FakeConnection([cursor])
        with mock.patch.object(report_model, "get_connection", return_value=conn):
            insights = report_model.ReportModel.get_report_insights(
                dt.date(2026, 5, 1),
                dt.date(2026, 5, 13),
            )
        self.assertEqual(insights["peak_sales_day"], "May 13")
        self.assertIn("most_sold_product", insights)


if __name__ == "__main__":
    unittest.main()
