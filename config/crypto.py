"""
VideoBot Pro - Sistema de Criptografia Multi-Camada
===================================================
Camada 1: Argon2id (Key Derivation)
Camada 2: AES-256-GCM (Encriptação Autenticada)
Camada 3: RSA-4096 (Troca de Chaves)
Camada 4: HMAC-SHA512 (Integridade)
Camada 5: Tokenização (Dados Sensíveis)
"""

import os
import sys
import json
import time
import hashlib
import hmac
import secrets
import base64
import struct
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
    logger.warning("cryptography não instalado. Instale com: pip install cryptography")


class CryptoError(Exception):
    pass


class IntegrityError(CryptoError):
    pass


class DecryptionError(CryptoError):
    pass


@dataclass
class EncryptedData:
    data: str
    nonce: str
    tag: str
    algorithm: str
    key_id: str
    timestamp: float
    version: int = 1


@dataclass
class TokenData:
    token: str
    original_hash: str
    created_at: float
    expires_at: Optional[float] = None
    metadata: Optional[Dict] = None


class Argon2KDF:
    TIME_COST = 3
    MEMORY_COST = 65536
    PARALLELISM = 4
    HASH_LENGTH = 32
    SALT_LENGTH = 16

    @staticmethod
    def derive_key(password: str, salt: bytes = None, key_length: int = 32) -> Tuple[bytes, bytes]:
        if salt is None:
            salt = secrets.token_bytes(Argon2KDF.SALT_LENGTH)

        if HAS_CRYPTO:
            kdf = Argon2id(
                time_cost=Argon2KDF.TIME_COST,
                memory_cost=Argon2KDF.MEMORY_COST,
                parallelism=Argon2KDF.PARALLELISM,
                hash_len=Argon2KDF.HASH_LENGTH,
                salt=salt,
            )
            key = kdf.derive(password.encode())
        else:
            key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt,
                iterations=480000,
                dklen=key_length
            )

        return key[:key_length], salt

    @staticmethod
    def verify(password: str, key: bytes, salt: bytes) -> bool:
        derived, _ = Argon2KDF.derive_key(password, salt, len(key))
        return hmac.compare_digest(derived, key)


class AES256GCM:
    def __init__(self, key: bytes = None):
        if key is None:
            key = secrets.token_bytes(32)
        self.key = key
        if HAS_CRYPTO:
            self.aesgcm = AESGCM(key)

    def encrypt(self, plaintext: bytes, associated_data: bytes = None) -> Tuple[bytes, bytes]:
        nonce = secrets.token_bytes(12)
        if HAS_CRYPTO:
            ciphertext = self.aesgcm.encrypt(nonce, plaintext, associated_data)
        else:
            ciphertext = plaintext
        return ciphertext, nonce

    def decrypt(self, ciphertext: bytes, nonce: bytes, associated_data: bytes = None) -> bytes:
        if HAS_CRYPTO:
            return self.aesgcm.decrypt(nonce, ciphertext, associated_data)
        return ciphertext

    @staticmethod
    def generate_key() -> bytes:
        return secrets.token_bytes(32)


class ChaCha20:
    def __init__(self, key: bytes = None):
        if key is None:
            key = secrets.token_bytes(32)
        self.key = key
        if HAS_CRYPTO:
            self.chacha = ChaCha20Poly1305(key)

    def encrypt(self, plaintext: bytes, associated_data: bytes = None) -> Tuple[bytes, bytes]:
        nonce = secrets.token_bytes(12)
        if HAS_CRYPTO:
            ciphertext = self.chacha.encrypt(nonce, plaintext, associated_data)
        else:
            ciphertext = plaintext
        return ciphertext, nonce

    def decrypt(self, ciphertext: bytes, nonce: bytes, associated_data: bytes = None) -> bytes:
        if HAS_CRYPTO:
            return self.chacha.decrypt(nonce, ciphertext, associated_data)
        return ciphertext


class RSAKeyManager:
    def __init__(self, key_size: int = 4096):
        self.key_size = key_size
        self._private_key = None
        self._public_key = None

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        if HAS_CRYPTO:
            self._private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.key_size,
                backend=default_backend()
            )
            self._public_key = self._private_key.public_key()

            private_pem = self._private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.BestAvailableEncryption(b"videobot-secure")
            )
            public_pem = self._public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            return private_pem, public_pem
        return b"", b""

    def encrypt_with_public(self, data: bytes, public_key_pem: bytes) -> bytes:
        if HAS_CRYPTO and public_key_pem:
            public_key = serialization.load_pem_public_key(public_key_pem, backend=default_backend())
            return public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        return data

    def decrypt_with_private(self, data: bytes, private_key_pem: bytes) -> bytes:
        if HAS_CRYPTO and private_key_pem:
            private_key = serialization.load_pem_private_key(
                private_key_pem, password=b"videobot-secure", backend=default_backend()
            )
            return private_key.decrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        return data


class HMACIntegrity:
    @staticmethod
    def generate(data: bytes, key: bytes) -> str:
        return hmac.new(key, data, hashlib.sha512).hexdigest()

    @staticmethod
    def verify(data: bytes, key: bytes, expected: str) -> bool:
        actual = hmac.new(key, data, hashlib.sha512).hexdigest()
        return hmac.compare_digest(actual, expected)

    @staticmethod
    def generate_key() -> bytes:
        return secrets.token_bytes(64)


class Tokenizer:
    def __init__(self):
        self._tokens: Dict[str, TokenData] = {}
        self._reverse: Dict[str, str] = {}

    def tokenize(self, sensitive_data: str, expires_in: float = None) -> str:
        token = f"tok_{secrets.token_urlsafe(32)}"
        original_hash = hashlib.sha256(sensitive_data.encode()).hexdigest()

        expires_at = None
        if expires_in:
            expires_at = time.time() + expires_in

        token_data = TokenData(
            token=token,
            original_hash=original_hash,
            created_at=time.time(),
            expires_at=expires_at,
        )

        self._tokens[token] = token_data
        self._reverse[original_hash] = token

        return token

    def detokenize(self, token: str, verify_func=None) -> Optional[str]:
        if token not in self._tokens:
            return None

        token_data = self._tokens[token]

        if token_data.expires_at and time.time() > token_data.expires_at:
            del self._tokens[token]
            return None

        if verify_func:
            return verify_func(token_data.original_hash)

        return token_data.original_hash

    def revoke(self, token: str):
        self._tokens.pop(token, None)


class SecureVault:
    def __init__(self, vault_path: Path = None):
        self.vault_path = vault_path or Path("./encrypted/vault.json")
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
        self._master_key: Optional[bytes] = None
        self._keys: Dict[str, bytes] = {}
        self._loaded = False

    def initialize(self, master_password: str) -> str:
        self._master_key, salt = Argon2KDF.derive_key(master_password)
        self._keys["master"] = self._master_key
        self._save_vault()
        return base64.b64encode(salt).decode()

    def unlock(self, master_password: str, salt_b64: str) -> bool:
        try:
            salt = base64.b64decode(salt_b64)
            self._master_key, _ = Argon2KDF.derive_key(master_password, salt)
            self._load_vault()
            return True
        except Exception as e:
            logger.error(f"Erro ao destravar vault: {e}")
            return False

    def add_key(self, name: str, key: bytes = None) -> bytes:
        if key is None:
            key = AES256GCM.generate_key()
        self._keys[name] = key
        self._save_vault()
        return key

    def get_key(self, name: str) -> Optional[bytes]:
        return self._keys.get(name)

    def remove_key(self, name: str):
        self._keys.pop(name, None)
        self._save_vault()

    def _save_vault(self):
        if not self._master_key:
            return

        data = {
            name: base64.b64encode(key).decode()
            for name, key in self._keys.items()
        }

        json_data = json.dumps(data).encode()
        aes = AES256GCM(self._master_key)
        ciphertext, nonce = aes.encrypt(json_data)

        vault = {
            "version": 1,
            "nonce": base64.b64encode(nonce).decode(),
            "data": base64.b64encode(ciphertext).decode(),
            "created_at": datetime.now().isoformat(),
        }

        with open(self.vault_path, "w") as f:
            json.dump(vault, f, indent=2)

    def _load_vault(self):
        if not self.vault_path.exists():
            return

        try:
            with open(self.vault_path) as f:
                vault = json.load(f)

            nonce = base64.b64decode(vault["nonce"])
            ciphertext = base64.b64decode(vault["data"])

            aes = AES256GCM(self._master_key)
            json_data = aes.decrypt(ciphertext, nonce)

            data = json.loads(json_data)
            self._keys = {
                name: base64.b64decode(key_b64)
                for name, key_b64 in data.items()
            }
            self._loaded = True
        except Exception as e:
            logger.error(f"Erro ao carregar vault: {e}")


class AuditLog:
    def __init__(self, log_path: Path = None):
        self.log_path = log_path or Path("./encrypted/audit.log")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._hmac_key = HMACIntegrity.generate_key()

    def log(self, action: str, user: str = None, details: Dict = None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user": user or "system",
            "details": details or {},
        }

        entry_json = json.dumps(entry, sort_keys=True).encode()
        signature = HMACIntegrity.generate(entry_json, self._hmac_key)

        log_line = f"{base64.b64encode(entry_json).decode()}:{signature}\n"

        with open(self.log_path, "a") as f:
            f.write(log_line)

    def verify(self) -> bool:
        if not self.log_path.exists():
            return True

        with open(self.log_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    b64_data, signature = line.rsplit(":", 1)
                    entry_json = base64.b64decode(b64_data)
                    if not HMACIntegrity.verify(entry_json, self._hmac_key, signature):
                        return False
                except Exception:
                    return False
        return True


class CryptoManager:
    def __init__(self, master_password: str = None):
        self.master_password = master_password or os.getenv("MASTER_KEY", "videobot-default")
        self._kdf_salt = None
        self._derived_key = None
        self.vault = SecureVault()
        self.audit = AuditLog()
        self.tokenizer = Tokenizer()
        self.rsa = RSAKeyManager()

        self._init_crypto()

    def _init_crypto(self):
        salt_hex = os.getenv("KDF_SALT", "")
        if salt_hex:
            self._kdf_salt = bytes.fromhex(salt_hex)
        else:
            self._kdf_salt = secrets.token_bytes(16)

        self._derived_key, _ = Argon2KDF.derive_key(
            self.master_password,
            self._kdf_salt,
            key_length=64
        )

        self._aes_key = self._derived_key[:32]
        self._hmac_key = self._derived_key[32:]

    def encrypt(self, data: str, context: str = None) -> str:
        try:
            plaintext = data.encode()
            aad = context.encode() if context else None

            aes = AES256GCM(self._aes_key)
            ciphertext, nonce = aes.encrypt(plaintext, aad)

            tag = HMACIntegrity.generate(ciphertext, self._hmac_key)

            encrypted = EncryptedData(
                data=base64.b64encode(ciphertext).decode(),
                nonce=base64.b64encode(nonce).decode(),
                tag=tag,
                algorithm="AES-256-GCM",
                key_id="master",
                timestamp=time.time(),
            )

            self.audit.log("encrypt", details={"context": context, "size": len(data)})

            return base64.b64encode(json.dumps(asdict(encrypted)).encode()).decode()

        except Exception as e:
            logger.error(f"Erro ao criptografar: {e}")
            raise CryptoError(f"Falha na criptografia: {e}")

    def decrypt(self, encrypted_b64: str, context: str = None) -> str:
        try:
            encrypted_json = base64.b64decode(encrypted_b64).decode()
            encrypted = EncryptedData(**json.loads(encrypted_json))

            ciphertext = base64.b64decode(encrypted.data)
            nonce = base64.b64decode(encrypted.nonce)

            if not HMACIntegrity.verify(ciphertext, self._hmac_key, encrypted.tag):
                self.audit.log("integrity_fail", details={"context": context})
                raise IntegrityError("Falha na verificação de integridade")

            aes = AES256GCM(self._aes_key)
            plaintext = aes.decrypt(ciphertext, nonce, context.encode() if context else None)

            self.audit.log("decrypt", details={"context": context})

            return plaintext.decode()

        except IntegrityError:
            raise
        except Exception as e:
            logger.error(f"Erro ao descriptografar: {e}")
            raise DecryptionError(f"Falha na descriptografia: {e}")

    def encrypt_file(self, input_path: Path, output_path: Path = None) -> Path:
        if output_path is None:
            output_path = input_path.with_suffix(".encrypted")

        with open(input_path, "rb") as f:
            data = f.read()

        encrypted = self.encrypt(base64.b64encode(data).decode(), context=str(input_path))

        with open(output_path, "w") as f:
            f.write(encrypted)

        self.audit.log("file_encrypt", details={"file": str(input_path)})
        return output_path

    def decrypt_file(self, input_path: Path, output_path: Path = None) -> Path:
        if output_path is None:
            output_path = input_path.with_suffix(".decrypted")

        with open(input_path) as f:
            encrypted = f.read()

        data_b64 = self.decrypt(encrypted, context=str(output_path))
        data = base64.b64decode(data_b64)

        with open(output_path, "wb") as f:
            f.write(data)

        self.audit.log("file_decrypt", details={"file": str(output_path)})
        return output_path

    def hash_password(self, password: str) -> Tuple[str, str]:
        salt = secrets.token_hex(16)
        key, _ = Argon2KDF.derive_key(password, bytes.fromhex(salt))
        return salt, base64.b64encode(key).decode()

    def verify_password(self, password: str, salt_hex: str, key_b64: str) -> bool:
        key = base64.b64decode(key_b64)
        derived, _ = Argon2KDF.derive_key(password, bytes.fromhex(salt_hex), len(key))
        return hmac.compare_digest(derived, key)

    def generate_token(self, data: str, expires_in: float = 3600) -> str:
        return self.tokenizer.tokenize(data, expires_in)

    def generate_key(self, name: str) -> bytes:
        return self.vault.add_key(name)

    def secure_string(self, data: str) -> str:
        return self.encrypt(data, context="secure_string")


crypto_manager = CryptoManager()
