import os
import hashlib
import hmac
import base64
import json
import time
from typing import Optional, Dict, Any
from app.core.config import settings

def get_password_hash(password: str) -> str:
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return base64.b64encode(salt + key).decode('ascii')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        decoded = base64.b64decode(hashed_password.encode('ascii'))
        salt = decoded[:16]
        key = decoded[16:]
        new_key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000)
        return hmac.compare_digest(key, new_key)
    except Exception:
        return False

def create_access_token(data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = int(time.time()) + (expires_delta or (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60))
    to_encode.update({"exp": expire})
    
    header = {"alg": "HS256", "typ": "JWT"}
    header_bytes = base64.urlsafe_b64encode(json.dumps(header).encode('utf-8')).rstrip(b'=')
    payload_bytes = base64.urlsafe_b64encode(json.dumps(to_encode).encode('utf-8')).rstrip(b'=')
    
    signature = hmac.new(
        settings.SECRET_KEY.encode('utf-8'),
        header_bytes + b'.' + payload_bytes,
        hashlib.sha256
    ).digest()
    sig_bytes = base64.urlsafe_b64encode(signature).rstrip(b'=')
    
    return f"{header_bytes.decode('utf-8')}.{payload_bytes.decode('utf-8')}.{sig_bytes.decode('utf-8')}"

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        header_bytes, payload_bytes, sig_bytes = parts
        
        expected_sig = hmac.new(
            settings.SECRET_KEY.encode('utf-8'),
            f"{header_bytes}.{payload_bytes}".encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # pad base64
        padded_sig = sig_bytes + '=' * (-len(sig_bytes) % 4)
        actual_sig = base64.urlsafe_b64decode(padded_sig.encode('utf-8'))
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
            
        padded_payload = payload_bytes + '=' * (-len(payload_bytes) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded_payload.encode('utf-8')).decode('utf-8'))
        
        if payload.get("exp", 0) < time.time():
            return None
            
        return payload
    except Exception:
        return None

