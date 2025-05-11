from mcprotocol import SecureServer, endpoint
import blockchain_logger
import logging

class AuditLoggerMCP(SecureServer):
    def __init__(self, host='localhost', port=8000):
        # Initialize parent class
        super().__init__(host, port)
        # Initialize blockchain logger
        self.logger = blockchain_logger.configure()
        # Set standard logger
        self.std_logger = logging.getLogger(__name__)
        
    @endpoint('/v1/log/record')
    def log_operation(self, params):
        """Record operation to blockchain"""
        try:
            # Validate required parameters
            if 'action' not in params:
                raise ValueError("Missing required action parameter")
                
            # Record operation
            self.logger.log(
                action=params['action'],
                metadata=params.get('meta', {})
            )
            
            # Return transaction hash
            return {
                "status": "success",
                "tx_hash": self.logger.last_tx_hash
            }
            
        except Exception as e:
            self.std_logger.error(f"Failed to record operation: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    @endpoint('/v1/log/query')
    def query_logs(self, params):
        """Query historical log records"""
        try:
            start_time = params.get('start_time')
            end_time = params.get('end_time')
            action_type = params.get('action_type')
            
            logs = self.logger.query(
                start_time=start_time,
                end_time=end_time,
                action_type=action_type
            )
            
            return {
                "status": "success",
                "logs": logs
            }
            
        except Exception as e:
            self.std_logger.error(f"Failed to query logs: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def start(self):
        """Start server"""
        try:
            self.std_logger.info("Starting audit log server...")
            super().start()
        except Exception as e:
            self.std_logger.error(f"Server startup failed: {str(e)}")
            raise
