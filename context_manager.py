from mcprotocol import SecureServer
from cryptography.fernet import Fernet

class ContextManager(SecureServer):
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        
    @endpoint('/v1/context/update')
    def update_context(self, params):
        encrypted = self.cipher.encrypt(params['profile'].encode())
        # 存储加密后的用户画像
        return {"status": "success"}