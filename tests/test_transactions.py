import mock
from lib.etl.transactions import TransactionsETL
from lib.history.dao import create_tables
from lib.new_relic.client import NewRelicClient
from lib.new_relic.models import Event
from tests.base import BaseTestCase, test_db_location
from tests.data import transactions
from tests.helpers import MockNewRelicHTTP


class MockCrittercismClient(mock.MagicMock):
    def transactions_details(self, ignoreb, ignorec):
        return transactions.TRANSACTIONS_DETAILS_DATA

    def get_paged_transaction_data(self, ignoreb, url):
        return transactions.TRANSACTIONS_GROUPS_DATA[url]


class TransactionsTestCase(BaseTestCase):
    @mock.patch('crittercism.client.CrittercismClient', MockCrittercismClient)
    @mock.patch('lib.etl.base.CrittercismClient', MockCrittercismClient)
    @mock.patch('httplib2.Http', MockNewRelicHTTP)
    def test_transactions_etl(self):
        etl_obj = TransactionsETL('bogusAppId', 8008, 666, 1)
        events = etl_obj.unpacked_events()

        for e in events:
            self.validate_event(e)
            self.assertIn(e.as_dict()['group'], {'bogusName1', 'bogusName2', 'bogusName3', 'bogusName4'})

        nrc = NewRelicClient(1, 'bogusKey')
        nrc.post_events(events[:2])
