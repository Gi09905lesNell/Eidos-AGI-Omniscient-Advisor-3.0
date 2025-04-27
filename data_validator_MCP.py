from mcprotocol import SecureServer
from pydantic import BaseModel

class DataValidatorMCP(SecureServer):
    @endpoint('/v1/validate/schema')
    def validate_data(self, params):
        class RequestModel(BaseModel):
            data: dict
        return RequestModel(**params).dict()