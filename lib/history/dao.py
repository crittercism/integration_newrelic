import logging
import sqlite3


def db_location():
    return 'history.db'


def create_db_connection():
    try:
        return sqlite3.connect(db_location())

    except:
        logging.getLogger().critical('FAILED to connect(%s)', 'history.db')
        raise


CREATE_ERROR_HISTORY_TABLE_QUERY = '''CREATE TABLE IF NOT EXISTS error_history (
    app_id varchar,
    error_type varchar,
    crash_hash varchar,
    version varchar,
    date date,
    num_crashes integer
);'''

CREATE_APP_LOAD_HISTORY_TABLE_QUERY = '''CREATE TABLE IF NOT EXISTS app_load_history (
    app_id varchar,
    start_date date,
    end_date date,
    num_app_loads integer
);'''

CREATE_INDEX_ON_ERROR_HISTORY_QUERY = '''CREATE INDEX ch_idx ON error_history
                                         (app_id, error_type, crash_hash, version, date);'''
CREATE_INDEX_ON_APP_LOAD_HISTORY_QUERY = '''CREATE INDEX ch_idx2 ON app_load_history
                                            (app_id, start_date, end_date);'''


def create_tables():
    # No exception handling because we should fail hard in this scenario.
    db_conn = create_db_connection()
    cursor = db_conn.cursor()
    cursor.execute(CREATE_ERROR_HISTORY_TABLE_QUERY)
    cursor.execute(CREATE_APP_LOAD_HISTORY_TABLE_QUERY)
    db_conn.commit()

    try:
        db_conn = create_db_connection()
        cursor.execute(CREATE_INDEX_ON_ERROR_HISTORY_QUERY)
        db_conn.commit()

    except:
        logging.getLogger().debug('Do not create duplicate index on error_history')

    try:
        db_conn = create_db_connection()
        cursor.execute(CREATE_INDEX_ON_APP_LOAD_HISTORY_QUERY)
        db_conn.commit()

    except:
        logging.getLogger().debug('Do not create duplicate index on app_load_history')


class CRErrorHistoryDAO(object):
    WHERE_CLAUSE = 'WHERE app_id=? AND error_type=? AND crash_hash=? AND version=? AND date=?;'
    SELECT_QUERY = 'SELECT num_crashes FROM error_history ' + WHERE_CLAUSE
    COUNT_QUERY = 'SELECT COUNT(*) FROM error_history ' + WHERE_CLAUSE
    UPDATE_QUERY = 'UPDATE error_history SET num_crashes=? ' + WHERE_CLAUSE
    CREATE_QUERY = ('INSERT INTO error_history (num_crashes, app_id, error_type, crash_hash, version, date)' +
                    'VALUES (?, ?, ?, ?, ?, ?);')

    @staticmethod
    def num_previously_known(app_id, error_type, crash_hash, version, date):
        db_conn = create_db_connection()
        cursor = db_conn.cursor()
        cursor.execute(CRErrorHistoryDAO.SELECT_QUERY, (app_id, error_type, crash_hash, version, date))
        all_results = cursor.fetchall()

        if len(all_results):
            return all_results[0][0]

        return 0

    @staticmethod
    def set_known_occurrences(app_id, error_type, crash_hash, version, date, num_crashes):
        db_conn = create_db_connection()
        cursor = db_conn.cursor()
        cursor.execute(CRErrorHistoryDAO.COUNT_QUERY, (app_id, error_type, crash_hash, version, date))
        count = cursor.fetchone()[0]
        query = CRErrorHistoryDAO.UPDATE_QUERY if count else CRErrorHistoryDAO.CREATE_QUERY
        cursor.execute(query, (num_crashes, app_id, error_type, crash_hash, version, date))
        db_conn.commit()


class CRAppLoadHistoryDAO(object):
    WHERE_CLAUSE = 'WHERE app_id=? AND start_date=? AND end_date=?;'
    SELECT_QUERY = 'SELECT num_app_loads FROM app_load_history ' + WHERE_CLAUSE
    COUNT_QUERY = 'SELECT COUNT(*) FROM app_load_history ' + WHERE_CLAUSE
    UPDATE_QUERY = 'UPDATE app_load_history SET num_app_loads=? ' + WHERE_CLAUSE
    CREATE_QUERY = ('INSERT INTO app_load_history (num_app_loads, app_id, start_date, end_date)' +
                    'VALUES (?, ?, ?, ?);')

    @staticmethod
    def num_previously_known(app_id, start_date, end_date):
        db_conn = create_db_connection()
        cursor = db_conn.cursor()
        cursor.execute(CRAppLoadHistoryDAO.SELECT_QUERY, (app_id, start_date, end_date))
        all_results = cursor.fetchall()

        if len(all_results):
            return all_results[0][0]

        return 0

    @staticmethod
    def set_known_occurrences(app_id, start_date, end_date, num_app_loads):
        db_conn = create_db_connection()
        cursor = db_conn.cursor()
        cursor.execute(CRAppLoadHistoryDAO.COUNT_QUERY, (app_id, start_date, end_date))
        count = cursor.fetchone()[0]
        query = CRAppLoadHistoryDAO.UPDATE_QUERY if count else CRAppLoadHistoryDAO.CREATE_QUERY
        cursor.execute(query, (num_app_loads, app_id, start_date, end_date))
        db_conn.commit()

