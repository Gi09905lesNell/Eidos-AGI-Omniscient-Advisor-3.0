from mcprotocol import SecureServer
import semver
import logging
from typing import Dict, Any, Optional
from datetime import datetime
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VersionControlMCP(SecureServer):
    """
    Version Control Management Class for handling semantic versioning operations
    Inherits from SecureServer to provide secure API endpoints
    """
    
    def __init__(self):
        """Initialize the VersionControlMCP with default configurations"""
        super().__init__()
        self.version_history = {}
        self.last_check = datetime.now()
    
    @endpoint('/v1/version/compare')
    def compare_versions(self, params: Dict[str, str]) -> Dict[str, int]:
        """
        Compare two semantic versions and return their relationship
        
        Args:
            params (Dict): Dictionary containing v1 and v2 version strings
            
        Returns:
            Dict: Contains comparison result (-1, 0, or 1)
        """
        try:
            # Validate input parameters
            self._validate_version_params(params)
            
            # Log the comparison request
            logger.info(f"Comparing versions: {params['v1']} vs {params['v2']}")
            
            # Perform version comparison
            result = semver.compare(params['v1'], params['v2'])
            
            # Store comparison in history
            self._record_comparison(params['v1'], params['v2'], result)
            
            return {"result": result}
            
        except ValueError as e:
            logger.error(f"Version comparison error: {str(e)}")
            raise InvalidVersionError(f"Invalid version format: {str(e)}")
    
    @endpoint('/v1/version/validate')
    def validate_version(self, params: Dict[str, str]) -> Dict[str, bool]:
        """
        Validate if a version string follows semantic versioning rules
        
        Args:
            params (Dict): Dictionary containing version string
            
        Returns:
            Dict: Contains validation result
        """
        try:
            version = params.get('version')
            is_valid = semver.VersionInfo.isvalid(version)
            return {"is_valid": is_valid}
        except Exception as e:
            logger.error(f"Version validation error: {str(e)}")
            return {"is_valid": False}
    
    @endpoint('/v1/version/increment')
    def increment_version(self, params: Dict[str, str]) -> Dict[str, str]:
        """
        Increment version number based on specified part (major, minor, patch)
        
        Args:
            params (Dict): Dictionary containing version and part to increment
            
        Returns:
            Dict: Contains new version string
        """
        version = params.get('version')
        part = params.get('part', 'patch')
        
        ver_info = semver.VersionInfo.parse(version)
        
        if part == 'major':
            new_version = ver_info.bump_major()
        elif part == 'minor':
            new_version = ver_info.bump_minor()
        else:
            new_version = ver_info.bump_patch()
            
        return {"new_version": str(new_version)}
    
    def _validate_version_params(self, params: Dict[str, str]) -> None:
        """
        Validate version parameters
        
        Args:
            params (Dict): Parameters to validate
            
        Raises:
            ValueError: If parameters are invalid
        """
        if 'v1' not in params or 'v2' not in params:
            raise ValueError("Missing version parameters")
            
        if not semver.VersionInfo.isvalid(params['v1']) or \
           not semver.VersionInfo.isvalid(params['v2']):
            raise ValueError("Invalid version format")
    
    def _record_comparison(self, v1: str, v2: str, result: int) -> None:
        """
        Record version comparison in history
        
        Args:
            v1 (str): First version
            v2 (str): Second version
            result (int): Comparison result
        """
        timestamp = datetime.now()
        self.version_history[timestamp] = {
            'v1': v1,
            'v2': v2,
            'result': result
        }

class InvalidVersionError(Exception):
    """Custom exception for invalid version formats"""
    pass
