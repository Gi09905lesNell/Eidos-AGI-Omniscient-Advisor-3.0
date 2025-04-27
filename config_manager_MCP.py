from mcprotocol import SecureServer
import configparser

class ConfigManagerMCP(SecureServer):
    def __init__(self):
        self.config = configparser.ConfigParser()
        
    @endpoint('/v1/config/update')
    def update_config(self, params):
        self.config[params['section']] = params['values']
        return {"status": "updated"}