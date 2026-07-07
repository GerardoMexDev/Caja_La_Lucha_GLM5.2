from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from models.database import DatabaseManager


class CajaController:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def abrir_caja(self, usuario_id: int, fondo_inicial: float) -> Dict[str, Any]:
        now = datetime.now()
        fecha = now.strftime("%Y-%m-%d")
        hora = now.strftime("%H:%M:%S")
        sql = """
            INSERT INTO cajas (fecha_apertura, hora_apertura, usuario_id_abre, fondo_inicial_pesos, estado)
            VALUES (?, ?, ?, ?, 'abierta')
        """
        cursor = self.db.ejecutar_query(sql, (fecha, hora, usuario_id, fondo_inicial))
        return {
            'id': cursor.lastrowid,
            'fecha_apertura': fecha,
            'hora_apertura': hora,
            'usuario_id_abre': usuario_id,
            'fondo_inicial_pesos': fondo_inicial,
            'estado': 'abierta'
        }

    def obtener_caja_activa(self) -> Optional[Dict[str, Any]]:
        sql = "SELECT * FROM cajas WHERE estado = 'abierta' LIMIT 1"
        cursor = self.db.ejecutar_query(sql, ())
        row = cursor.fetchone()
        return dict(row) if row else None

    def calcular_saldo_actual(self, caja_id: int) -> Dict[str, Any]:
        row = self.db.ejecutar_query(
            "SELECT fondo_inicial_pesos FROM cajas WHERE id = ?", (caja_id,)
        ).fetchone()
        fondo_inicial = row['fondo_inicial_pesos'] if row else 0.0

        movimientos = self.db.ejecutar_query(
            "SELECT tipo, moneda, monto, es_banco FROM movimientos WHERE caja_id = ?",
            (caja_id,)
        ).fetchall()

        result: Dict[str, Any] = {
            'fondo_inicial': fondo_inicial,
            'totales': {
                m: {'ingresos': 0.0, 'egresos': 0.0, 'saldo': 0.0}
                for m in ('UYU', 'USD', 'BRL')
            },
            'efectivo_uyu': fondo_inicial,
            'banco_uyu': 0.0,
        }

        for mov in movimientos:
            moneda, monto, tipo, es_banco = mov['moneda'], mov['monto'], mov['tipo'], mov['es_banco']
            if tipo == 'ingreso':
                result['totales'][moneda]['ingresos'] += monto
            else:
                result['totales'][moneda]['egresos'] += monto

            if moneda == 'UYU':
                signo = 1 if tipo == 'ingreso' else -1
                if es_banco == 0:
                    result['efectivo_uyu'] += signo * monto
                else:
                    result['banco_uyu'] += signo * monto

        for moneda in ('UYU', 'USD', 'BRL'):
            t = result['totales'][moneda]
            t['saldo'] = t['ingresos'] - t['egresos']

        return result

    def cerrar_caja(self, caja_id: int, usuario_id: int) -> Dict[str, Any]:
        now = datetime.now()
        fecha = now.strftime("%Y-%m-%d")
        hora = now.strftime("%H:%M:%S")
        saldo = self.calcular_saldo_actual(caja_id)
        saldo_final_efectivo = saldo['efectivo_uyu']

        sql = """
            UPDATE cajas
            SET estado = 'cerrada', fecha_cierre = ?, hora_cierre = ?,
                usuario_id_cierra = ?, saldo_final_pesos = ?
            WHERE id = ?
        """
        self.db.ejecutar_query(sql, (fecha, hora, usuario_id, saldo_final_efectivo, caja_id))
        return {'caja_id': caja_id, 'fecha_cierre': fecha, 'hora_cierre': hora, 'saldo': saldo}
    
    def obtener_ultimo_saldo_cerrado(self) -> float:
        sql = "SELECT saldo_final_pesos FROM cajas WHERE estado = 'cerrada' ORDER BY id DESC LIMIT 1"
        row = self.db.ejecutar_query(sql, ()).fetchone()
        return row['saldo_final_pesos'] if row and row['saldo_final_pesos'] else 0.0

    # =====================================================================
    # NUEVOS MÉTODOS PARA HISTORIAL (Sesión 7)
    # =====================================================================

    @staticmethod
    def obtener_rango_semana(fecha_str: str) -> Tuple[str, str]:
        """Dado un fecha cualquiera, devuelve el Lunes y el Sábado de esa semana."""
        dt = datetime.strptime(fecha_str, "%Y-%m-%d")
        lunes = dt - timedelta(days=dt.weekday()) # Monday is 0
        sabado = lunes + timedelta(days=5)
        return lunes.strftime("%Y-%m-%d"), sabado.strftime("%Y-%m-%d")

    def obtener_cajas_por_fecha(self, fecha: str) -> List[Dict[str, Any]]:
        """Devuelve las cajas cerradas de un día específico."""
        sql = """
            SELECT c.id, c.fecha_apertura, c.hora_apertura, c.hora_cierre, 
                   c.fondo_inicial_pesos, c.saldo_final_pesos, u.nombre_usuario
            FROM cajas c
            JOIN usuarios u ON c.usuario_id_abre = u.id
            WHERE c.estado = 'cerrada' AND c.fecha_apertura = ?
            ORDER BY c.hora_apertura DESC
        """
        rows = self.db.ejecutar_query(sql, (fecha,)).fetchall()
        return [dict(row) for row in rows]

    def obtener_resumen_por_rango(self, fecha_inicio: str, fecha_fin: str) -> Dict[str, Any]:
        """Calcula ingresos, egresos, efectivo y banco en un rango de fechas."""
        sql = """
            SELECT tipo, moneda, monto, es_banco 
            FROM movimientos m
            JOIN cajas c ON m.caja_id = c.id
            WHERE c.estado = 'cerrada' AND c.fecha_apertura BETWEEN ? AND ?
        """
        movimientos = self.db.ejecutar_query(sql, (fecha_inicio, fecha_fin)).fetchall()
        
        resumen = {
            'UYU': {'ingresos': 0.0, 'egresos': 0.0},
            'USD': {'ingresos': 0.0, 'egresos': 0.0},
            'BRL': {'ingresos': 0.0, 'egresos': 0.0},
            'banco_uyu': 0.0,
        }

        for mov in movimientos:
            moneda, monto, tipo, es_banco = mov['moneda'], mov['monto'], mov['tipo'], mov['es_banco']
            if tipo == 'ingreso':
                resumen[moneda]['ingresos'] += monto
                if moneda == 'UYU' and es_banco == 1: resumen['banco_uyu'] += monto
            else:
                resumen[moneda]['egresos'] += monto
                if moneda == 'UYU' and es_banco == 1: resumen['banco_uyu'] -= monto

        return resumen

    def obtener_datos_grafico_mensual(self, anio: int, mes: int) -> List[Dict[str, Any]]:
        """Devuelve los totales de UYU agrupados por número de semana para un mes dado."""
        # Formatear mes para coincidir con YYYY-MM
        mes_str = f"{anio}-{mes:02d}"
        sql = """
            SELECT 
                strftime('%W', c.fecha_apertura) AS semana,
                SUM(CASE WHEN m.tipo = 'ingreso' AND m.moneda = 'UYU' THEN m.monto ELSE 0 END) AS ingresos_uyu,
                SUM(CASE WHEN m.tipo = 'egreso' AND m.moneda = 'UYU' THEN m.monto ELSE 0 END) AS egresos_uyu
            FROM movimientos m
            JOIN cajas c ON m.caja_id = c.id
            WHERE c.estado = 'cerrada' AND c.fecha_apertura LIKE ?
            GROUP BY semana
            ORDER BY semana
        """
        rows = self.db.ejecutar_query(sql, (f"{mes_str}%",)).fetchall()
        return [dict(row) for row in rows]