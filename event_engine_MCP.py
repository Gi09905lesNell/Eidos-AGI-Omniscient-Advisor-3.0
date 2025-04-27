from mcprotocol import SecureServer
from collections import defaultdict

class EventEngineMCP(SecureServer):
    def __init__(self):
        self.handlers = defaultdict(list)
        
    @endpoint('/v1/event/register')
    def register_handler(self, params):
        self.handlers[params['event_type']].append(params['callback'])
        return {"status": "registered"}