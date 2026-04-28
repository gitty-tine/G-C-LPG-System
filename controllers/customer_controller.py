import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.customer_model import CustomerModel
from controllers.login_controller import LoginController


class CustomerController:

    @staticmethod
    def _current_user_id():
        user = LoginController.get_current_user()
        if user and isinstance(user, dict):
            return user.get("id", 0)
        return 0

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
            user_id = CustomerController._current_user_id()
            new_id = CustomerModel.add(full_name, address, contact_number, notes, user_id=user_id)
            created = CustomerModel.get_by_id(new_id)
            return True, created
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update_customer(customer_id, full_name, address, contact_number, notes=""):
        try:
            user_id = CustomerController._current_user_id()
            CustomerModel.update(customer_id, full_name, address, contact_number, notes, user_id=user_id)
            updated = CustomerModel.get_by_id(customer_id)
            return True, updated
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete_customer(customer_id):
        try:
            user_id = CustomerController._current_user_id()
            CustomerModel.delete(customer_id, user_id=user_id)
            return True, "Customer deleted."
        except Exception as e:
            return False, str(e)

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
