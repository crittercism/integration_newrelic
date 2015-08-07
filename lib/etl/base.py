import os
from crittercism.client import CrittercismClient


class BaseETL(object):
    def __init__(self, app_id, lookback_minutes, new_relic_account, new_relic_app_id, event_type):
        self._lookback_minutes = lookback_minutes
        self._app_id = app_id
        self._events = []
        self._new_relic_account = new_relic_account
        self._new_relic_app_id = new_relic_app_id
        self._event_type = event_type

        self._c_client = CrittercismClient({
            'client_id': os.environ.get('CR_CLIENT_ID'),
            'username': os.environ.get('CR_USERNAME'),
            'password': os.environ.get('CR_PASSWORD'),
        })

    def unpacked_events(self):
        return self._events

    def save_state(self):
        pass