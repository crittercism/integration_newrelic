import time


class Event(object):
    TRANSLATION_MAP = {
        'os': 'osVersion',
        'latency': 'interactionDuration',
    }

    def __init__(self, accountId, appId, eventType, dtime):
        seconds_since_epoch = time.mktime(dtime.timetuple()) + dtime.microsecond / 1E6
        self._dict = {
            'accountId': int(accountId),
            'appId': appId,
            'eventType': eventType,
            'timestamp': int(seconds_since_epoch),
            # 'category': 'Custom',
            # 'category': 'Interaction',
        }

    def as_dict(self):
        return self._dict

    def set(self, key, value):
        self._dict[self.TRANSLATION_MAP.get(key, key)] = value