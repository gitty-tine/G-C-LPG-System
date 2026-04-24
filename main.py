import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from views.login_view import main as run_login


def main():
    run_login()


if __name__ == "__main__":
    main()
    