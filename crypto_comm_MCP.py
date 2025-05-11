from mcprotocol import SecureServer
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidKey
import logging
class CryptoCommMCP(SecureServer):
    """Encryption communication processing class, providing secure data encryption and key management"""
    
    def __init__(self, key_size=2048):
        """
        Initialize encryption communication instance
        :param key_size: RSA key length
        """
        super().__init__()
        self.key_size = key_size
        self.keys = self._generate_keys()
        self.logger = logging.getLogger(__name__)
        
    def _generate_keys(self):
        """Generate RSA key pair"""
        try:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.key_size
            )
            public_key = private_key.public_key()
            return {
                'private': private_key,
                'public': public_key
            }
        except Exception as e:
            self.logger.error(f"Key generation failed: {str(e)}")
            raise
    
    @endpoint('/v1/crypto/encrypt')
    def encrypt_data(self, params):
        """
        Encrypt input data
        :param params: Parameter dictionary containing data to be encrypted
        :return: Encrypted data
        """
        try:
            if not params or 'data' not in params:
                raise ValueError("Missing required data parameter")
                
            data = params['data'].encode('utf-8')
            encrypted = self.keys['public'].encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return {
                "encrypted": encrypted.hex(),
                "status": "success"
            }
            
        except Exception as e:
            self.logger.error(f"Error occurred during encryption: {str(e)}")
            return {
                "error": str(e),
                "status": "failed"
            }
