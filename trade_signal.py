from mcprotocol import SecureServer
from eidos_sdk.strategy import SignalGenerator
from eidos_sdk.models import MarketData, RiskProfile, TradeSignalResponse
from eidos_sdk.validation import validate_market_data, validate_risk_profile
from eidos_sdk.exceptions import InvalidParameterError, SignalGenerationError
import logging
from typing import Dict, Any
from datetime import datetime
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradeSignal(SecureServer):
    """
    Trade signal generation service that provides endpoints for generating trading signals
    based on market data and risk profiles.
    """
    
    def __init__(self):
        """
        Initialize the TradeSignal service with required components and configurations
        """
        super().__init__()
        self.generator = SignalGenerator()
        self.last_signal_time = None
        self.signal_cooldown = 60  # Minimum seconds between signals
        
    def _validate_input_parameters(self, params: Dict[str, Any]) -> tuple:
        """
        Validate input parameters for signal generation
        
        Args:
            params: Dictionary containing market data and risk profile
            
        Returns:
            tuple: Validated market data and risk profile objects
            
        Raises:
            InvalidParameterError: If parameters are invalid
        """
        try:
            market_data = MarketData(**params.get('data', {}))
            risk_profile = RiskProfile(**params.get('risk', {}))
            
            validate_market_data(market_data)
            validate_risk_profile(risk_profile)
            
            return market_data, risk_profile
            
        except Exception as e:
            logger.error(f"Parameter validation failed: {str(e)}")
            raise InvalidParameterError(f"Invalid parameters: {str(e)}")
    
    def _check_rate_limit(self) -> None:
        """
        Check if signal generation is within rate limits
        
        Raises:
            SignalGenerationError: If rate limit is exceeded
        """
        if self.last_signal_time:
            time_diff = (datetime.now() - self.last_signal_time).total_seconds()
            if time_diff < self.signal_cooldown:
                raise SignalGenerationError(
                    f"Rate limit exceeded. Please wait {self.signal_cooldown - time_diff:.1f} seconds"
                )
    
    @endpoint('/v1/signal/generate')
    def generate_signal(self, params: Dict[str, Any]) -> TradeSignalResponse:
        """
        Generate trading signals based on market data and risk profile
        
        Args:
            params: Dictionary containing:
                - data: Market data parameters
                - risk: Risk profile parameters
                
        Returns:
            TradeSignalResponse: Generated trading signal with metadata
            
        Raises:
            InvalidParameterError: If input parameters are invalid
            SignalGenerationError: If signal generation fails
        """
        try:
            # Validate rate limiting
            self._check_rate_limit()
            
            # Validate input parameters
            market_data, risk_profile = self._validate_input_parameters(params)
            
            # Generate trading signal
            signal = self.generator.generate(
                market_data=market_data,
                risk_profile=risk_profile
            )
            
            # Update last signal time
            self.last_signal_time = datetime.now()
            
            # Log successful signal generation
            logger.info(
                f"Signal generated successfully: {signal.signal_type} "
                f"for {market_data.symbol} at {signal.timestamp}"
            )
            
            return TradeSignalResponse(
                signal=signal,
                metadata={
                    'generated_at': self.last_signal_time,
                    'market_conditions': market_data.market_conditions,
                    'risk_level': risk_profile.risk_level
                }
            )
            
        except (InvalidParameterError, SignalGenerationError) as e:
            logger.error(f"Signal generation failed: {str(e)}")
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error during signal generation: {str(e)}")
            raise SignalGenerationError(f"Signal generation failed: {str(e)}")
