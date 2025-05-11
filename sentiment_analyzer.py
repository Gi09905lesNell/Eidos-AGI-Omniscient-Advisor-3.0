from mcprotocol import SecureServer
from transformers import pipeline
import logging
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import numpy as np
from datetime import datetime
# Data class to structure sentiment analysis results
@dataclass
class SentimentResult:
    text: str
    sentiment: str
    confidence: float
    timestamp: str

class SentimentAnalyzer(SecureServer):
    """
    A secure sentiment analysis server that processes text using transformer models.
    Provides endpoints for sentiment analysis with error handling and logging.
    """
    
    def __init__(self, model_name: str = "finiteautomata/bertweet-base-sentiment-analysis"):
        """
        Initialize the sentiment analyzer with specified model and configurations
        """
        super().__init__()
        # Configure logging
        self._setup_logging()
        
        # Initialize sentiment analysis pipeline
        try:
            self.nlp = pipeline("text-classification", model=model_name)
        except Exception as e:
            self.logger.error(f"Failed to initialize model: {str(e)}")
            raise
            
        # Cache for storing recent results
        self.cache = {}
        self.cache_size = 1000
        
    def _setup_logging(self):
        """Configure logging for the sentiment analyzer"""
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def _validate_text(self, text: str) -> bool:
        """
        Validate input text
        """
        if not text or not isinstance(text, str):
            return False
        if len(text.strip()) == 0:
            return False
        return True

    def _process_sentiment(self, text: str) -> SentimentResult:
        """
        Process text and return structured sentiment result
        """
        result = self.nlp(text)[0]
        return SentimentResult(
            text=text,
            sentiment=result['label'],
            confidence=result['score'],
            timestamp=datetime.now().isoformat()
        )

    @endpoint('/v1/sentiment/analyze')
    def analyze_sentiment(self, params: Dict) -> Dict:
        """
        Analyze sentiment of provided text
        
        Args:
            params: Dictionary containing 'text' key with input string
            
        Returns:
            Dictionary containing sentiment analysis results
        """
        try:
            text = params.get('text', '')
            
            # Input validation
            if not self._validate_text(text):
                return {
                    'error': 'Invalid input text',
                    'status': 400
                }

            # Check cache
            cache_key = hash(text)
            if cache_key in self.cache:
                self.logger.info("Returning cached result")
                return self.cache[cache_key]

            # Process sentiment
            result = self._process_sentiment(text)
            
            # Format response
            response = {
                'text': result.text,
                'sentiment': result.sentiment,
                'confidence': result.confidence,
                'timestamp': result.timestamp,
                'status': 200
            }

            # Update cache
            self.cache[cache_key] = response
            if len(self.cache) > self.cache_size:
                self.cache.pop(next(iter(self.cache)))

            self.logger.info(f"Successfully analyzed sentiment for text: {text[:50]}...")
            return response

        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {str(e)}")
            return {
                'error': 'Internal server error',
                'status': 500
            }

    @endpoint('/v1/sentiment/batch_analyze')
    def batch_analyze_sentiment(self, params: Dict) -> List[Dict]:
        """
        Analyze sentiment for multiple texts in batch
        
        Args:
            params: Dictionary containing 'texts' key with list of input strings
            
        Returns:
            List of dictionaries containing sentiment analysis results
        """
        texts = params.get('texts', [])
        if not isinstance(texts, list):
            return [{'error': 'Invalid input format', 'status': 400}]
            
        results = []
        for text in texts:
            result = self.analyze_sentiment({'text': text})
            results.append(result)
            
        return results

    @endpoint('/v1/sentiment/stats')
    def get_stats(self) -> Dict:
        """
        Get statistics about the sentiment analyzer's usage
        """
        return {
            'cache_size': len(self.cache),
            'cache_limit': self.cache_size,
            'status': 200
        }
