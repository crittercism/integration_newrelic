from crittercism.models import ErrorMonitoringPie
import mock
from lib.etl.app_loads import AppLoadETL
from lib.history.dao import create_tables
from tests.base import BaseTestCase, test_db_location
from tests.data.app_loads import APP_LOAD_DATA


class MockCrittercismClient(mock.MagicMock):
    def error_monitoring_pie(self, error_monitoring_request):
        for data_set in (APP_LOAD_DATA,):
            for t in data_set:
                body = t[4] if len(t) > 4 else None
                if body == {
                    'params': error_monitoring_request.as_hash()
                }:
                    return ErrorMonitoringPie(t[3])

        raise Exception('Did not find data for request: %s' % error_monitoring_request.as_hash())

class AppLoadsTestCase(BaseTestCase):
    @mock.patch('lib.history.dao.db_location', test_db_location)
    def setUp(self):
        super(AppLoadsTestCase, self).setUp()
        create_tables()

    @mock.patch('crittercism.client.CrittercismClient', MockCrittercismClient)
    @mock.patch('lib.etl.base.CrittercismClient', MockCrittercismClient)
    @mock.patch('lib.history.dao.db_location', test_db_location)
    def test_transactions_etl(self):
        etl_obj = AppLoadETL('bogusAppId', 8008, 666, 1)
        events = etl_obj.unpacked_events()

        for e in events:
            self.validate_event(e)

            event_keys = set(e.as_dict().keys())
            for k in {'timestamp', 'appVersion', 'carrier', 'eventType', 'appId', 'device', 'osVersion', 'accountId'}:
                self.assertIn(k, event_keys)

        self.assertEqual(len(events), 10612)
        etl_obj.save_state()

        etl_obj = AppLoadETL('bogusAppId', 8008, 666, 1)
        events = etl_obj.unpacked_events()
        self.assertEqual(len(events), 0)