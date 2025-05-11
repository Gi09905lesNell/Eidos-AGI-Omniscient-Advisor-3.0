from mcprotocol import SecureServer
from sentry_sdk import capture_exception
import uuid
import logging
from typing import Dict, Any
# Exception Handler class for managing and reporting errors
class ExceptionHandlerMCP(SecureServer):
    """
    A secure exception handling service that captures and reports errors.
    Inherits from SecureServer to ensure secure communication.
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    @endpoint('/v1/error/report')
    def report_error(self, params: Dict[str, Any]) -> Dict[str, str]:
        """
        Handles error reporting by capturing exceptions and generating unique event IDs.
        
        Args:
            params: Dictionary containing exception details
                   Must include 'exception' key with the exception object
        
        Returns:
            Dict containing generated event ID for error tracking
        
        Raises:
            KeyError: If exception parameter is missing
        """
        try:
            # Validate input parameters
            if 'exception' not in params:
                raise KeyError("Missing required 'exception' parameter")
                
            # Generate unique event ID for tracking
            event_id = str(uuid.uuid4())
            
            # Capture exception with Sentry
            capture_exception(params['exception'])
            
            # Log the error event
            self.logger.error(f"Error reported - Event ID: {event_id}")
            
            return {"event_id": event_id}
            
        except Exception as e:
            self.logger.error(f"Error in report_error handler: {str(e)}")
            raise
