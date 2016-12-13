import logging
from lib.etl.base import BaseETL
from lib.etl.helpers import random_set_with, random_timestamp
from lib.new_relic.models import Event


class MetricsAggregateSplitter(BaseETL):
    NAME = 'name'
    VALUE = 'value'
    TRUE = 'true'
    FALSE = 'false'
    UNKNOWN = 'unknown'

    def mean_strategy(self, metric, metric_data):
        for group in self.get_groups():
            for group_name, (start, end) in self._ranges[group].items():
                # In case there are differences in the numbers returned due to not getting all data atomically
                end = min(end, len(self._events))
                values = random_set_with(end - start, metric_data[group].value_for_group_name(group_name))
                for i in range(start, end):
                    self._events[i].set(metric, values[i - start])

    def percentage_strategy(self, metric, metric_data):
        for group in self.get_groups():
            for group_name, (start, end) in self._ranges[group].items():
                # In case there are differences in the numbers returned due to not getting all data atomically
                end = min(end, len(self._events))
                percentage_true = metric_data[group].value_for_group_name(group_name) / 100.0
                num_true = int((end - start) * percentage_true)
                end_true = min(start + num_true + 1, end)
                for i in range(start, end_true):
                    self._events[i].set(metric, self.TRUE)
                for i in range(end_true, end):
                    self._events[i].set(metric, self.FALSE)

    def __init__(self,
                 app_id,
                 lookback_minutes,
                 new_relic_account,
                 new_relic_app_id,
                 event_type):
        super(MetricsAggregateSplitter, self).__init__(
            app_id,
            lookback_minutes,
            new_relic_account,
            new_relic_app_id, event_type
        )

        volumes = self.get_data(self.get_volume_metric())
        events_in_volume = []
        self._events = []
        for volume in volumes.values():
            events_in_volume.append(volume.total())
        num_events = max(events_in_volume)
        self._start_time, self._end_time = volumes.values()[0].time_range()
        logging.getLogger().debug('start_time: %s end_time: %s',
                                  self._start_time,
                                  self._end_time)

        if not num_events:
            logging.getLogger().info('No events to upload.')
            return

        logging.getLogger().debug('Creating events')

        for i in range(num_events):
            self._events.append(
                Event(new_relic_account,
                      new_relic_app_id,
                      event_type,
                      random_timestamp(self._start_time, self._end_time)
                      )
            )

        logging.getLogger().debug('Extracting ranges and setting volumes.')
        self._ranges = self.get_event_ranges(volumes)
        logging.getLogger().debug('Getting the rest of the data and processing')
        for metric, strategy in self.get_metrics_and_strategies():
            metric_data = self.get_data(metric)
            strategy(self, metric, metric_data)
        logging.getLogger().info('ETL Completed')

    def get_event_ranges(self, volumes):
        ranges = {}
        for group in self.get_groups():
            ranges[group] = {}
            events_updated = 0
            for s in volumes[group].get_slices():
                num_in_group = int(s[self.VALUE])
                ranges[group][s[self.NAME]] = (events_updated,
                                               events_updated + num_in_group)
                for i in range(events_updated,
                               events_updated + num_in_group):
                    try:
                        self._events[i].set(group, s[self.NAME])
                    except IndexError as e:
                        raise
                events_updated += num_in_group
            while events_updated < len(self._events):
                self._events[events_updated].set(group, self.UNKNOWN)
                events_updated += 1
        return ranges

    def get_volume_metric(self):
        raise

    def get_data(self, metric):
        raise

    def get_groups(self):
        raise

    def get_metrics_and_strategies(self):
        raise
