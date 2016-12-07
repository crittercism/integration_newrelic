import mock

import crittercism.client
from tests.base import BaseTestCase


class CrittercismClientTestCase(BaseTestCase):

    def setUp(self):

        self.standard_headers = {
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8',
            'Accept': 'application/json',
            'Connection': 'keep-alive',
            'CR-source': 'integration_new_relic',
            'Authorization': 'Bearer bogusToken',
        }

        self.base_url = 'https://developers.crittercism.com/v2/{}'

        self.cc = crittercism.client.CrittercismClient({'token': 'bogusToken'})

        # patch out requests
        get_patcher = mock.patch.object(crittercism.client.requests, 'get')
        post_patcher = mock.patch.object(crittercism.client.requests, 'post')

        # patcher will start and stop automatically when these tests are run
        self.mock_get = get_patcher.start()
        self.mock_post = post_patcher.start()
        self.addCleanup(get_patcher.stop)
        self.addCleanup(post_patcher.stop)

    # This method was lifted from
    # cypythonlib/soaclients/tests/unit/test_ams_wrapper.py
    @staticmethod
    def _response_with_json_data(status_code, json_data):
        response = mock.Mock()
        response.status_code = status_code
        response.json.return_value = json_data
        return response

    def test_app_versions(self):
        self.mock_get.side_effect = [self._response_with_json_data(
            200,
            {'data': {'bogusAppId': {'appVersions': ['version1', 'version2']}}}
            )
        ]
        versions = self.cc.app_versions('bogusAppId')

        self.mock_get.assert_called_with(
            self.base_url.format('apps'),
            headers=self.standard_headers,
            params={'attributes': 'appVersions'}
        )
        self.assertItemsEqual(versions, ['version1', 'version2'])

    def test_crash_paginated_tables_with_version(self):
        self.mock_get.side_effect = [self._response_with_json_data(
                200,
                {'data': {'foo': 'bar'}}
            )
        ]

        crash_data = self.cc.crash_paginated_tables(
            'bogusAppId',
            'bogusVersion'
        )

        self.mock_get.assert_called_with(
            self.base_url.format('bogusAppId/crash/paginatedtable'),
            headers=self.standard_headers,
            params={'appVersion': 'bogusVersion'}
        )
        self.assertEqual(crash_data['data'], {'foo': 'bar'})
