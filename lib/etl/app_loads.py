import logging
from crittercism.models import ErrorMonitoringRequest
from lib.etl.metrics_aggregate_splitter import MetricsAggregateSplitter
from lib.history.dao import CRAppLoadHistoryDAO


class AppLoadETL(MetricsAggregateSplitter):
    ALL_GROUPS = ['appVersion', 'os', 'carrier', 'device']

    NO_ADDITIONAL_METRICS = {}

    def __init__(self, app_id, lookback_minutes, new_relic_account, new_relic_app_id):
        super(AppLoadETL, self).__init__(app_id, lookback_minutes, new_relic_account, new_relic_app_id, 'apteligent_appload')

    def get_data(self, metric):
        logging.getLogger().debug('Getting data for metric=%s', metric)

        minutes = self._lookback_minutes if self._lookback_minutes in ErrorMonitoringRequest.VALID_DURATIONS else 1440
        performance_request = ErrorMonitoringRequest(self._app_id, metric, minutes)

        data = {}
        for group in self.ALL_GROUPS:
            logging.getLogger().debug('Getting data for metric=%s groupBy=%s', metric, group)
            performance_request.add_optional_params({'groupBy': group})
            data[group] = self._c_client.error_monitoring_pie(performance_request)

        return data

    def get_groups(self):
        return self.ALL_GROUPS

    def get_metrics_and_strategies(self):
        return self.NO_ADDITIONAL_METRICS.items()

    def get_volume_metric(self):
        return 'appLoads'

    def get_num_already_uploaded(self):
        return CRAppLoadHistoryDAO.num_previously_known(self._app_id, self._start_time, self._end_time)

    def save_state(self):
        num_uploaded = len(self.unpacked_events())
        if num_uploaded:
            CRAppLoadHistoryDAO.set_known_occurrences(self._app_id, self._start_time, self._end_time, num_uploaded)

