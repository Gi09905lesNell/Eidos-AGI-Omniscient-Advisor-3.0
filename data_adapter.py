from mcprotocol import SecureServer
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from sklearn.preprocessing import StandardScaler, RobustScaler

class DataAdapter(SecureServer):
    """
    Data Adapter class for normalizing and processing data
    Inherits from SecureServer for secure data handling
    """
    def __init__(self, scaler_type: str = 'standard'):
        """
        Initialize DataAdapter with configurable scaler
        
        Args:
            scaler_type: Type of scaler to use ('standard' or 'robust')
        """
        self.sources: Dict = {}
        # Allow flexible choice of scalers for different use cases
        self.scaler = StandardScaler() if scaler_type == 'standard' else RobustScaler()
        self.scaler_type = scaler_type
        self._fitted = False

    @endpoint('/v1/data/normalize')
    def normalize_data(self, params: Dict[str, List[Any]], columns: Optional[List[str]] = None) -> List[Dict]:
        """
        Normalize input data using standardization
        
        Args:
            params: Dictionary containing data to normalize
            columns: Optional list of specific columns to normalize
            
        Returns:
            List of normalized data records as dictionaries
        
        Raises:
            ValueError: If input data is empty or invalid
        """
        # Input validation
        if not params.get('data'):
            raise ValueError("Input data cannot be empty")

        # Convert input data to DataFrame
        df = pd.DataFrame(params['data'])
        
        # Handle missing values before normalization
        df = df.fillna(df.mean())
        
        # Select columns for normalization
        numeric_columns = columns if columns else df.select_dtypes(
            include=['float64', 'int64']).columns
            
        if len(numeric_columns) > 0:
            try:
                # Normalize only numeric columns
                df[numeric_columns] = self.scaler.fit_transform(df[numeric_columns])
                self._fitted = True
            except Exception as e:
                raise ValueError(f"Normalization failed: {str(e)}")
                
        # Add metadata about normalization
        result = df.to_dict(orient='records')
        metadata = {
            "normalized_columns": list(numeric_columns),
            "scaler_type": self.scaler_type,
            "num_records": len(df)
        }
        
        return {"data": result, "metadata": metadata}
