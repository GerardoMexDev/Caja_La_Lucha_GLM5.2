# Sesión 3 — Dashboard, Portal de Jornada y Movimientos
## Sistema de Caja "La Lucha"

**Fecha:** 2026-07-01  
**Estado:** Aprobado  
**Sesión anterior:** Login funcional con MVC completo (Sesión 2)

---

## 1. Objetivo

Implementar las tres pantallas post-login del sistema:
1. **Portal de Jornada** — apertura de caja diaria
2. **Dashboard con Sidebar** — navegación principal
3. **MovimientosView** — registro de ingresos/egresos
4. **ResumenView** — totales del día con desglose por moneda

---

## 2. Corrección de datos

El campo `moneda` en la tabla `movimientos` usaba `'ARS'` como valor por defecto. Se corrige a `'UYU'` (pesos uruguayos) en `database.py` y en todos los controladores y vistas. Las monedas soportadas son: **UYU, USD, BRL**.

---

## 3. Arquitectura — Ventana única con frame swapping

`CajaLaLuchaApp` en `main.py` se convierte en la ventana `CTk` raíz (router). Los frames se intercambian con `pack_forget` / `pack`. No hay ventanas `CTk` adicionales.

```
CajaLaLuchaApp(CTk)  ← ventana única, router de navegación
    ├── LoginFrame(CTkFrame)       → muestra al iniciar
    ├── PortalFrame(CTkFrame)      → muestra si no hay caja abierta
    └── DashboardFrame(CTkFrame)   → muestra al tener caja abierta
           ├── Sidebar (CTkFrame fijo, 200px)
           └── ContentArea (CTkFrame derecha, intercambia)
                 ├── MovimientosView  ← activo por defecto
                 └── ResumenView
```

### Flujo de navegación
1. App inicia → muestra `LoginFrame`
2. Login exitoso → `CajaController.obtener_caja_activa()`:
   - Si no hay caja abierta → muestra `PortalFrame`
   - Si hay caja abierta → muestra `DashboardFrame` directamente
3. Portal confirma apertura → `CajaController.abrir_caja()` → muestra `DashboardFrame`
4. Cerrar sesión (desde sidebar) → destruye frames → vuelve a `LoginFrame`

---

## 4. Nuevos archivos

| Archivo | Responsabilidad |
|---|---|
| `src/controllers/caja_controller.py` | Abrir caja, obtener caja activa, calcular saldos |
| `src/controllers/movimiento_controller.py` | Registrar movimiento, listar movimientos del día |
| `src/views/portal_view.py` | Frame de apertura de jornada |
| `src/views/dashboard_view.py` | Frame principal con sidebar + content area |
| `src/views/movimientos_view.py` | Formulario + tabla de movimientos del día |
| `src/views/resumen_view.py` | Panel de totales y últimos movimientos |
| `src/utils/constants.py` | Constantes de colores compartidas por todas las vistas |

### Archivos modificados
| Archivo | Cambio |
|---|---|
| `src/models/database.py` | `DEFAULT 'ARS'` → `DEFAULT 'UYU'` en tabla movimientos |
| `src/main.py` | `CajaLaLuchaApp` pasa a heredar de `CTk`, implementa router |
| `src/views/login_view.py` | `LoginView` pasa a ser `LoginFrame(CTkFrame)` en lugar de `CTk` |

---

## 5. Controladores

### `CajaController`
```python
# Métodos principales
abrir_caja(usuario_id: int, fondo_inicial: float) -> Dict[str, Any]
obtener_caja_activa() -> Optional[Dict[str, Any]]
calcular_saldo_actual(caja_id: int) -> Dict[str, float]
```
- `abrir_caja`: inserta en tabla `cajas` con `estado='abierta'`, fecha y hora actuales
- `obtener_caja_activa`: SELECT WHERE estado='abierta' LIMIT 1
- `calcular_saldo_actual`: suma movimientos por moneda, separa efectivo/banco

### `MovimientoController`
```python
# Métodos principales
registrar_movimiento(caja_id, tipo, categoria, motivo, monto, moneda, metodo_pago, empleado, observaciones) -> Tuple[bool, str]
obtener_movimientos_del_dia(caja_id: int) -> List[Dict[str, Any]]
obtener_resumen_del_dia(caja_id: int) -> Dict[str, Any]
```
- `es_banco` se calcula automáticamente: `1` si `metodo_pago != 'Efectivo'`
- `obtener_resumen_del_dia`: agrupa por moneda, tipo y método para el panel de resumen

---

## 6. Vistas

### 6.1 `LoginFrame` (migración de `LoginView`)
- Misma lógica y UI actual, pero hereda de `CTkFrame` en lugar de `CTk`
- Recibe el frame contenedor de `CajaLaLuchaApp` como parent
- Callback `on_login_success(user)` permanece igual

### 6.2 `PortalFrame`
- Se muestra cuando no hay caja abierta al iniciar sesión
- Contenido:
  - Saludo con nombre de usuario y fecha actual
  - Campo numérico para fondo inicial (UYU, acepta decimales, valor mínimo 0)
  - Botón "ABRIR CAJA Y COMENZAR" (deshabilitado hasta tener valor válido)
- Al confirmar: llama `CajaController.abrir_caja()` → callback `on_caja_abierta(caja)`

### 6.3 `DashboardFrame`
Layout de dos columnas: sidebar fijo (200px) + content area expandible.

**Sidebar:**
- Logo/título "La Lucha"
- Botón "Movimientos" (activo por defecto, resaltado con COLOR_ACCENT)
- Botón "Resumen del Día"
- Separador
- Label con nombre de usuario
- Botón "Cerrar Sesión" (COLOR_ERROR)

**Content Area:**
- Carga `MovimientosView` por defecto
- Intercambia a `ResumenView` al presionar el botón correspondiente en sidebar
- Transición inmediata (sin animación)

### 6.4 `MovimientosView`
Layout de dos columnas dentro del content area:

**Columna izquierda — Formulario:**
| Campo | Widget | Valores |
|---|---|---|
| Tipo | CTkSegmentedButton | Ingreso / Egreso |
| Categoría | CTkOptionMenu | servicio_taller, venta, pago_credito, compra_tiendas, adelanto_sueldo, deposito_bancario_ext |
| Motivo | CTkEntry | Texto libre |
| Monto | CTkEntry | Solo números decimales |
| Moneda | CTkSegmentedButton | UYU / USD / BRL |
| Método de Pago | CTkOptionMenu | Efectivo, Tarjeta Débito, Tarjeta Crédito, Transferencia, Cheque |
| Empleado | CTkEntry (condicional) | Solo visible si categoría = adelanto_sueldo |
| Observaciones | CTkEntry (condicional) | Solo visible si categoría = compra_tiendas |

- `es_banco` se asigna automáticamente (no es campo de UI)
- Botón "REGISTRAR" valida campos requeridos antes de llamar al controlador
- Al registrar con éxito: limpia formulario, actualiza tabla derecha, muestra mensaje de confirmación

**Columna derecha — Tabla del día:**
- Lista scrollable de todos los movimientos de la caja activa
- Columnas: Hora, Tipo, Categoría, Motivo, Monto + Moneda, Método
- Color de fila: verde tenue para ingresos, rojo tenue para egresos
- Se actualiza en tiempo real tras cada registro

### 6.5 `ResumenView`
Panel de solo lectura con tres secciones:

**Encabezado:** fecha, hora de apertura, nombre del cajero

**Tabla de totales por moneda:**
| Moneda | Ingresos | Egresos | Saldo |
|---|---|---|---|
| UYU | $X | $X | $X |
| USD | $X | $X | $X |
| BRL | $X | $X | $X |

Los saldos en distintas monedas no se suman entre sí.

**Efectivo vs Banco (solo UYU):**
- Efectivo en caja: fondo_inicial + ingresos_efectivo_UYU − egresos_efectivo_UYU
- En banco: suma de movimientos con `es_banco=1` en UYU

**Últimos movimientos:** tabla idéntica a la de `MovimientosView` (máx. 10 filas)

---

## 7. Paleta de colores (heredada de `LoginView`)

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

Estas constantes se definen una sola vez en un módulo compartido `src/utils/constants.py` y se importan en todas las vistas (evita duplicación).

---

## 8. Decisiones de diseño confirmadas

- Fondo inicial solo en UYU (ARS corregido a UYU)
- Monedas: UYU, USD, BRL
- No hay cierre de caja en esta sesión (queda para Sesión 4)
- No hay historial de cajas pasadas en esta sesión
- El saldo actual no mezcla monedas (cada una se muestra por separado)
- `es_banco` es automático, no lo elige el usuario
- Campos condicionales (Empleado, Observaciones) aparecen/desaparecen según categoría seleccionada
