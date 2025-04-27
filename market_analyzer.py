from mcprotocol import SecureServer
from ta import add_all_ta_features

class MarketAnalyzer(SecureServer):
    @endpoint('/v1/market/analyze')
    def analyze_market(self, params):
        df = pd.DataFrame(params['ohlcv'])
        df = add_all_ta_features(df)
        return df.tail(1).to_dict(orient='records')[0]