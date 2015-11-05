from sqlite3 import OperationalError
import mock
from lib.history.dao import create_tables, CRErrorHistoryDAO, CRAppLoadHistoryDAO
from tests.base import BaseTestCase, test_db_location


class HistoryTestCase(BaseTestCase):
    def verify_fails_on_nonexistent_db(self, crash_tuple, app_load_tuple):
        app_id, error_type, crash_hash, version, date, num_crashes = crash_tuple

        with self.assertRaises(OperationalError) as e:
            CRErrorHistoryDAO.num_previously_known(app_id, error_type, crash_hash, version, date)

        self.assertEqual(e.exception.args[0], 'no such table: error_history')

        with self.assertRaises(OperationalError) as e:
            CRErrorHistoryDAO.set_known_occurrences(app_id, error_type, crash_hash, version, date, num_crashes)

        self.assertEqual(e.exception.args[0], 'no such table: error_history')

        start_date, end_date, num_app_loads = app_load_tuple
        with self.assertRaises(OperationalError) as e:
            CRAppLoadHistoryDAO.num_previously_known(app_id, start_date, end_date)

        self.assertEqual(e.exception.args[0], 'no such table: app_load_history')

        with self.assertRaises(OperationalError) as e:
            CRAppLoadHistoryDAO.set_known_occurrences(app_id, start_date, end_date, num_app_loads)

        self.assertEqual(e.exception.args[0], 'no such table: app_load_history')


    @mock.patch('lib.history.dao.db_location', test_db_location)
    def test_all_daos(self):
        crash_data = ('bogusAppId', 'bogusErrorType', 'bogusCrashHash',
                      'bogusVersion', '2099-09-09', 8008)
        app_id, error_type, crash_hash, version, date, num_crashes = crash_data

        app_load_data = ('2099-09-09', '2107-01-05', 8008)
        start_date, end_date, num_app_loads = app_load_data
        self.verify_fails_on_nonexistent_db(crash_data, app_load_data)

        create_tables()

        self.assertEqual(0, CRErrorHistoryDAO.num_previously_known(app_id, error_type, crash_hash, version, date))
        CRErrorHistoryDAO.set_known_occurrences(app_id, error_type, crash_hash, version, date, num_crashes)
        self.assertEqual(num_crashes, CRErrorHistoryDAO.num_previously_known(app_id, error_type, crash_hash, version,
                                                                             date))
        self.assertEqual(0, CRErrorHistoryDAO.num_previously_known(app_id, error_type, crash_hash, 'bad', date))
        self.assertEqual(0, CRErrorHistoryDAO.num_previously_known(app_id, error_type, crash_hash, version, 'bad'))
        self.assertEqual(0, CRErrorHistoryDAO.num_previously_known(app_id, error_type, 'bad', version, date))
        self.assertEqual(0, CRErrorHistoryDAO.num_previously_known(app_id, 'bad', crash_hash, version, date))
        self.assertEqual(0, CRErrorHistoryDAO.num_previously_known('bad', error_type, crash_hash, version, date))

        self.assertEqual(0, CRAppLoadHistoryDAO.num_previously_known(app_id, start_date, end_date))
        CRAppLoadHistoryDAO.set_known_occurrences(app_id, start_date, end_date, num_app_loads)
        self.assertEqual(num_app_loads, CRAppLoadHistoryDAO.num_previously_known(app_id, start_date, end_date))
        self.assertEqual(0, CRAppLoadHistoryDAO.num_previously_known('bad', start_date, end_date))
        self.assertEqual(0, CRAppLoadHistoryDAO.num_previously_known(app_id, 'bad', end_date))
        self.assertEqual(0, CRAppLoadHistoryDAO.num_previously_known(app_id, start_date, 'bad'))






