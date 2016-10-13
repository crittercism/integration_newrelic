import base64
from datetime import datetime
import os
import requests


from models import CRCrash
from models import TimeoutException
from models import MalformedRequestException
from models import AuthenticationException
from models import RateLimitExceededException
from models import ServerErrorException
from models import CrittercismException
from models import PerformanceManagementPie
from models import App
from models import ErrorMonitoringPie
from models import ErrorMonitoringGraph
from models import CRException


class CrittercismClient(object):
    crittercism_api_domain = os.environ.get(
        'CR_API_DOMAIN',
        'developers.crittercism.com'
    )
    crittercism_url = 'https://{}/v2/{}'
    crittercism_txn_url = 'https://{}/v2/transactions/{}/{}'
    get = 'GET'
    post = 'POST'
    token = 'TOKEN'
    appversions = 'appVersions'

    def __init__(self, auth_hash):
        self._client_id = auth_hash.get('client_id')
        self._username = auth_hash.get('username')
        self._password = auth_hash.get('password')
        self._oauth_token = auth_hash.get('token')
        self._transaction_tokens = {}

        if not self._oauth_token:
            self._oauth_token = self.authenticate()

    def __token_for_app_id(self, app_id):
        token = self._transaction_tokens.get(app_id)
        if not token:
            token = self.authenticate(
                scope='app/{}/transactions'.format(app_id)
            )
            self._transaction_tokens[app_id] = token

        return token

    def __request(self, verb, url_suffix=None, params=None):
        return self.__request_helper(
            verb,
            self.crittercism_url.format(
                self.crittercism_api_domain,
                url_suffix),
            params=params,
            token=self._oauth_token
        )

    def get_paged_transaction_data(self, app_id, url):
        """
        For API endpoints that have paged data, get every page of data available.

        :param app_id: string, Id of the app to retrieve information about
        :param url: string, url that will be called to get paged data
        :return: list of dictionaries of data returned by the API
        """
        pagenum = 'pageNum'
        pagination = 'pagination'
        token = self.__token_for_app_id(app_id)
        pages = []
        params = {pagenum: 1}
        page = self.__request_helper(self.get, url, params={}, token=token)

        while page:
            pages.append(page)
            params[pagenum] += 1
            if page.get(pagination) and page.get(pagination)[u'nextPage']:
                page = self.__request_helper(
                    self.get,
                    url,
                    params=params,
                    token=token)
            else:
                page = None

        return pages

    # TODO (sf) this is probably obsolete
    def __get_transaction_url(self, url, token):
        """
        Bypass the __request method for transactions endpoints.

        :param url: string, url that will be called to get paged data
        :param token: string, user's oauth token
        :return: calls __request_helper
        """
        return self.__request_helper(self.get, url, {}, token)

    def __request_helper(self,
                         verb,
                         url,
                         params=None,
                         token=None,
                         extra_headers=None):
        """

        :param verb: string, 'GET', 'POST', or 'TOKEN' to determine http method
        :param url: string, API endpoint to be called
        :param params: dict, parameters for the API call
        :param token: string, user's oauth token
        :param extra_headers: dict, any extra headers for the http request
        :return: dict, API response
        """

        headers = {
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8',
            'Accept': 'application/json',
            'Connection': 'keep-alive',
            'CR-source': 'integration_new_relic'
        }

        if token:
            headers.update({'Authorization': 'Bearer {}'.format(token)})

        if extra_headers:
            headers.update(extra_headers)

        response = None

        if verb == self.get:
            response = requests.get(url, headers=headers, params=params)
        elif verb == self.post:
            response = requests.post(url, headers=headers, json=params)
        elif verb == self.token:
            response = requests.post(url, headers=headers, params=params)
        else:
            raise TypeError

        if not response:
            raise TimeoutException

        # TODO (SF) requests has its own exceptions for these; use them.
        http_response_status = response.status_code
        if http_response_status == 400:
            # 400	Request parameters were invalid/malformed
            raise MalformedRequestException(
                {'message': 'You provided invalid/malformed request parameters.',
                 'response': response})

        elif http_response_status == 401:
            # 401	Invalid oauth token
            raise AuthenticationException(
                {'message': 'You provided an invalid token. Please re-authenticate.',
                 'response': response})

        elif http_response_status == 429:
            # 429	API rate limit exceeded
            raise RateLimitExceededException(
                {'message': 'You have exceeded your rate limit. Please decrease your request frequency.',
                 'response': response})

        elif http_response_status == 500:
            raise ServerErrorException(
                {'message': 'Server error on Crittercism API. Please contact Crittercism support',
                 'response': response})

        elif http_response_status != 200:
            raise CrittercismException(
                {'message': 'Unknown error on Crittercism API.',
                 'response': response})

        return response.json()

    #TODO (sf) scope is probably unnecessary now that transactions is fixed
    def authenticate(self, scope=None):
        """
        Uses a username and password to generate an oauth token from the API

        :param scope: string, scope for the token
        :return: string, oauth token
        """
        body = {
            'grant_type': 'password',
            'username': self._username,
            'password': self._password,
            'duration': 31536000,
        }

        if scope:
            body['scope'] = scope

        authstr = base64.encodestring('%s' % self._client_id).replace('\n', '')
        data = self.__request_helper(
            self.token,
            'https://developers.crittercism.com/v1.0/token',
            body,
            None,
            {
                'Authorization': 'Basic {}'.format(authstr),
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )

        return data['access_token']

    APP_ATTRIBUTE_CHOICES = {"appName",
                             "appType",
                             "appVersions",
                             "crashPercent",
                             "dau",
                             "latency",
                             "latestAppStoreReleaseDate",
                             "latestVersionString",
                             "linkToAppStore",
                             "iconURL",
                             "mau",
                             "rating",
                             "role"}

    def apps(self, attributes=None):
        """The apps endpoint provides information about a customer's mobile applications.
        The apps endpoint returns a list of apps with links to additional metric endpoints.
        Information requested in the attributes parameter is made available as a series of
        key-value pairs inside the object representing each app.
        API endpoint: /apps

        Required keyword arguments:
        <None>

        Optional keyword arguments:
        attributes -- list of attributes desired as part of app response data
            Possible contents: "appName",
                                "appType",
                                "appVersions",
                                "crashPercent",
                                "dau",
                                "latency",
                                "latestAppStoreReleaseDate",
                                "latestVersionString",
                                "linkToAppStore",
                                "iconURL",
                                "mau",
                                "rating",
                                "role"

        """
        params = {}

        url_suffix = 'apps'
        params['attributes'] = ','.join(
            attributes or list(self.APP_ATTRIBUTE_CHOICES)
        )
        content = self.__request(self.get, url_suffix, params=params)

        response = [App(app_id, app_data) for app_id, app_data in content.items()]
        return response

    def app_versions(self, app_id):
        """
        Calls the apps summary endpoint and gets a list of app versions
        for a particular app ID
        API endpoint: /apps

        :param app_id: string

        :return: list of app version strings
        """
        url_suffix = 'apps'

        params = {'attributes': self.appversions}

        content = self.__request(self.get, url_suffix, params=params)

        versions = content['data'][app_id][self.appversions]

        return versions

    #TODO (sf) is nothing calling this? Find out!
    def error_monitoring_graph(self, error_monitoring_request):
        """
        Calls the error monitoring graph API
        API endpoint: /errorMonitoring/graph

        :param error_monitoring_request: error monitoring request object
        :return: error monitoring graph object
        """
        url_suffix = 'errorMonitoring/graph'

        params = error_monitoring_request.as_hash()

        content = self.__request(self.get, url_suffix, params=params)

        return ErrorMonitoringGraph(content)

    def error_monitoring_pie(self, error_monitoring_request):
        """
        Calls the error monitoring pie API
        API endpoint: /errorMonitoring/pie

        :param error_monitoring_request: error monitoring request object
        :return: error monitoring pie object
        """
        url_suffix = 'errorMonitoring/pie'

        params = error_monitoring_request.as_hash()

        content = self.__request(self.get, url_suffix, params=params)

        return ErrorMonitoringPie(content)

    def lookback_start(self, t_delta):
        """
        This helps us override code for unit testing

        :param t_delta: timedelta object, time in minutes to look back
        :return: string, current time minus time in minutes to look back
        """
        return (datetime.utcnow() - t_delta).strftime('%Y-%m-%dT%H:%M:%S+00:00')

    def app_crash_counts(self, app_id):
        """
        Get crash counts for an app.
        API endpoint: /app/{appId}/crash/counts

        :param app_id: string, app ID to retrieve data about
        :return: dict, API response
        """
        url_suffix = 'app/{}/crash/counts'.format(app_id)
        content = self.__request(self.get, url_suffix, {})

        return content

    def crash_paginated_tables(self, app_id, app_version=None,
                               lookback_timedelta=None):
        """
        Get information about crashes from the paginated table endpoint
        API endpoint: /{appId}/crash/paginatedtable

        :param app_id: string, app ID to retrieve data about
        :param app_version: string, version of app
        :param lookback_timedelta: timedelta object, time in minutes to look back
        :return: dict, API response
        """

        params = {}

        url_suffix = '{}/crash/paginatedtable'.format(app_id)

        if app_version:
            params['appVersion'] = app_version

        if lookback_timedelta:
            start_date = (datetime.now() - lookback_timedelta).isoformat()
            end_date = datetime.now().isoformat()

            params['startDate'] = start_date
            params['endDate'] = end_date

        content = self.__request(self.get, url_suffix, params=params)

        return content

    #TODO (sf) is anything still calling this?
    def app_crash_summaries(self, app_id, lookback_timedelta=None):
        """
        Get crash summary data for an app
        API endpoint: /app/{appId}/crash/summaries

        :param app_id: string, app ID to retrieve data about
        :param lookback_timedelta: timedelta object, time in minutes to look back
        :return: dict, API response
        """
        url_suffix = 'app/{}/crash/summaries'.format(app_id)

        params = {}

        if lookback_timedelta:
            params['lastOccurredStart'] = self.lookback_start(
                lookback_timedelta
            )

        content = self.__request(self.get, url_suffix, params=params)

        return content

    def crash_details(self, content):
        """
        :param content: dict, crash data from the API
        :return: a CRCrash object
        """
        return CRCrash(content)

    def app_exception_counts(self, app_id):
        """
        Get exception counts for an app
        API endpoint: /app/{appId}/exception/counts

        :param app_id: string, app ID to retrieve data about
        :return: dict, API response
        """
        url_suffix = 'app/{}/exception/counts'.format(app_id)
        content = self.__request(self.get, url_suffix, params={})

        return content

    def app_exception_summaries(self, app_id, lookback_timedelta=None):
        """
        Get exception summaries for an app
        API endpoint: /app/{appId}/exception/summaries

        :param app_id: string, app ID to retrieve data about
        :lookback_timedelta: timedelta object, minutes to look back
        :return: dict, API response
        """
        url_suffix = 'app/{}/exception/summaries'.format(app_id)

        params = {}

        if lookback_timedelta:
            params['lastOccurredStart'] = self.lookback_start(
                lookback_timedelta
            )

        content = self.__request(self.get, url_suffix, params=params)

        return content

    def exception_details(self, app_id, exception_hash, include_diagnostics=False):
        """
        Get detailed data about each exception by hash
        API endpoint: /exception/{appId}/{hash}

        :param app_id: string, app ID to retrieve data about
        :param exception_hash: string, hash of a specific exception
        :param include_diagnostics: bool, request diagnostics data from the API
        :return: a CRException object
        """
        url_suffix = 'exception/{}/{}'.format(app_id, exception_hash)

        params = {'dailyOccurrences': True,
                  'diagnostics': include_diagnostics}

        content = self.__request(self.get, url_suffix, params=params)
        return CRException(content['data'])

    def performance_management_pie(self, performance_management_request):
        """
        Get performance management pie data for an app
        API endpoint: /performanceManagement/pie

        :param performance_management_request: object
        :return: object
        """
        url_suffix = 'performanceManagement/pie'

        params = performance_management_request.as_hash()

        content = self.__request(self.get, url_suffix, params=params)

        return PerformanceManagementPie(content)

    # TODO (sf) I bet this can be changed to match the other API calls
    def transactions_details(self, app_id, period=None):
        """
        Get transactions data for an app
        API endpoint: transactions/details/change/{period}
        :param app_id: string, app ID to retrieve data about
        :param period: string, ISO period
        :return: list, a list of API response dicts
        """
        url_suffix = 'details/change/{}'.format(period)
        url = self.crittercism_txn_url.format(
            self.crittercism_api_domain,
            app_id,
            url_suffix)
        content = self.get_paged_transaction_data(app_id, url)
        return content
