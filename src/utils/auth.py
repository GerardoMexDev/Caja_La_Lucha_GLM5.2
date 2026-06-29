"""
Módulo de utilidades para autenticación.
Maneja el hash y verificación de contraseñas.
"""

import hashlib
import hmac
import os
from typing import Tuple


class AuthUtils:
    """Clase con métodos estáticos para manejo de contraseñas."""

    # Salt fijo para la aplicación (en producción usar salts únicos por usuario)
    _APP_SALT = b"caja_la_lucha_2024_secure_salt"

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Genera un hash seguro para la contraseña.

        Args:
            password: Contraseña en texto plano.

        Returns:
            Hash hexadecimal de la contraseña.
        """
        # Combinar salt con la contraseña
        salted = AuthUtils._APP_SALT + password.encode('utf-8')
        # Generar hash SHA-256
        return hashlib.sha256(salted).hexdigest()

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verifica si una contraseña coincide con su hash.

        Args:
            password: Contraseña en texto plano a verificar.
            hashed_password: Hash almacenado en la base de datos.

        Returns:
            True si la contraseña es correcta, False en caso contrario.
        """
        computed_hash = AuthUtils.hash_password(password)
        # Usar hmac.compare_digest para evitar timing attacks
        return hmac.compare_digest(computed_hash, hashed_password)

    @staticmethod
    def create_default_admin(password: str = "admin123") -> Tuple[str, str]:
        """
        Crea las credenciales por defecto del administrador.

        Args:
            password: Contraseña por defecto.

        Returns:
            Tupla con (username, password_hash).
        """
        return ("admin", AuthUtils.hash_password(password))