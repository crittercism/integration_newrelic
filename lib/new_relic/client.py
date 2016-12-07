import logging
import os
import requests


class NewRelicClient(object):
    NEW_RELIC_API_DOMAIN = os.environ.get(
        'NR_API_DOMAIN',
        'insights-collector.newrelic.com'
    )
    NEW_RELIC_URL = 'https://{}/v1/accounts/{}/events'
    EVENTS_PER_CHUNK = os.environ.get('NR_EVENTS_PER_CHUNK', 1000)

    def __init__(self, account_id, insert_key):

        self._insert_key = insert_key  # auth_hash.get('insert_key')
        self.account_id = account_id  # auth_hash.get('account_id')

        if not self._insert_key:
            raise Exception('Need Insert Key')

        if not self.account_id:
            raise Exception('Need Account Id')

    def __request(self, verb, body_data):
        headers = {
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8',
            'Accept': 'application/json',
            'Connection': 'keep-alive',
        }

        if self._insert_key:
            headers.update({'X-Insert-Key': self._insert_key})

        url = self.NEW_RELIC_URL.format(
            self.NEW_RELIC_API_DOMAIN,
            self.account_id
        )

        logging.getLogger().debug('Making request to: {}'.format(url))

        response = None

        if verb == 'GET':
            response = requests.get(url, headers=headers)
        elif verb == 'POST':
            response = requests.post(url, headers=headers, json=body_data)
        else:
            raise TypeError

        return response.json()

    def post_events(self, events):
        logging.getLogger().info(
            'Posting events to New Relic num_events: {}'.format(len(events))
        )
        logging.getLogger().debug(
            'chunk_size: {}'.format(self.EVENTS_PER_CHUNK)
        )

        num_events = len(events)
        num_chunks = num_events / self.EVENTS_PER_CHUNK + 1

        #TODO (sf) figure out what the heck this is and then kill it with fire
        chunked_events = [events[i * self.EVENTS_PER_CHUNK:min((i + 1) * self.EVENTS_PER_CHUNK, num_events)] for i in
                          range(0, num_chunks)]

        for chunk in chunked_events:
            logging.getLogger().info(
                'Posting chunk to New Relic length: {}'.format(len(chunk))
            )

            if len(chunk):
                logging.getLogger().debug(
                    'First event in chunk: {}'.format(chunk[0].as_dict())
                )

            body = [event.as_dict() for event in chunk]
            response = self.__request('POST', body)
            logging.getLogger().debug('NewRelic response={}'.format(response))
