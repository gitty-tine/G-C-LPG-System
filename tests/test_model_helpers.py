import datetime as dt
import unittest
from decimal import Decimal

from tests.helpers import install_dependency_stubs


install_dependency_stubs()


class DeliveryModelHelpersTest(unittest.TestCase):
    def test_date_note_money_and_display_helpers(self):
        from models.delivery_model import DeliveryModel

        self.assertEqual(DeliveryModel._coerce_date("2026-05-13"), dt.date(2026, 5, 13))
        self.assertEqual(
            DeliveryModel._coerce_date(dt.datetime(2026, 5, 13, 10, 30)),
            dt.date(2026, 5, 13),
        )
        with self.assertRaisesRegex(ValueError, "Invalid schedule date"):
            DeliveryModel._coerce_date("bad-date")

        self.assertIsNone(DeliveryModel._normalize_notes("  "))
        self.assertEqual(DeliveryModel._money("12.345"), Decimal("12.34"))
        self.assertEqual(DeliveryModel._format_money("1234.5"), "1,234.50")
        self.assertEqual(DeliveryModel._format_date(dt.datetime(2026, 5, 13)), "2026-05-13")
        self.assertEqual(DeliveryModel._display_item_type("new_tank"), "New Tank")

    def test_normalize_items_validates_required_fields(self):
        from models.delivery_model import DeliveryModel

        rows = DeliveryModel._normalize_items(
            [
                {
                    "item_id": "",
                    "product_id": "3",
                    "quantity": "2",
                    "type": "New Tank",
                }
            ]
        )

        self.assertEqual(
            rows,
            [{"item_id": None, "product_id": 3, "quantity": 2, "type": "new_tank"}],
        )
        with self.assertRaisesRegex(ValueError, "at least one product"):
            DeliveryModel._normalize_items([])
        with self.assertRaisesRegex(ValueError, "product and quantity"):
            DeliveryModel._normalize_items([{"quantity": 1}])
        with self.assertRaisesRegex(ValueError, "Refill or New Tank"):
            DeliveryModel._normalize_items([{"product_id": 1, "quantity": 1, "type": "lease"}])
        with self.assertRaisesRegex(ValueError, "at least 1"):
            DeliveryModel._normalize_items([{"product_id": 1, "quantity": 0, "type": "refill"}])

    def test_item_matching_and_change_detection(self):
        from models.delivery_model import DeliveryModel

        existing = [
            {"item_id": 7, "product_id": 2, "quantity": 1, "type": "refill"},
            {"item_id": 8, "product_id": 3, "quantity": 2, "type": "new_tank"},
        ]
        incoming = [
            {"item_id": None, "product_id": 2, "quantity": 1, "type": "refill"},
            {"item_id": 8, "product_id": 3, "quantity": 2, "type": "new_tank"},
        ]

        DeliveryModel._attach_exact_existing_item_ids(incoming, existing)
        self.assertEqual(incoming[0]["item_id"], 7)
        self.assertFalse(DeliveryModel._items_changed(incoming, existing))

        changed = [
            {"item_id": 7, "product_id": 2, "quantity": 3, "type": "refill"},
            {"item_id": 8, "product_id": 3, "quantity": 2, "type": "new_tank"},
        ]
        self.assertTrue(DeliveryModel._items_changed(changed, existing))
        self.assertEqual(DeliveryModel._active_product_ids_required(changed, existing), [2])

        with self.assertRaisesRegex(ValueError, "Duplicate delivery item"):
            DeliveryModel._items_changed([incoming[0], incoming[0]], existing)
        with self.assertRaisesRegex(ValueError, "no longer belong"):
            DeliveryModel._items_changed(
                [{"item_id": 999, "product_id": 2, "quantity": 1, "type": "refill"}],
                existing,
            )

    def test_item_totals_catalog_prices_and_audit_formatting(self):
        from models.delivery_model import DeliveryModel

        items = [
            {
                "product_id": 4,
                "product_name": "Regasco 11kg",
                "quantity": 2,
                "type": "refill",
                "price_at_delivery": "940",
            }
        ]

        self.assertEqual(DeliveryModel._items_total(items), Decimal("1880.00"))
        self.assertEqual(
            DeliveryModel._format_items_for_audit(items),
            "Regasco 11kg x2 (Refill) @ Php 940.00",
        )
        self.assertEqual(
            DeliveryModel._catalog_price({"refill_price": "940", "new_tank_price": "2200"}, "refill"),
            Decimal("940.00"),
        )
        with self.assertRaisesRegex(ValueError, "price is invalid"):
            DeliveryModel._catalog_price({"refill_price": "0"}, "refill")


class AuditModelHelpersTest(unittest.TestCase):
    def test_field_name_extraction_and_human_join(self):
        from models.audit_logs_model import _audit_field_names, _human_join

        self.assertEqual(
            _audit_field_names("Name: Old, Address: A", "Name: New, Contact Number: 09"),
            ["Name", "Address", "Contact Number"],
        )
        self.assertEqual(_human_join([]), "")
        self.assertEqual(_human_join(["Name"]), "Name")
        self.assertEqual(_human_join(["Name", "Address"]), "Name and Address")
        self.assertEqual(_human_join(["Name", "Address", "Notes"]), "Name, Address, and Notes")

    def test_apply_change_summaries_updates_update_rows_only(self):
        from models.audit_logs_model import AuditLogModel

        rows = [
            {"raw_action": "UPDATE", "old_value": "Name: Old", "new_value": "Name: New"},
            {"raw_action": "INSERT", "old_value": "-", "new_value": "Name: New"},
        ]

        AuditLogModel._apply_change_summaries(rows)

        self.assertEqual(rows[0]["changed_fields"], ["Name"])
        self.assertEqual(rows[0]["description"], "Name changed")
        self.assertNotIn("changed_fields", rows[1])


class DeliveryLogsModelHelpersTest(unittest.TestCase):
    def test_row_mapping_title_cases_status_fields(self):
        from models.delivery_logs_model import DeliveryLogsModel

        model = DeliveryLogsModel()
        row = model._to_view_dict(
            {
                "delivery_id": "12",
                "customer_name": "juan dela cruz",
                "old_status": "in transit",
                "new_status": "delivered",
                "changed_by": "Admin",
                "changed_at": "May 13",
                "changed_on": dt.date(2026, 5, 13),
                "address": "Manila",
                "scheduled_date": "May 13, 2026",
                "products": "Gas x1",
                "notes": "Gate code",
            }
        )

        self.assertEqual(row["customer_name"], "Juan Dela Cruz")
        self.assertEqual(row["old_status"], "In Transit")
        self.assertEqual(row["new_status"], "Delivered")


class MessageModelHelpersTest(unittest.TestCase):
    def test_user_and_message_normalization(self):
        from models.message_model import MessageModel

        self.assertEqual(MessageModel._role_label("owner"), "Owner")
        self.assertEqual(MessageModel._role_label("admin"), "Admin")
        self.assertEqual(MessageModel._role_label("cashier"), "Staff")
        self.assertEqual(
            MessageModel._normalize_user({"id": "5", "username": "admin", "role": "ADMIN"})[
                "display_name"
            ],
            "admin",
        )
        message = MessageModel._normalize_message(
            {"id": "9", "sender_id": "7", "receiver_id": "8", "body": "Hello"},
            current_user_id=7,
        )
        self.assertTrue(message["is_from_me"])
        self.assertEqual(message["sender_name"], "Staff")

    def test_send_message_validation_runs_before_database_access(self):
        from models.message_model import MessageModel

        with self.assertRaisesRegex(ValueError, "cannot be empty"):
            MessageModel.send_message(1, 2, "  ")
        with self.assertRaisesRegex(ValueError, "too long"):
            MessageModel.send_message(1, 2, "x" * 1001)
        with self.assertRaisesRegex(ValueError, "yourself"):
            MessageModel.send_message(1, 1, "hello")


class NotificationModelHelpersTest(unittest.TestCase):
    def test_basic_formatters_and_snapshot_helpers(self):
        from models.notification_model import NotificationModel

        self.assertEqual(NotificationModel._plural(1, "delivery", "deliveries"), "delivery")
        self.assertEqual(NotificationModel._plural(2, "delivery", "deliveries"), "deliveries")
        self.assertEqual(NotificationModel._money("1234.5"), "PHP 1,234.50")
        self.assertIsNone(NotificationModel._coerce_limit("bad"))
        self.assertEqual(NotificationModel._coerce_limit("3"), 3)
        self.assertEqual(
            NotificationModel._snapshot_map("Name: Juan, Payment Status: unpaid"),
            {"name": "Juan", "payment status": "unpaid"},
        )
        self.assertEqual(NotificationModel._pretty_value("in_transit"), "In Transit")
        self.assertEqual(NotificationModel._record_ref(22), " #22")

    def test_audit_titles_and_messages_are_human_readable(self):
        from models.notification_model import NotificationModel

        delivery_row = {
            "table_name": "deliveries",
            "action": "UPDATE",
            "record_id": 10,
            "changed_by": "Ana",
            "old_value": "Customer: Ben, Status: pending",
            "new_value": "Customer: Ben, Status: delivered",
        }
        transaction_row = {
            "table_name": "transactions",
            "action": "UPDATE",
            "record_id": 8,
            "changed_by": "Ana",
            "old_value": "Payment Status: unpaid",
            "new_value": "Payment Status: paid",
        }

        self.assertEqual(NotificationModel._audit_title(delivery_row), "Delivery status changed")
        self.assertIn("from Pending to Delivered", NotificationModel._audit_message(delivery_row))
        self.assertEqual(NotificationModel._audit_title(transaction_row), "Payment updated")
        self.assertIn("marked transaction #8 as paid", NotificationModel._audit_message(transaction_row))

    def test_record_description_active_change_and_summary_payload(self):
        from models.notification_model import NotificationModel

        self.assertEqual(
            NotificationModel._record_description(
                "lpg_products",
                {"name": "Solane", "size": "11kg"},
            ),
            "Solane 11kg",
        )
        self.assertEqual(
            NotificationModel._active_change({"active": "yes"}, {"active": "no"}),
            "archived",
        )
        self.assertEqual(
            NotificationModel._changed_fields({"name": "Old"}, {"name": "New"}),
            ["Name changed from Old to New"],
        )
        payload = NotificationModel._summary_notification(
            "key",
            "Title",
            "Message",
            "Deliveries",
            "high",
            "deliveries",
            "now",
            "May 13",
        )
        self.assertEqual(payload["severity_label"], "High")
        self.assertEqual(payload["source"], "summary")


class OwnerDashboardModelHelpersTest(unittest.TestCase):
    def test_date_bounds_and_default_merging(self):
        from models.owner_dashboard_model import OwnerDashboardModel

        day = dt.date(2026, 5, 13)
        self.assertEqual(
            OwnerDashboardModel._week_bounds(day),
            (dt.date(2026, 5, 11), dt.date(2026, 5, 17)),
        )
        self.assertEqual(
            OwnerDashboardModel._month_bounds(day),
            (dt.date(2026, 5, 1), dt.date(2026, 5, 31)),
        )
        self.assertEqual(
            OwnerDashboardModel._previous_month_bounds(day),
            (dt.date(2026, 4, 1), dt.date(2026, 4, 30)),
        )
        merged = OwnerDashboardModel._merge_defaults({"a": 1, "b": 2}, {"b": 9})
        self.assertEqual(merged, {"a": 1, "b": 9})


class ReportModelHelpersTest(unittest.TestCase):
    def test_month_start_coerces_common_inputs(self):
        from models.report_model import ReportModel

        self.assertEqual(ReportModel._month_start("2026-05-13"), dt.date(2026, 5, 1))
        self.assertEqual(
            ReportModel._month_start(dt.datetime(2026, 12, 31, 23, 59)),
            dt.date(2026, 12, 1),
        )


class ProductModelHelpersTest(unittest.TestCase):
    def test_price_helpers_return_decimals(self):
        from models.owner_product_model import OwnerProductModel
        from models.product_model import ProductModel

        self.assertEqual(ProductModel._price("12.50"), Decimal("12.50"))
        self.assertEqual(OwnerProductModel._price("99.99"), Decimal("99.99"))


if __name__ == "__main__":
    unittest.main()
