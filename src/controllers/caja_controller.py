from datetime import datetime
from typing import Optional, Dict, Any
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
