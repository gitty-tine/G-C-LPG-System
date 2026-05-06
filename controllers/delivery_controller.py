import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.delivery_model import DeliveryModel
from controllers.notification_controller import notify_notifications_changed
from utils.error_logger import log_exception


class DeliveryController:

    def list_deliveries(self):
        try:
            return True, DeliveryModel.get_all()
        except Exception as e:
            log_exception(e, source="controllers.delivery_controller", action="list_deliveries")
            return False, str(e)

    def list_customers(self):
        try:
            return True, DeliveryModel.get_customer_dropdown()
        except Exception as e:
            log_exception(e, source="controllers.delivery_controller", action="list_customers")
            return False, str(e)

    def list_products(self):
        try:
            return True, DeliveryModel.get_product_dropdown()
        except Exception as e:
            log_exception(e, source="controllers.delivery_controller", action="list_products")
            return False, str(e)

    def get_items(self, delivery_id):
        try:
            return True, DeliveryModel.get_items(delivery_id)
        except Exception as e:
            log_exception(
                e,
                source="controllers.delivery_controller",
                action="get_items",
                context={"delivery_id": delivery_id},
            )
            return False, str(e)

    def update_status(self, delivery_id, new_status, user_id=None):
        try:
            DeliveryModel.update_status(delivery_id, new_status, user_id or 0)
            notify_notifications_changed("delivery_status")
            return True, None
        except Exception as e:
            log_exception(
                e,
                source="controllers.delivery_controller",
                action="update_status",
                context={"delivery_id": delivery_id, "new_status": new_status},
            )
            return False, str(e)

    def create_delivery(self, customer_id, user_id, schedule_date, notes, items):
        try:
            new_id = DeliveryModel.create(customer_id, user_id, schedule_date, notes, items)
            notify_notifications_changed("delivery_created")
            return True, new_id
        except Exception as e:
            log_exception(
                e,
                source="controllers.delivery_controller",
                action="create_delivery",
                context={"customer_id": customer_id, "schedule_date": schedule_date},
            )
            return False, str(e)

    def update_delivery(self, delivery_id, user_id, schedule_date, notes, items):
        try:
            DeliveryModel.update(delivery_id, user_id or 0, schedule_date, notes, items)
            notify_notifications_changed("delivery_updated")
            return True, None
        except Exception as e:
            log_exception(
                e,
                source="controllers.delivery_controller",
                action="update_delivery",
                context={"delivery_id": delivery_id, "schedule_date": schedule_date},
            )
            return False, str(e)
