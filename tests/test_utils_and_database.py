import importlib
import sys
import types
import unittest
from email import message_from_string
from unittest import mock

from tests.helpers import FakeConnection, FakeCursor, install_dependency_stubs


install_dependency_stubs()


class ValidatorsTest(unittest.TestCase):
    def test_password_strength_reports_each_rule(self):
        from utils.validators import validate_password_strength

        cases = [
            ("", False, "empty"),
            ("short", False, "at least 8"),
            ("lowercase1!", False, "uppercase"),
            ("UPPERCASE1!", False, "lowercase"),
            ("NoNumber!", False, "number"),
            ("NoSpecial1", False, "special"),
            ("GoodPass1!", True, ""),
        ]

        for password, expected_ok, expected_text in cases:
            with self.subTest(password=password):
                ok, message = validate_password_strength(password)
                self.assertEqual(ok, expected_ok)
                self.assertIn(expected_text, message)

    def test_email_validation_accepts_clean_email_and_rejects_bad_input(self):
        from utils.validators import validate_email

        self.assertEqual(validate_email("name@example.com"), (True, ""))
        self.assertEqual(
            validate_email(" name@example.com")[1],
            "Email address cannot start or end with spaces.",
        )
        self.assertEqual(
            validate_email("name @example.com")[1],
            "Email address cannot contain spaces.",
        )
        self.assertIn("valid email", validate_email("missing-at")[1])


class ErrorHandlerTest(unittest.TestCase):
    def test_clean_db_error_maps_common_database_errors(self):
        import utils.error_handler as error_handler

        with mock.patch.object(error_handler, "log_exception") as log_exception:
            self.assertEqual(
                error_handler.clean_db_error("Duplicate entry 'admin' for key 'username'"),
                "Username is already taken.",
            )
            self.assertEqual(
                error_handler.clean_db_error("Duplicate entry 'x' for key 'email'"),
                "Email is already in use by another account.",
            )
            self.assertEqual(
                error_handler.clean_db_error("Cannot delete or update a parent row"),
                "This record cannot be deleted because it is linked to other records.",
            )
            self.assertEqual(
                error_handler.clean_db_error("Can't connect to MySQL server"),
                "Could not connect to the database. Please try again.",
            )
            self.assertEqual(
                error_handler.clean_db_error("Access denied for user"),
                "Database access denied. Please contact your administrator.",
            )
            self.assertEqual(
                error_handler.clean_db_error("unexpected"),
                "An unexpected error occurred. Please try again.",
            )

        self.assertEqual(log_exception.call_count, 6)

    def test_clean_db_error_strips_mysql_error_prefix(self):
        import utils.error_handler as error_handler

        with mock.patch.object(error_handler, "log_exception"):
            self.assertEqual(
                error_handler.clean_db_error("1644 (45000): Product is already active."),
                "Product is already active.",
            )


class ErrorLoggerTest(unittest.TestCase):
    def setUp(self):
        import utils.error_logger as error_logger

        self.error_logger = error_logger
        self.error_logger._table_ready = False
        self.error_logger._is_logging = False
        self.error_logger._hooks_installed = False
        self.addCleanup(self._reset_logger_state)

    def _reset_logger_state(self):
        self.error_logger._table_ready = False
        self.error_logger._is_logging = False
        self.error_logger._hooks_installed = False

    def test_ensure_error_logs_table_creates_table_and_view_once(self):
        cursor = FakeCursor()
        conn = FakeConnection([cursor])

        with mock.patch.object(self.error_logger, "get_connection", return_value=conn):
            self.assertTrue(self.error_logger.ensure_error_logs_table())
            self.assertTrue(self.error_logger.ensure_error_logs_table())

        self.assertEqual(len(cursor.executed), 2)
        self.assertEqual(conn.commits, 1)
        self.assertTrue(cursor.closed)
        self.assertTrue(conn.closed)

    def test_log_exception_writes_structured_payload_without_reraising(self):
        cursor = FakeCursor(lastrowid=44)
        conn = FakeConnection([cursor])
        error = RuntimeError("boom")

        with mock.patch.object(self.error_logger, "ensure_error_logs_table", return_value=True):
            with mock.patch.object(self.error_logger, "get_connection", return_value=conn):
                log_id = self.error_logger.log_exception(
                    error,
                    source="tests",
                    action="explode",
                    severity="warning",
                    context={"safe": True},
                    user={"id": "7", "username": "admin", "role": "owner"},
                )

        self.assertEqual(log_id, 44)
        self.assertEqual(conn.commits, 1)
        sql, payload = cursor.executed[0]
        self.assertIn("INSERT INTO error_logs", sql)
        self.assertEqual(payload["user_id"], 7)
        self.assertEqual(payload["severity"], "WARNING")
        self.assertEqual(payload["source"], "tests")
        self.assertIn('"safe": true', payload["context_json"])
        self.assertTrue(cursor.closed)
        self.assertTrue(conn.closed)

    def test_log_exception_is_idempotent_for_same_exception(self):
        error = RuntimeError("already logged")
        with mock.patch.object(self.error_logger, "ensure_error_logs_table", return_value=True):
            with mock.patch.object(self.error_logger, "get_connection", return_value=FakeConnection()):
                self.assertEqual(self.error_logger.log_exception(error), 101)
                self.assertIsNone(self.error_logger.log_exception(error))

    def test_log_exception_converts_plain_message_and_handles_logging_failure(self):
        cursor = FakeCursor(execute_side_effect=RuntimeError("insert failed"))
        conn = FakeConnection([cursor])

        with mock.patch.object(self.error_logger, "ensure_error_logs_table", return_value=True):
            with mock.patch.object(self.error_logger, "get_connection", return_value=conn):
                with mock.patch.object(self.error_logger, "_print_error") as print_error:
                    self.assertIsNone(self.error_logger.log_exception("plain problem"))

        self.assertEqual(conn.rollbacks, 0)
        print_error.assert_called_once()

    def test_private_formatting_helpers(self):
        el = self.error_logger

        self.assertEqual(el._severity("critical"), "CRITICAL")
        self.assertEqual(el._severity("unknown"), "ERROR")
        self.assertEqual(el._positive_int("9"), 9)
        self.assertIsNone(el._positive_int("-1"))
        self.assertEqual(el._shorten("abcdef", 5), "...[truncated]")
        self.assertIn('"bad"', el._json_text({"bad": object()}))
        self.assertEqual(el._module_name("models/user_model.py"), "models.user_model")


class DatabaseConnectionTest(unittest.TestCase):
    def test_get_connection_uses_configured_mysql_connector(self):
        import database.connection as connection

        sentinel = object()
        with mock.patch.object(connection.mysql.connector, "connect", return_value=sentinel) as connect:
            self.assertIs(connection.get_connection(), sentinel)

        connect.assert_called_once_with(**connection.DB_CONFIG)

    def test_get_connection_logs_and_raises_clean_failure(self):
        import database.connection as connection

        error = connection.Error("no database")
        with mock.patch.object(connection.mysql.connector, "connect", side_effect=error):
            with mock.patch("utils.error_logger.log_exception") as log_exception:
                with self.assertRaisesRegex(Exception, "Database connection failed"):
                    connection.get_connection()

        log_exception.assert_called_once()


class EmailSenderTest(unittest.TestCase):
    def test_send_reset_code_uses_mocked_smtp_only(self):
        import utils.email_sender as email_sender

        smtp = mock.Mock()
        smtp_context = mock.Mock()
        smtp_context.__enter__ = mock.Mock(return_value=smtp)
        smtp_context.__exit__ = mock.Mock(return_value=None)

        with mock.patch.object(email_sender.smtplib, "SMTP_SSL", return_value=smtp_context) as smtp_ssl:
            email_sender.send_reset_code("user@example.com", "123456", full_name="Tina")

        smtp_ssl.assert_called_once_with("smtp.gmail.com", 465)
        smtp.login.assert_called_once_with(
            email_sender.GMAIL_ADDRESS,
            email_sender.GMAIL_APP_PASSWORD,
        )
        args = smtp.sendmail.call_args.args
        self.assertEqual(args[:2], (email_sender.GMAIL_ADDRESS, "user@example.com"))
        message = message_from_string(args[2])
        html = message.get_payload(0).get_payload(decode=True).decode("utf-8")
        self.assertIn("123456", html)
        self.assertIn("Tina", html)


class MainModuleTest(unittest.TestCase):
    def test_main_installs_hooks_before_running_login_view(self):
        if "main" in sys.modules:
            del sys.modules["main"]

        fake_login_view = types.ModuleType("views.login_view")
        fake_login_view.main = mock.Mock()
        with mock.patch.dict(sys.modules, {"views.login_view": fake_login_view}):
            main = importlib.import_module("main")
            with mock.patch.object(main, "install_error_logging_hooks") as install_hooks:
                main.main()

        install_hooks.assert_called_once()
        fake_login_view.main.assert_called_once()


if __name__ == "__main__":
    unittest.main()
