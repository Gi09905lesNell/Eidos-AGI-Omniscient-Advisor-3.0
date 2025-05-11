import pandas as pd
import numpy as np
from mcprotocol import SecureServer
from ta import add_all_ta_features
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketAnalyzer(SecureServer):
    """
    A class for analyzing market data using technical indicators
    Inherits from SecureServer for secure API endpoints
    """
    
    def __init__(self):
        super().__init__()
        self.required_columns = ['open', 'high', 'low', 'close', 'volume']
        
    def validate_input(self, data: Dict) -> bool:
        """
        Validate input data format and required columns
        """
        try:
            if 'ohlcv' not in data:
                logger.error("Missing 'ohlcv' key in input data")
                return False
                
            df = pd.DataFrame(data['ohlcv'])
            missing_cols = [col for col in self.required_columns if col not in df.columns]
            
            if missing_cols:
                logger.error(f"Missing required columns: {missing_cols}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Input validation error: {str(e)}")
            return False
            
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess market data before analysis
        """
        # Remove any missing values
        df = df.dropna()
        
        # Ensure proper data types
        df['volume'] = df['volume'].astype(float)
        for col in ['open', 'high', 'low', 'close']:
            df[col] = df[col].astype(float)
            
        # Add timestamp if not present
        if 'timestamp' not in df.columns:
            df['timestamp'] = pd.date_range(end=pd.Timestamp.now(), periods=len(df))
            
        return df
        
    def calculate_custom_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate additional custom technical indicators
        """
        # Average True Range (ATR)
        df['tr1'] = abs(df['high'] - df['low'])
        df['tr2'] = abs(df['high'] - df['close'].shift())
        df['tr3'] = abs(df['low'] - df['close'].shift())
        df['true_range'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        df['atr'] = df['true_range'].rolling(window=14).mean()
        
        # Money Flow Index (MFI)
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        money_flow = typical_price * df['volume']
        
        positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0).rolling(14).sum()
        negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0).rolling(14).sum()
        
        money_ratio = positive_flow / negative_flow
        df['mfi'] = 100 - (100 / (1 + money_ratio))
        
        return df
        
    def generate_signals(self, df: pd.DataFrame) -> Dict:
        """
        Generate trading signals based on technical indicators
        """
        signals = {
            'trend': 'neutral',
            'strength': 0,
            'support': None,
            'resistance': None,
            'risk_level': 'medium'
        }
        
        # Trend analysis using multiple indicators
        last_row = df.iloc[-1]
        
        # RSI analysis
        if 'momentum_rsi' in last_row:
            if last_row['momentum_rsi'] > 70:
                signals['trend'] = 'overbought'
            elif last_row['momentum_rsi'] < 30:
                signals['trend'] = 'oversold'
                
        # MACD analysis
        if all(x in last_row for x in ['trend_macd', 'trend_macd_signal']):
            macd_diff = last_row['trend_macd'] - last_row['trend_macd_signal']
            signals['strength'] = abs(macd_diff)
            
        # Support/Resistance levels
        recent_lows = df['low'].tail(20).min()
        recent_highs = df['high'].tail(20).max()
        signals['support'] = round(recent_lows, 2)
        signals['resistance'] = round(recent_highs, 2)
        
        return signals

    @endpoint('/v1/market/analyze')
    def analyze_market(self, params: Dict) -> Dict:
        """
        Main endpoint for market analysis
        Processes OHLCV data and returns technical analysis results
        """
        try:
            # Validate input
            if not self.validate_input(params):
                raise ValueError("Invalid input data format")
                
            # Create DataFrame and preprocess
            df = pd.DataFrame(params['ohlcv'])
            df = self.preprocess_data(df)
            
            # Add technical indicators
            df = add_all_ta_features(df)
            df = self.calculate_custom_indicators(df)
            
            # Generate analysis results
            last_indicators = df.tail(1).to_dict(orient='records')[0]
            signals = self.generate_signals(df)
            
            # Combine results
            analysis_result = {
                'indicators': last_indicators,
                'signals': signals,
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return {'error': str(e)}
