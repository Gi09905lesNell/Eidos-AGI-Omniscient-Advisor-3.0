from mcprotocol import SecureServer
from eidos_sdk.strategy import SignalGenerator

class TradeSignal(SecureServer):
    def __init__(self):
        self.generator = SignalGenerator()
        
    @endpoint('/v1/signal/generate')
    def generate_signal(self, params):
        return self.generator.generate(
            market_data=params['data'],
            risk_profile=params['risk']
        )