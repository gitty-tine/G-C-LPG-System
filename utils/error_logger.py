import json
import os
import sys
import traceback

from database.connection import get_connection


CREATE_ERROR_LOGS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS error_logs (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NULL,
    username VARCHAR(50) NULL,
    user_role VARCHAR(20) NULL,
    severity ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') NOT NULL DEFAULT 'ERROR',
    status ENUM('new', 'reviewed', 'resolved') NOT NULL DEFAULT 'new',
    source VARCHAR(120) NOT NULL,
    action VARCHAR(160) NULL,
    exception_type VARCHAR(120) NULL,
    error_message TEXT NOT NULL,
    user_message TEXT NULL,
    module_name VARCHAR(160) NULL,
    function_name VARCHAR(160) NULL,
    file_path VARCHAR(255) NULL,
    line_number INT NULL,
    traceback_text LONGTEXT NULL,
    context_json JSON NULL,
    python_version VARCHAR(80) NULL,
    platform_info VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_error_logs_user_id (user_id),
    KEY idx_error_logs_severity (severity),
    KEY idx_error_logs_source (source),
    KEY idx_error_logs_created_at_id (created_at, id),
    CONSTRAINT error_logs_ibfk_1
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
"""

CREATE_ERROR_LOGS_VIEW_SQL = """
CREATE OR REPLACE VIEW vw_error_logs AS
SELECT
    e.id,
    e.created_at,
    DATE_FORMAT(e.created_at, '%b %d, %Y %h:%i %p') AS logged_at,
    e.severity,
    e.status,
    e.source,
    e.action,
    e.exception_type,
    e.error_message,
    e.user_message,
    COALESCE(e.username, u.username, 'System') AS username,
    COALESCE(e.user_role, u.role, 'system') AS user_role,
    e.module_name,
    e.function_name,
    e.file_path,
    e.line_number,
    e.context_json,
    e.traceback_text,
    e.python_version,
    e.platform_info
FROM error_logs e
LEFT JOIN users u ON u.id = e.user_id
"""

INSERT_ERROR_LOG_SQL = """
INSERT INTO error_logs (
    user_id,
    username,
    user_role,
    severity,
    source,
    action,
    exception_type,
    error_message,
    user_message,
    module_name,
    function_name,
    file_path,
    line_number,
    traceback_text,
    context_json,
    python_version,
    platform_info
) VALUES (
    %(user_id)s,
    %(username)s,
    %(user_role)s,
    %(severity)s,
    %(source)s,
    %(action)s,
    %(exception_type)s,
    %(error_message)s,
    %(user_message)s,
    %(module_name)s,
    %(function_name)s,
    %(file_path)s,
    %(line_number)s,
    %(traceback_text)s,
    %(context_json)s,
    %(python_version)s,
    %(platform_info)s
)
"""

VALID_SEVERITIES = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

_table_ready = False
_hooks_installed = False
_original_excepthook = None
_is_logging = False


def ensure_error_logs_table():
    """Create the error log table and readable view if they do not exist."""
    global _table_ready

    if _table_ready:
        return True

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(CREATE_ERROR_LOGS_TABLE_SQL)
        cursor.execute(CREATE_ERROR_LOGS_VIEW_SQL)
        conn.commit()
        _table_ready = True
        return True
    except Exception as exc:
        _print_error(f"Could not prepare error_logs table: {exc}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def install_error_logging_hooks():
    """Log unhandled application errors before Python prints them."""
    global _hooks_installed
    global _original_excepthook

    if _hooks_installed:
        return

    ensure_error_logs_table()
    _original_excepthook = sys.excepthook

    def handle_unhandled_error(exc_type, exc_value, exc_traceback):
        log_exception(
            exc_value,
            source="application",
            action="unhandled_exception",
            severity="CRITICAL",
            context={"hook": "sys.excepthook"},
        )
        _original_excepthook(exc_type, exc_value, exc_traceback)

    sys.excepthook = handle_unhandled_error
    _hooks_installed = True


def log_exception(
    exc=None,
    *,
    source=None,
    action=None,
    severity="ERROR",
    user_message=None,
    context=None,
    user=None,
    force=False,
):
    """
    Save an exception to error_logs.

    This function is safe to call inside except blocks. It will not raise a new
    error if logging fails.
    """
    global _is_logging

    exc_type, exc_value, exc_traceback = sys.exc_info()
    if exc is None:
        exc = exc_value
    if exc is None:
        return None
    if isinstance(exc, (KeyboardInterrupt, SystemExit)):
        return None
    if not isinstance(exc, BaseException):
        exc = RuntimeError(str(exc))
        exc_type = RuntimeError
        exc_traceback = None
        force = True
    elif exc is not exc_value:
        exc_type = type(exc)
        exc_traceback = exc.__traceback__

    if _is_logging:
        return None
    if not force and _already_logged(exc):
        return None

    _mark_logged(exc)
    _is_logging = True

    conn = None
    cursor = None
    try:
        if not ensure_error_logs_table():
            return None

        user_info = _user_info(user)
        details = _exception_details(exc, exc_type, exc_traceback)
        data = {
            "user_id": user_info["id"],
            "username": _shorten(user_info["username"], 50),
            "user_role": _shorten(user_info["role"], 20),
            "severity": _severity(severity),
            "source": _shorten(source or details["module_name"] or "application", 120),
            "action": _shorten(action, 160),
            "exception_type": _shorten(details["exception_type"], 120),
            "error_message": _shorten(details["error_message"] or "Unknown error", 60000),
            "user_message": _shorten(user_message, 60000),
            "module_name": _shorten(details["module_name"], 160),
            "function_name": _shorten(details["function_name"], 160),
            "file_path": _shorten(details["file_path"], 255),
            "line_number": details["line_number"],
            "traceback_text": details["traceback_text"],
            "context_json": _json_text(context),
            "python_version": _shorten(sys.version.split()[0], 80),
            "platform_info": _shorten(sys.platform, 255),
        }

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(INSERT_ERROR_LOG_SQL, data)
        conn.commit()
        return cursor.lastrowid
    except Exception as logging_error:
        _print_error(f"Could not write error log: {logging_error}; original error: {exc}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        _is_logging = False


def log_message(
    message,
    *,
    source="application",
    action=None,
    severity="ERROR",
    context=None,
    user=None,
):
    """Save a plain error message to error_logs."""
    error = RuntimeError(str(message or "Application error"))
    return log_exception(
        error,
        source=source,
        action=action,
        severity=severity,
        context=context,
        user=user,
        force=True,
    )


def _severity(value):
    text = str(value or "ERROR").upper()
    return text if text in VALID_SEVERITIES else "ERROR"


def _exception_details(exc, exc_type, exc_traceback):
    frames = traceback.extract_tb(exc_traceback) if exc_traceback else []
    last_frame = frames[-1] if frames else None
    file_path = _relative_path(last_frame.filename) if last_frame else None

    return {
        "exception_type": exc_type.__name__ if exc_type else type(exc).__name__,
        "error_message": str(exc),
        "module_name": _module_name(file_path),
        "function_name": last_frame.name if last_frame else None,
        "file_path": file_path,
        "line_number": last_frame.lineno if last_frame else None,
        "traceback_text": "".join(traceback.format_exception(exc_type, exc, exc_traceback)),
    }


def _relative_path(path):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        relative = os.path.relpath(os.path.abspath(path), root)
        if not relative.startswith(".."):
            return relative.replace("\\", "/")
    except Exception:
        pass
    return str(path or "").replace("\\", "/")


def _module_name(path):
    if not path:
        return None
    text = path[:-3] if path.endswith(".py") else path
    return text.replace("\\", ".").replace("/", ".")


def _user_info(user=None):
    if user is None:
        user = _current_user()
    if not isinstance(user, dict):
        return {"id": None, "username": None, "role": None}
    return {
        "id": _positive_int(user.get("id")),
        "username": user.get("username"),
        "role": user.get("role"),
    }


def _current_user():
    try:
        from controllers.login_controller import LoginController

        return LoginController.get_current_user()
    except Exception:
        return None


def _positive_int(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _json_text(value):
    if value is None:
        return None
    try:
        return _shorten(json.dumps(value, default=str), 60000)
    except Exception:
        return json.dumps({"context": str(value)})


def _shorten(value, limit):
    if value is None:
        return None
    text = str(value)
    if len(text) <= limit:
        return text
    return text[: limit - 15] + "...[truncated]"


def _already_logged(exc):
    try:
        return bool(exc._gnc_lpg_error_logged)
    except Exception:
        return False


def _mark_logged(exc):
    try:
        exc._gnc_lpg_error_logged = True
    except Exception:
        pass


def _print_error(message):
    try:
        print(message, file=sys.stderr)
    except Exception:
        pass
