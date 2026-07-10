"""
Módulo de Base de Datos - Sistema de Caja 'La Lucha'
"""

import sqlite3
from typing import Optional


class DatabaseManager:
    """Clase responsable de interactuar con la base de datos SQLite local."""

    def __init__(self, db_name: str = "lucha_caja.db"):
        self.db_name = db_name
        self.conn: Optional[sqlite3.Connection] = None
        self._conectar()
        self._crear_tablas()
        self._migrar_campos()

    def _conectar(self) -> None:
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            print(f"Error crítico al conectar a la base de datos: {e}")
            raise

    def _crear_tablas(self) -> None:
        cursor = self.conn.cursor()

        sql_usuarios = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL,
            es_admin INTEGER NOT NULL DEFAULT 0,
            activo INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );
        """

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
            estado TEXT NOT NULL DEFAULT 'abierta',
            saldo_final_pesos REAL,
            FOREIGN KEY (usuario_id_abre) REFERENCES usuarios(id),
            FOREIGN KEY (usuario_id_cierra) REFERENCES usuarios(id)
        );
        """

        sql_movimientos = """
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caja_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            motivo TEXT NOT NULL,
            monto REAL NOT NULL,
            moneda TEXT NOT NULL DEFAULT 'UYU',
            metodo_pago TEXT NOT NULL DEFAULT 'Efectivo',
            es_banco INTEGER NOT NULL DEFAULT 0,
            empleado TEXT,
            observaciones TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (caja_id) REFERENCES cajas(id)
        );
        """

        sql_empleados = """
        CREATE TABLE IF NOT EXISTS empleados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            sueldo_semanal REAL NOT NULL DEFAULT 0.0,
            activo INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );
        """

        sql_proveedores = """
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            telefono TEXT,
            email TEXT,
            direccion TEXT,
            activo INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );
        """

        sql_facturas = """
        CREATE TABLE IF NOT EXISTS facturas_proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proveedor_id INTEGER NOT NULL,
            descripcion TEXT NOT NULL,
            fecha_compra TEXT NOT NULL,
            monto_base REAL NOT NULL,
            iva_porcentaje REAL NOT NULL DEFAULT 0.0,
            iva_monto REAL NOT NULL DEFAULT 0.0,
            total REAL NOT NULL,
            moneda TEXT NOT NULL DEFAULT 'UYU',
            fecha_pago TEXT,
            estado TEXT NOT NULL DEFAULT 'pendiente',
            observaciones TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
        );
        """

        cursor.executescript(
            sql_usuarios + sql_cajas + sql_movimientos +
            sql_empleados + sql_proveedores + sql_facturas
        )
        self.conn.commit()

    def _migrar_campos(self) -> None:
        """Agrega columnas faltantes a tablas existentes (migraciones en vivo)."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT moneda FROM facturas_proveedores LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute(
                "ALTER TABLE facturas_proveedores ADD COLUMN moneda TEXT NOT NULL DEFAULT 'UYU'"
            )
            self.conn.commit()

    def cerrar_conexion(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    def obtener_cursor(self) -> sqlite3.Cursor:
        return self.conn.cursor()

    def ejecutar_query(self, sql: str, parametros: tuple = ()) -> sqlite3.Cursor:
        cursor = self.obtener_cursor()
        cursor.execute(sql, parametros)
        self.conn.commit()
        return cursor


if __name__ == "__main__":
    print("Inicializando base de datos de prueba...")
    db = DatabaseManager(":memory:")
    print("¡Tablas creadas exitosamente en memoria!")
    db.cerrar_conexion()
