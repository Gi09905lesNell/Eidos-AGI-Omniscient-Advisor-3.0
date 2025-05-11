from mcprotocol import SecureServer
from collections import defaultdict
from typing import Callable, Dict, List, Optional
import logging
from dataclasses import dataclass

@dataclass
class EventHandler:
    """Data class to store event handler information"""
    callback: Callable
    event_type: str
    priority: int = 0

class EventEngineMCP(SecureServer):
    """
    Event Engine implementation for MCP protocol.
    Handles event registration and management with secure communication.
    """
    
    def __init__(self):
        """
        Initialize the event engine with an empty handler registry.
        Uses defaultdict to automatically create empty lists for new event types.
        """
        super().__init__()
        self.handlers: Dict[str, List[EventHandler]] = defaultdict(list)
        self.logger = logging.getLogger(__name__)
        
    def _validate_handler_params(self, event_type: str, callback: Callable) -> None:
        """
        Validate handler registration parameters
        
        Args:
            event_type: Event type to validate
            callback: Callback function to validate
            
        Raises:
            ValueError: If parameters are invalid
        """
        if not isinstance(event_type, str):
            raise ValueError("Event type must be a string")
        if not callable(callback):
            raise ValueError("Callback must be a callable")
        if not event_type or not callback:
            raise ValueError("Event type and callback must be provided")

    @endpoint('/v1/event/register')
    def register_handler(self, params: dict) -> dict:
        """
        Register a new event handler for a specific event type.
        
        Args:
            params (dict): Must contain 'event_type' and 'callback' keys
                event_type: Type of event to register for
                callback: Callback function to execute when event occurs
                priority: Optional priority level for the handler (default: 0)
                
        Returns:
            dict: Registration status
        
        Raises:
            KeyError: If required parameters are missing
        """
        try:
            event_type = params['event_type']
            callback = params['callback']
            priority = params.get('priority', 0)
            
            # Validate parameters
            self._validate_handler_params(event_type, callback)
                
            # Create handler object and insert based on priority
            handler = EventHandler(callback=callback, event_type=event_type, priority=priority)
            handlers_list = self.handlers[event_type]
            
            # Insert handler maintaining priority order
            insert_idx = 0
            for idx, existing_handler in enumerate(handlers_list):
                if existing_handler.priority <= priority:
                    insert_idx = idx
                    break
            handlers_list.insert(insert_idx, handler)
            
            self.logger.info(f"Registered new handler for event type: {event_type} with priority: {priority}")
            
            return {
                "status": "registered",
                "event_type": event_type,
                "handler_count": len(self.handlers[event_type]),
                "priority": priority
            }
            
        except KeyError as e:
            self.logger.error(f"Missing required parameter: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error registering handler: {str(e)}")
            raise
