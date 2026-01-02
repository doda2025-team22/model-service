import time
from collections import OrderedDict


class SMSCache:
    def __init__(self, ttl=300, max_size=1000):
        self.cache = OrderedDict()
        self.ttl = ttl
        self.max_size = max_size

    def get(self, key):
        now = time.time()
        if key in self.cache:
            value, timestamp = self.cache.get(key)
            if now - timestamp < self.ttl:
                self.cache.move_to_end(key)
                return value
        return None

    def set(self, key, value):
        now = time.time()
        if key in self.cache:
            self.cache.pop(key)
        elif len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        self.cache[key] = (value, now)

    def clear(self):
        self.cache.clear()
