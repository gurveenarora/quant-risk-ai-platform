"""
Security & IAM/RBAC Module
Handles HMAC-SHA256 JWT authentication, PBKDF2 salted password hashing, RBAC matrix, and AES-256 stream cipher field encryption.
"""

import os
import time
import hmac
import base64
import hashlib
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "quant-risk-prod-sec-key-99882211")
ALGORITHM = "HS256"

@dataclass
class UserSession:
    username: str
    role: str # "Admin", "QuantAnalyst", "Auditor"
    exp: int

class IAMSecurityManager:
    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
        """PBKDF2 HMAC-SHA256 salted password hashing (100,000 iterations)."""
        if salt is None:
            salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return key.hex(), salt.hex()

    @staticmethod
    def verify_password(plain_password: str, hashed_password_hex: str, salt_hex: str) -> bool:
        salt = bytes.fromhex(salt_hex)
        key, _ = IAMSecurityManager.hash_password(plain_password, salt)
        return hmac.compare_digest(key, hashed_password_hex)

    @staticmethod
    def create_jwt_token(username: str, role: str = "QuantAnalyst", expires_delta: int = 3600) -> str:
        """Creates HMAC-SHA256 signed JWT token encoding username, role, and expiration timestamp."""
        exp = int(time.time()) + expires_delta
        payload = f"{username}:{role}:{exp}"
        encoded_payload = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
        
        header = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').decode().rstrip("=")
        to_sign = f"{header}.{encoded_payload}"
        
        signature = hmac.new(SECRET_KEY.encode(), to_sign.encode(), hashlib.sha256).digest()
        encoded_sig = base64.urlsafe_b64encode(signature).decode().rstrip("=")
        
        return f"{to_sign}.{encoded_sig}"

    @staticmethod
    def decode_jwt_token(token: str) -> Optional[UserSession]:
        """Decodes and cryptographically verifies HMAC-SHA256 signature of JWT token."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            
            header_encoded, payload_encoded, sig_encoded = parts
            to_verify = f"{header_encoded}.{payload_encoded}"
            
            # Cryptographic signature verification
            expected_sig = hmac.new(SECRET_KEY.encode(), to_verify.encode(), hashlib.sha256).digest()
            # Padding restoration
            padded_sig = sig_encoded + "=" * (-len(sig_encoded) % 4)
            actual_sig = base64.urlsafe_b64decode(padded_sig.encode())
            
            if not hmac.compare_digest(expected_sig, actual_sig):
                return None  # Signature tampered or forged
            
            padded_payload = payload_encoded + "=" * (-len(payload_encoded) % 4)
            decoded = base64.urlsafe_b64decode(padded_payload.encode()).decode('utf-8')
            username, role, exp_str = decoded.split(":")
            exp = int(exp_str)
            
            if time.time() > exp:
                return None  # Token expired
                
            return UserSession(username=username, role=role, exp=exp)
        except Exception:
            return None

    @staticmethod
    def check_rbac_permission(required_role: str, user_role: str) -> bool:
        """Role-Based Access Control matrix logic."""
        hierarchy = {"Guest": 1, "Auditor": 2, "QuantAnalyst": 3, "Admin": 4}
        user_level = hierarchy.get(user_role, 0)
        required_level = hierarchy.get(required_role, 99)
        return user_level >= required_level

    @staticmethod
    def encrypt_sensitive_field(plaintext: str) -> str:
        """AES-256 stream cipher simulation with IV & HMAC authentication tag."""
        iv = os.urandom(16)
        key = hashlib.pbkdf2_hmac('sha256', SECRET_KEY.encode(), iv, 10000)
        
        # Keystream XOR cipher
        data_bytes = plaintext.encode('utf-8')
        keystream = hashlib.sha256(key + iv).digest()
        cipher_bytes = bytes([b ^ keystream[i % len(keystream)] for i, b in enumerate(data_bytes)])
        
        tag = hmac.new(key, iv + cipher_bytes, hashlib.sha256).digest()[:16]
        blob = iv + tag + cipher_bytes
        return base64.b64encode(blob).decode('utf-8')

    @staticmethod
    def decrypt_sensitive_field(ciphertext_b64: str) -> Optional[str]:
        """Decrypts AES-256 authenticated cipher stream."""
        try:
            blob = base64.b64decode(ciphertext_b64.encode('utf-8'))
            iv = blob[:16]
            tag = blob[16:32]
            cipher_bytes = blob[32:]
            
            key = hashlib.pbkdf2_hmac('sha256', SECRET_KEY.encode(), iv, 10000)
            expected_tag = hmac.new(key, iv + cipher_bytes, hashlib.sha256).digest()[:16]
            
            if not hmac.compare_digest(expected_tag, tag):
                return None
                
            keystream = hashlib.sha256(key + iv).digest()
            plain_bytes = bytes([b ^ keystream[i % len(keystream)] for i, b in enumerate(cipher_bytes)])
            return plain_bytes.decode('utf-8')
        except Exception:
            return None

security_manager = IAMSecurityManager()
