from crittercism.models import CRException, CRCrash
import mock
from lib.etl.crashes import CrashETL
from lib.etl.exceptions import ExceptionETL
from lib.history.dao import create_tables
from tests.base import BaseTestCase, test_db_location
from tests.data.crashes import EXAMPLE_CRASH_HASH_1
from tests.data.exceptions import EXAMPLE_EXCEPTION_HASH_1


class MockCrittercismClient(mock.MagicMock):
    def app_exception_summaries(self, app_id, lookback_timedelta=None):
        return [{u'hash': EXAMPLE_EXCEPTION_HASH_1[u'hash']}]

    def exception_details(self, hash):
        if hash == EXAMPLE_EXCEPTION_HASH_1[u'hash']:
            return CRException(EXAMPLE_EXCEPTION_HASH_1)

        return None

    def app_crash_summaries(self, app_id, lookback_timedelta=None):
        return [{u'hash': EXAMPLE_CRASH_HASH_1[u'hash']}]

    def crash_details(self, hash):
        if hash == EXAMPLE_CRASH_HASH_1[u'hash']:
            return CRCrash(EXAMPLE_CRASH_HASH_1)

        return None


class ExceptionsTestCase(BaseTestCase):
    @mock.patch('lib.history.dao.db_location', test_db_location)
    def setUp(self):
        super(ExceptionsTestCase, self).setUp()
        create_tables()

    @mock.patch('crittercism.client.CrittercismClient', MockCrittercismClient)
    @mock.patch('lib.etl.base.CrittercismClient', MockCrittercismClient)
    @mock.patch('lib.history.dao.db_location', test_db_location)
    def test_transactions_etl(self):
        etl_obj = ExceptionETL('bogusAppId', 8008, 666, 1)
        events = etl_obj.unpacked_events()

        for e in events:
            self.validate_event(e)

            event_keys = set(e.as_dict().keys())
            for k in {'displayReason', 'hash', 'name', 'appType', 'crAppId', 'timestamp', 'reason', 'unsymbolizedHash',
                      'eventType', u'version', 'appId', 'firstOccurred', 'accountId'}:
                self.assertIn(k, event_keys)

        self.assertEqual(len(events), 235)
        etl_obj.save_state()

        etl_obj = ExceptionETL('bogusAppId', 8008, 666, 1)
        events = etl_obj.unpacked_events()
        self.assertEqual(len(events), 0)


class CrashesTestCase(BaseTestCase):
    @mock.patch('lib.history.dao.db_location', test_db_location)
    def setUp(self):
        super(CrashesTestCase, self).setUp()
        create_tables()

    @mock.patch('crittercism.client.CrittercismClient', MockCrittercismClient)
    @mock.patch('lib.etl.base.CrittercismClient', MockCrittercismClient)
    @mock.patch('lib.history.dao.db_location', test_db_location)
    def test_transactions_etl(self):
        etl_obj = CrashETL('bogusAppId', 8008, 666, 1)
        events = etl_obj.unpacked_events()

        for e in events:
            self.validate_event(e)

            event_keys = set(e.as_dict().keys())
            for k in {'displayReason', 'hash', 'name', 'appType', 'crAppId', 'timestamp', 'reason', 'unsymbolizedHash',
                      'eventType', u'version', 'appId', 'firstOccurred', 'accountId'}:
                self.assertIn(k, event_keys)

        self.assertEqual(len(events), 314)
        etl_obj.save_state()

        etl_obj = CrashETL('bogusAppId', 8008, 666, 1)
        events = etl_obj.unpacked_events()
        self.assertEqual(len(events), 0)


