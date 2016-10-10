import json
import logging

from mock import MagicMock


def _response(response_code):
    return {
        'status': str(response_code),
    }


def _response_map_key(verb, url, body=None):
    print "response map", '{}|{}|{}'.format(verb, url, body)
    return '{}|{}|{}'.format(verb, url, body)


class MockHTTP(MagicMock):
    def __init__(self, *args, **kw):
        super(MockHTTP, self).__init__(*args, **kw)
        self.__response_map = {}

    def add_response_ignore_body_mapping(self, verb, url, response_code, response_content):
        self.__response_map[_response_map_key(verb, url)] = (response_code, response_content)

    def add_response_raw_mapping(self, verb, url, response_code, response_content, request_body=None):
        self.__response_map[_response_map_key(verb, url, request_body)] = (response_code, response_content)

    def add_response_mapping(self, verb, url, response_code, response_content, request_body=None):
        self.__response_map[_response_map_key(verb,
                                              url,
                                              json.dumps(request_body or {}))] = (response_code, response_content)

    def request(self, url, verb, headers=None, body=None):
        logging.getLogger().warn("MockHTTP requesting url=%s verb=%s headers=%s body=%s", url, verb, headers, body)
        try:
            response_code, response_content = self.__response_map.get(_response_map_key(verb, url, body),
                                                                      self.__response_map[_response_map_key(verb, url)])
            return _response(response_code), json.dumps(response_content)

        except KeyError, e:
            logging.getLogger().error("Unmocked request. Existing mocks: %s", self.__response_map.keys())
            raise


class MockNewRelicHTTP(MockHTTP):
    def __init__(self, *args, **kw):
        super(MockNewRelicHTTP, self).__init__(*args, **kw)

        self.add_response_ignore_body_mapping('POST',
                                              'https://insights-collector.newrelic.com/v1/accounts/1/events',
                                              200, {})
#
#
# class MockApiHTTP(MockHTTP):
#     def __init__(self, *args, **kwargs):
#         super(MockApiHTTP, self).__init__(*args, **kwargs)
#
#         self.add_response_ignore_body_mapping(
#             'GET',
#             'https://developers.crittercism.com/v1.0/apps?attributes=appVersions',
#             200,
#             {}
#         )