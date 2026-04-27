import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.customer_model import CustomerModel
from models.audit_actor_model import AuditActorModel
from controllers.login_controller import LoginController


class CustomerController:
    """
    Thin controller layer that wires CustomerModel to any views.
    Returns (success, payload) tuples where payload is either data or an error message.
    """

    @staticmethod
    def _current_user_id():
        user = LoginController.get_current_user()
        if user and isinstance(user, dict):
            return user.get("id", 0)
        return 0

    @staticmethod
    def _customer_snapshot(customer):
        if not customer:
            return "-"
        return ", ".join(
            str(part).strip()
            for part in (
                customer.get("full_name", ""),
                customer.get("address", ""),
                customer.get("contact_number", ""),
            )
            if str(part).strip()
        ) or "-"

    @staticmethod
    def list_customers():
        try:
            return True, CustomerModel.get_all()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def search_customers(keyword):
        try:
            if not keyword:
                return True, CustomerModel.get_all()
            return True, CustomerModel.search(keyword)
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
            new_id = CustomerModel.add(full_name, address, contact_number, notes)
            created = CustomerModel.get_by_id(new_id)
            AuditActorModel.sync_actor(
                "customers",
                new_id,
                "INSERT",
                CustomerController._current_user_id(),
                old_value="-",
                new_value=CustomerController._customer_snapshot(created),
            )
            return True, created
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update_customer(customer_id, full_name, address, contact_number, notes=""):
        try:
            before = CustomerModel.get_by_id(customer_id)
            CustomerModel.update(customer_id, full_name, address, contact_number, notes)
            updated = CustomerModel.get_by_id(customer_id)
            AuditActorModel.sync_actor(
                "customers",
                customer_id,
                "UPDATE",
                CustomerController._current_user_id(),
                old_value=CustomerController._customer_snapshot(before),
                new_value=CustomerController._customer_snapshot(updated),
            )
            return True, updated
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete_customer(customer_id):
        try:
            existing = CustomerModel.get_by_id(customer_id)
            CustomerModel.delete(customer_id)
            AuditActorModel.sync_actor(
                "customers",
                customer_id,
                "DELETE",
                CustomerController._current_user_id(),
                old_value=CustomerController._customer_snapshot(existing),
                new_value="-",
            )
            return True, "Customer deleted."
        except Exception as e:
            return False, str(e)


# Convenience functions for quick imports
def list_customers():
    return CustomerController.list_customers()


def search_customers(keyword):
    return CustomerController.search_customers(keyword)


def get_active_customers():
    return CustomerController.get_active_customers()


def add_customer(full_name, address, contact_number, notes=""):
    return CustomerController.add_customer(full_name, address, contact_number, notes)


def update_customer(customer_id, full_name, address, contact_number, notes=""):
    return CustomerController.update_customer(customer_id, full_name, address, contact_number, notes)


def delete_customer(customer_id):
    return CustomerController.delete_customer(customer_id)
