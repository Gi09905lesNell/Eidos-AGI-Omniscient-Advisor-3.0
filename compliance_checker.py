from mcprotocol import SecureServer
from eidos_sdk.legal import ComplianceEngine
from typing import Dict, Any, Optional
from http import HTTPStatus
from datetime import datetime
import logging
from dataclasses import dataclass

@dataclass
class ComplianceRequest:
    """Data class for compliance check request parameters"""
    action: str
    jurisdiction: str

class ComplianceChecker(SecureServer):
    """A secure server implementation for compliance checking"""
    
    def __init__(self):
        super().__init__()
        self.engine = ComplianceEngine()
        self.last_check_time: Optional[datetime] = None
        self._setup_logging()
    
    def _setup_logging(self):
        """Initialize logging configuration"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
    def _validate_request_params(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate incoming request parameters"""
        required_params = {'action', 'jurisdiction'}
        if not all(key in params for key in required_params):
            missing = required_params - set(params.keys())
            return {
                'status': HTTPStatus.BAD_REQUEST,
                'error': f'Missing required parameters: {", ".join(missing)}'
            }
        return None
        
    @endpoint('/v1/compliance/check')
    def check_compliance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check compliance for given action and jurisdiction
        
        Args:
            params: Dictionary containing action and jurisdiction
            
        Returns:
            Dict containing compliance check results and metadata
        """
        try:
            # Validate parameters
            validation_error = self._validate_request_params(params)
            if validation_error:
                return validation_error
                
            # Create request object
            request = ComplianceRequest(
                action=params['action'],
                jurisdiction=params['jurisdiction']
            )
            
            # Record check time
            self.last_check_time = datetime.utcnow()
            
            # Perform compliance validation
            self.logger.info(f"Performing compliance check for action: {request.action} in {request.jurisdiction}")
            validation_result = self.engine.validate(
                action=request.action,
                jurisdiction=request.jurisdiction
            )
            
            response = {
                'status': HTTPStatus.OK,
                'result': validation_result,
                'timestamp': self.last_check_time.isoformat(),
                'request_params': {
                    'action': request.action,
                    'jurisdiction': request.jurisdiction
                }
            }
            
            self.logger.info(f"Compliance check completed: {response}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error during compliance check: {str(e)}", exc_info=True)
            return {
                'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'error': str(e)
            }
            
    def get_last_check_time(self) -> Optional[str]:
        """Return the timestamp of last compliance check"""
        return self.last_check_time.isoformat() if self.last_check_time else None
        
    def health_check(self) -> Dict[str, Any]:
        """Return the health status of the compliance checker"""
        return {
            'status': 'healthy',
            'last_check_time': self.get_last_check_time(),
            'engine_status': self.engine.status()
        }
