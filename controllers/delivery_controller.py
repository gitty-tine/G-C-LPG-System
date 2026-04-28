import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.delivery_model import DeliveryModel


class DeliveryController:

    @staticmethod
    def _delivery_snapshot(delivery):
        if not delivery:
            return "-"
        return ", ".join(
            str(part).strip()
            for part in (
                f"Customer: {delivery.get('customer_name', '')}",
                f"Date: {delivery.get('schedule_date_fmt') or delivery.get('schedule_date') or ''}",
                f"Status: {delivery.get('status', '')}",
            )
            if str(part).strip()
        ) or "-"

    def list_deliveries(self):
        try:
            return True, DeliveryModel.get_all()
        except Exception as e:
            return False, str(e)

    def list_customers(self):
        try:
            return True, DeliveryModel.get_customer_dropdown()
        except Exception as e:
            return False, str(e)

    def list_products(self):
        try:
            return True, DeliveryModel.get_product_dropdown()
        except Exception as e:
            return False, str(e)

    def get_items(self, delivery_id):
        try:
            return True, DeliveryModel.get_items(delivery_id)
        except Exception as e:
            return False, str(e)

    def get_summary(self):
        try:
            return True, DeliveryModel.get_summary_counts()
        except Exception as e:
            return False, str(e)

    def update_status(self, delivery_id, new_status, user_id=None):
        try:
            DeliveryModel.update_status(delivery_id, new_status, user_id or 0)
            return True, None
        except Exception as e:
            return False, str(e)

    def create_delivery(self, customer_id, user_id, schedule_date, notes, items):
        try:
            new_id = DeliveryModel.create(customer_id, user_id, schedule_date, notes, items)
            return True, new_id
        except Exception as e:
            return False, str(e)
