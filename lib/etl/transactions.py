from datetime import datetime
from lib.etl.base import BaseETL
from lib.new_relic.models import Event


class TransactionsETL(BaseETL):
    def __init__(self, app_id, lookback_minutes, new_relic_account, new_relic_app_id):
        super(TransactionsETL, self).__init__(app_id, lookback_minutes, new_relic_account, new_relic_app_id,
                                              'Transaction')

        period = 'PT%sM' % lookback_minutes

        transactions_groups = self._c_client.transactions_details(self._app_id, period)

        groups = [[(g[u'name'], g[u'link']) for g in t[u'groups']] for t in transactions_groups]

        for group_pages in groups:
            for group_name, group_url in group_pages:
                # We modify the URL because of bug in API not including API version
                url = '%s/traces/%s' % (group_url, period)
                url = url.replace(app_id, 'v1.0/%s' % app_id)

                for page in self._c_client.get_paged_transaction_data(app_id, url):
                    for trace in page[u'traces']:
                        self._events.append(self.make_event(trace, group_name))

    def make_event(self, trace, group_name):
        dt = datetime.strptime(trace[u'traceTs'], '%Y-%m-%dT%H:%M:%S.000Z')
        e = Event(self._new_relic_account, self._new_relic_app_id, self._event_type, dt)
        e.set('group', group_name)
        for k, v in trace.items():
            e.set(k, v)
        return e

