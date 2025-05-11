from mcprotocol import SecureServer
from datetime import timedelta
from cachetools import TTLCache
from typing import Any, Optional
from logging import getLogger
logger = getLogger(__name__)

class DataCacheMCP(SecureServer):
    """
    A secure caching server implementation that provides TTL-based caching functionality.
    Inherits from SecureServer to ensure secure communication.
    """
    
    def __init__(self, maxsize: int = 1000, ttl_minutes: int = 5):
        """
        Initialize the cache with configurable size and TTL.
        
        Args:
            maxsize (int): Maximum number of items in cache
            ttl_minutes (int): Time-to-live in minutes for cache entries
        """
        super().__init__()
        self.cache = TTLCache(maxsize=maxsize, ttl=timedelta(minutes=ttl_minutes))
        
    @endpoint('/v1/cache/get')
    def get_cached(self, params: dict) -> Optional[Any]:
        """
        Retrieve a value from cache by key.
        
        Args:
            params (dict): Request parameters containing the 'key'
            
        Returns:
            Optional[Any]: Cached value if found, None otherwise
            
        Raises:
            KeyError: If 'key' is not provided in params
        """
        try:
            key = params['key']
            value = self.cache.get(key)
            if value is None:
                logger.debug(f"Cache miss for key: {key}")
            return value
        except KeyError:
            logger.error("Missing required 'key' parameter")
            raise KeyError("Missing required 'key' parameter")
