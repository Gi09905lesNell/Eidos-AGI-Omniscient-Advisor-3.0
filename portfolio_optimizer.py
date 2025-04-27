from mcprotocol import SecureServer
from pypfopt import EfficientFrontier

class PortfolioOptimizer(SecureServer):
    @endpoint('/v1/portfolio/optimize')
    def optimize_portfolio(self, params):
        ef = EfficientFrontier(
            params['expected_returns'],
            params['cov_matrix']
        )
        return ef.max_sharpe()