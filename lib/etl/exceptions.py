from datetime import timedelta
from lib.etl.errors_by_version import ErrorsByVersionProcessor


class ExceptionETL(ErrorsByVersionProcessor):
    EVENT_TYPE = 'apteligent_exception'

    def __init__(self, app_id, lookback_minutes, new_relic_account, new_relic_app_id):
        super(ExceptionETL, self).__init__(app_id, lookback_minutes, new_relic_account, new_relic_app_id,
                                           self.EVENT_TYPE)

    def get_errors_with_details(self, lookback_minutes):
        exception_summaries = self._c_client.app_exception_summaries(self._app_id,
                                                                     lookback_timedelta=timedelta(
                                                                     minutes=lookback_minutes))
        exceptions = [self._c_client.exception_details(summary[u'hash']) for summary in exception_summaries]
        return exceptions