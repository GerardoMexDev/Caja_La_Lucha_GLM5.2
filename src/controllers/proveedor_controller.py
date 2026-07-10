"""
Controlador de Proveedores y Cuentas por Pagar.
"""

from typing import List, Dict, Any, Optional
from models.database import DatabaseManager


class ProveedorController:
    """Lógica de negocio para proveedores y sus facturas."""

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    # ── PROVEEDORES ──────────────────────────────────────────────────────────

    def crear_proveedor(
        self, nombre: str, telefono: str = "", email: str = "", direccion: str = ""
    ) -> int:
        sql = """
            INSERT INTO proveedores (nombre, telefono, email, direccion)
            VALUES (?, ?, ?, ?)
        """
        cursor = self.db.ejecutar_query(sql, (nombre, telefono, email, direccion))
        return cursor.lastrowid

    def obtener_proveedores(self, activos_solo: bool = True) -> List[Dict[str, Any]]:
        cursor = self.db.obtener_cursor()
        if activos_solo:
            cursor.execute("SELECT * FROM proveedores WHERE activo = 1 ORDER BY nombre")
        else:
            cursor.execute("SELECT * FROM proveedores ORDER BY nombre")
        return [dict(row) for row in cursor.fetchall()]

    def toggle_proveedor_estado(self, proveedor_id: int) -> bool:
        cursor = self.db.obtener_cursor()
        cursor.execute("SELECT activo FROM proveedores WHERE id = ?", (proveedor_id,))
        row = cursor.fetchone()
        if not row:
            return False
        nuevo_estado = 0 if row["activo"] == 1 else 1
        self.db.ejecutar_query(
            "UPDATE proveedores SET activo = ? WHERE id = ?", (nuevo_estado, proveedor_id)
        )
        return True

    # ── FACTURAS / CUENTAS POR PAGAR ─────────────────────────────────────────

    def crear_factura(
        self,
        proveedor_id: int,
        descripcion: str,
        fecha_compra: str,
        monto_base: float,
        iva_porcentaje: float,
        iva_monto: float,
        total: float,
        moneda: str = "UYU",
        fecha_pago: str = "",
        estado: str = "pendiente",
        observaciones: str = "",
    ) -> int:
        sql = """
            INSERT INTO facturas_proveedores
                (proveedor_id, descripcion, fecha_compra, monto_base, iva_porcentaje,
                 iva_monto, total, moneda, fecha_pago, estado, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self.db.ejecutar_query(
            sql,
            (proveedor_id, descripcion, fecha_compra, monto_base, iva_porcentaje,
             iva_monto, total, moneda, fecha_pago, estado, observaciones),
        )
        return cursor.lastrowid

    def obtener_facturas(
        self, estado: Optional[str] = None, proveedor_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        cursor = self.db.obtener_cursor()
        sql = """
            SELECT f.*, p.nombre AS proveedor_nombre
            FROM facturas_proveedores f
            JOIN proveedores p ON f.proveedor_id = p.id
            WHERE 1=1
        """
        params: list = []
        if estado:
            sql += " AND f.estado = ?"
            params.append(estado)
        if proveedor_id:
            sql += " AND f.proveedor_id = ?"
            params.append(proveedor_id)
        sql += " ORDER BY f.fecha_compra DESC, f.id DESC"
        cursor.execute(sql, tuple(params))
        return [dict(row) for row in cursor.fetchall()]

    def marcar_factura_pagada(self, factura_id: int, fecha_pago: str) -> bool:
        sql = """
            UPDATE facturas_proveedores
            SET estado = 'pagada', fecha_pago = ?, updated_at = datetime('now','localtime')
            WHERE id = ?
        """
        self.db.ejecutar_query(sql, (fecha_pago, factura_id))
        return True

    def cancelar_factura(self, factura_id: int) -> bool:
        sql = """
            UPDATE facturas_proveedores
            SET estado = 'cancelada', updated_at = datetime('now','localtime')
            WHERE id = ?
        """
        self.db.ejecutar_query(sql, (factura_id,))
        return True

    def obtener_resumen_cuentas_por_pagar(self) -> Dict[str, Any]:
        cursor = self.db.obtener_cursor()
        cursor.execute(
            "SELECT moneda, COUNT(*) AS cantidad, COALESCE(SUM(total), 0) AS total_pendiente "
            "FROM facturas_proveedores WHERE estado = 'pendiente' GROUP BY moneda"
        )
        rows = cursor.fetchall()

        resumen: Dict[str, Any] = {
            "cantidad_pendientes": 0,
            "total_uyu": 0.0,
            "total_usd": 0.0,
        }
        for r in rows:
            moneda = r["moneda"] if r["moneda"] else "UYU"
            resumen["cantidad_pendientes"] += r["cantidad"]
            if moneda == "USD":
                resumen["total_usd"] = r["total_pendiente"]
            else:
                resumen["total_uyu"] = r["total_pendiente"]
        return resumen
