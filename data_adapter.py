from mcprotocol import SecureServer
import pandas as pd

class DataAdapter(SecureServer):
    def __init__(self):
        self.sources = {}
        
    @endpoint('/v1/data/normalize')
    def normalize_data(self, params):
        df = pd.DataFrame(params['data'])
        # 数据标准化逻辑
        return df.to_dict(orient='records')