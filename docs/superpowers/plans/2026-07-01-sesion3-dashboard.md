# Sesión 3 — Dashboard, Portal y Movimientos — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar el flujo post-login completo: portal de apertura de jornada, dashboard con sidebar, formulario de movimientos y panel de resumen del día.

**Architecture:** Ventana única `CTk` (`CajaLaLuchaApp`) que actúa como router; los frames (`LoginFrame`, `PortalFrame`, `DashboardFrame`) se intercambian con `pack`/`pack_forget`. `DashboardFrame` contiene un sidebar fijo y un content area que alterna entre `MovimientosView` y `ResumenView`.

**Tech Stack:** Python 3.14, CustomTkinter 5.2.2, SQLite (via `DatabaseManager`), pytest.

## Global Constraints

- Todos los archivos fuente viven en `src/`. Los imports son relativos a `src/` (ej: `from models.database import DatabaseManager`).
- Monedas soportadas: `UYU`, `USD`, `BRL`. **No usar ARS en ningún valor nuevo.**
- Paleta de colores: importar siempre desde `utils.constants` — nunca hardcodear colores en las vistas.
- MVC estricto: las vistas no acceden a la DB directamente; usan controladores.
- `es_banco` se calcula automáticamente: `1` si `metodo_pago != 'Efectivo'`, `0` en caso contrario.
- Para correr tests: `cd src` luego `python -m pytest ../tests/ -v` (o `$env:PYTHONPATH="src"; python -m pytest tests/ -v` desde la raíz en PowerShell).
- Para correr la app: desde `src/`, `python main.py`.
- Ejecutable del venv en Windows: `venv\Scripts\python`, `venv\Scripts\pip`, `venv\Scripts\pytest`.

---

## Mapa de archivos

| Acción | Archivo | Responsabilidad |
|---|---|---|
| Crear | `src/utils/constants.py` | Colores compartidos por todas las vistas |
| Modificar | `src/models/database.py` | Cambiar DEFAULT `'ARS'` → `'UYU'` en tabla movimientos |
| Modificar | `src/requirements.txt` | Agregar pytest |
| Crear | `tests/conftest.py` | Configurar PYTHONPATH para pytest |
| Crear | `src/controllers/caja_controller.py` | Abrir caja, obtener caja activa, calcular saldos |
| Crear | `tests/test_caja_controller.py` | Tests unitarios de CajaController |
| Crear | `src/controllers/movimiento_controller.py` | Registrar y listar movimientos |
| Crear | `tests/test_movimiento_controller.py` | Tests unitarios de MovimientoController |
| Modificar | `src/views/login_view.py` | `LoginView(CTk)` → `LoginFrame(CTkFrame)` |
| Modificar | `src/main.py` | `CajaLaLuchaApp` hereda `CTk`, implementa router |
| Crear | `src/views/portal_view.py` | Frame de apertura de jornada |
| Crear | `src/views/dashboard_view.py` | Frame con sidebar + content area |
| Crear | `src/views/movimientos_view.py` | Formulario + tabla de movimientos |
| Crear | `src/views/resumen_view.py` | Panel de totales y últimos movimientos |

---

## Task 1: Infraestructura base — constants, DB fix, pytest

**Files:**
- Create: `src/utils/constants.py`
- Modify: `src/models/database.py` (línea 85 — DEFAULT `'ARS'`)
- Modify: `requirements.txt`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

**Interfaces:**
- Produces: `COLOR_PRIMARY`, `COLOR_SECONDARY`, `COLOR_ACCENT`, `COLOR_BG`, `COLOR_CARD`, `COLOR_TEXT`, `COLOR_ERROR`, `COLOR_SUCCESS` — importables desde `utils.constants`.

- [ ] **Step 1: Crear `src/utils/constants.py`**

```python
COLOR_PRIMARY   = "#1a5276"
COLOR_SECONDARY = "#2980b9"
COLOR_ACCENT    = "#e67e22"
COLOR_BG        = "#0f1923"
COLOR_CARD      = "#1a2332"
COLOR_TEXT      = "#ecf0f1"
COLOR_ERROR     = "#e74c3c"
COLOR_SUCCESS   = "#27ae60"
```

- [ ] **Step 2: Corregir `src/models/database.py` — ARS → UYU**

Buscar la línea que contiene `DEFAULT 'ARS'` (dentro del bloque `sql_movimientos`) y reemplazar:
```python
# ANTES:
            moneda TEXT NOT NULL DEFAULT 'ARS', -- 'ARS', 'USD', 'BRL'
# DESPUÉS:
            moneda TEXT NOT NULL DEFAULT 'UYU', -- 'UYU', 'USD', 'BRL'
```

- [ ] **Step 3: Agregar pytest a `requirements.txt`**

Agregar al final del archivo:
```
pytest
```

- [ ] **Step 4: Instalar pytest en el venv**

```powershell
venv\Scripts\pip install pytest
```
Salida esperada: `Successfully installed pytest-...`

- [ ] **Step 5: Crear `tests/__init__.py`** (archivo vacío)

- [ ] **Step 6: Crear `tests/conftest.py`**

```python
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
```

- [ ] **Step 7: Verificar que el import funciona**

```powershell
cd src; python -c "from utils.constants import COLOR_BG; print(COLOR_BG)"
```
Salida esperada: `#0f1923`

- [ ] **Step 8: Commit**

```powershell
git add src/utils/constants.py src/models/database.py requirements.txt tests/__init__.py tests/conftest.py
git commit -m "feat: constants compartidos, corrección UYU y setup pytest"
```

---

## Task 2: CajaController + tests

**Files:**
- Create: `src/controllers/caja_controller.py`
- Create: `tests/test_caja_controller.py`

**Interfaces:**
- Consumes: `DatabaseManager` de `models.database`
- Produces:
  - `CajaController(db: DatabaseManager)`
  - `abrir_caja(usuario_id: int, fondo_inicial: float) -> Dict[str, Any]` — retorna dict con keys: `id`, `fecha_apertura`, `hora_apertura`, `usuario_id_abre`, `fondo_inicial_pesos`, `estado`
  - `obtener_caja_activa() -> Optional[Dict[str, Any]]` — retorna dict de caja o `None`
  - `calcular_saldo_actual(caja_id: int) -> Dict[str, Any]` — retorna dict con `fondo_inicial`, `totales` (por moneda, cada uno con `ingresos`, `egresos`, `saldo`), `efectivo_uyu`, `banco_uyu`

- [ ] **Step 1: Escribir el test**

Crear `tests/test_caja_controller.py`:
```python
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
```

- [ ] **Step 2: Correr test y verificar que falla**

```powershell
cd src; python -m pytest ../tests/test_caja_controller.py -v
```
Salida esperada: `ERROR` o `ImportError` — `caja_controller` no existe aún.

- [ ] **Step 3: Crear `src/controllers/caja_controller.py`**

```python
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
```

- [ ] **Step 4: Correr tests y verificar que pasan**

```powershell
cd src; python -m pytest ../tests/test_caja_controller.py -v
```
Salida esperada:
```
test_abrir_caja_retorna_caja_con_id PASSED
test_obtener_caja_activa_devuelve_none_si_no_existe PASSED
test_obtener_caja_activa_devuelve_caja_abierta PASSED
test_calcular_saldo_sin_movimientos PASSED
```

- [ ] **Step 5: Commit**

```powershell
git add src/controllers/caja_controller.py tests/test_caja_controller.py
git commit -m "feat: CajaController con tests"
```

---

## Task 3: MovimientoController + tests

**Files:**
- Create: `src/controllers/movimiento_controller.py`
- Create: `tests/test_movimiento_controller.py`

**Interfaces:**
- Consumes: `DatabaseManager`, `CajaController.abrir_caja()`
- Produces:
  - `CATEGORIAS: list[str]` — lista de categorías válidas
  - `METODOS_PAGO: list[str]` — lista de métodos válidos
  - `MONEDAS: list[str]` — `['UYU', 'USD', 'BRL']`
  - `MovimientoController(db: DatabaseManager)`
  - `registrar_movimiento(caja_id, tipo, categoria, motivo, monto, moneda, metodo_pago, empleado, observaciones) -> Tuple[bool, str]`
  - `obtener_movimientos_del_dia(caja_id: int) -> List[Dict[str, Any]]` — lista ordenada DESC por `created_at`
  - `obtener_resumen_del_dia(caja_id: int) -> Dict[str, Any]` — dict con keys: `UYU`, `USD`, `BRL` (cada uno con `ingresos`, `egresos`, `saldo`), `efectivo_uyu`, `banco_uyu`, `ultimos_movimientos` (lista, máx 10)

- [ ] **Step 1: Escribir los tests**

Crear `tests/test_movimiento_controller.py`:
```python
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
```

- [ ] **Step 2: Correr tests y verificar que fallan**

```powershell
cd src; python -m pytest ../tests/test_movimiento_controller.py -v
```
Salida esperada: `ImportError` — `movimiento_controller` no existe aún.

- [ ] **Step 3: Crear `src/controllers/movimiento_controller.py`**

```python
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

        resumen: Dict[str, Any] = {
            'UYU': {'ingresos': 0.0, 'egresos': 0.0, 'saldo': 0.0},
            'USD': {'ingresos': 0.0, 'egresos': 0.0, 'saldo': 0.0},
            'BRL': {'ingresos': 0.0, 'egresos': 0.0, 'saldo': 0.0},
            'efectivo_uyu': 0.0,
            'banco_uyu': 0.0,
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
```

- [ ] **Step 4: Correr todos los tests**

```powershell
cd src; python -m pytest ../tests/ -v
```
Salida esperada: todos los tests en `PASSED`.

- [ ] **Step 5: Commit**

```powershell
git add src/controllers/movimiento_controller.py tests/test_movimiento_controller.py
git commit -m "feat: MovimientoController con tests"
```

---

## Task 4: Migrar LoginView → LoginFrame

**Files:**
- Modify: `src/views/login_view.py`

**Interfaces:**
- Consumes: `utils.constants.*`, `controllers.user_controller.UserController`
- Produces: `LoginFrame(parent, user_controller, on_login_success)` — `CTkFrame` con el formulario de login. El callback `on_login_success(user: Dict[str, Any])` permanece igual.

- [ ] **Step 1: Editar `src/views/login_view.py`**

Solo cuatro cambios — no tocar nada más:

**1. Renombrar la clase y cambiar herencia (línea ~11):**
```python
# ANTES:
class LoginView(ctk.CTk):
# DESPUÉS:
class LoginFrame(ctk.CTkFrame):
```

**2. Cambiar `__init__` — agregar `parent`, ajustar `super().__init__` y quitar `_configure_window`:**
```python
# ANTES:
    def __init__(
        self,
        user_controller: UserController,
        on_login_success: Callable[[Dict[str, Any]], None]
    ) -> None:
        super().__init__()
        self.user_controller = user_controller
        self.on_login_success = on_login_success
        self._login_attempts = 0
        self._show_password = False
        self._configure_window()
        self._create_widgets()
        self._bind_events()

# DESPUÉS:
    def __init__(
        self,
        parent,
        user_controller: UserController,
        on_login_success: Callable[[Dict[str, Any]], None]
    ) -> None:
        super().__init__(parent, fg_color=self.COLOR_BG)
        self.user_controller = user_controller
        self.on_login_success = on_login_success
        self._login_attempts = 0
        self._show_password = False
        self._create_widgets()
        self._bind_events()
```

**3. Eliminar el método `_configure_window` completo** (el bloque completo desde `def _configure_window(self)` hasta antes de `def _create_widgets`). Los temas y geometría ahora son responsabilidad de `CajaLaLuchaApp`.

**IMPORTANTE:** Las constantes de color de clase (`COLOR_PRIMARY`, etc.) **se mantienen tal cual** — los métodos del archivo las usan como `self.COLOR_*` y seguirán funcionando.

- [ ] **Step 2: Test manual — verificar que el archivo no tiene errores de sintaxis**

```powershell
cd src; python -c "from views.login_view import LoginFrame; print('OK')"
```
Salida esperada: `OK`

- [ ] **Step 3: Commit**

```powershell
git add src/views/login_view.py
git commit -m "refactor: LoginView → LoginFrame (CTkFrame)"
```

---

## Task 5: Refactorizar `main.py` como router CTk

**Files:**
- Modify: `src/main.py`

**Interfaces:**
- Consumes: `LoginFrame`, `CajaController`, `MovimientoController`, `PortalFrame` (Task 6), `DashboardFrame` (Task 7)
- Produces: `CajaLaLuchaApp(CTk)` — ventana única que implementa navegación entre frames.

> Nota: En este task, `PortalFrame` y `DashboardFrame` no existen aún. Se importan y se usan en métodos que serán llamados después de que esos tasks estén completos. La app arrancará correctamente hasta el punto de login; los métodos `_show_portal` y `_show_dashboard` darán `ImportError` hasta que Task 6 y 7 estén listos. Eso es aceptable — no correr la app completa hasta terminar Task 7.

- [ ] **Step 1: Reemplazar `src/main.py` completo**

```python
"""
Punto de entrada principal del Sistema Caja La Lucha.
"""

import sys
import customtkinter as ctk
from typing import Dict, Any, Optional

from models.database import DatabaseManager
from controllers.user_controller import UserController
from controllers.caja_controller import CajaController
from controllers.movimiento_controller import MovimientoController
from views.login_view import LoginFrame
from utils.constants import COLOR_BG


class CajaLaLuchaApp(ctk.CTk):
    """Ventana principal — router de navegación entre frames."""

    def __init__(self) -> None:
        super().__init__()

        self.db = DatabaseManager()
        self.user_controller = UserController(self.db)
        self.caja_controller = CajaController(self.db)
        self.movimiento_controller = MovimientoController(self.db)
        self.user_controller.ensure_admin_exists()

        self.current_user: Optional[Dict[str, Any]] = None
        self.current_caja: Optional[Dict[str, Any]] = None
        self._active_frame: Optional[ctk.CTkFrame] = None

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=COLOR_BG)

        self._show_login()
        self.mainloop()

    # ── navegación ────────────────────────────────────────────────────────────

    def _clear_frame(self) -> None:
        if self._active_frame:
            self._active_frame.destroy()
            self._active_frame = None

    def _center(self, w: int, h: int) -> None:
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _show_login(self) -> None:
        self._clear_frame()
        self.title("Caja La Lucha — Inicio de Sesión")
        self._center(450, 550)
        self._active_frame = LoginFrame(
            parent=self,
            user_controller=self.user_controller,
            on_login_success=self._on_login_success,
        )
        self._active_frame.pack(fill="both", expand=True)

    def _on_login_success(self, user: Dict[str, Any]) -> None:
        self.current_user = user
        caja_activa = self.caja_controller.obtener_caja_activa()
        if caja_activa:
            self.current_caja = caja_activa
            self._show_dashboard()
        else:
            self._show_portal()

    def _show_portal(self) -> None:
        from views.portal_view import PortalFrame
        self._clear_frame()
        self.title("Caja La Lucha — Apertura de Jornada")
        self._center(500, 420)
        self._active_frame = PortalFrame(
            parent=self,
            usuario=self.current_user,
            caja_controller=self.caja_controller,
            on_caja_abierta=self._on_caja_abierta,
        )
        self._active_frame.pack(fill="both", expand=True)

    def _on_caja_abierta(self, caja: Dict[str, Any]) -> None:
        self.current_caja = caja
        self._show_dashboard()

    def _show_dashboard(self) -> None:
        from views.dashboard_view import DashboardFrame
        self._clear_frame()
        self.title("Caja La Lucha — Dashboard")
        self._center(1200, 700)
        self.minsize(900, 600)
        self._active_frame = DashboardFrame(
            parent=self,
            usuario=self.current_user,
            caja=self.current_caja,
            movimiento_controller=self.movimiento_controller,
            on_logout=self._on_logout,
        )
        self._active_frame.pack(fill="both", expand=True)

    def _on_logout(self) -> None:
        self.current_user = None
        self.current_caja = None
        self.minsize(0, 0)
        self._show_login()


def main() -> None:
    try:
        CajaLaLuchaApp()
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verificar importaciones sin errores**

```powershell
cd src; python -c "from main import CajaLaLuchaApp; print('imports OK')"
```
Salida esperada: `imports OK` (sin levantar la ventana).

- [ ] **Step 3: Commit**

```powershell
git add src/main.py
git commit -m "refactor: main.py como router CTk con frame swapping"
```

---

## Task 6: PortalFrame

**Files:**
- Create: `src/views/portal_view.py`

**Interfaces:**
- Consumes: `utils.constants.*`, `CajaController.abrir_caja()`
- Produces: `PortalFrame(parent, usuario, caja_controller, on_caja_abierta)`
  - `on_caja_abierta(caja: Dict[str, Any])` — callback llamado tras apertura exitosa

- [ ] **Step 1: Crear `src/views/portal_view.py`**

```python
"""
Frame de apertura de jornada.
Se muestra cuando no hay caja activa al iniciar sesión.
"""

import customtkinter as ctk
from datetime import datetime
from typing import Dict, Any, Callable

from controllers.caja_controller import CajaController
from utils.constants import (
    COLOR_ACCENT, COLOR_BG, COLOR_CARD, COLOR_TEXT,
    COLOR_ERROR, COLOR_SUCCESS
)

_DIAS = {
    'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado',
    'Sunday': 'Domingo',
}


class PortalFrame(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        usuario: Dict[str, Any],
        caja_controller: CajaController,
        on_caja_abierta: Callable[[Dict[str, Any]], None],
    ) -> None:
        super().__init__(parent, fg_color=COLOR_BG)
        self.usuario = usuario
        self.caja_controller = caja_controller
        self.on_caja_abierta = on_caja_abierta
        self._create_widgets()

    def _create_widgets(self) -> None:
        card = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=20)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.88)

        ctk.CTkLabel(card, text="💰", font=ctk.CTkFont(size=50), text_color=COLOR_ACCENT).pack(pady=(30, 5))

        ctk.CTkLabel(
            card, text="INICIO DE JORNADA",
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack()

        now = datetime.now()
        dia_en = now.strftime("%A")
        dia_es = _DIAS.get(dia_en, dia_en)
        fecha_str = f"{dia_es} {now.strftime('%d/%m/%Y')}"
        ctk.CTkLabel(
            card,
            text=f"Hola, {self.usuario['nombre_usuario']} 👋\n{fecha_str}",
            font=ctk.CTkFont(size=14),
            text_color="#bdc3c7",
            justify="center",
        ).pack(pady=(10, 15))

        ctk.CTkFrame(card, height=2, fg_color="#2c3e50").pack(fill="x", padx=40, pady=(0, 20))

        ctk.CTkLabel(
            card, text="Fondo Inicial de Caja (UYU)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#bdc3c7",
        ).pack()

        self.fondo_entry = ctk.CTkEntry(
            card,
            height=50,
            placeholder_text="$ 0.00",
            font=ctk.CTkFont(size=18),
            corner_radius=10,
            border_width=2,
            border_color="#34495e",
            fg_color="#1c2833",
            text_color=COLOR_TEXT,
            justify="center",
        )
        self.fondo_entry.pack(fill="x", padx=60, pady=(8, 0))
        self.fondo_entry.bind("<KeyRelease>", self._validate_fondo)

        self.open_btn = ctk.CTkButton(
            card,
            text="ABRIR CAJA Y COMENZAR",
            height=50,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=12,
            fg_color="#2c3e50",
            state="disabled",
            command=self._abrir_caja,
        )
        self.open_btn.pack(fill="x", padx=60, pady=(20, 0))

        self.status_label = ctk.CTkLabel(
            card, text="",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT,
        )
        self.status_label.pack(pady=(10, 0))

    def _validate_fondo(self, event=None) -> None:
        value = self.fondo_entry.get().strip().replace(",", ".")
        try:
            fondo = float(value)
            if fondo >= 0:
                self.open_btn.configure(state="normal", fg_color=COLOR_SUCCESS)
                return
        except ValueError:
            pass
        self.open_btn.configure(state="disabled", fg_color="#2c3e50")

    def _abrir_caja(self) -> None:
        value = self.fondo_entry.get().strip().replace(",", ".")
        try:
            fondo = float(value)
        except ValueError:
            self.status_label.configure(text="Ingrese un monto válido.", text_color=COLOR_ERROR)
            return

        self.open_btn.configure(state="disabled", text="Abriendo...")
        caja = self.caja_controller.abrir_caja(self.usuario['id'], fondo)
        self.after(300, lambda: self.on_caja_abierta(caja))
```

- [ ] **Step 2: Verificar importaciones**

```powershell
cd src; python -c "from views.portal_view import PortalFrame; print('OK')"
```
Salida esperada: `OK`

- [ ] **Step 3: Commit**

```powershell
git add src/views/portal_view.py
git commit -m "feat: PortalFrame — apertura de jornada"
```

---

## Task 7: DashboardFrame con sidebar

**Files:**
- Create: `src/views/dashboard_view.py`

**Interfaces:**
- Consumes: `utils.constants.*`, `MovimientoController`, `MovimientosView` (Task 8), `ResumenView` (Task 9)
- Produces: `DashboardFrame(parent, usuario, caja, movimiento_controller, on_logout)`
  - Sidebar con botones "Movimientos" y "Resumen del Día"
  - `content_area` donde se intercambian las vistas

> Las importaciones de `MovimientosView` y `ResumenView` se hacen dentro de los métodos `_show_movimientos` y `_show_resumen` (lazy imports) para evitar `ImportError` mientras esos tasks no están completos.

- [ ] **Step 1: Crear `src/views/dashboard_view.py`**

```python
"""
Frame principal del sistema con sidebar de navegación.
"""

import customtkinter as ctk
from typing import Dict, Any, Callable, Optional

from controllers.movimiento_controller import MovimientoController
from utils.constants import (
    COLOR_ACCENT, COLOR_BG, COLOR_CARD, COLOR_TEXT,
    COLOR_ERROR, COLOR_PRIMARY,
)


class DashboardFrame(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        usuario: Dict[str, Any],
        caja: Dict[str, Any],
        movimiento_controller: MovimientoController,
        on_logout: Callable[[], None],
    ) -> None:
        super().__init__(parent, fg_color=COLOR_BG)
        self.usuario = usuario
        self.caja = caja
        self.movimiento_controller = movimiento_controller
        self.on_logout = on_logout
        self._active_content: Optional[ctk.CTkFrame] = None

        self._create_layout()
        self._show_movimientos()

    def _create_layout(self) -> None:
        self.sidebar = ctk.CTkFrame(self, width=210, fg_color=COLOR_CARD, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._create_sidebar()

        self.content_area = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0)
        self.content_area.pack(side="right", fill="both", expand=True)

    def _create_sidebar(self) -> None:
        ctk.CTkLabel(
            self.sidebar, text="💰",
            font=ctk.CTkFont(size=35), text_color=COLOR_ACCENT,
        ).pack(pady=(25, 0))
        ctk.CTkLabel(
            self.sidebar, text="LA LUCHA",
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(pady=(0, 5))

        ctk.CTkFrame(self.sidebar, height=1, fg_color="#2c3e50").pack(fill="x", padx=15, pady=10)

        self.btn_movimientos = ctk.CTkButton(
            self.sidebar,
            text="📝  Movimientos",
            anchor="w",
            height=42,
            corner_radius=8,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_PRIMARY,
            font=ctk.CTkFont(size=13),
            command=self._show_movimientos,
        )
        self.btn_movimientos.pack(fill="x", padx=10, pady=(5, 2))

        self.btn_resumen = ctk.CTkButton(
            self.sidebar,
            text="📊  Resumen del Día",
            anchor="w",
            height=42,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLOR_PRIMARY,
            font=ctk.CTkFont(size=13),
            command=self._show_resumen,
        )
        self.btn_resumen.pack(fill="x", padx=10, pady=2)

        bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", padx=10, pady=15)

        ctk.CTkFrame(bottom, height=1, fg_color="#2c3e50").pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            bottom,
            text=f"👤 {self.usuario['nombre_usuario']}",
            font=ctk.CTkFont(size=12),
            text_color="#7f8c8d",
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkButton(
            bottom,
            text="Cerrar Sesión",
            height=35,
            corner_radius=8,
            fg_color=COLOR_ERROR,
            hover_color="#c0392b",
            font=ctk.CTkFont(size=12),
            command=self.on_logout,
        ).pack(fill="x", pady=(8, 0))

    def _clear_content(self) -> None:
        if self._active_content:
            self._active_content.destroy()
            self._active_content = None

    def _show_movimientos(self) -> None:
        from views.movimientos_view import MovimientosView
        self._clear_content()
        self.btn_movimientos.configure(fg_color=COLOR_ACCENT)
        self.btn_resumen.configure(fg_color="transparent")
        self._active_content = MovimientosView(
            parent=self.content_area,
            caja=self.caja,
            movimiento_controller=self.movimiento_controller,
        )
        self._active_content.pack(fill="both", expand=True)

    def _show_resumen(self) -> None:
        from views.resumen_view import ResumenView
        self._clear_content()
        self.btn_resumen.configure(fg_color=COLOR_ACCENT)
        self.btn_movimientos.configure(fg_color="transparent")
        self._active_content = ResumenView(
            parent=self.content_area,
            caja=self.caja,
            movimiento_controller=self.movimiento_controller,
        )
        self._active_content.pack(fill="both", expand=True)
```

- [ ] **Step 2: Verificar importaciones**

```powershell
cd src; python -c "from views.dashboard_view import DashboardFrame; print('OK')"
```
Salida esperada: `OK`

- [ ] **Step 3: Commit**

```powershell
git add src/views/dashboard_view.py
git commit -m "feat: DashboardFrame con sidebar de navegación"
```

---

## Task 8: MovimientosView — formulario + tabla

**Files:**
- Create: `src/views/movimientos_view.py`

**Interfaces:**
- Consumes: `utils.constants.*`, `MovimientoController`, `CATEGORIAS`, `METODOS_PAGO`, `MONEDAS`
- Produces: `MovimientosView(parent, caja, movimiento_controller)`

- [ ] **Step 1: Crear `src/views/movimientos_view.py`**

```python
"""
Vista de registro de movimientos (ingresos/egresos).
"""

import customtkinter as ctk
from typing import Dict, Any

from controllers.movimiento_controller import (
    MovimientoController, CATEGORIAS, METODOS_PAGO, MONEDAS,
)
from utils.constants import (
    COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_SECONDARY,
    COLOR_PRIMARY, COLOR_ERROR, COLOR_SUCCESS,
)


class MovimientosView(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        caja: Dict[str, Any],
        movimiento_controller: MovimientoController,
    ) -> None:
        super().__init__(parent, fg_color=COLOR_BG)
        self.caja = caja
        self.movimiento_controller = movimiento_controller
        self._create_layout()
        self._load_movimientos()

    # ── layout ────────────────────────────────────────────────────────────────

    def _create_layout(self) -> None:
        ctk.CTkLabel(
            self, text="Registro de Movimientos",
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=20, pady=(15, 10))

        columns = ctk.CTkFrame(self, fg_color="transparent")
        columns.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.form_frame = ctk.CTkScrollableFrame(
            columns, fg_color=COLOR_CARD, corner_radius=12, width=340,
        )
        self.form_frame.pack(side="left", fill="y", padx=(5, 5), pady=5)
        self._create_form()

        self.table_frame = ctk.CTkFrame(columns, fg_color=COLOR_CARD, corner_radius=12)
        self.table_frame.pack(side="right", fill="both", expand=True, padx=(5, 5), pady=5)
        self._create_table_header()

    # ── formulario ────────────────────────────────────────────────────────────

    def _lbl(self, text: str) -> None:
        ctk.CTkLabel(
            self.form_frame, text=text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#bdc3c7", anchor="w",
        ).pack(fill="x", padx=15)

    def _create_form(self) -> None:
        ctk.CTkLabel(
            self.form_frame, text="Nuevo Movimiento",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(pady=(15, 10))

        self._lbl("Tipo")
        self.tipo_var = ctk.StringVar(value="ingreso")
        ctk.CTkSegmentedButton(
            self.form_frame, values=["ingreso", "egreso"],
            variable=self.tipo_var,
            fg_color="#1c2833",
            selected_color=COLOR_SECONDARY,
            selected_hover_color=COLOR_PRIMARY,
            font=ctk.CTkFont(size=13),
        ).pack(fill="x", padx=15, pady=(2, 12))

        self._lbl("Categoría")
        self.categoria_var = ctk.StringVar(value=CATEGORIAS[0])
        ctk.CTkOptionMenu(
            self.form_frame, values=CATEGORIAS,
            variable=self.categoria_var,
            fg_color="#1c2833",
            button_color=COLOR_SECONDARY,
            button_hover_color=COLOR_PRIMARY,
            font=ctk.CTkFont(size=13),
            command=self._on_categoria_change,
        ).pack(fill="x", padx=15, pady=(2, 12))

        self._lbl("Motivo")
        self.motivo_entry = ctk.CTkEntry(
            self.form_frame, height=40,
            placeholder_text="Descripción del movimiento",
            fg_color="#1c2833", border_color="#34495e",
            text_color=COLOR_TEXT, font=ctk.CTkFont(size=13),
        )
        self.motivo_entry.pack(fill="x", padx=15, pady=(2, 12))

        self._lbl("Monto")
        self.monto_entry = ctk.CTkEntry(
            self.form_frame, height=40,
            placeholder_text="0.00",
            fg_color="#1c2833", border_color="#34495e",
            text_color=COLOR_TEXT, font=ctk.CTkFont(size=13),
        )
        self.monto_entry.pack(fill="x", padx=15, pady=(2, 12))

        self._lbl("Moneda")
        self.moneda_var = ctk.StringVar(value="UYU")
        ctk.CTkSegmentedButton(
            self.form_frame, values=MONEDAS,
            variable=self.moneda_var,
            fg_color="#1c2833",
            selected_color=COLOR_SECONDARY,
            selected_hover_color=COLOR_PRIMARY,
            font=ctk.CTkFont(size=13),
        ).pack(fill="x", padx=15, pady=(2, 12))

        self._lbl("Método de Pago")
        self.metodo_var = ctk.StringVar(value="Efectivo")
        ctk.CTkOptionMenu(
            self.form_frame, values=METODOS_PAGO,
            variable=self.metodo_var,
            fg_color="#1c2833",
            button_color=COLOR_SECONDARY,
            button_hover_color=COLOR_PRIMARY,
            font=ctk.CTkFont(size=13),
        ).pack(fill="x", padx=15, pady=(2, 12))

        # Campos condicionales — se crean pero NO se empaquetan aún
        self._empleado_lbl = ctk.CTkLabel(
            self.form_frame, text="Empleado",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#bdc3c7", anchor="w",
        )
        self.empleado_entry = ctk.CTkEntry(
            self.form_frame, height=40,
            placeholder_text="Nombre del empleado",
            fg_color="#1c2833", border_color="#34495e",
            text_color=COLOR_TEXT, font=ctk.CTkFont(size=13),
        )
        self._obs_lbl = ctk.CTkLabel(
            self.form_frame, text="Observaciones",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#bdc3c7", anchor="w",
        )
        self.observaciones_entry = ctk.CTkEntry(
            self.form_frame, height=40,
            placeholder_text="Detalle de la compra",
            fg_color="#1c2833", border_color="#34495e",
            text_color=COLOR_TEXT, font=ctk.CTkFont(size=13),
        )

        self.submit_btn = ctk.CTkButton(
            self.form_frame,
            text="REGISTRAR MOVIMIENTO",
            height=45, corner_radius=10,
            fg_color=COLOR_SECONDARY,
            hover_color=COLOR_PRIMARY,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._registrar,
        )
        self.submit_btn.pack(fill="x", padx=15, pady=(10, 5))

        self.status_label = ctk.CTkLabel(
            self.form_frame, text="",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT, wraplength=300,
        )
        self.status_label.pack(pady=(0, 15))

    def _on_categoria_change(self, value: str) -> None:
        self._empleado_lbl.pack_forget()
        self.empleado_entry.pack_forget()
        self._obs_lbl.pack_forget()
        self.observaciones_entry.pack_forget()

        if value == "adelanto_sueldo":
            self._empleado_lbl.pack(fill="x", padx=15, before=self.submit_btn)
            self.empleado_entry.pack(fill="x", padx=15, pady=(2, 12), before=self.submit_btn)
        elif value == "compra_tiendas":
            self._obs_lbl.pack(fill="x", padx=15, before=self.submit_btn)
            self.observaciones_entry.pack(fill="x", padx=15, pady=(2, 12), before=self.submit_btn)

    # ── tabla ─────────────────────────────────────────────────────────────────

    _COLS = [("Hora", 60), ("Tipo", 70), ("Categoría", 130), ("Motivo", 170), ("Monto", 110), ("Método", 110)]

    def _create_table_header(self) -> None:
        ctk.CTkLabel(
            self.table_frame, text="Movimientos del Día",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.table_scroll = ctk.CTkScrollableFrame(self.table_frame, fg_color="transparent")
        self.table_scroll.pack(fill="both", expand=True, padx=5, pady=(0, 10))

        header = ctk.CTkFrame(self.table_scroll, fg_color="#1c2833", corner_radius=6)
        header.pack(fill="x", pady=(0, 2))
        for col, w in self._COLS:
            ctk.CTkLabel(
                header, text=col,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#7f8c8d", width=w, anchor="w",
            ).pack(side="left", padx=5, pady=5)

    def _load_movimientos(self) -> None:
        for widget in list(self.table_scroll.winfo_children())[1:]:
            widget.destroy()

        movimientos = self.movimiento_controller.obtener_movimientos_del_dia(self.caja['id'])

        if not movimientos:
            ctk.CTkLabel(
                self.table_scroll,
                text="No hay movimientos registrados hoy.",
                font=ctk.CTkFont(size=12), text_color="#7f8c8d",
            ).pack(pady=20)
            return

        for mov in movimientos:
            hora = mov['created_at'][11:16] if mov['created_at'] else "--:--"
            motivo_txt = mov['motivo']
            if len(motivo_txt) > 20:
                motivo_txt = motivo_txt[:20] + "..."
            row_color = "#1a3a2a" if mov['tipo'] == 'ingreso' else "#3a1a1a"

            row = ctk.CTkFrame(self.table_scroll, fg_color=row_color, corner_radius=6)
            row.pack(fill="x", pady=1)

            for text, w in zip(
                [hora, mov['tipo'].capitalize(), mov['categoria'],
                 motivo_txt, f"${mov['monto']:.2f} {mov['moneda']}", mov['metodo_pago']],
                [c[1] for c in self._COLS],
            ):
                ctk.CTkLabel(
                    row, text=text,
                    font=ctk.CTkFont(size=11),
                    text_color=COLOR_TEXT, width=w, anchor="w",
                ).pack(side="left", padx=5, pady=4)

    # ── acciones ──────────────────────────────────────────────────────────────

    def _registrar(self) -> None:
        motivo = self.motivo_entry.get().strip()
        monto_str = self.monto_entry.get().strip().replace(",", ".")
        empleado = (
            self.empleado_entry.get().strip()
            if self.empleado_entry.winfo_ismapped() else None
        )
        observaciones = (
            self.observaciones_entry.get().strip()
            if self.observaciones_entry.winfo_ismapped() else None
        )

        try:
            monto = float(monto_str)
        except ValueError:
            self.status_label.configure(
                text="El monto debe ser un número válido.", text_color=COLOR_ERROR,
            )
            return

        ok, msg = self.movimiento_controller.registrar_movimiento(
            caja_id=self.caja['id'],
            tipo=self.tipo_var.get(),
            categoria=self.categoria_var.get(),
            motivo=motivo,
            monto=monto,
            moneda=self.moneda_var.get(),
            metodo_pago=self.metodo_var.get(),
            empleado=empleado or None,
            observaciones=observaciones or None,
        )

        if ok:
            self.status_label.configure(text=f"✓ {msg}", text_color=COLOR_SUCCESS)
            self._reset_form()
            self._load_movimientos()
        else:
            self.status_label.configure(text=f"✗ {msg}", text_color=COLOR_ERROR)

    def _reset_form(self) -> None:
        self.tipo_var.set("ingreso")
        self.categoria_var.set(CATEGORIAS[0])
        self.motivo_entry.delete(0, "end")
        self.monto_entry.delete(0, "end")
        self.moneda_var.set("UYU")
        self.metodo_var.set("Efectivo")
        self.empleado_entry.delete(0, "end")
        self.observaciones_entry.delete(0, "end")
        self._on_categoria_change(CATEGORIAS[0])
```

- [ ] **Step 2: Verificar importaciones**

```powershell
cd src; python -c "from views.movimientos_view import MovimientosView; print('OK')"
```
Salida esperada: `OK`

- [ ] **Step 3: Commit**

```powershell
git add src/views/movimientos_view.py
git commit -m "feat: MovimientosView — formulario y tabla de movimientos"
```

---

## Task 9: ResumenView + run integración

**Files:**
- Create: `src/views/resumen_view.py`

**Interfaces:**
- Consumes: `utils.constants.*`, `MovimientoController.obtener_resumen_del_dia()`
- Produces: `ResumenView(parent, caja, movimiento_controller)`

- [ ] **Step 1: Crear `src/views/resumen_view.py`**

```python
"""
Panel de resumen del día: totales por moneda, efectivo vs banco, últimos movimientos.
"""

import customtkinter as ctk
from typing import Dict, Any

from controllers.movimiento_controller import MovimientoController
from utils.constants import (
    COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_ACCENT,
    COLOR_ERROR, COLOR_SUCCESS,
)


class ResumenView(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        caja: Dict[str, Any],
        movimiento_controller: MovimientoController,
    ) -> None:
        super().__init__(parent, fg_color=COLOR_BG)
        self.caja = caja
        self.movimiento_controller = movimiento_controller
        self._create_widgets()
        self._load_data()

    def _create_widgets(self) -> None:
        ctk.CTkLabel(
            self, text="Resumen del Día",
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=20, pady=(15, 5))

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=5)

    def _load_data(self) -> None:
        for w in self.scroll.winfo_children():
            w.destroy()

        resumen = self.movimiento_controller.obtener_resumen_del_dia(self.caja['id'])

        # ── encabezado ────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self.scroll, fg_color=COLOR_CARD, corner_radius=12)
        header.pack(fill="x", padx=5, pady=(5, 3))
        ctk.CTkLabel(
            header,
            text=f"Caja abierta el {self.caja.get('fecha_apertura', '')} "
                 f"a las {self.caja.get('hora_apertura', '')}",
            font=ctk.CTkFont(size=13), text_color="#7f8c8d",
        ).pack(pady=12)

        # ── totales por moneda ────────────────────────────────────────────────
        totals_card = ctk.CTkFrame(self.scroll, fg_color=COLOR_CARD, corner_radius=12)
        totals_card.pack(fill="x", padx=5, pady=3)

        ctk.CTkLabel(
            totals_card, text="Totales por Moneda",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=15, pady=(12, 5))

        hdr_row = ctk.CTkFrame(totals_card, fg_color="#1c2833", corner_radius=6)
        hdr_row.pack(fill="x", padx=10, pady=(0, 2))
        for col in ["Moneda", "Ingresos", "Egresos", "Saldo"]:
            ctk.CTkLabel(
                hdr_row, text=col,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#7f8c8d", anchor="w", width=160,
            ).pack(side="left", padx=10, pady=8)

        for moneda in ("UYU", "USD", "BRL"):
            data = resumen[moneda]
            saldo = data['saldo']
            row = ctk.CTkFrame(totals_card, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=1)
            ctk.CTkLabel(row, text=moneda, font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_ACCENT, width=160, anchor="w").pack(side="left", padx=10, pady=6)
            ctk.CTkLabel(row, text=f"${data['ingresos']:.2f}", font=ctk.CTkFont(size=13), text_color=COLOR_SUCCESS, width=160, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"${data['egresos']:.2f}", font=ctk.CTkFont(size=13), text_color=COLOR_ERROR, width=160, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"${saldo:.2f}", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_SUCCESS if saldo >= 0 else COLOR_ERROR, width=160, anchor="w").pack(side="left", padx=10)

        ctk.CTkFrame(totals_card, height=1, fg_color="#2c3e50").pack(fill="x", padx=10, pady=(5, 10))

        # ── efectivo vs banco ─────────────────────────────────────────────────
        efect_card = ctk.CTkFrame(self.scroll, fg_color=COLOR_CARD, corner_radius=12)
        efect_card.pack(fill="x", padx=5, pady=3)

        ctk.CTkLabel(
            efect_card, text="Efectivo vs Banco (UYU)",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=15, pady=(12, 5))

        fondo = self.caja.get('fondo_inicial_pesos', 0.0)
        efectivo_total = fondo + resumen['efectivo_uyu']

        for label, value in [
            ("Efectivo en caja:", f"${efectivo_total:.2f} UYU"),
            ("En cuenta bancaria:", f"${resumen['banco_uyu']:.2f} UYU"),
        ]:
            r = ctk.CTkFrame(efect_card, fg_color="transparent")
            r.pack(fill="x", padx=15, pady=2)
            ctk.CTkLabel(r, text=label, font=ctk.CTkFont(size=13), text_color="#bdc3c7", width=180, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(r, text=value, font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_TEXT).pack(side="left", padx=5)

        ctk.CTkFrame(efect_card, height=1, fg_color="transparent").pack(pady=8)

        # ── últimos movimientos ───────────────────────────────────────────────
        movs_card = ctk.CTkFrame(self.scroll, fg_color=COLOR_CARD, corner_radius=12)
        movs_card.pack(fill="x", padx=5, pady=3)

        ctk.CTkLabel(
            movs_card, text="Últimos Movimientos",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=15, pady=(12, 5))

        ultimos = resumen.get('ultimos_movimientos', [])
        if not ultimos:
            ctk.CTkLabel(
                movs_card, text="No hay movimientos registrados aún.",
                font=ctk.CTkFont(size=12), text_color="#7f8c8d",
            ).pack(pady=(0, 12))
        else:
            for mov in ultimos:
                hora = mov['created_at'][11:16] if mov['created_at'] else "--:--"
                motivo_txt = mov['motivo'][:28] + "..." if len(mov['motivo']) > 28 else mov['motivo']
                row_color = "#1a3a2a" if mov['tipo'] == 'ingreso' else "#3a1a1a"
                row = ctk.CTkFrame(movs_card, fg_color=row_color, corner_radius=6)
                row.pack(fill="x", padx=10, pady=1)
                for text, w in [
                    (hora, 60), (mov['tipo'].capitalize(), 75),
                    (motivo_txt, 220), (f"${mov['monto']:.2f} {mov['moneda']}", 120),
                    (mov['metodo_pago'], 120),
                ]:
                    ctk.CTkLabel(
                        row, text=text,
                        font=ctk.CTkFont(size=11), text_color=COLOR_TEXT,
                        width=w, anchor="w",
                    ).pack(side="left", padx=5, pady=4)
            ctk.CTkFrame(movs_card, height=1, fg_color="transparent").pack(pady=5)
```

- [ ] **Step 2: Verificar importaciones**

```powershell
cd src; python -c "from views.resumen_view import ResumenView; print('OK')"
```
Salida esperada: `OK`

- [ ] **Step 3: Correr todos los tests finales**

```powershell
cd src; python -m pytest ../tests/ -v
```
Salida esperada: todos los tests en `PASSED`.

- [ ] **Step 4: Correr la aplicación completa**

```powershell
cd src; python main.py
```
Verificar manualmente:
- [ ] Login con `admin` / `admin123` funciona
- [ ] Si no hay caja abierta → aparece PortalFrame
- [ ] Ingresar fondo `1000` → botón se habilita → click abre el Dashboard
- [ ] Sidebar muestra "Movimientos" activo (naranja)
- [ ] Registrar un ingreso: tipo=ingreso, categoría=venta, motivo=Test, monto=500, UYU, Efectivo → aparece en tabla
- [ ] Registrar un egreso: tipo=egreso, categoría=compra_tiendas, monto=200 → aparece con fondo rojo
- [ ] Click "Resumen del Día" → muestra totales correctos
- [ ] Click "Cerrar Sesión" → vuelve al login
- [ ] Login de nuevo → Dashboard directo (caja ya abierta)

- [ ] **Step 5: Commit final**

```powershell
git add src/views/resumen_view.py
git commit -m "feat: ResumenView — totales, efectivo/banco y últimos movimientos"
```
