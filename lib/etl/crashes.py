from datetime import timedelta
from lib.etl.errors_by_version import ErrorsByVersionProcessor


class CrashETL(ErrorsByVersionProcessor):
    EVENT_TYPE = 'apteligent_crash'

    def __init__(self, app_id, lookback_minutes, new_relic_account, new_relic_app_id):
        super(CrashETL, self).__init__(app_id, lookback_minutes, new_relic_account, new_relic_app_id, self.EVENT_TYPE)

    def get_errors_with_details(self, lookback_minutes):
        ERRORS = 'errors'

        crash_summaries = self._c_client.crash_paginated_tables(
            self._app_id,
            app_version='all',
            lookback_timedelta=timedelta(minutes=lookback_minutes)
        )

        versions = self._c_client.app_versions(self._app_id)

        daily_occurrences = {}
        for version in versions:
            versioned_summary = self._c_client.crash_paginated_tables(
                self._app_id,
                app_version=version,
                lookback_timedelta=timedelta(minutes=lookback_minutes)
            )
            for error in versioned_summary[ERRORS]:
                if daily_occurrences.get(error['hash']):
                    daily_occurrences[error['hash']][version] = error['daily_occurrences']

                else:
                    daily_occurrences[error['hash']] = {version: error['daily_occurrences']}
        crashes = []
        for summary in crash_summaries[ERRORS]:
            summary['daily_occurrences_by_version'] = daily_occurrences.get(
                summary['hash']
            )
            crashes.append(self._c_client.crash_details(summary))

        return crashes
