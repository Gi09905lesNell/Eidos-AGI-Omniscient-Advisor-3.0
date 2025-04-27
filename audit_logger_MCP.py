from mcprotocol import SecureServer
import blockchain_logger

class AuditLoggerMCP(SecureServer):
    def __init__(self):
        self.logger = blockchain_logger.configure()
        
    @endpoint('/v1/log/record')
    def log_operation(self, params):
        self.logger.log(params['action'], metadata=params.get('meta'))
        return {"tx_hash": self.logger.last_tx_hash}