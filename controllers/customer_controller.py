import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.customer_model import CustomerModel
from controllers.login_controller import LoginController
from controllers.notification_controller import notify_notifications_changed


class CustomerController:

    @staticmethod
    def _current_user_id():
        user = LoginController.get_current_user()
        if user and isinstance(user, dict):
            return user.get("id", 0)
        return 0

    @staticmethod
    def _friendly_customer_error(exc, action=None):
        message = str(exc or "").strip()
        lowered = message.lower()

        if "data too long for condition item" in lowered and "message_text" in lowered:
            if action == "delete":
                return "Customer has delivery history. Archive instead."
            return "The database rejected this action. Please try again."

        if action == "delete" and (
            "delivery history" in lowered
            or "delivery records" in lowered
            or "permanently deleted" in lowered
        ):
            return "Customer has delivery history. Archive instead."

        return message

    @staticmethod
    def list_customers(archived=False):
        try:
            return True, CustomerModel.get_all(archived=archived)
        except Exception as e:
            return False, str(e)

    @staticmethod
    def search_customers(keyword, archived=False):
        try:
            if not keyword:
                return True, CustomerModel.get_all(archived=archived)
            return True, CustomerModel.search(keyword, archived=archived)
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_active_customers():
        try:
            return True, CustomerModel.get_active()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def add_customer(full_name, address, contact_number, notes=""):
        try:
            user_id = CustomerController._current_user_id()
            new_id = CustomerModel.add(full_name, address, contact_number, notes, user_id=user_id)
            created = CustomerModel.get_by_id(new_id)
            notify_notifications_changed("customer_created")
            return True, created
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update_customer(customer_id, full_name, address, contact_number, notes=""):
        try:
            user_id = CustomerController._current_user_id()
            CustomerModel.update(customer_id, full_name, address, contact_number, notes, user_id=user_id)
            updated = CustomerModel.get_by_id(customer_id)
            notify_notifications_changed("customer_updated")
            return True, updated
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete_customer(customer_id):
        try:
            user_id = CustomerController._current_user_id()
            CustomerModel.delete(customer_id, user_id=user_id)
            notify_notifications_changed("customer_deleted")
            return True, "Customer deleted."
        except Exception as e:
            return False, CustomerController._friendly_customer_error(e, action="delete")

    @staticmethod
    def archive_customer(customer_id):
        try:
            user_id = CustomerController._current_user_id()
            CustomerModel.archive(customer_id, user_id=user_id)
            notify_notifications_changed("customer_archived")
            return True, "Customer archived."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def restore_customer(customer_id):
        try:
            user_id = CustomerController._current_user_id()
            CustomerModel.restore(customer_id, user_id=user_id)
            notify_notifications_changed("customer_restored")
            return True, "Customer restored."
        except Exception as e:
            return False, str(e)

def list_customers(archived=False):
    return CustomerController.list_customers(archived=archived)

def search_customers(keyword, archived=False):
    return CustomerController.search_customers(keyword, archived=archived)

def get_active_customers():
    return CustomerController.get_active_customers()

def add_customer(full_name, address, contact_number, notes=""):
    return CustomerController.add_customer(full_name, address, contact_number, notes)

def update_customer(customer_id, full_name, address, contact_number, notes=""):
    return CustomerController.update_customer(customer_id, full_name, address, contact_number, notes)

def delete_customer(customer_id):
    return CustomerController.delete_customer(customer_id)

def archive_customer(customer_id):
    return CustomerController.archive_customer(customer_id)

def restore_customer(customer_id):
    return CustomerController.restore_customer(customer_id)
