from mcprotocol import SecureServer
import cProfile
import time
from typing import Dict, Any, Optional
import logging
import json
class ProfilerMCP(SecureServer):
    """
    Advanced profiling server that provides endpoints for performance monitoring
    """
    
    def __init__(self):
        super().__init__()
        self.profiler: Optional[cProfile.Profile] = None
        self.profile_data: Dict[str, Any] = {}
        self.start_time: float = 0
        self.logger = logging.getLogger(__name__)

    @endpoint('/v1/profile/start')
    def start_profiling(self) -> Dict[str, Any]:
        """
        Start the profiler and begin collecting performance data
        
        Returns:
            Dict containing status and configuration parameters
        """
        try:
            if self.profiler is None:
                self.profiler = cProfile.Profile()
                self.profiler.enable()
                self.start_time = time.time()
                self.profile_data["params"] = {
                    "start_timestamp": self.start_time,
                    "sampling_interval": 0.1,
                    "include_memory": True
                }
                self.logger.info("Profiling started successfully")
                return {
                    "status": "started",
                    "params": self.profile_data.get("params")
                }
            else:
                return {
                    "status": "error",
                    "message": "Profiler already running"
                }
        except Exception as e:
            self.logger.error(f"Failed to start profiler: {str(e)}")
            return {
                "status": "error", 
                "message": f"Failed to start profiler: {str(e)}"
            }

    @endpoint('/v1/profile/clear')
    def clear_profile_data(self) -> Dict[str, str]:
        """
        Clear all profiling data and reset profiler state
        
        Returns:
            Dict containing status message
        """
        try:
            if self.profiler is not None:
                self.profiler.disable()
            
            self.profiler = None
            self.profile_data = {}
            self.start_time = 0
            self.logger.info("Profile data cleared successfully")
            
            return {
                "status": "success",
                "message": "Profiler data cleared"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to clear profile data: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to clear profiler data: {str(e)}"
            }

    @endpoint('/v1/profile/status')
    def get_profile_status(self) -> Dict[str, Any]:
        """
        Get current profiler status and basic statistics
        
        Returns:
            Dict containing profiler status and metrics
        """
        try:
            status = "running" if self.profiler else "stopped"
            duration = time.time() - self.start_time if self.profiler else 0
            
            return {
                "status": status,
                "duration": round(duration, 2),
                "active_functions": len(self.profiler.getstats()) if self.profiler else 0,
                "params": self.profile_data.get("params", {})
            }
        except Exception as e:
            self.logger.error(f"Failed to get profile status: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get profile status: {str(e)}"
            }

    @endpoint('/v1/profile/save')
    def save_profile_data(self, filename: str) -> Dict[str, str]:
        """
        Save current profile data to a file
        
        Args:
            filename: Name of file to save profile data
            
        Returns:
            Dict containing status message
        """
        try:
            if not self.profiler:
                return {
                    "status": "error",
                    "message": "No active profiler session to save"
                }
                
            self.profiler.dump_stats(filename)
            self.logger.info(f"Profile data saved to {filename}")
            
            return {
                "status": "success",
                "message": f"Profile data saved to {filename}"
            }
        except Exception as e:
            self.logger.error(f"Failed to save profile data: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to save profile data: {str(e)}"
            }
