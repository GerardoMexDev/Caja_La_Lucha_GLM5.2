"""
Módulo de Base de Datos - Sistema de Caja 'La Lucha'

Descripción:
Gestiona la conexión a SQLite y la creación de las tablas principales.
Utiliza Patrones de Diseño Singleton implícito para mantener una única conexión.

Autor: [Tu Nombre/El del equipo]
Fecha de creación: 2023-10-27
"""

import sqlite3
from typing import Optional


class DatabaseManager:
    """Clase responsable de interactuar con la base de datos SQLite local."""

    def __init__(self, db_name: str = "lucha_caja.db"):
        """
        Inicializa la conexión con la base de datos y crea las tablas si no existen.
        
        Args:
            db_name (str): Nombre del archivo de la base de datos. Por defecto 'lucha_caja.db'.
        """
        self.db_name = db_name
        self.conn: Optional[sqlite3.Connection] = None
        self._conectar()
        self._crear_tablas()

    def _conectar(self) -> None:
        """Establece la conexión a SQLite. Usa row_factory para devolver diccionarios."""
        try:
            # row_factory permite acceder a las columnas por nombre (ej: row['monto']) 
            # en lugar de por índice (ej: row[0]), haciendo el código más legible.
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row 
        except sqlite3.Error as e:
            print(f"Error crítico al conectar a la base de datos: {e}")
            raise

    def _crear_tablas(self) -> None:
        """Ejecuta los scripts SQL para crear la estructura inicial del sistema."""
        cursor = self.conn.cursor()

        # Tabla de Usuarios (Cajeros y Administrador)
        sql_usuarios = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL,
            es_admin INTEGER NOT NULL DEFAULT 0, -- 0 = False, 1 = True
            activo INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );
        """

        # Tabla de Cajas (Apertura y Cierre)
        sql_cajas = """
        CREATE TABLE IF NOT EXISTS cajas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_apertura TEXT NOT NULL,
            hora_apertura TEXT NOT NULL,
            usuario_id_abre INTEGER NOT NULL,
            fondo_inicial_pesos REAL NOT NULL DEFAULT 0.0,
            fecha_cierre TEXT,
            hora_cierre TEXT,
            usuario_id_cierra INTEGER,
            estado TEXT NOT NULL DEFAULT 'abierta', -- 'abierta' o 'cerrada'
            saldo_final_pesos REAL,
            FOREIGN KEY (usuario_id_abre) REFERENCES usuarios(id),
            FOREIGN KEY (usuario_id_cierra) REFERENCES usuarios(id)
        );
        """

        # Tabla de Movimientos (Ingresos y Egresos)
        sql_movimientos = """
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caja_id INTEGER NOT NULL,
            tipo TEXT NOT NULL, -- 'ingreso' o 'egreso'
            categoria TEXT NOT NULL, -- 'servicio_taller', 'venta', 'pago_credito', 'compra_tiendas', 'adelanto_sueldo', 'deposito_bancario_ext'
            motivo TEXT NOT NULL,
            monto REAL NOT NULL,
            moneda TEXT NOT NULL DEFAULT 'ARS', -- 'ARS', 'USD', 'BRL'
            metodo_pago TEXT NOT NULL DEFAULT 'Efectivo', -- 'Efectivo', 'Tarjeta Débito', 'Tarjeta Crédito', 'Transferencia', 'Cheque'
            es_banco INTEGER NOT NULL DEFAULT 0, -- 1 si va a la cuenta bancaria virtual (Todo lo que no sea efectivo)
            empleado TEXT, -- Solo se usa si categoria es 'adelanto_sueldo'
            observaciones TEXT, -- Solo se usa si categoria es 'compra_tiendas'
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (caja_id) REFERENCES cajas(id)
        );
        """

        # Ejecutar todas las creaciones
        cursor.executescript(sql_usuarios + sql_cajas + sql_movimientos)
        self.conn.commit()

    def cerrar_conexion(self) -> None:
        """Cierra la conexión con la base de datos de forma segura."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def obtener_cursor(self) -> sqlite3.Cursor:
        """
        Retorna un cursor para ejecutar consultas.
        Útil para los Controladores.
        
        Returns:
            sqlite3.Cursor: Cursor activo de la base de datos.
        """
        return self.conn.cursor()

    def ejecutar_query(self, sql: str, parametros: tuple = ()) -> sqlite3.Cursor:
        """
        Método auxiliar para ejecutar consultas INSERT, UPDATE, DELETE.
        Confirma automáticamente los cambios (commit).
        
        Args:
            sql (str): Sentencia SQL con placeholders (?).
            parametros (tuple): Valores a insertar en los placeholders.
            
        Returns:
            sqlite3.Cursor: Cursor tras la ejecución.
        """
        cursor = self.obtener_cursor()
        cursor.execute(sql, parametros)
        self.conn.commit()
        return cursor

# Bloque de prueba (Solo se ejecuta si corres este archivo directamente)
if __name__ == "__main__":
    print("Inicializando base de datos de prueba...")
    db = DatabaseManager(":memory:") # Usa memoria RAM para no crear el archivo aún
    print("¡Tablas creadas exitosamente en memoria!")
    db.cerrar_conexion()