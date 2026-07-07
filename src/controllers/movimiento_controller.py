from typing import Optional, Dict, Any, List, Tuple
from models.database import DatabaseManager

CATEGORIAS: List[str] = [
    'servicio_taller',
    'venta',
    'pago_credito',
    'compra_insumos',  # MODIFICADO
    'adelanto_sueldo',
    'viatico',         # NUEVO
    'deposito_bancario_ext',
]

METODOS_PAGO: List[str] = [
    'Efectivo', 'Tarjeta Débito', 'Tarjeta Crédito', 'Transferencia', 'Cheque'
]

MONEDAS: List[str] = ['UYU', 'USD', 'BRL']


class MovimientoController:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def registrar_movimiento(
        self, caja_id: int, tipo: str, categoria: str, motivo: str, monto: float,
        moneda: str = 'UYU', metodo_pago: str = 'Efectivo',
        empleado: Optional[str] = None, observaciones: Optional[str] = None,
    ) -> Tuple[bool, str]:
        if tipo not in ('ingreso', 'egreso'): return (False, "Tipo debe ser 'ingreso' o 'egreso'.")
        if categoria not in CATEGORIAS: return (False, f"Categoría inválida: {categoria}")
        if moneda not in MONEDAS: return (False, f"Moneda inválida: {moneda}")
        if metodo_pago not in METODOS_PAGO: return (False, f"Método de pago inválido: {metodo_pago}")
        if monto <= 0: return (False, "El monto debe ser mayor a 0.")
        if not motivo.strip(): return (False, "El motivo es requerido.")

        es_banco = 0 if metodo_pago == 'Efectivo' else 1
        sql = """
            INSERT INTO movimientos
            (caja_id, tipo, categoria, motivo, monto, moneda, metodo_pago, es_banco, empleado, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            self.db.ejecutar_query(sql, (
                caja_id, tipo, categoria, motivo.strip(),
                monto, moneda, metodo_pago, es_banco, empleado, observaciones,
            ))
            return (True, "Movimiento registrado.")
        except Exception as e:
            return (False, f"Error al registrar: {str(e)}")

    def obtener_movimientos_del_dia(self, caja_id: int) -> List[Dict[str, Any]]:
        sql = """
            SELECT id, tipo, categoria, motivo, monto, moneda,
                   metodo_pago, es_banco, empleado, observaciones, created_at
            FROM movimientos WHERE caja_id = ? ORDER BY created_at DESC
        """
        rows = self.db.ejecutar_query(sql, (caja_id,)).fetchall()
        return [dict(row) for row in rows]

    def obtener_resumen_del_dia(self, caja_id: int) -> Dict[str, Any]:
        movimientos = self.obtener_movimientos_del_dia(caja_id)
        row = self.db.ejecutar_query("SELECT fondo_inicial_pesos FROM cajas WHERE id = ?", (caja_id,)).fetchone()
        fondo_inicial = row['fondo_inicial_pesos'] if row else 0.0

        resumen: Dict[str, Any] = {
            'UYU': {'ingresos': 0.0, 'egresos': 0.0, 'saldo': 0.0},
            'USD': {'ingresos': 0.0, 'egresos': 0.0, 'saldo': 0.0},
            'BRL': {'ingresos': 0.0, 'egresos': 0.0, 'saldo': 0.0},
            'efectivo_uyu': fondo_inicial, 'banco_uyu': 0.0,
            'fondo_inicial': fondo_inicial, 'ultimos_movimientos': movimientos[:10],
        }

        for mov in movimientos:
            moneda, monto, tipo, es_banco = mov['moneda'], mov['monto'], mov['tipo'], mov['es_banco']
            if tipo == 'ingreso': resumen[moneda]['ingresos'] += monto
            else: resumen[moneda]['egresos'] += monto

            if moneda == 'UYU':
                signo = 1 if tipo == 'ingreso' else -1
                if es_banco == 0: resumen['efectivo_uyu'] += signo * monto
                else: resumen['banco_uyu'] += signo * monto

        for moneda in ('UYU', 'USD', 'BRL'):
            d = resumen[moneda]
            d['saldo'] = d['ingresos'] - d['egresos']
        return resumen

    def obtener_movimiento_por_id(self, movimiento_id: int) -> Optional[Dict[str, Any]]:
        row = self.db.ejecutar_query("SELECT * FROM movimientos WHERE id = ?", (movimiento_id,)).fetchone()
        return dict(row) if row else None

    def actualizar_movimiento(
        self, movimiento_id: int, tipo: str, categoria: str, motivo: str, monto: float,
        moneda: str = 'UYU', metodo_pago: str = 'Efectivo',
        empleado: Optional[str] = None, observaciones: Optional[str] = None,
    ) -> Tuple[bool, str]:
        if tipo not in ('ingreso', 'egreso'): return (False, "Tipo inválido.")
        if categoria not in CATEGORIAS: return (False, "Categoría inválida.")
        if moneda not in MONEDAS: return (False, "Moneda inválida.")
        if metodo_pago not in METODOS_PAGO: return (False, "Método de pago inválido.")
        if monto <= 0: return (False, "El monto debe ser mayor a 0.")
        if not motivo.strip(): return (False, "El motivo es requerido.")

        es_banco = 0 if metodo_pago == 'Efectivo' else 1
        sql = """
            UPDATE movimientos 
            SET tipo = ?, categoria = ?, motivo = ?, monto = ?, moneda = ?,
                metodo_pago = ?, es_banco = ?, empleado = ?, observaciones = ?, 
                updated_at = datetime('now','localtime')
            WHERE id = ?
        """
        try:
            self.db.ejecutar_query(sql, (
                tipo, categoria, motivo.strip(), monto, moneda, 
                metodo_pago, es_banco, empleado, observaciones, movimiento_id
            ))
            return (True, "Movimiento actualizado correctamente.")
        except Exception as e:
            return (False, f"Error al actualizar: {str(e)}")

    def eliminar_movimiento(self, movimiento_id: int) -> Tuple[bool, str]:
        sql = "DELETE FROM movimientos WHERE id = ?"
        try:
            self.db.ejecutar_query(sql, (movimiento_id,))
            return (True, "Movimiento eliminado correctamente.")
        except Exception as e:
            return (False, f"Error al eliminar: {str(e)}")
        

    def obtener_adelantos_por_rango(self, fecha_desde: str, fecha_hasta: str) -> List[Dict[str, Any]]:
        sql = """
            SELECT id, empleado, motivo, monto, moneda, created_at
            FROM movimientos
            WHERE categoria = 'adelanto_sueldo'
              AND DATE(created_at) BETWEEN ? AND ?
            ORDER BY created_at DESC
        """
        rows = self.db.ejecutar_query(sql, (fecha_desde, fecha_hasta)).fetchall()
        return [dict(row) for row in rows]

    def obtener_viaticos_por_rango(self, fecha_desde: str, fecha_hasta: str) -> List[Dict[str, Any]]:
        sql = """
            SELECT id, motivo, monto, moneda, created_at
            FROM movimientos
            WHERE categoria = 'viatico'
              AND DATE(created_at) BETWEEN ? AND ?
            ORDER BY created_at DESC
        """
        rows = self.db.ejecutar_query(sql, (fecha_desde, fecha_hasta)).fetchall()
        return [dict(row) for row in rows]
    
    def obtener_adelantos_viaticos_mensual(self, anio: int, mes: int) -> Dict[int, Dict[str, float]]:
        """Devuelve los totales de adelantos y viáticos agrupados por semana dentro de un mes."""
        mes_str = f"{anio}-{mes:02d}"
        sql = """
            SELECT categoria, monto, created_at 
            FROM movimientos 
            WHERE (categoria = 'adelanto_sueldo' OR categoria = 'viatico')
              AND strftime('%Y-%m', created_at) = ?
              AND moneda = 'UYU'
        """
        rows = self.db.ejecutar_query(sql, (mes_str,)).fetchall()
        
        # Inicializar hasta 5 semanas posibles en un mes
        semanas = {i: {'adelantos': 0.0, 'viaticos': 0.0} for i in range(1, 6)}
        
        for row in rows:
            try:
                # Extraer el día para calcular a qué semana pertenece
                dia = int(row['created_at'].split(' ')[0].split('-')[2])
                semana = (dia - 1) // 7 + 1
                if semana > 5: semana = 5
            except:
                continue
                
            if row['categoria'] == 'adelanto_sueldo':
                semanas[semana]['adelantos'] += row['monto']
            elif row['categoria'] == 'viatico':
                semanas[semana]['viaticos'] += row['monto']
                
        return semanas