import io
import unittest

from salesreport.config import Config
from salesreport.logging_utils import Logger, get_logger


class ConfigTests(unittest.TestCase):
    def test_defaults(self):
        config = Config()
        self.assertEqual(config.input_format, "csv")
        self.assertEqual(config.output_format, "json")
        self.assertFalse(config.verbose)
        self.assertFalse(config.debug_dump)
        self.assertEqual(config.sort_by, "region")
        self.assertEqual(config.decimals, 2)

    def test_from_empty_env(self):
        self.assertEqual(Config.from_env({}), Config())

    def test_from_env_overrides(self):
        config = Config.from_env(
            {
                "SALESREPORT_INPUT": "json",
                "SALESREPORT_OUTPUT": "xml",
                "SALESREPORT_VERBOSE": "1",
                "SALESREPORT_DEBUG": "1",
                "SALESREPORT_SORT": "total",
                "SALESREPORT_DECIMALS": "0",
            }
        )
        self.assertEqual(config.input_format, "json")
        self.assertEqual(config.output_format, "xml")
        self.assertTrue(config.verbose)
        self.assertTrue(config.debug_dump)
        self.assertEqual(config.sort_by, "total")
        self.assertEqual(config.decimals, 0)

    def test_verbose_requires_exactly_one(self):
        self.assertFalse(Config.from_env({"SALESREPORT_VERBOSE": "yes"}).verbose)

    def test_bad_decimals(self):
        with self.assertRaises(ValueError):
            Config.from_env({"SALESREPORT_DECIMALS": "many"})


class LoggerTests(unittest.TestCase):
    def test_silent_by_default(self):
        stream = io.StringIO()
        logger = Logger(stream=stream)
        logger.info("a")
        logger.debug("b")
        self.assertEqual(stream.getvalue(), "")

    def test_verbose_writes_levels(self):
        stream = io.StringIO()
        logger = Logger(verbose=True, stream=stream)
        logger.info("a")
        logger.debug("b")
        self.assertEqual(stream.getvalue(), "[INFO] a\n[DEBUG] b\n")

    def test_get_logger_uses_config(self):
        self.assertTrue(get_logger(Config(verbose=True)).verbose)
        self.assertFalse(get_logger(Config()).verbose)
