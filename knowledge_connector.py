from mcprotocol import SecureServer
from eidos_sdk.knowledge import GraphQuery

class KnowledgeConnector(SecureServer):
    def __init__(self):
        self.graph = GraphQuery(cache_size=1000)
        
    @endpoint('/v1/knowledge/query')
    def query_knowledge(self, params):
        return self.graph.execute(
            entity=params['entity'],
            relation=params.get('relation'),
            depth=params.get('depth', 1)
        )