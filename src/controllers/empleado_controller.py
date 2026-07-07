from typing import Dict, Any, List, Tuple, Optional
from models.database import DatabaseManager


class EmpleadoController:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def crear_empleado(self, nombre: str, sueldo_semanal: float) -> Tuple[bool, str]:
        if not nombre.strip():
            return (False, "El nombre es requerido.")
        if sueldo_semanal <= 0:
            return (False, "El sueldo debe ser mayor a 0.")
        try:
            self.db.ejecutar_query(
                "INSERT INTO empleados (nombre, sueldo_semanal) VALUES (?, ?)",
                (nombre.strip(), sueldo_semanal)
            )
            return (True, "Empleado creado correctamente.")
        except Exception as e:
            return (False, f"Error al crear empleado: {str(e)}")

    def obtener_empleados_activos(self) -> List[Dict[str, Any]]:
        rows = self.db.ejecutar_query(
            "SELECT id, nombre, sueldo_semanal FROM empleados WHERE activo = 1 ORDER BY nombre ASC"
        ).fetchall()
        return [dict(row) for row in rows]

    def obtener_todos_los_empleados(self) -> List[Dict[str, Any]]:
        rows = self.db.ejecutar_query(
            "SELECT * FROM empleados ORDER BY nombre ASC"
        ).fetchall()
        return [dict(row) for row in rows]

    def toggle_estado(self, empleado_id: int) -> None:
        self.db.ejecutar_query(
            "UPDATE empleados SET activo = CASE WHEN activo = 1 THEN 0 ELSE 1 END WHERE id = ?",
            (empleado_id,)
        )

    def calcular_liquidacion_por_rango(self, fecha_desde: str, fecha_hasta: str) -> List[Dict[str, Any]]:
        empleados = self.obtener_empleados_activos()
        liquidacion = []
        
        for emp in empleados:
            # Buscar adelantos de este empleado en el rango
            sql = """
                SELECT COALESCE(SUM(monto), 0) as total_adelantos
                FROM movimientos
                WHERE categoria = 'adelanto_sueldo'
                  AND empleado = ?
                  AND DATE(created_at) BETWEEN ? AND ?
                  AND moneda = 'UYU'
            """
            row = self.db.ejecutar_query(sql, (emp['nombre'], fecha_desde, fecha_hasta)).fetchone()
            total_adelantos = row['total_adelantos'] if row else 0.0
            
            pago_final = emp['sueldo_semanal'] - total_adelantos
            
            liquidacion.append({
                'id': emp['id'],
                'nombre': emp['nombre'],
                'sueldo_base': emp['sueldo_semanal'],
                'total_adelantos': total_adelantos,
                'pago_final': pago_final
            })
            
        return liquidacion