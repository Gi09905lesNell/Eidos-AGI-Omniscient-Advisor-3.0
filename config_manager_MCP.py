from mcprotocol import SecureServer
import configparser
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

class ConfigStatus(Enum):
    """Configuration status enumeration"""
    SUCCESS = "success"
    ERROR = "error"

@dataclass
class ConfigResponse:
    """Configuration operation response data class"""
    status: ConfigStatus
    message: str

class ConfigManagerMCP(SecureServer):
    """Enhanced configuration management system with secure server capabilities"""
    
    DEFAULT_CONFIG = {
        'server_host': 'localhost',
        'server_port': '8080',
        'debug_mode': 'False'
    }
    
    def __init__(self, config_path: str = "config.ini"):
        super().__init__()
        self.config = configparser.ConfigParser()
        self.config_path = Path(config_path)
        self._setup_logging()
        self._load_config()
    
    def _setup_logging(self) -> None:
        """Configure logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("config_manager.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _load_config(self) -> None:
        """Load configuration file, create default config if not exists"""
        try:
            if self.config_path.exists():
                self.config.read(self.config_path)
                self.logger.info("Configuration loaded successfully")
            else:
                self._create_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            raise
    
    def _create_default_config(self) -> None:
        """Create default configuration file"""
        self.config['DEFAULT'] = self.DEFAULT_CONFIG
        self._save_config()
        
    def _save_config(self) -> None:
        """Save configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)
            self.logger.info("Configuration saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
            raise

    def _validate_config_params(self, params: Dict[str, Any]) -> Optional[ConfigResponse]:
        """Validate configuration parameters"""
        if not all(key in params for key in ['section', 'values']):
            return ConfigResponse(
                ConfigStatus.ERROR,
                "Missing required parameters: 'section' and 'values'"
            )
        
        if not isinstance(params['values'], dict):
            return ConfigResponse(
                ConfigStatus.ERROR,
                "Parameter 'values' must be a dictionary"
            )
        
        return None

    @endpoint('/v1/config/update')
    def update_config(self, params: Dict[str, Any]) -> Dict[str, str]:
        """Update configuration with validation and error handling"""
        try:
            # Validate parameters
            validation_result = self._validate_config_params(params)
            if validation_result:
                return validation_result.__dict__
            
            section = params['section']
            values = params['values']
            
            # Ensure configuration section exists
            if section not in self.config:
                self.config.add_section(section)
            
            # Update configuration values
            for key, value in values.items():
                self.config.set(section, key, str(value))
            
            self._save_config()
            self.logger.info(f"Configuration updated for section: {section}")
            
            return ConfigResponse(
                ConfigStatus.SUCCESS,
                f"Configuration updated successfully for section: {section}"
            ).__dict__
            
        except Exception as e:
            error_msg = f"Configuration update failed: {str(e)}"
            self.logger.error(error_msg)
            return ConfigResponse(
                ConfigStatus.ERROR,
                error_msg
            ).__dict__
