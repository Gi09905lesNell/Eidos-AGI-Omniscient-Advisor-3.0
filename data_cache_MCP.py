from mcprotocol import SecureServer
from datetime import timedelta
from cachetools import TTLCache

class DataCacheMCP(SecureServer):
    def __init__(self):
        self.cache = TTLCache(maxsize=1000, ttl=timedelta(minutes=5))
        
    @endpoint('/v1/cache/get')
    def get_cached(self, params):
        return self.cache.get(params['key'])