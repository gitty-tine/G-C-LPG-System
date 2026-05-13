import datetime as dt
import unittest
from decimal import Decimal
from unittest import mock

from tests.helpers import FakeView, install_dependency_stubs


install_dependency_stubs()


class LoginControllerTest(unittest.TestCase):
    def setUp(self):
        from controllers.login_controller import LoginController

        LoginController.logout()
        self.LoginController = LoginController
        self.addCleanup(LoginController.logout)

    def test_login_requires_credentials(self):
        self.assertEqual(
            self.LoginController.login("", ""),
            (False, "Please enter your username and password."),
        )

    def test_login_sets_current_user_on_success(self):
        import controllers.login_controller as login_controller

        user = {"id": 1, "username": "admin", "role": "admin"}
        with mock.patch.object(login_controller.LoginModel, "authenticate", return_value=user):
            self.assertEqual(self.LoginController.login("admin", "secret"), (True, ""))

        self.assertEqual(self.LoginController.get_current_user(), user)

    def test_login_handles_bad_credentials_and_database_errors(self):
        import controllers.login_controller as login_controller

        with mock.patch.object(login_controller.LoginModel, "authenticate", return_value=None):
            self.assertEqual(
                self.LoginController.login("admin", "wrong"),
                (False, "Incorrect username or password."),
            )

        with mock.patch.object(login_controller.LoginModel, "authenticate", side_effect=RuntimeError("db")):
            with mock.patch.object(login_controller, "log_exception") as log_exception:
                ok, message = self.LoginController.login("admin", "secret")

        self.assertFalse(ok)
        self.assertIn("database", message.lower())
        log_exception.assert_called_once()

    def test_handle_login_builds_dashboard_for_authenticated_user(self):
        dashboard = object()
        with mock.patch.object(self.LoginController, "login", return_value=(True, "")):
            with mock.patch.object(
                self.LoginController,
                "get_current_user",
                return_value={"id": 1, "role": "owner"},
            ):
                with mock.patch.object(
                    self.LoginController,
                    "build_dashboard_for_user",
                    return_value=dashboard,
                ):
                    self.assertEqual(
                        self.LoginController().handle_login("owner", "secret"),
                        (True, "", dashboard),
                    )


class AccountControllerTest(unittest.TestCase):
    def test_current_user_requires_signed_in_user(self):
        import controllers.account_controller as account_controller

        with mock.patch.object(account_controller.LoginController, "get_current_user", return_value=None):
            with self.assertRaisesRegex(ValueError, "No signed-in user"):
                account_controller.AccountController._current_user()

    def test_update_profile_validates_and_updates_session_user(self):
        import controllers.account_controller as account_controller

        session_user = {"id": 7, "role": "admin"}
        refreshed = {"id": 7, "role": "admin", "password": "hash"}
        with mock.patch.object(
            account_controller.LoginController,
            "get_current_user",
            return_value=session_user,
        ):
            with mock.patch.object(
                account_controller.AccountModel,
                "update_profile",
                return_value=refreshed,
            ) as update_profile:
                with mock.patch.object(account_controller.LoginController, "set_current_user") as set_user:
                    updated = account_controller.AccountController.update_profile(
                        " Admin User ",
                        " admin ",
                        "admin@example.com",
                    )

        update_profile.assert_called_once_with(7, "Admin User", "admin", "admin@example.com")
        set_user.assert_called_once_with(updated)
        self.assertEqual(updated["full_name"], "Admin User")
        self.assertEqual(updated["username"], "admin")

    def test_update_profile_rejects_invalid_input_and_cleans_db_errors(self):
        import controllers.account_controller as account_controller

        with mock.patch.object(
            account_controller.LoginController,
            "get_current_user",
            return_value={"id": 7},
        ):
            with self.assertRaisesRegex(ValueError, "Full name cannot be empty"):
                account_controller.AccountController.update_profile("", "admin")
            with self.assertRaisesRegex(ValueError, "Username cannot be empty"):
                account_controller.AccountController.update_profile("Name", "")
            with self.assertRaisesRegex(ValueError, "valid email"):
                account_controller.AccountController.update_profile("Name", "admin", "bad")

            with mock.patch.object(
                account_controller.AccountModel,
                "update_profile",
                side_effect=RuntimeError("duplicate"),
            ):
                with mock.patch.object(account_controller, "clean_db_error", return_value="Username taken"):
                    with self.assertRaisesRegex(ValueError, "Username taken"):
                        account_controller.AccountController.update_profile("Name", "admin")

    def test_change_password_validates_and_delegates_to_model(self):
        import controllers.account_controller as account_controller

        with mock.patch.object(
            account_controller.LoginController,
            "get_current_user",
            return_value={"id": 7},
        ):
            with mock.patch.object(account_controller.AccountModel, "update_password", return_value=True) as update:
                self.assertTrue(
                    account_controller.AccountController.change_password(
                        "Current1!",
                        "NewStrong1!",
                    )
                )

        update.assert_called_once_with(7, "Current1!", "NewStrong1!")


class CustomerControllerTest(unittest.TestCase):
    def test_list_search_and_active_customer_reads(self):
        import controllers.customer_controller as customer_controller

        with mock.patch.object(customer_controller.CustomerModel, "get_all", return_value=["all"]) as get_all:
            self.assertEqual(customer_controller.CustomerController.list_customers(), (True, ["all"]))
            self.assertEqual(customer_controller.CustomerController.search_customers("", archived=True), (True, ["all"]))
        self.assertEqual(get_all.call_count, 2)

        with mock.patch.object(customer_controller.CustomerModel, "search", return_value=["match"]) as search:
            self.assertEqual(
                customer_controller.CustomerController.search_customers("ana"),
                (True, ["match"]),
            )
        search.assert_called_once_with("ana", archived=False)

        with mock.patch.object(customer_controller.CustomerModel, "get_active", return_value=["active"]):
            self.assertEqual(customer_controller.CustomerController.get_active_customers(), (True, ["active"]))

    def test_customer_mutations_use_current_user_and_notify(self):
        import controllers.customer_controller as customer_controller

        with mock.patch.object(
            customer_controller.LoginController,
            "get_current_user",
            return_value={"id": 9},
        ):
            with mock.patch.object(customer_controller.CustomerModel, "add", return_value=33) as add:
                with mock.patch.object(customer_controller.CustomerModel, "get_by_id", return_value={"id": 33}):
                    with mock.patch.object(customer_controller, "notify_notifications_changed") as notify:
                        self.assertEqual(
                            customer_controller.CustomerController.add_customer("Ana", "Manila", "0917"),
                            (True, {"id": 33}),
                        )

        add.assert_called_once_with("Ana", "Manila", "0917", "", user_id=9)
        notify.assert_called_once_with("customer_created")

        with mock.patch.object(customer_controller.LoginController, "get_current_user", return_value={"id": 9}):
            with mock.patch.object(customer_controller.CustomerModel, "update", return_value=True):
                with mock.patch.object(customer_controller.CustomerModel, "get_by_id", return_value={"id": 33}):
                    with mock.patch.object(customer_controller, "notify_notifications_changed") as notify:
                        self.assertEqual(
                            customer_controller.CustomerController.update_customer(33, "Ana", "Makati", "0917"),
                            (True, {"id": 33}),
                        )
        notify.assert_called_once_with("customer_updated")

    def test_customer_delete_archive_restore_errors_are_safe(self):
        import controllers.customer_controller as customer_controller

        with mock.patch.object(customer_controller.LoginController, "get_current_user", return_value={"id": 9}):
            with mock.patch.object(
                customer_controller.CustomerModel,
                "delete",
                side_effect=RuntimeError("Customer has delivery history"),
            ):
                with mock.patch.object(customer_controller, "log_exception"):
                    ok, message = customer_controller.CustomerController.delete_customer(33)
        self.assertFalse(ok)
        self.assertEqual(message, "Customer has delivery history. Archive instead.")

        with mock.patch.object(customer_controller.LoginController, "get_current_user", return_value={"id": 9}):
            with mock.patch.object(customer_controller.CustomerModel, "archive", return_value=True):
                with mock.patch.object(customer_controller, "notify_notifications_changed") as notify:
                    self.assertEqual(
                        customer_controller.CustomerController.archive_customer(33),
                        (True, "Customer archived."),
                    )
        notify.assert_called_once_with("customer_archived")

        with mock.patch.object(customer_controller.LoginController, "get_current_user", return_value={"id": 9}):
            with mock.patch.object(customer_controller.CustomerModel, "restore", return_value=True):
                with mock.patch.object(customer_controller, "notify_notifications_changed") as notify:
                    self.assertEqual(
                        customer_controller.CustomerController.restore_customer(33),
                        (True, "Customer restored."),
                    )
        notify.assert_called_once_with("customer_restored")


class DeliveryAndProductControllerTest(unittest.TestCase):
    def test_delivery_controller_reads_and_mutations(self):
        import controllers.delivery_controller as delivery_controller

        controller = delivery_controller.DeliveryController()
        with mock.patch.object(delivery_controller.DeliveryModel, "get_all", return_value=["delivery"]):
            self.assertEqual(controller.list_deliveries(), (True, ["delivery"]))
        with mock.patch.object(delivery_controller.DeliveryModel, "get_customer_dropdown", return_value=["customer"]):
            self.assertEqual(controller.list_customers(), (True, ["customer"]))
        with mock.patch.object(delivery_controller.DeliveryModel, "get_product_dropdown", return_value=["product"]):
            self.assertEqual(controller.list_products(), (True, ["product"]))
        with mock.patch.object(delivery_controller.DeliveryModel, "get_items", return_value=["item"]):
            self.assertEqual(controller.get_items(1), (True, ["item"]))

        with mock.patch.object(delivery_controller.DeliveryModel, "update_status", return_value=True):
            with mock.patch.object(delivery_controller, "notify_notifications_changed") as notify:
                self.assertEqual(controller.update_status(1, "delivered"), (True, None))
        notify.assert_called_once_with("delivery_status")

        with mock.patch.object(delivery_controller.DeliveryModel, "create", return_value=44):
            with mock.patch.object(delivery_controller, "notify_notifications_changed"):
                self.assertEqual(controller.create_delivery(1, 2, "2026-05-13", "", []), (True, 44))

        with mock.patch.object(delivery_controller.DeliveryModel, "update", return_value=True):
            with mock.patch.object(delivery_controller, "notify_notifications_changed"):
                self.assertEqual(controller.update_delivery(44, 2, "2026-05-13", "", []), (True, None))

    def test_product_controller_searches_and_updates_view(self):
        import controllers.product_controller as product_controller

        view = FakeView()
        controller = product_controller.ProductController(view=view)

        with mock.patch.object(product_controller.ProductModel, "get_all", return_value=["all"]):
            self.assertEqual(product_controller.ProductController.list_products(), (True, ["all"]))
            controller.on_products_requested("")
        self.assertEqual(view.calls[-1][0], "set_products")

        with mock.patch.object(product_controller.ProductModel, "search", return_value=["match"]) as search:
            self.assertEqual(product_controller.ProductController.search_products("gas"), (True, ["match"]))
        search.assert_called_once_with("gas")

        with mock.patch.object(product_controller.ProductModel, "search", side_effect=RuntimeError("db")):
            with mock.patch.object(product_controller, "log_exception"):
                controller.on_products_requested("gas")
        self.assertEqual(view.calls[-1][0], "show_error")


class DashboardAndLogsControllerTest(unittest.TestCase):
    def test_admin_dashboard_pushes_payload_or_error_to_view(self):
        import controllers.admin_dashboard_controller as admin_controller

        view = FakeView()
        controller = admin_controller.AdminDashboardController(view=None).attach_view(
            view,
            request_initial=False,
        )

        with mock.patch.object(
            admin_controller.AdminDashboardModel,
            "get_all_dashboard_data",
            return_value={"kpi_counts": {}},
        ):
            controller.refresh_dashboard()
        self.assertEqual(view.calls[-1][0], "set_dashboard_data")

        with mock.patch.object(
            admin_controller.AdminDashboardModel,
            "get_all_dashboard_data",
            side_effect=RuntimeError("db"),
        ):
            with mock.patch.object(admin_controller, "log_exception"):
                controller.refresh_dashboard()
        self.assertEqual(view.calls[-1][0], "show_error")

        with mock.patch.object(admin_controller.AdminDashboardModel, "get_kpi_counts", return_value={"total": 1}):
            self.assertEqual(admin_controller.AdminDashboardController.get_kpi_counts(), (True, {"total": 1}))
        with mock.patch.object(admin_controller.AdminDashboardModel, "get_todays_deliveries", return_value=[]):
            self.assertEqual(admin_controller.AdminDashboardController.get_todays_deliveries(), (True, []))
        with mock.patch.object(admin_controller.AdminDashboardModel, "get_unpaid_deliveries", return_value=[]):
            self.assertEqual(admin_controller.AdminDashboardController.get_unpaid_deliveries(), (True, []))

    def test_owner_dashboard_pushes_payload_or_error_to_view(self):
        import controllers.owner_dashboard_controller as owner_controller

        view = FakeView()
        controller = owner_controller.OwnerDashboardController(view=None).attach_view(
            view,
            request_initial=False,
        )

        with mock.patch.object(
            owner_controller.OwnerDashboardModel,
            "get_all_dashboard_data",
            return_value={"sales_kpis": {}},
        ):
            controller.refresh_dashboard()
        self.assertEqual(view.calls[-1][0], "set_dashboard_data")

        with mock.patch.object(
            owner_controller.OwnerDashboardModel,
            "get_all_dashboard_data",
            side_effect=RuntimeError("db"),
        ):
            with mock.patch.object(owner_controller, "log_exception"):
                controller.refresh_dashboard()
        self.assertEqual(view.calls[-1][0], "show_error")

    def test_audit_and_delivery_logs_controllers_use_injected_models(self):
        from controllers.audit_logs_controller import AuditLogsController
        from controllers.delivery_logs_controller import DeliveryLogsController

        audit_view = FakeView()
        audit_model = mock.Mock()
        audit_model.get_logs.return_value = [{"id": 1}]
        self.assertEqual(AuditLogsController(audit_view, audit_model).load(action="Added"), (True, [{"id": 1}]))
        audit_model.get_logs.assert_called_once()
        self.assertEqual(audit_view.calls[-1][0], "load_logs")

        logs_view = FakeView()
        logs_model = mock.Mock()
        logs_model.get_all_logs.return_value = [{"delivery_id": "1"}]
        self.assertEqual(DeliveryLogsController(logs_view, logs_model).load(), (True, [{"delivery_id": "1"}]))
        logs_model.get_all_logs.assert_called_once()
        self.assertEqual(logs_view.calls[-1][0], "load_logs")


class TransactionControllerTest(unittest.TestCase):
    def test_load_and_mark_paid_refresh_view_and_notify(self):
        import controllers.admin_transaction_controller as transaction_controller

        view = FakeView()
        controller = transaction_controller.AdminTransactionController(view=view)
        with mock.patch.object(transaction_controller.TransactionModel, "get_all", return_value=["tx"]):
            self.assertEqual(controller.load("2026-05-01", "2026-05-13"), (True, ["tx"]))
        self.assertEqual(view.calls[-1][0], "load_transactions")

        with mock.patch.object(
            transaction_controller.LoginController,
            "get_current_user",
            return_value={"id": 5},
        ):
            with mock.patch.object(transaction_controller.TransactionModel, "mark_paid", return_value=True):
                with mock.patch.object(transaction_controller.TransactionModel, "get_all", return_value=["fresh"]):
                    with mock.patch.object(transaction_controller, "notify_notifications_changed") as notify:
                        self.assertEqual(controller.mark_paid(9), (True, None))
        notify.assert_called_once_with("transaction_paid")

    def test_mark_paid_value_error_is_not_logged_as_system_failure(self):
        import controllers.admin_transaction_controller as transaction_controller

        view = FakeView()
        controller = transaction_controller.AdminTransactionController(view=view)
        with mock.patch.object(transaction_controller.TransactionModel, "mark_paid", side_effect=ValueError("Already paid")):
            with mock.patch.object(transaction_controller, "log_exception") as log_exception:
                ok, message = controller.mark_paid(9)

        self.assertFalse(ok)
        self.assertEqual(message, "Already paid")
        log_exception.assert_not_called()
        self.assertEqual(view.calls[-1][0], "show_error")


class MessageAndNotificationControllerTest(unittest.TestCase):
    def test_message_controller_validates_staff_user(self):
        import controllers.message_controller as message_controller

        with mock.patch.object(message_controller, "log_exception"):
            self.assertEqual(message_controller.MessageController(user={}).unread_count()[0], False)
            self.assertIn(
                "Only owners and admins",
                message_controller.MessageController(user={"id": 3, "role": "cashier"}).list_conversations()[1],
            )

    def test_message_controller_delegates_to_model(self):
        import controllers.message_controller as message_controller

        controller = message_controller.MessageController(user={"id": 3, "role": "admin"})
        with mock.patch.object(message_controller.MessageModel, "get_unread_count", return_value=2):
            self.assertEqual(controller.unread_count(), (True, 2))
        with mock.patch.object(message_controller.MessageModel, "list_conversations", return_value=["c"]):
            self.assertEqual(controller.list_conversations(), (True, ["c"]))
        with mock.patch.object(message_controller.MessageModel, "mark_thread_read", return_value=True):
            with mock.patch.object(message_controller.MessageModel, "get_thread", return_value=["m"]):
                self.assertEqual(controller.open_conversation("9"), (True, ["m"]))
        with mock.patch.object(message_controller.MessageModel, "send_message", return_value=10):
            self.assertEqual(controller.send_message("9", "hello"), (True, None))

    def test_notification_event_bus_and_controller_methods(self):
        import controllers.notification_controller as notification_controller

        bus = notification_controller.NotificationEventBus()
        reasons = []

        def collect(reason):
            reasons.append(reason)

        bus.notifications_changed.connect(collect)
        bus.notifications_changed.emit("changed")
        self.assertEqual(reasons, ["changed"])

        controller = notification_controller.NotificationController(user={"id": 7, "role": "owner"})
        with mock.patch.object(notification_controller.NotificationModel, "get_for_user", return_value=["n"]):
            self.assertEqual(controller.list_notifications(), (True, ["n"]))
        with mock.patch.object(notification_controller.NotificationModel, "mark_read", return_value=True):
            self.assertEqual(controller.mark_read("key"), (True, None))
        with mock.patch.object(notification_controller.NotificationModel, "mark_many_read", return_value=True):
            self.assertEqual(controller.mark_all_read(["a", "b"]), (True, None))


class OwnerProductControllerTest(unittest.TestCase):
    def test_normalization_price_parsing_and_validation(self):
        import controllers.owner_product_controller as owner_product_controller

        product = {
            "name": " Solane ",
            "cylinder_size": "11",
            "refill_price": "PHP 940.50",
            "new_tank_price": "2,200",
        }
        with mock.patch.object(owner_product_controller.OwnerProductModel, "exists", return_value=False):
            normalized, errors = owner_product_controller.OwnerProductController.validate_product(product)

        self.assertEqual(errors, {})
        self.assertEqual(normalized["name"], "Solane")
        self.assertEqual(normalized["cylinder_size"], "11kg")
        self.assertEqual(normalized["refill_price"], Decimal("940.50"))
        self.assertEqual(normalized["new_tank_price"], Decimal("2200"))

        with mock.patch.object(owner_product_controller.OwnerProductModel, "exists", return_value=False):
            _normalized, errors = owner_product_controller.OwnerProductController.validate_product(
                {"name": "", "cylinder_size": "-1", "refill_price": "x", "new_tank_price": "0"}
            )
        self.assertIn("name", errors)
        self.assertIn("cylinder_size", errors)
        self.assertIn("refill_price", errors)
        self.assertIn("new_tank_price", errors)

    def test_add_update_archive_delete_restore_product_paths(self):
        import controllers.owner_product_controller as owner_product_controller

        controller = owner_product_controller.OwnerProductController()
        product = {
            "id": 42,
            "name": "Solane",
            "cylinder_size": "11kg",
            "refill_price": "940",
            "new_tank_price": "2200",
        }

        with mock.patch.object(owner_product_controller.LoginController, "get_current_user", return_value={"id": 8}):
            with mock.patch.object(owner_product_controller.OwnerProductModel, "exists", return_value=False):
                with mock.patch.object(owner_product_controller.OwnerProductModel, "add", return_value=42):
                    with mock.patch.object(owner_product_controller.OwnerProductModel, "get_by_id", return_value=product):
                        with mock.patch.object(owner_product_controller.OwnerProductModel, "get_all", return_value=[product]):
                            with mock.patch.object(owner_product_controller, "notify_notifications_changed") as notify:
                                self.assertEqual(controller.add_product(product), (True, product))
        notify.assert_called_once_with("product_created")

        with mock.patch.object(owner_product_controller.LoginController, "get_current_user", return_value={"id": 8}):
            with mock.patch.object(owner_product_controller.OwnerProductModel, "exists", return_value=False):
                with mock.patch.object(owner_product_controller.OwnerProductModel, "update", return_value=True):
                    with mock.patch.object(owner_product_controller.OwnerProductModel, "get_by_id", return_value=product):
                        with mock.patch.object(owner_product_controller.OwnerProductModel, "get_all", return_value=[product]):
                            with mock.patch.object(owner_product_controller, "notify_notifications_changed") as notify:
                                self.assertEqual(controller.update_product(product), (True, product))
        notify.assert_called_once_with("product_updated")

        for method_name, model_name, reason in [
            ("archive_product", "archive", "product_archived"),
            ("delete_product", "delete", "product_deleted"),
            ("restore_product", "restore", "product_restored"),
        ]:
            with self.subTest(method_name=method_name):
                with mock.patch.object(owner_product_controller.LoginController, "get_current_user", return_value={"id": 8}):
                    with mock.patch.object(owner_product_controller.OwnerProductModel, model_name, return_value=True):
                        with mock.patch.object(owner_product_controller.OwnerProductModel, "get_all", return_value=[product]):
                            with mock.patch.object(owner_product_controller, "notify_notifications_changed") as notify:
                                self.assertEqual(getattr(controller, method_name)(product), (True, None))
                notify.assert_called_once_with(reason)

    def test_friendly_product_error_maps_expected_database_messages(self):
        import controllers.owner_product_controller as owner_product_controller

        self.assertEqual(
            owner_product_controller.OwnerProductController._friendly_product_error(
                "Product with this name already exists"
            ),
            {"name": owner_product_controller.OwnerProductController.DUPLICATE_PRODUCT_MESSAGE},
        )
        self.assertEqual(
            owner_product_controller.OwnerProductController._friendly_product_error("delivery history"),
            {"form": "This product has delivery history. Archive it instead."},
        )


class ReportControllerTest(unittest.TestCase):
    def test_build_payload_normalizes_summary_and_rows(self):
        from controllers.report_controller import ReportController

        controller = ReportController()
        payload = controller._build_payload(
            "Daily",
            {
                "total_deliveries": "2",
                "total_sales": "1880.5",
                "peak_sales_day": "2026-05-13",
            },
            [
                {
                    "id": 1,
                    "schedule_date": dt.date(2026, 5, 13),
                    "customer": "Ana",
                    "product": "Solane",
                    "quantity": "2",
                    "type": "new_tank",
                    "amount": "1880.5",
                    "payment_status": "unpaid",
                    "delivery_status": "in_transit",
                }
            ],
        )

        self.assertEqual(payload["summary"]["total_deliveries"], 2)
        self.assertEqual(payload["summary"]["total_sales"], 1880.5)
        self.assertEqual(payload["rows"][0]["date"], "2026-05-13")
        self.assertEqual(payload["rows"][0]["type"], "New Tank")

    def test_load_period_merges_completed_snapshot_and_updates_view(self):
        import controllers.report_controller as report_controller

        view = FakeView()
        controller = report_controller.ReportController(view=view)
        date_from = dt.date(2026, 5, 12)
        date_to = dt.date(2026, 5, 12)

        with mock.patch.object(controller, "_today", return_value=dt.date(2026, 5, 13)):
            with mock.patch.object(report_controller.ReportModel, "get_summary", return_value={"total_deliveries": 1}):
                with mock.patch.object(
                    report_controller.ReportModel,
                    "get_daily_snapshot_summary",
                    return_value={"snapshot_count": 1, "total_deliveries": 9, "total_sales": 100},
                ):
                    with mock.patch.object(report_controller.ReportModel, "get_report_insights", return_value={}):
                        with mock.patch.object(report_controller.ReportModel, "get_detailed_breakdown", return_value=[]):
                            ok, payload = controller.load_period("Daily", date_from, date_to)

        self.assertTrue(ok)
        self.assertEqual(payload["summary"]["total_deliveries"], 9)
        self.assertEqual(view.calls[-1][0], "load_report_data")


if __name__ == "__main__":
    unittest.main()
