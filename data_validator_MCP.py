from mcprotocol import SecureServer
from pydantic import BaseModel, validator
from typing import Dict, Any, Optional
from datetime import datetime
import logging

class DataValidatorMCP(SecureServer):
    """
    Data validation service using MCP protocol
    Handles schema validation requests through a secure endpoint
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    @endpoint('/v1/validate/schema')
    def validate_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates incoming data against a predefined schema
        
        Args:
            params: Dictionary containing data to validate
            
        Returns:
            Validated and sanitized data dictionary
        """
        class RequestModel(BaseModel):
            data: Dict[str, Any]
            timestamp: datetime = datetime.now()
            schema_version: Optional[str] = "1.0"
            
            class Config:
                # Enable extra validation features
                extra = "forbid"
                validate_assignment = True
                
            @validator('data')
            def validate_data_structure(cls, v):
                if not isinstance(v, dict):
                    raise ValueError("Data must be a dictionary")
                if not v:
                    raise ValueError("Data dictionary cannot be empty")
                return v
                
        try:
            # Validate and sanitize input data
            validated_data = RequestModel(**params).dict(
                exclude_unset=True,
                exclude_none=True,
                by_alias=True
            )
            
            self.logger.info(f"Successfully validated data with schema version {validated_data.get('schema_version')}")
            
            return {
                "status": "success",
                "data": validated_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Validation failed: {str(e)}")
            # Handle validation errors gracefully
            return {
                "error": str(e),
                "status": "validation_failed",
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "error_type": e.__class__.__name__,
                    "params_received": params
                }
            }
