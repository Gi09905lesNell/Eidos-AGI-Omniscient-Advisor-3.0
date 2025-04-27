from mcprotocol import SecureServer
from eidos_sdk.legal import ComplianceEngine

class ComplianceChecker(SecureServer):
    def __init__(self):
        self.engine = ComplianceEngine()
        
    @endpoint('/v1/compliance/check')
    def check_compliance(self, params):
        return self.engine.validate(
            action=params['action'],
            jurisdiction=params['jurisdiction']
        )