import os
import re
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

    @staticmethod
    def _normalize_product_payload(product):
        normalized = dict(product or {})
        normalized["name"] = (normalized.get("name") or "").strip()

        size = (normalized.get("cylinder_size") or "").strip()
        if size and not size.lower().endswith("kg"):
            size = size + "kg"
        normalized["cylinder_size"] = size

        normalized["refill_price"] = float(normalized.get("refill_price"))
        normalized["new_tank_price"] = float(normalized.get("new_tank_price"))
        return normalized

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

        if "same name and size" in lowered:
            return {"name": "Product already exists."}

        if "product with id" in lowered and "not found" in lowered:
            return {"form": "This product could not be found anymore. Please refresh and try again."}

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

        if normalized["refill_price"] <= 0:
            errors["refill_price"] = "Prices must be greater than zero."
        if normalized["new_tank_price"] <= 0:
            errors["new_tank_price"] = "Prices must be greater than zero."

        if not errors:
            clean_name = re.sub(r"[^a-zA-Z0-9\s]", "", normalized["name"]).strip()
            normalized["name"] = clean_name
            if product_id:
                exists = OwnerProductModel.exists(
                    clean_name,
                    normalized["cylinder_size"],
                    exclude_id=product_id,
                )
                if exists:
                    errors["name"] = "A product with this name already exists."
            elif OwnerProductModel.exists(clean_name, normalized["cylinder_size"]):
                errors["name"] = "A product with this name already exists."

        return normalized, errors

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
            normalized, errors = self.validate_product(product)
            if errors:
                return False, errors

            new_id = OwnerProductModel.add(
                normalized["name"],
                normalized["cylinder_size"],
                normalized["refill_price"],
                normalized["new_tank_price"],
            )
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
            return True, created
        except Exception as exc:  # pylint: disable=broad-except
            return False, self._friendly_product_error(exc)

    def update_product(self, product):
        try:
            product_id = product.get("id")
            if not product_id:
                return False, {"form": "Product id is required for update."}

            normalized, errors = self.validate_product(product, product_id=product_id)
            if errors:
                return False, errors

            before = OwnerProductModel.get_by_id(product_id)
            OwnerProductModel.update(
                product_id,
                normalized["name"],
                normalized["cylinder_size"],
                normalized["refill_price"],
                normalized["new_tank_price"],
            )
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
            return True, after
        except Exception as exc:  # pylint: disable=broad-except
            return False, self._friendly_product_error(exc)

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
