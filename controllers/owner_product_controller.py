import os
import re
import sys
from decimal import Decimal, InvalidOperation

from PySide6.QtCore import QObject

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.owner_product_model import OwnerProductModel
from controllers.login_controller import LoginController
from controllers.notification_controller import notify_notifications_changed


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

    @staticmethod
    def _normalize_product_payload(product):
        normalized = dict(product or {})
        normalized["name"] = (normalized.get("name") or "").strip()

        size = (normalized.get("cylinder_size") or "").strip()
        if size and not size.lower().endswith("kg"):
            size = size + "kg"
        normalized["cylinder_size"] = size

        normalized["refill_price"] = OwnerProductController._parse_price(
            normalized.get("refill_price")
        )
        normalized["new_tank_price"] = OwnerProductController._parse_price(
            normalized.get("new_tank_price")
        )
        return normalized

    @staticmethod
    def _parse_price(value):
        try:
            raw = str(value).strip().replace("PHP", "").replace("Php", "").replace(",", "")
            if not raw:
                return None
            return Decimal(raw)
        except (InvalidOperation, ValueError):
            return None

    @staticmethod
    def _parse_cylinder_size(size):
        raw = (size or "").strip()
        if not raw:
            return None

        match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*kg?", raw, re.IGNORECASE)
        if match:
            return float(match.group(1))

        match = re.fullmatch(r"(\d+(?:\.\d+)?)", raw)
        if match:
            return float(match.group(1))

        return None

    @staticmethod
    def _friendly_product_error(exc):
        raw_message = str(exc or "").strip()
        lowered = raw_message.lower()
        cleaned = re.sub(r"^\d+\s*\([^)]+\)\s*:\s*", "", raw_message).strip()

        if "product with this name already exists" in lowered or "name already exists" in lowered:
            return {"name": "Product already exists."}

        if "same name and size" in lowered or "name and cylinder size" in lowered:
            return {"name": "Product already exists."}

        if "product is already active" in lowered:
            return {"form": "This product is already active."}

        if "already active" in lowered or "already exists" in lowered:
            return {"name": "Product already exists."}

        if "product with id" in lowered and "not found" in lowered:
            return {"form": "This product could not be found anymore. Please refresh and try again."}

        if "active product" in lowered:
            return {"form": "This product is no longer active. Please refresh and try again."}

        if "delivery history" in lowered or "cannot be permanently deleted" in lowered:
            return {"form": "This product has delivery history. Archive it instead."}

        return {"form": cleaned or "Unable to save the product. Please try again."}

    @staticmethod
    def validate_product(product, product_id=None):
        normalized = OwnerProductController._normalize_product_payload(product)
        errors = {}

        if not normalized["name"]:
            errors["name"] = "Product name is required."
        if not normalized["cylinder_size"]:
            errors["cylinder_size"] = "Cylinder size is required."
        else:
            size_value = OwnerProductController._parse_cylinder_size(
                normalized["cylinder_size"]
            )
            if size_value is None:
                errors["cylinder_size"] = "Enter a valid cylinder size like 2.7 or 11kg."
            elif size_value <= 0:
                errors["cylinder_size"] = "Cylinder size must be greater than zero."

        if normalized["refill_price"] is None:
            errors["refill_price"] = "Refill price must be a valid number."
        elif normalized["refill_price"] <= 0:
            errors["refill_price"] = "Prices must be greater than zero."
        if normalized["new_tank_price"] is None:
            errors["new_tank_price"] = "New tank price must be a valid number."
        elif normalized["new_tank_price"] <= 0:
            errors["new_tank_price"] = "Prices must be greater than zero."

        if not errors:
            if product_id:
                exists = OwnerProductModel.exists(
                    normalized["name"],
                    normalized["cylinder_size"],
                    exclude_id=product_id,
                )
                if exists:
                    errors["name"] = "A product with this name already exists."
            elif OwnerProductModel.exists(normalized["name"], normalized["cylinder_size"]):
                errors["name"] = "A product with this name already exists."

        return normalized, errors

    def attach_view(self, view):
        self._view = view
        return self

    # Public actions -----------------------------------------------------------------
    def refresh_products(self, archived=False):
        ok, res = self.list_products(archived=archived)
        if ok:
            self._push(res)
        else:
            self._error("Load Failed", res)

    def search_products(self, keyword, archived=False):
        ok, res = self.search(keyword, archived=archived)
        if ok:
            self._push(res)
        else:
            self._error("Search Failed", res)

    def add_product(self, product):
        try:
            normalized, errors = self.validate_product(product)
            if errors:
                return False, errors
            user_id = self._current_user_id()
            new_id = OwnerProductModel.add(
                normalized["name"],
                normalized["cylinder_size"],
                normalized["refill_price"],
                normalized["new_tank_price"],
                user_id=user_id,
            )
            created = OwnerProductModel.get_by_id(new_id)
            self.refresh_products()
            notify_notifications_changed("product_created")
            return True, created
        except Exception as exc:
            return False, self._friendly_product_error(exc)

    def update_product(self, product):
        try:
            product_id = product.get("id")
            if not product_id:
                return False, {"form": "Product id is required for update."}
            normalized, errors = self.validate_product(product, product_id=product_id)
            if errors:
                return False, errors
            user_id = self._current_user_id()
            OwnerProductModel.update(
                product_id,
                normalized["name"],
                normalized["cylinder_size"],
                normalized["refill_price"],
                normalized["new_tank_price"],
                user_id=user_id,
            )
            after = OwnerProductModel.get_by_id(product_id)
            self.refresh_products()
            notify_notifications_changed("product_updated")
            return True, after
        except Exception as exc:
            return False, self._friendly_product_error(exc)

    def archive_product(self, product):
        try:
            product_id = product.get("id")
            if not product_id:
                raise ValueError("Product id is required for archive.")
            user_id = self._current_user_id()
            OwnerProductModel.archive(product_id, user_id=user_id)
            self.refresh_products()
            notify_notifications_changed("product_archived")
            return True, None
        except Exception as exc:
            self._error("Archive Product Failed", exc)
            return False, self._friendly_product_error(exc)

    def delete_product(self, product, archived=False):
        try:
            product_id = product.get("id")
            if not product_id:
                raise ValueError("Product id is required for deletion.")
            user_id = self._current_user_id()
            OwnerProductModel.delete(product_id, user_id=user_id)
            self.refresh_products(archived=archived)
            notify_notifications_changed("product_deleted")
            return True, None
        except Exception as exc:
            return False, self._friendly_product_error(exc)

    def restore_product(self, product):
        try:
            product_id = product.get("id")
            if not product_id:
                raise ValueError("Product id is required for restore.")
            user_id = self._current_user_id()
            OwnerProductModel.restore(product_id, user_id=user_id)
            self.refresh_products(archived=True)
            notify_notifications_changed("product_restored")
            return True, None
        except Exception as exc:
            return False, self._friendly_product_error(exc)

    # Static helpers (legacy-style) --------------------------------------------------
    @staticmethod
    def list_products(archived=False):
        try:
            return True, OwnerProductModel.get_all(archived=archived)
        except Exception as e:
            return False, str(e)

    @staticmethod
    def search(keyword, archived=False):
        try:
            kw = (keyword or "").strip()
            if not kw:
                return True, OwnerProductModel.get_all(archived=archived)
            return True, OwnerProductModel.search(kw, archived=archived)
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
