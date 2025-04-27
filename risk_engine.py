from mcprotocol import SecureServer
from eidos_sdk.quant import MonteCarloSimulator

class RiskEngine(SecureServer):
    def __init__(self):
        self.simulator = MonteCarloSimulator(threads=4)
        
    @endpoint('/v1/risk/evaluate')
    def evaluate_risk(self, params):
        return self.simulator.run(
            portfolio=params['portfolio'],
            scenarios=params.get('scenarios', 10000)
        )