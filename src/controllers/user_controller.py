"""
Controlador de Usuarios.
Adaptado para usar DatabaseManager y los nombres de columna actuales.
"""

import sqlite3
from typing import Optional, Dict, Any, Tuple
from models.database import DatabaseManager
from utils.auth import AuthUtils


class UserController:
    """Controlador para gestionar usuarios del sistema."""

    def __init__(self, db: DatabaseManager) -> None:
        """
        Inicializa el controlador con la conexión a la base de datos.

        Args:
            db: Instancia de DatabaseManager.
        """
        self.db = db

    def authenticate(self, nombre_usuario: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica un usuario con sus credenciales.

        Args:
            nombre_usuario: Nombre de usuario.
            password: Contraseña en texto plano.

        Returns:
            Diccionario con datos del usuario si autenticación exitosa,
            None si las credenciales son inválidas.
        """
        query = """
            SELECT id, nombre_usuario, contrasena, es_admin, activo
            FROM usuarios
            WHERE nombre_usuario = ?
        """
        cursor = self.db.ejecutar_query(query, (nombre_usuario,))
        row = cursor.fetchone()

        if row is None:
            return None

        user_dict = {
            'id': row['id'],
            'nombre_usuario': row['nombre_usuario'],
            'contrasena': row['contrasena'],
            'es_admin': row['es_admin'],
            'activo': row['activo']
        }

        # Verificar si el usuario está activo
        if not user_dict['activo']:
            return None

        # Verificar contraseña
        if not AuthUtils.verify_password(password, user_dict['contrasena']):
            return None

        # Retornar datos sin la contraseña
        del user_dict['contrasena']
        return user_dict

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por su ID."""
        query = """
            SELECT id, nombre_usuario, es_admin, activo
            FROM usuarios
            WHERE id = ?
        """
        cursor = self.db.ejecutar_query(query, (user_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return {
            'id': row['id'],
            'nombre_usuario': row['nombre_usuario'],
            'es_admin': row['es_admin'],
            'activo': row['activo']
        }

    def create_user(
        self,
        nombre_usuario: str,
        password: str,
        es_admin: int = 0,
        activo: int = 1
    ) -> Tuple[bool, str]:
        """
        Crea un nuevo usuario en el sistema.

        Args:
            nombre_usuario: Nombre de usuario único.
            password: Contraseña en texto plano.
            es_admin: 1 si es admin, 0 si es cajero.
            activo: 1 activo, 0 inactivo.

        Returns:
            Tupla (éxito, mensaje).
        """
        # Verificar si el usuario ya existe
        query_check = "SELECT id FROM usuarios WHERE nombre_usuario = ?"
        cursor = self.db.ejecutar_query(query_check, (nombre_usuario,))
        if cursor.fetchone() is not None:
            return (False, "El nombre de usuario ya existe.")

        # Hashear contraseña
        password_hash = AuthUtils.hash_password(password)

        # Insertar usuario
        query = """
            INSERT INTO usuarios (nombre_usuario, contrasena, es_admin, activo)
            VALUES (?, ?, ?, ?)
        """
        try:
            self.db.ejecutar_query(query, (nombre_usuario, password_hash, es_admin, activo))
            return (True, "Usuario creado exitosamente.")
        except sqlite3.Error as e:
            return (False, f"Error al crear usuario: {str(e)}")

    def ensure_admin_exists(self) -> None:
        """
        Verifica si existe al menos un usuario admin.
        Si no existe, crea el usuario admin por defecto.
        """
        query = "SELECT id FROM usuarios WHERE es_admin = 1"
        cursor = self.db.ejecutar_query(query, ())
        
        if cursor.fetchone() is None:
            username, password_hash = AuthUtils.create_default_admin()
            query = """
                INSERT INTO usuarios (nombre_usuario, contrasena, es_admin, activo)
                VALUES (?, ?, 1, 1)
            """
            self.db.ejecutar_query(query, (username, password_hash))
            print("✅ Usuario admin por defecto creado (admin/admin123)")

    def get_all_users(self) -> list[Dict[str, Any]]:
        """Obtiene todos los usuarios del sistema."""
        query = """
            SELECT id, nombre_usuario, es_admin, activo
            FROM usuarios
            ORDER BY id
        """
        cursor = self.db.ejecutar_query(query, ())
        rows = cursor.fetchall()

        return [
            {
                'id': row['id'],
                'nombre_usuario': row['nombre_usuario'],
                'es_admin': row['es_admin'],
                'activo': row['activo']
            }
            for row in rows
        ]