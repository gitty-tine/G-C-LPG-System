import os
import sys

from PySide6.QtCore import QObject

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.owner_product_model import OwnerProductModel
from models.audit_actor_model import AuditActorModel
from controllers.login_controller import LoginController


class OwnerProductController(QObject):
    """
    Controller for owner product management.
    Bridges OwnerProductsView <-> OwnerProductModel with simple CRUD + search.
    """

    def __init__(self, view=None):
        super().__init__()
        self._view = view

    @staticmethod
    def _current_user_id():
        user = LoginController.get_current_user()
        if user and isinstance(user, dict):
            return user.get("id", 0)
        return 0

    @staticmethod
    def _product_snapshot(product):
        if not product:
            return "-"
        name = (product.get("name") or "").strip()
        size = (product.get("cylinder_size") or "").strip()
        refill = product.get("refill_price")
        new_tank = product.get("new_tank_price")
        return ", ".join(
            part for part in (
                " ".join(x for x in (name, size) if x).strip(),
                f"Refill: {refill}",
                f"New Tank: {new_tank}",
            ) if part
        ) or "-"

    def attach_view(self, view):
        self._view = view
        return self

    # Public actions -----------------------------------------------------------------
    def refresh_products(self):
        ok, res = self.list_products()
        if ok:
            self._push(res)
        else:
            self._error("Load Failed", res)

    def search_products(self, keyword):
        ok, res = self.search(keyword)
        if ok:
            self._push(res)
        else:
            self._error("Search Failed", res)

    def add_product(self, product):
        try:
            name = (product.get("name") or "").strip()
            size = (product.get("cylinder_size") or "").strip()
            refill = float(product.get("refill_price"))
            new_tank = float(product.get("new_tank_price"))
            if not name or not size:
                raise ValueError("Name and cylinder size are required.")
            if OwnerProductModel.exists(name, size):
                raise ValueError("A product with the same name and size already exists.")
            new_id = OwnerProductModel.add(name, size, refill, new_tank)
            product["id"] = new_id
            created = OwnerProductModel.get_by_id(new_id)
            AuditActorModel.sync_actor(
                "lpg_products",
                new_id,
                "INSERT",
                self._current_user_id(),
                old_value="-",
                new_value=self._product_snapshot(created),
            )
            self.refresh_products()
        except Exception as exc:  # pylint: disable=broad-except
            self._error("Add Product Failed", exc)

    def update_product(self, product):
        try:
            product_id = product.get("id")
            if not product_id:
                raise ValueError("Product id is required for update.")
            name = (product.get("name") or "").strip()
            size = (product.get("cylinder_size") or "").strip()
            refill = float(product.get("refill_price"))
            new_tank = float(product.get("new_tank_price"))
            if not name or not size:
                raise ValueError("Name and cylinder size are required.")
            if OwnerProductModel.exists(name, size, exclude_id=product_id):
                raise ValueError("Another product with the same name and size exists.")
            before = OwnerProductModel.get_by_id(product_id)
            OwnerProductModel.update(product_id, name, size, refill, new_tank)
            after = OwnerProductModel.get_by_id(product_id)
            AuditActorModel.sync_actor(
                "lpg_products",
                product_id,
                "UPDATE",
                self._current_user_id(),
                old_value=self._product_snapshot(before),
                new_value=self._product_snapshot(after),
            )
            self.refresh_products()
        except Exception as exc:  # pylint: disable=broad-except
            self._error("Update Product Failed", exc)

    def delete_product(self, product):
        try:
            product_id = product.get("id")
            if not product_id:
                raise ValueError("Product id is required for deletion.")
            existing = OwnerProductModel.get_by_id(product_id)
            OwnerProductModel.delete(product_id)
            AuditActorModel.sync_actor(
                "lpg_products",
                product_id,
                "DELETE",
                self._current_user_id(),
                old_value=self._product_snapshot(existing),
                new_value="-",
            )
            self.refresh_products()
        except Exception as exc:  # pylint: disable=broad-except
            self._error("Delete Product Failed", exc)

    # Static helpers (legacy-style) --------------------------------------------------
    @staticmethod
    def list_products():
        try:
            return True, OwnerProductModel.get_all()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def search(keyword):
        try:
            kw = (keyword or "").strip()
            if not kw:
                return True, OwnerProductModel.get_all()
            return True, OwnerProductModel.search(kw)
        except Exception as e:
            return False, str(e)

    # Internal helpers ---------------------------------------------------------------
    def _push(self, products):
        if self._view and hasattr(self._view, "load_products"):
            self._view.load_products(products)

    def _error(self, title, message):
        if self._view and hasattr(self._view, "show_error"):
            self._view.show_error(title, message)
        else:
            # Fallback to stderr for debugging when no view is attached.
            sys.stderr.write(f"{title}: {message}\n")
