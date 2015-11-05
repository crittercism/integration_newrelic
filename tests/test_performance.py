from crittercism.models import PerformanceManagementPie
import mock
from lib.etl.performance import PerformanceMetricsETL
from tests.base import BaseTestCase
from tests.data.performance import PERFORMANCE_REQUESTS_AND_RESPONSES
from tests.helpers import MagicMock


class MockCrittercismClient(MagicMock):
    def performance_management_pie(self, performance_management_request):
        for data_set in (PERFORMANCE_REQUESTS_AND_RESPONSES,):
            for t in data_set:
                body = t[4] if len(t) > 4 else None
                if body == {
                    'params': performance_management_request.as_hash()
                }:
                    return PerformanceManagementPie(t[3])

        raise Exception('Did not find data for request: %s' % performance_management_request.as_hash())


class PerformanceTestCase(BaseTestCase):
    @mock.patch('crittercism.client.CrittercismClient', MockCrittercismClient)
    @mock.patch('lib.etl.base.CrittercismClient', MockCrittercismClient)
    def test_transactions_etl(self):
        etl_obj = PerformanceMetricsETL('bogusAppId', 8008, 666, 1)
        events = etl_obj.unpacked_events()

        for e in events:
            self.validate_event(e)

            event_keys = set(e.as_dict().keys())
            for k in {'errors', 'service', 'timestamp', 'dataIn', 'appVersion', 'osVersion', 'carrier', 'device',
                      'dataOut', 'eventType', 'appId', 'interactionDuration', 'accountId'}:
                self.assertIn(k, event_keys)

        self.assertEqual(len(events), 7219)

