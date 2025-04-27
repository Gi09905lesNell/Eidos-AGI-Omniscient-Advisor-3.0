from mcprotocol import SecureServer
from transformers import pipeline

class SentimentAnalyzer(SecureServer):
    def __init__(self):
        self.nlp = pipeline("text-classification", model="finiteautomata/bertweet-base-sentiment-analysis")
        
    @endpoint('/v1/sentiment/analyze')
    def analyze_sentiment(self, params):
        return self.nlp(params['text'])