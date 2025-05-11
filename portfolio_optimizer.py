from mcprotocol import SecureServer
from pypfopt import EfficientFrontier, risk_models, expected_returns
from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd

class PortfolioOptimizer(SecureServer):
    """
    A portfolio optimization service that uses Modern Portfolio Theory to construct optimal portfolios.
    Inherits from SecureServer to provide secure API endpoints.
    """

    def __init__(self):
        super().__init__()
        self.risk_free_rate = 0.02  # Default risk-free rate
        self.min_weight = 0.0  # Minimum weight constraint
        self.max_weight = 1.0  # Maximum weight constraint

    @endpoint('/v1/portfolio/optimize')
    def optimize_portfolio(self, params: Dict) -> Dict:
        """
        Optimize portfolio weights using the Efficient Frontier approach.
        
        Args:
            params (Dict): Dictionary containing:
                - expected_returns: Expected returns for each asset
                - cov_matrix: Covariance matrix of asset returns
                - optimization_criteria (optional): Optimization method to use
                - constraints (optional): Additional portfolio constraints
        
        Returns:
            Dict: Optimized portfolio weights and performance metrics
        """
        try:
            # Validate input parameters
            self._validate_inputs(params)
            
            # Initialize the Efficient Frontier optimizer
            ef = EfficientFrontier(
                expected_returns=params['expected_returns'],
                cov_matrix=params['cov_matrix'],
                weight_bounds=(self.min_weight, self.max_weight)
            )
            
            # Apply any additional constraints
            if 'constraints' in params:
                self._apply_constraints(ef, params['constraints'])
            
            # Optimize based on specified criteria
            optimization_criteria = params.get('optimization_criteria', 'sharpe')
            weights = self._optimize_by_criteria(ef, optimization_criteria)
            
            # Calculate portfolio performance metrics
            performance_metrics = self._calculate_performance_metrics(
                weights, 
                params['expected_returns'],
                params['cov_matrix']
            )
            
            return {
                'weights': weights,
                'metrics': performance_metrics,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def _validate_inputs(self, params: Dict) -> None:
        """Validate input parameters for portfolio optimization."""
        required_params = ['expected_returns', 'cov_matrix']
        for param in required_params:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")
                
        if not isinstance(params['expected_returns'], (pd.Series, np.ndarray)):
            raise TypeError("Expected returns must be a pandas Series or numpy array")
            
        if not isinstance(params['cov_matrix'], (pd.DataFrame, np.ndarray)):
            raise TypeError("Covariance matrix must be a pandas DataFrame or numpy array")

    def _apply_constraints(self, ef: EfficientFrontier, constraints: Dict) -> None:
        """Apply additional optimization constraints to the Efficient Frontier."""
        if 'sector_constraints' in constraints:
            ef.add_sector_constraints(constraints['sector_constraints'])
            
        if 'position_constraints' in constraints:
            ef.add_constraint(lambda w: w >= constraints['position_constraints']['min'])
            ef.add_constraint(lambda w: w <= constraints['position_constraints']['max'])

    def _optimize_by_criteria(self, ef: EfficientFrontier, criteria: str) -> Dict:
        """
        Optimize portfolio based on specified criteria.
        
        Available criteria:
        - 'sharpe': Maximize Sharpe ratio
        - 'minvol': Minimize volatility
        - 'maxret': Maximize expected return
        """
        optimization_methods = {
            'sharpe': ef.max_sharpe,
            'minvol': ef.min_volatility,
            'maxret': ef.max_quadratic_utility
        }
        
        if criteria not in optimization_methods:
            raise ValueError(f"Invalid optimization criteria: {criteria}")
            
        return optimization_methods[criteria]()

    def _calculate_performance_metrics(
        self, 
        weights: Dict, 
        expected_returns: Union[pd.Series, np.ndarray],
        cov_matrix: Union[pd.DataFrame, np.ndarray]
    ) -> Dict:
        """Calculate key performance metrics for the optimized portfolio."""
        portfolio_return = np.sum(weights * expected_returns)
        portfolio_volatility = np.sqrt(
            np.dot(weights.T, np.dot(cov_matrix, weights))
        )
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
        
        return {
            'expected_return': float(portfolio_return),
            'volatility': float(portfolio_volatility),
            'sharpe_ratio': float(sharpe_ratio)
        }
