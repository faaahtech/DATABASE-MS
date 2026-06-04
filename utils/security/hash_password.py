"""Compatibilidade para imports antigos de hash de senha."""

from utils.security import hash_password, verify_password

__all__ = ["hash_password", "verify_password"]
