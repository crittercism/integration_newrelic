import copy
import logging
from datetime import datetime
from lib.etl.base import BaseETL
from lib.history.dao import CRErrorHistoryDAO
from lib.new_relic.models import Event


class ErrorsByVersionProcessor(BaseETL):
    def __init__(self, app_id, lookback_minutes, new_relic_account, new_relic_app_id, event_type):
        super(ErrorsByVersionProcessor, self).__init__(app_id, lookback_minutes,
                                                       new_relic_account, new_relic_app_id, event_type)

        self._to_save = []
        errors_with_details = self.get_errors_with_details(lookback_minutes)

        events = []
        cumulative_errors_found = 0
        cumulative_previously_known = 0
        for cr_error in errors_with_details:
            todays_date = cr_error.current_date().strftime('%Y-%m-%d')
            e = Event(new_relic_account, new_relic_app_id, event_type, datetime.now())

            for k, v in cr_error.as_event_dict().items():
                e.set(k, v)

            for version, version_occurrences in cr_error.current_date_occurrences().items():
                previously_known = CRErrorHistoryDAO.num_previously_known(self._app_id, event_type,
                                                                          cr_error.crittercism_hash(),
                                                                          version, todays_date)

                delta = version_occurrences - previously_known

                cumulative_errors_found += version_occurrences
                cumulative_previously_known += previously_known

                logging.getLogger().debug('Building event for cr_error=%s version=%s previously_known=%s num_new=%s',
                                          cr_error.crittercism_hash(), version, previously_known, delta)
                version_event = copy.deepcopy(e)
                version_event.set(u'version', version)

                events += [version_event] * delta

                self._to_save.append((event_type, cr_error.crittercism_hash(), version,
                                      todays_date, version_occurrences))

        self._events = events
        logging.getLogger().info('AppId=%s Event=%s num_found=%s num_known=%s num_new=%s',
                                 app_id, event_type, cumulative_errors_found, cumulative_previously_known, len(events))

    def get_errors_with_details(self, lookback_minutes):
        raise

    def save_state(self):
        num_uploaded = len(self.unpacked_events())
        if num_uploaded:
            for update_tuple in self._to_save:
                event_type, cr_hash, version, todays_date, version_occurrences = update_tuple
                CRErrorHistoryDAO.set_known_occurrences(self._app_id, event_type, cr_hash, version, todays_date,
                                                        version_occurrences)



