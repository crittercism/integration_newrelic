from datetime import timedelta
from lib.etl.errors_by_version import ErrorsByVersionProcessor


class CrashETL(ErrorsByVersionProcessor):
    EVENT_TYPE = 'Crash'

    def __init__(self, app_id, lookback_minutes, new_relic_account, new_relic_app_id):
        super(CrashETL, self).__init__(app_id, lookback_minutes, new_relic_account, new_relic_app_id, self.EVENT_TYPE)

    def get_errors_with_details(self, lookback_minutes):
        crash_summaries = self._c_client.app_crash_summaries(self._app_id,
                                                             lookback_timedelta=timedelta(minutes=lookback_minutes))
        crashes = [self._c_client.crash_details(summary[u'hash']) for summary in crash_summaries]

        return crashes