from collections import defaultdict
from datetime import datetime, timedelta


class CrittercismException(Exception):
    pass


class TimeoutException(CrittercismException):
    pass


class MalformedRequestException(CrittercismException):
    pass


class RateLimitExceededException(CrittercismException):
    pass


class ServerErrorException(CrittercismException):
    pass


class AuthenticationException(CrittercismException):
    pass


class App(object):
    def __init__(self, app_id, hash_init):
        self._data = hash_init
        self._app_id = app_id
        self._app_load_data = None

    def app_id(self):
        return self._app_id

    def platform(self):
        return self._data[u'appType']

    def name(self):
        return self._data[u'appName']

    def versions(self):
        return self._data[u'appVersions']

    def set_app_load_data(self, app_load_data):
        self._app_load_data = app_load_data

    def app_load_data(self):
        return self._app_load_data


ONE_DAY = timedelta(days=1)


class CRErrorBase(object):
    def __init__(self, hash_init):
        self._data = hash_init
        self._oldest_available = None
        self._tz_offset = self._data[u'appTimeZoneOffset']
        self._todays_date = (datetime.utcnow() + timedelta(hours=self._tz_offset))
        self._latest_complete_date, self.date_map = self.build_date_map()
        self._today_partial_occurrences = self.latest_occurrences_by_version()

    def latest_complete_date_occurrences(self):
        return self.date_map[self._latest_complete_date]

    def latest_complete_date(self):
        return self._latest_complete_date

    def oldest_available_date(self):
        return self._oldest_available

    def current_date_occurrences(self):
        return self._today_partial_occurrences

    def current_date(self):
        return self._todays_date

    @staticmethod
    def normalize_datetime_to_midnight(dt):
        return datetime.strptime(dt.strftime('%Y-%m-%d'), '%Y-%m-%d')

    def date_occurrences(self, date):
        return self.date_map.get(self.normalize_datetime_to_midnight(date), 0)

    def latest_occurrences_by_version(self):
        todays_date = self._todays_date.strftime('%Y-%m-%d')
        return {
            version: num_list[0] if date == todays_date else 0
            for version, [date, num_list]
            in self._data[u'dailyOccurrencesByVersion'].items()
        }

    def build_date_map(self):
        daily_occurrences_by_version = self._data[u'dailyOccurrencesByVersion']
        total = defaultdict(int)
        for version, errors in daily_occurrences_by_version.items():
            start_date = datetime.strptime(errors[0], '%Y-%m-%d')
            daily_error_counts = errors[1]
            for index, error_count in enumerate(reversed(daily_error_counts)):
                date = (start_date - timedelta(days=index))
                total[date] += error_count

        dates = sorted(total.keys())
        total_daily_occurrences = (dates[-1].strftime('%Y-%m-%d'), [])

        for date in dates:
            total_daily_occurrences[1].append(total[date])

        incomplete_data_latest_date, daily_data = total_daily_occurrences
        latest_complete_datetime = datetime.strptime(incomplete_data_latest_date, '%Y-%m-%d')

        today = datetime.today().strftime('%Y-%m-%d')
        if incomplete_data_latest_date == today:
            latest_complete_datetime -= ONE_DAY

        date_map = {}
        date_cursor = latest_complete_datetime
        for one_day_occurrences in daily_data[1:]:
            date_map[date_cursor] = one_day_occurrences
            self._oldest_available = date_cursor
            date_cursor -= ONE_DAY

        return latest_complete_datetime, date_map

    def unique_session_count(self):
        return self._data[u'uniqueSessionCountsByVersion'][u'total']

    def crittercism_hash(self):
        return self._data[u'hash']

    def crittercism_app_id(self):
        return self._data[u'appId']

    def as_event_dict(self):
        return {
            'crAppId': self._data[u'appId'],
            'hash': self._data[u'hash'],
            'unsymbolizedHash': self._data[u'unsymbolizedHash'],
            'firstOccurred': self._data[u'firstOccurred'],
            'appType': self._data[u'appType'],
            'name': self._data[u'name'],
            'reason': self._data[u'reason'],
            'displayReason': self._data[u'displayReason'],
        }

    def __str__(self):
        return '%s' % self._data


class CRCrash(CRErrorBase):
    pass


class CRException(CRErrorBase):
    pass


class ErrorMonitoringRequest(object):
    METRIC_KEY = 'graph'
    DURATION_KEY = 'duration'
    GROUP_BY_KEY = 'groupBy'
    FILTERS_KEY = 'filters'
    APP_IDS_KEY = 'appIds'
    APP_ID_KEY = 'appId'

    VALID_METRICS = {'dau', 'mau', 'rating', 'crashes', 'crashPercent', 'appLoads', 'affectedUsers',
                     'affectedUserPercent'}
    VALID_DURATIONS = {1440, 10800, 43200}

    def __init__(self, app_id, metric, duration=43200, extras=None):
        if not metric in self.VALID_METRICS:
            raise MalformedRequestException

        if not duration in self.VALID_DURATIONS:
            raise MalformedRequestException

        self._data = {
            self.METRIC_KEY: metric,
            self.DURATION_KEY: duration,
            self.APP_ID_KEY: app_id,
        }

        if extras:
            self._data.update(extras)

    def as_hash(self):
        if not self._data.get(self.APP_IDS_KEY) and not self._data.get(self.APP_ID_KEY):
            raise MalformedRequestException

        return self._data

    def add_optional_params(self, params):
        self._data.update(params)


class CrittercismMonitoringResponse(object):
    def __init__(self, response):
        self._response = response[u'data']
        self._slices = self._response.get(u'slices', [])
        self._total_pie = sum([s[u'value'] for s in self._slices])
        self._slices_by_name = {s[u'name']: s[u'value'] for s in self._slices}
        self._slices_by_label = {s[u'label']: s[u'value'] for s in self._slices}
        self._group_list = [(s[u'name'], s[u'label']) for s in self._slices]
        self._start_time = datetime.strptime(self._response[u'start'], '%Y-%m-%dT%H:%M:%S')
        self._end_time = datetime.strptime(self._response[u'end'], '%Y-%m-%dT%H:%M:%S')

    def slices(self):
        return self._slices

    def all_group_names(self):
        return self._group_list

    def total(self):
        return self._total_pie

    def value_for_group_name(self, name):
        return self._slices_by_name[name]

    def value_for_group_label(self, label):
        return self._slices_by_label[label]

    # Size of bucket in seconds
    def interval(self):
        return self._response[u'interval']

    def time_range(self):
        return self._start_time, self._end_time


class ErrorMonitoringGraph(CrittercismMonitoringResponse):
    def __init__(self, response):
        super(ErrorMonitoringGraph, self).__init__(response)
        self._date_map = self.build_date_map()

    def build_date_map(self):
        date_map = {}
        d = self._start_time

        for day_data in self._response[u'series'][0][u'points']:
            date_map[d] = day_data
            d += ONE_DAY

        assert d == datetime.strptime(self._response[u'end'], '%Y-%m-%dT%H:%M:%S')
        return date_map

    def earliest_date(self):
        return self._start_time

    def loads_for_date(self, date):
        return self._date_map.get(date, 0)

    def dates_after(self, date):
        return [d for d in self._date_map.keys() if d > date]


class ErrorMonitoringPie(CrittercismMonitoringResponse):
    pass


class ErrorMonitoringSparkline(CrittercismMonitoringResponse):
    pass


class PerformanceManagementRequest(object):
    METRIC_KEY = 'graph'
    DURATION_KEY = 'duration'
    GROUP_BY_KEY = 'groupBy'
    FILTERS_KEY = 'filters'
    APP_IDS_KEY = 'appIds'

    VALID_METRICS = {'latency', 'dataIn', 'dataOut', 'volume', 'errors'}
    VALID_DURATIONS = {15, 60, 240, 480, 720, 1440, 2880, 10080, 43200}

    def __init__(self, metric, duration):
        if not metric in self.VALID_METRICS:
            raise MalformedRequestException

        if not duration in self.VALID_DURATIONS:
            raise MalformedRequestException

        self._data = {
            self.METRIC_KEY: metric,
            self.DURATION_KEY: duration,
        }

    @staticmethod
    def from_dict(the_dict):
        r = PerformanceManagementRequest('latency', 15)
        r.add_optional_params(the_dict)
        return r

    def add_optional_params(self, params):
        self._data.update(params)

    def as_hash(self):
        if not self._data.get(self.APP_IDS_KEY) and not self._data.get('appId'):
            raise MalformedRequestException

        return self._data


class PerformanceManagementPie(CrittercismMonitoringResponse):
    pass
