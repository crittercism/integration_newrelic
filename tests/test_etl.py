import mock

import crittercism.client
from lib.etl.crashes import CrashETL
from tests.base import BaseTestCase


class TestCrashETL(CrashETL):
    _c_client = mock.MagicMock()
    def __init__(self):
        self._app_id = 'bogusAppId'
        self._c_client.crash_paginated_tables.return_value = {
            'data': {'errors': [{'hash':'bogusHash',
                                 'daily_occurrences': 2}]}
        }
        self._c_client.app_versions.return_value = ['bogusVersion']
        self._c_client.crash_details.return_value = {'bogusHash': {'bogusVersion': 1}}


class EtlTestCase(BaseTestCase):
    def setUp(self):
        pass

    def test_get_errors_with_details(self):
        client_object = TestCrashETL()
        crashes = client_object.get_errors_with_details(15)
        self.assertEqual(crashes, [{'bogusHash': {'bogusVersion': 1}}])