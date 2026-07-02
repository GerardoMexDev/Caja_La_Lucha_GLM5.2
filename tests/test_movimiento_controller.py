import pytest
from models.database import DatabaseManager
from controllers.caja_controller import CajaController
from controllers.movimiento_controller import MovimientoController, CATEGORIAS, MONEDAS


@pytest.fixture
def db():
    manager = DatabaseManager(":memory:")
    manager.ejecutar_query(
        "INSERT INTO usuarios (nombre_usuario, contrasena, es_admin) VALUES (?, ?, ?)",
        ("cajero1", "hash", 0)
    )
    yield manager
    manager.cerrar_conexion()


@pytest.fixture
def caja_id(db):
    caja = CajaController(db).abrir_caja(usuario_id=1, fondo_inicial=500.0)
    return caja['id']


@pytest.fixture
def controller(db):
    return MovimientoController(db)


def test_registrar_movimiento_valido(controller, caja_id):
    ok, msg = controller.registrar_movimiento(
        caja_id=caja_id, tipo='ingreso', categoria='venta',
        motivo='Venta del día', monto=1000.0,
        moneda='UYU', metodo_pago='Efectivo'
    )
    assert ok is True


def test_registrar_movimiento_monto_negativo_falla(controller, caja_id):
    ok, msg = controller.registrar_movimiento(
        caja_id=caja_id, tipo='ingreso', categoria='venta',
        motivo='Test', monto=-100.0, moneda='UYU', metodo_pago='Efectivo'
    )
    assert ok is False


def test_registrar_movimiento_motivo_vacio_falla(controller, caja_id):
    ok, msg = controller.registrar_movimiento(
        caja_id=caja_id, tipo='ingreso', categoria='venta',
        motivo='   ', monto=100.0, moneda='UYU', metodo_pago='Efectivo'
    )
    assert ok is False


def test_es_banco_automatico_para_transferencia(controller, db, caja_id):
    controller.registrar_movimiento(
        caja_id=caja_id, tipo='ingreso', categoria='venta',
        motivo='Transferencia', monto=200.0, moneda='UYU', metodo_pago='Transferencia'
    )
    row = db.ejecutar_query("SELECT es_banco FROM movimientos WHERE caja_id = ?", (caja_id,)).fetchone()
    assert row['es_banco'] == 1


def test_es_banco_cero_para_efectivo(controller, db, caja_id):
    controller.registrar_movimiento(
        caja_id=caja_id, tipo='ingreso', categoria='venta',
        motivo='Efectivo', monto=300.0, moneda='UYU', metodo_pago='Efectivo'
    )
    row = db.ejecutar_query("SELECT es_banco FROM movimientos WHERE caja_id = ?", (caja_id,)).fetchone()
    assert row['es_banco'] == 0


def test_obtener_movimientos_del_dia(controller, caja_id):
    controller.registrar_movimiento(
        caja_id=caja_id, tipo='ingreso', categoria='venta',
        motivo='Mov 1', monto=100.0, moneda='UYU', metodo_pago='Efectivo'
    )
    controller.registrar_movimiento(
        caja_id=caja_id, tipo='egreso', categoria='compra_tiendas',
        motivo='Mov 2', monto=50.0, moneda='UYU', metodo_pago='Efectivo'
    )
    movs = controller.obtener_movimientos_del_dia(caja_id)
    assert len(movs) == 2


def test_obtener_resumen_del_dia(controller, caja_id):
    controller.registrar_movimiento(
        caja_id=caja_id, tipo='ingreso', categoria='venta',
        motivo='Ing', monto=1000.0, moneda='UYU', metodo_pago='Efectivo'
    )
    controller.registrar_movimiento(
        caja_id=caja_id, tipo='egreso', categoria='compra_tiendas',
        motivo='Egr', monto=300.0, moneda='UYU', metodo_pago='Efectivo'
    )
    resumen = controller.obtener_resumen_del_dia(caja_id)
    assert resumen['UYU']['ingresos'] == 1000.0
    assert resumen['UYU']['egresos'] == 300.0
    assert resumen['UYU']['saldo'] == 700.0
    assert resumen['efectivo_uyu'] == 700.0  # ingresos - egresos en efectivo
    assert 'ultimos_movimientos' in resumen
