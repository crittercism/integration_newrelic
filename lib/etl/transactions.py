from datetime import datetime
from lib.etl.base import BaseETL
from lib.new_relic.models import Event


class TransactionsETL(BaseETL):
    def __init__(self,
                 app_id, lookback_minutes, new_relic_account, new_relic_app_id):
        super(TransactionsETL, self).__init__(
            app_id,
            lookback_minutes,
            new_relic_account,
            new_relic_app_id,
            'apteligent_userflow')

        period = 'PT%sM' % lookback_minutes

        transactions_groups = self._c_client.transactions_details(self._app_id,
                                                                  period)

        groups = []

        for transaction in transactions_groups:
            one_group = []
            for group in transaction['data']:
                corrected_url = group['link'].replace('txn-report', 'developers')
                corrected_v2_url = corrected_url.replace('v1.0', 'v2')
                name_and_link = (group['name'], corrected_v2_url)
                one_group.append(name_and_link)
            groups.append(one_group)

        traces_urls = []

        for group_pages in groups:
            for group_name, group_url in group_pages:
                url = '%s/traces/%s' % (group_url, period)
                traces_urls.append((group_name, url))

        for group_name, url in traces_urls:
            pages = self._c_client.get_paged_transaction_data(app_id, url)

            for page in pages:
                for trace in page['data']:
                    self._events.append(self.make_event(trace, group_name))

    def make_event(self, trace, group_name):
        dt = datetime.strptime(trace[u'traceTs'], '%Y-%m-%dT%H:%M:%S.%fZ')
        e = Event(self._new_relic_account, self._new_relic_app_id,
                  self._event_type, dt)
        e.set('group', group_name)
        for k, v in trace.items():
            e.set(k, v)
        return e

