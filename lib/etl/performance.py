import logging
from crittercism.models import PerformanceManagementRequest
from lib.etl.metrics_aggregate_splitter import MetricsAggregateSplitter


class PerformanceMetricsETL(MetricsAggregateSplitter):
    ALL_GROUPS = ['appId', 'appVersion', 'os', 'carrier', 'device', 'service']

    PERFORMANCE_METRICS = {
        'latency': MetricsAggregateSplitter.mean_strategy,
        'dataIn': MetricsAggregateSplitter.mean_strategy,
        'dataOut': MetricsAggregateSplitter.mean_strategy,
        'errors': MetricsAggregateSplitter.percentage_strategy
    }

    def __init__(self, app_id, lookback_minutes, new_relic_account, new_relic_app_id):
        super(PerformanceMetricsETL, self).__init__(app_id, lookback_minutes, new_relic_account, new_relic_app_id,
                                                    'Mobile')

    def get_data(self, metric):
        logging.getLogger().debug('Getting data for metric=%s', metric)

        minutes = self._lookback_minutes if self._lookback_minutes in PerformanceManagementRequest.VALID_DURATIONS else 15
        performance_request = PerformanceManagementRequest(metric, minutes)
        performance_request.add_optional_params({'appIds': [self._app_id]})

        data = {}
        for group in self.ALL_GROUPS:
            logging.getLogger().debug('Getting data for metric=%s groupBy=%s', metric, group)
            performance_request.add_optional_params({'groupBy': group})
            data[group] = self._c_client.performance_management_pie(performance_request)

        return data

    def get_groups(self):
        return self.ALL_GROUPS

    def get_metrics_and_strategies(self):
        return self.PERFORMANCE_METRICS.items()

    def get_volume_metric(self):
        return 'volume'