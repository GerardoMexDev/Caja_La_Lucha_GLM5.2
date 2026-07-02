import pytest
from models.database import DatabaseManager
from controllers.caja_controller import CajaController


@pytest.fixture
def db():
    manager = DatabaseManager(":memory:")
    # Crear usuario de prueba
    manager.ejecutar_query(
        "INSERT INTO usuarios (nombre_usuario, contrasena, es_admin) VALUES (?, ?, ?)",
        ("cajero1", "hash", 0)
    )
    yield manager
    manager.cerrar_conexion()


@pytest.fixture
def controller(db):
    return CajaController(db)


def test_abrir_caja_retorna_caja_con_id(controller):
    caja = controller.abrir_caja(usuario_id=1, fondo_inicial=1500.0)
    assert caja['id'] is not None
    assert caja['fondo_inicial_pesos'] == 1500.0
    assert caja['estado'] == 'abierta'


def test_obtener_caja_activa_devuelve_none_si_no_existe(controller):
    resultado = controller.obtener_caja_activa()
    assert resultado is None


def test_obtener_caja_activa_devuelve_caja_abierta(controller):
    controller.abrir_caja(usuario_id=1, fondo_inicial=500.0)
    caja = controller.obtener_caja_activa()
    assert caja is not None
    assert caja['estado'] == 'abierta'


def test_calcular_saldo_sin_movimientos(controller, db):
    caja = controller.abrir_caja(usuario_id=1, fondo_inicial=1000.0)
    saldo = controller.calcular_saldo_actual(caja['id'])
    assert saldo['fondo_inicial'] == 1000.0
    assert saldo['totales']['UYU']['ingresos'] == 0.0
    assert saldo['totales']['UYU']['egresos'] == 0.0
    assert saldo['efectivo_uyu'] == 1000.0
    assert saldo['banco_uyu'] == 0.0
