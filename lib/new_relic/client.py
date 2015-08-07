import logging
import os
import json
import httplib2


class NewRelicClient(object):
    NEW_RELIC_API_DOMAIN = os.environ.get('NR_API_DOMAIN', 'insights-collector.newrelic.com')
    NEW_RELIC_URL = 'https://%s/v1/accounts/%s/events'
    EVENTS_PER_CHUNK = os.environ.get('NR_EVENTS_PER_CHUNK', 1000)

    def __init__(self, account_id, insert_key):
        self._http = httplib2.Http(timeout=60)

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

        logging.getLogger().debug('Making request to: %s',
                                  self.NEW_RELIC_URL % (self.NEW_RELIC_API_DOMAIN, self.account_id))

        response, content = self._http.request(self.NEW_RELIC_URL % (self.NEW_RELIC_API_DOMAIN, self.account_id),
                                               verb,
                                               headers=headers,
                                               body=json.dumps(body_data))

        return json.loads(content)

    def post_events(self, events):
        logging.getLogger().info('Posting events to New Relic num_events: %s', len(events))
        logging.getLogger().debug('chunk_size: %s', self.EVENTS_PER_CHUNK)

        num_events = len(events)
        num_chunks = num_events / self.EVENTS_PER_CHUNK + 1

        chunked_events = [events[i * self.EVENTS_PER_CHUNK:min((i + 1) * self.EVENTS_PER_CHUNK, num_events)] for i in
                          range(0, num_chunks)]

        for chunk in chunked_events:
            logging.getLogger().info('Posting chunk to New Relic length: %s', len(chunk))
            if len(chunk):
                logging.getLogger().debug('First event in chunk: %s', chunk[0].as_dict())
            body = [event.as_dict() for event in chunk]
            response = self.__request('POST', body)
            logging.getLogger().debug('NewRelic response=%s', response)
