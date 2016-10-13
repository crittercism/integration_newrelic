import datetime

import crittercism.models
from tests.base import BaseTestCase

class CrittercismModelsTestCase(BaseTestCase):
    def setUp(self):
        hash_init_crash = {
            'display_reason': 'bogus_display',
            'reason': 'bogus_reason',
            'name': 'crash_name',
            'first_occurred_time': 'first_time',
            'hash': 'bogusHash',
            'app_timezone_offset': 2,
            'daily_occurrences': ['20161005', [2, 3, 4]],
            'daily_occurrences_by_version': {}
        }
        hash_init_exception = {
            'displayReason': 'bogus_display',
            'reason': 'bogus_reason',
            'name': 'exception_name',
            'appType': 'bogus_type',
            'firstOccurred': 'first_time',
            'appId': 'bogusAppId',
            'hash': 'bogusHash',
            'appTimeZoneOffset': 2,
            'dailyOccurrencesByVersion': {
                'total': ['2016-10-05', [1, 4, 2]]
            }
        }
        self.crash_object = crittercism.models.CRCrash(hash_init_crash)
        self.exception_object = crittercism.models.CRException(hash_init_exception)

    def test_build_date_map_crash(self):
        latest_date, date_map = self.crash_object.build_date_map()

        self.assertEqual(
            latest_date.strftime('%Y-%m-%d %I:%M:%S'),
            '2016-10-05 12:00:00'
        )
        self.assertItemsEqual(
            date_map.keys(),
            [
                datetime.datetime(2016, 10, 5, 0, 0),
                datetime.datetime(2016, 10, 4, 0, 0)
            ]
        )

    def test_build_date_map_exception(self):
        latest_date, date_map = self.exception_object.build_date_map()

        self.assertEqual(
            latest_date.strftime('%Y-%m-%d %I:%M:%S'),
            '2016-10-05 12:00:00'
        )
        self.assertItemsEqual(
            date_map.keys(),
            [
                datetime.datetime(2016, 10, 5, 0, 0),
                datetime.datetime(2016, 10, 4, 0, 0)
            ]
        )

    def test_as_event_dict_crash(self):
        event_dict = self.crash_object.as_event_dict('bogusAppId')
        self.assertEqual(
            event_dict,
            {'displayReason': 'bogus_display',
             'hash': 'bogusHash',
             'name': 'crash_name',
             'firstOccurred': 'first_time',
             'crAppId': 'bogusAppId',
             'reason': 'bogus_reason'}
        )

    def test_as_event_dict_exception(self):
        event_dict = self.exception_object.as_event_dict(None)
        self.assertEqual(
            event_dict,
            {'displayReason': 'bogus_display',
             'hash': 'bogusHash',
             'firstOccurred': 'first_time',
             'appType': 'bogus_type',
             'crAppId': 'bogusAppId',
             'reason': 'bogus_reason',
             'name': 'exception_name'}
        )