import mock

import crittercism.client
from tests.base import BaseTestCase


class AppVersionsTestCase(BaseTestCase):
    def setUp(self):
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
            {'bogusAppId': {'appVersions': ['version1', 'version2']}})]
        versions = crittercism.client.CrittercismClient.app_versions(
            self.cc,
            'bogusAppId'
        )

        self.assertIsInstance(versions, list)