from mcprotocol import SecureServer
from eidos_sdk.knowledge import GraphQuery
from typing import Dict, Any, Optional, List
import logging
import time
from datetime import datetime
from cachetools import TTLCache
class KnowledgeConnector(SecureServer):
    """
    Knowledge Graph API connector that provides secure access to knowledge graph operations
    """
    
    def __init__(self, cache_size: int = 1000, cache_ttl: int = 3600):
        """
        Initialize the knowledge connector with caching capabilities
        
        Args:
            cache_size: Maximum number of cached items
            cache_ttl: Time-to-live for cache entries in seconds
        """
        super().__init__()
        self.graph = GraphQuery(cache_size=cache_size)
        self.query_cache = TTLCache(maxsize=cache_size, ttl=cache_ttl)
        self.logger = logging.getLogger(__name__)
        
    @endpoint('/v1/knowledge/query')
    def query_knowledge(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a knowledge graph query with caching and error handling
        
        Args:
            params: Query parameters including entity, relation and depth
        Returns:
            Query results from the knowledge graph
        """
        try:
            # Generate cache key
            cache_key = f"{params['entity']}:{params.get('relation')}:{params.get('depth', 1)}"
            
            # Check cache first
            if cache_key in self.query_cache:
                self.logger.info(f"Cache hit for query: {cache_key}")
                return self.query_cache[cache_key]
            
            # Execute query
            result = self.graph.execute(
                entity=params['entity'],
                relation=params.get('relation'),
                depth=params.get('depth', 1)
            )
            
            # Cache the result
            self.query_cache[cache_key] = result
            return result
            
        except Exception as e:
            self.logger.error(f"Query failed: {str(e)}")
            raise
            
    @endpoint('/v1/knowledge/batch_query')
    def batch_query(self, params: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Execute multiple knowledge graph queries in batch
        
        Args:
            params: List of query parameters
        Returns:
            List of query results
        """
        results = []
        for query in params.get('queries', []):
            try:
                result = self.query_knowledge(query)
                results.append(result)
            except Exception as e:
                results.append({'error': str(e)})
        return results
        
    @endpoint('/v1/knowledge/stats')
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge graph and query performance
        """
        return {
            'cache_size': len(self.query_cache),
            'cache_info': self.query_cache.info(),
            'graph_stats': self.graph.get_statistics()
        }
        
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        Validate query parameters
        
        Args:
            params: Query parameters to validate
        Returns:
            True if parameters are valid
        """
        required_fields = ['entity']
        if not all(field in params for field in required_fields):
            raise ValueError(f"Missing required fields: {required_fields}")
            
        if 'depth' in params:
            depth = params['depth']
            if not isinstance(depth, int) or depth < 1 or depth > 5:
                raise ValueError("Depth must be an integer between 1 and 5")
                
        return True
        
    def cleanup(self):
        """
        Cleanup resources and connections
        """
        self.query_cache.clear()
        self.graph.close()
