from typing import Optional, Dict, Any, List, Tuple
from models.database import DatabaseManager

CATEGORIAS: List[str] = [
    'servicio_taller',
    'venta',
    'pago_credito',
    'compra_tiendas',
    'adelanto_sueldo',
    'deposito_bancario_ext',
]

METODOS_PAGO: List[str] = [
    'Efectivo',
    'Tarjeta Débito',
    'Tarjeta Crédito',
    'Transferencia',
    'Cheque',
]

MONEDAS: List[str] = ['UYU', 'USD', 'BRL']


class MovimientoController:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def registrar_movimiento(
        self,
        caja_id: int,
        tipo: str,
        categoria: str,
        motivo: str,
        monto: float,
        moneda: str = 'UYU',
        metodo_pago: str = 'Efectivo',
        empleado: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> Tuple[bool, str]:
        if tipo not in ('ingreso', 'egreso'):
            return (False, "Tipo debe ser 'ingreso' o 'egreso'.")
        if categoria not in CATEGORIAS:
            return (False, f"Categoría inválida: {categoria}")
        if moneda not in MONEDAS:
            return (False, f"Moneda inválida: {moneda}")
        if metodo_pago not in METODOS_PAGO:
            return (False, f"Método de pago inválido: {metodo_pago}")
        if monto <= 0:
            return (False, "El monto debe ser mayor a 0.")
        if not motivo.strip():
            return (False, "El motivo es requerido.")

        es_banco = 0 if metodo_pago == 'Efectivo' else 1

        sql = """
            INSERT INTO movimientos
            (caja_id, tipo, categoria, motivo, monto, moneda, metodo_pago, es_banco, empleado, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            self.db.ejecutar_query(sql, (
                caja_id, tipo, categoria, motivo.strip(),
                monto, moneda, metodo_pago, es_banco,
                empleado, observaciones,
            ))
            return (True, "Movimiento registrado.")
        except Exception as e:
            return (False, f"Error al registrar: {str(e)}")

    def obtener_movimientos_del_dia(self, caja_id: int) -> List[Dict[str, Any]]:
        sql = """
            SELECT id, tipo, categoria, motivo, monto, moneda,
                   metodo_pago, es_banco, empleado, observaciones, created_at
            FROM movimientos
            WHERE caja_id = ?
            ORDER BY created_at DESC
        """
        rows = self.db.ejecutar_query(sql, (caja_id,)).fetchall()
        return [dict(row) for row in rows]

    def obtener_resumen_del_dia(self, caja_id: int) -> Dict[str, Any]:
        movimientos = self.obtener_movimientos_del_dia(caja_id)

        # OBTENER FONDO INICIAL CORRECTAMENTE
        row = self.db.ejecutar_query(
            "SELECT fondo_inicial_pesos FROM cajas WHERE id = ?", (caja_id,)
        ).fetchone()
        fondo_inicial = row['fondo_inicial_pesos'] if row else 0.0

        resumen: Dict[str, Any] = {
            'UYU': {'ingresos': 0.0, 'egresos': 0.0, 'saldo': 0.0},
            'USD': {'ingresos': 0.0, 'egresos': 0.0, 'saldo': 0.0},
            'BRL': {'ingresos': 0.0, 'egresos': 0.0, 'saldo': 0.0},
            'efectivo_uyu': fondo_inicial,
            'banco_uyu': 0.0,
            'fondo_inicial': fondo_inicial,
            'ultimos_movimientos': movimientos[:10],
        }

        for mov in movimientos:
            moneda, monto, tipo, es_banco = (
                mov['moneda'], mov['monto'], mov['tipo'], mov['es_banco']
            )
            if tipo == 'ingreso':
                resumen[moneda]['ingresos'] += monto
            else:
                resumen[moneda]['egresos'] += monto

            if moneda == 'UYU':
                signo = 1 if tipo == 'ingreso' else -1
                if es_banco == 0:
                    resumen['efectivo_uyu'] += signo * monto
                else:
                    resumen['banco_uyu'] += signo * monto

        for moneda in ('UYU', 'USD', 'BRL'):
            d = resumen[moneda]
            d['saldo'] = d['ingresos'] - d['egresos']

        return resumen