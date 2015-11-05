import logging
import os
import random
from lib.etl.app_loads import AppLoadETL
from lib.etl.crashes import CrashETL
from lib.etl.exceptions import ExceptionETL
from lib.etl.performance import PerformanceMetricsETL
from lib.etl.transactions import TransactionsETL


DATA_ACTION = os.environ.get('DATA_ACTION', 'upload')
LOOKBACK_MINUTES = int(os.environ.get('LOOKBACK_MINUTES', 15))


class ETLDispatcher(object):
    def __init__(self, new_relic_client, crittercism_app_id):
        self._nrc = new_relic_client
        self.log = logging.getLogger()
        self.cr_app_id = crittercism_app_id

    def handle_events(self, etl_obj):
        events = etl_obj.unpacked_events()
        num_events = len(events)
        logging.getLogger().info('Events ready: %s', num_events)
        if DATA_ACTION == 'upload':
            self._nrc.post_events(events)
            etl_obj.save_state()
        elif events:
            logging.getLogger().debug('10 random events: %s' % [random.choice(events).as_dict()
                                                                for i in range(min(10, num_events))])

    ALL_ETL = {
        'Aggregates': PerformanceMetricsETL,
        'Exception': ExceptionETL,
        'Transactions': TransactionsETL,
        'Crash': CrashETL,
        'App Load': AppLoadETL,
    }

    def handle_etl(self):
        for etl_name, etl_class in self.ALL_ETL.items():
            self.log.info('Pulling %s Data from Crittercism and processing app_id=%s', etl_name, self.cr_app_id)
            etl_obj = etl_class(self.cr_app_id, LOOKBACK_MINUTES, self._nrc.account_id, 1)
            logging.getLogger().info('Uploading %s app_id=%s', etl_name, self.cr_app_id)
            self.handle_events(etl_obj)
            self.log.info('Completed %s app_id=%s', etl_name, self.cr_app_id)
