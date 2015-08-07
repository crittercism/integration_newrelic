import os
import unittest
from lib.new_relic.models import Event

UNIT_TEST_DB_FILE = os.environ.get('UNIT_TEST_DB_FILE', 'unittest.db')


def test_db_location():
    return UNIT_TEST_DB_FILE


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.remove_test_db()

    def tearDown(self):
        self.remove_test_db()

    def remove_test_db(self):
        try:
            os.remove(UNIT_TEST_DB_FILE)

        except OSError:
            # File was already gone. No need to panic.
            pass

    def validate_event(self, e):
        event_keys = set(e.as_dict().keys())
        for k in {'accountId', 'appId', 'eventType', 'timestamp'}:
            self.assertIn(k, event_keys)

        for k in event_keys:
            self.assertNotIn(k, Event.TRANSLATION_MAP.keys())
