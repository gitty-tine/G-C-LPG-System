import sys
import os

from PySide6.QtCore import QObject, Slot

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.product_model import ProductModel


class ProductController(QObject):
    """
    Read-only controller for product catalog used in the admin view.

    Static helpers keep legacy call sites working (returning (success, payload)),
    while instance methods act as Qt slots that talk to a view via set_products/show_error.
    """

    def __init__(self, view=None):
        super().__init__()
        self._view = view

    def attach_view(self, view):
        """Assign/replace the view this controller should update."""
        self._view = view
        return self

    @Slot(str)
    def on_products_requested(self, keyword):
        """Qt slot compatible with ProductView.productsRequested Signal."""
        ok, res = self.search_products(keyword)
        if not self._view:
            return
        if ok:
            self._view.set_products(res)
        else:
            title = "Search Failed" if keyword else "Load Failed"
            self._view.show_error(title, res)

    @staticmethod
    def list_products():
        try:
            return True, ProductModel.get_all()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def search_products(keyword):
        try:
            if not keyword:
                return True, ProductModel.get_all()
            return True, ProductModel.search(keyword)
        except Exception as e:
            return False, str(e)


# Convenience aliases
def list_products():
    return ProductController.list_products()


def search_products(keyword):
    return ProductController.search_products(keyword)
