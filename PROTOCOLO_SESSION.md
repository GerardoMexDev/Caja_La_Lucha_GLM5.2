🔄 El Protocolo Oficial de Sesiones
Al INICIAR una nueva sesión:

Tú me dices: "Hola, continuamos con La Lucha. Aquí tienes el log:"
Tú pegas el contenido actual de tu SESSION_LOG.md.
Yo lo leo, asimilo el contexto y te digo: "Perfecto, veo que nos quedamos en hacer el Login. ¿Empezamos?"
Al FINALIZAR una sesión:

Tú me dices: "Actualiza el log y prepara el cierre".
Yo te generaré un bloque de código con el nuevo contenido actualizado de SESSION_LOG.md (agregando lo que hicimos y los próximos pasos).
Tú lo copias, lo pegas en tu archivo, lo guardas (Ctrl+S).
Yo te daré los comandos de git add ., git commit y git push para que los ejecutes.


Si querés borrar esa caja de prueba para ver el flujo completo (Portal → Dashboard) desde cero, ejecutá esto en la terminal:

bash

sqlite3 src/lucha_caja.db "UPDATE cajas SET estado='cerrada' WHERE estado='abierta';"
Y volvé a correr:

bash

python main.py
Ahí sí te debería aparecer el Portal con el botón de "ABRIR CAJA Y COMENZAR".





Diseño — Sección 1: Arquitectura general
Flujo de navegación

CajaLaLuchaApp (CTk — ventana única, router)
    │
    ├── 1. LoginFrame      → on_success → destruye frame, muestra Portal
    ├── 2. PortalFrame     → on_abrir   → destruye frame, muestra Dashboard
    └── 3. DashboardFrame  → (ventana principal de trabajo)
           ├── Sidebar (CTkFrame fijo izquierda)
           │     ├── Btn: Movimientos (activo por defecto)
           │     ├── Btn: Resumen del Día
           │     └── Info usuario + Btn Cerrar Sesión
           └── ContentArea (CTkFrame derecha, intercambia contenido)
                 ├── MovimientosView  ← carga por defecto
                 └── ResumenView
Cambios en main.py
CajaLaLuchaApp pasa de lanzar LoginView como ventana separada a ser ella misma la CTk. Gestiona el estado de navegación y pasa los controladores a cada frame.

Nuevos archivos
Archivo	Responsabilidad
src/controllers/caja_controller.py	Abrir/cerrar cajas, obtener caja activa
src/controllers/movimiento_controller.py	Registrar/listar movimientos
src/views/portal_view.py	Frame de apertura de jornada
src/views/dashboard_view.py	Frame principal con sidebar + content area
src/views/movimientos_view.py	Formulario + tabla de movimientos del día
src/views/resumen_view.py	Totales, desglose monedas, últimos movimientos



Diseño — Sección 2: Portal de Jornada (portal_view.py)
Pantalla de apertura de caja
Se muestra inmediatamente después del login cuando no hay caja abierta. Si ya hay una caja abierta (caso de reapertura de la app durante el día), salta directo al Dashboard.


┌─────────────────────────────────┐
│          💰 LA LUCHA            │
│      Inicio de Jornada          │
│  ─────────────────────────────  │
│  Hola, [usuario] 👋             │
│  Fecha: Martes 01/07/2026       │
│                                 │
│  Fondo Inicial de Caja (UYU)    │
│  ┌───────────────────────────┐  │
│  │  $  0.00                  │  │
│  └───────────────────────────┘  │
│                                 │
│  [ ABRIR CAJA Y COMENZAR ]      │
└─────────────────────────────────┘
Validaciones:

Fondo inicial ≥ 0 (puede ser 0 si no hay efectivo)
Solo acepta números decimales
Botón deshabilitado hasta tener valor válido
Al confirmar: llama a CajaController.abrir_caja(usuario_id, fondo_inicial), que inserta en tabla cajas con estado='abierta' y la fecha/hora actual. Luego el router navega al Dashboard.



Sección 3: Dashboard + MovimientosView
Layout del Dashboard

┌──────────────┬─────────────────────────────────────────┐
│   SIDEBAR    │           CONTENT AREA                  │
│  (200px)     │                                         │
│              │                                         │
│ 💰 La Lucha  │   [contenido activo: Movimientos        │
│              │    o Resumen según sidebar]             │
│ ─────────    │                                         │
│ 📝 Movim.   │                                         │
│ 📊 Resumen  │                                         │
│              │                                         │
│ ─────────    │                                         │
│ 👤 [user]   │                                         │
│ [Salir]     │                                         │
└──────────────┴─────────────────────────────────────────┘
MovimientosView — Formulario de registro
Campos del formulario (columna izquierda) + tabla de movimientos del día (columna derecha):

Campo	Tipo	Valores
Tipo	Segmented button	Ingreso / Egreso
Categoría	OptionMenu	servicio_taller, venta, pago_credito, compra_tiendas, adelanto_sueldo, deposito_bancario_ext
Motivo	Entry texto libre	—
Monto	Entry numérico	—
Moneda	SegmentedButton	UYU / USD / BRL
Método de Pago	OptionMenu	Efectivo, Tarjeta Débito, Tarjeta Crédito, Transferencia, Cheque
Empleado	Entry (condicional)	Solo si categoría = adelanto_sueldo
Observaciones	Entry (condicional)	Solo si categoría = compra_tiendas
es_banco se calcula automáticamente: si método ≠ Efectivo → es_banco = 1.

La tabla de movimientos del día (columna derecha) se actualiza en tiempo real cada vez que se registra un movimiento. Muestra: hora, tipo, categoría, motivo, monto+moneda, método.



Sección 4: ResumenView
Resumen del Día
Panel de solo lectura, se actualiza automáticamente al navegar a esta sección.


┌─────────────────────────────────────────────────────┐
│  RESUMEN DEL DÍA — 01/07/2026                       │
│  Caja abierta por: [usuario] a las 09:00            │
├──────────────┬──────────────┬───────────────────────┤
│  INGRESOS    │   EGRESOS    │   SALDO ACTUAL         │
│  $12.500 UYU │  $3.200 UYU  │   $9.300 UYU          │
│  $150 USD    │  $0 USD      │   $150 USD             │
│  $0 BRL      │  $200 BRL    │   -$200 BRL            │
├──────────────┴──────────────┴───────────────────────┤
│  EFECTIVO vs BANCO                                  │
│  Efectivo:  $7.800 UYU    Banco: $1.500 UYU         │
├─────────────────────────────────────────────────────┤
│  ÚLTIMOS MOVIMIENTOS                                │
│  ┌──────┬─────────┬──────────────┬────────────────┐ │
│  │ Hora │  Tipo   │   Motivo     │    Monto       │ │
│  ├──────┼─────────┼──────────────┼────────────────┤ │
│  │09:45 │ Ingreso │ Servicio ... │ $2.500 UYU     │ │
│  │10:12 │ Egreso  │ Compra ...   │ $800 UYU       │ │
│  └──────┴─────────┴──────────────┴────────────────┘ │
└─────────────────────────────────────────────────────┘
El saldo actual en UYU = fondo inicial + ingresos UYU efectivo − egresos UYU efectivo. Los saldos USD y BRL se muestran informativos (no se suman entre sí).



Todo pusheado. Resumen de lo que quedó hecho hoy:

Tasks 1-6 completadas y en GitHub:

✅ utils/constants.py + DB fix (UYU) + pytest
✅ CajaController con 4 tests
✅ MovimientoController con 7 tests (11 en total)
✅ LoginFrame (migración de CTk a CTkFrame)
✅ main.py como router de ventana única
✅ portal_view.py — pantalla de apertura de jornada
Para la próxima sesión, retomar desde Task 7:

Task 7: dashboard_view.py — sidebar con Movimientos / Resumen
Task 8: movimientos_view.py — formulario + tabla
Task 9: resumen_view.py — totales y últimos movimientos
El ledger de progreso está en .superpowers/sdd/progress.md y el plan en docs/superpowers/plans/2026-07-01-sesion3-dashboard.md.




SESIÓN 8: Módulo de Empleados, Adelantos y Viáticos
Fecha: 2024-07-0X | Estado: Completada

Lo que se hizo:

Task 17: Cambio en el diccionario de Categorías. compra_tiendas pasó a ser compra_insumos. Se agregó la categoría viatico (definida como gasto general de la operación, no asociado a un empleado específico).
Task 18: Creada tabla empleados en database.py. Columnas: id, nombre, sueldo_semanal, activo.
Task 19: Creado empleado_controller.py con lógica de alta de empleados y obtención de listas.
Task 20: Modificado movimientos_view.py de forma profunda. Se implementó un menú desplegable dinámico: cuando el usuario elige la categoría adelanto_sueldo, aparece mágicamente un selector cargado con los empleados activos de la base de datos. En cualquier otra categoría, el selector se oculta.
Task 21: Creado empleados_view.py. Pantalla de gestión exclusiva para administradores con formulario de alta (Nombre, Sueldo Semanal) y tabla para activar/desactivar empleados.
Task 22: Inyectado empleado_controller en main.py y dashboard_view.py. Se agregó botón "👨‍🔧 Empleados" en el sidebar (visible solo para admin).
Task 23: Agregados métodos en movimiento_controller.py para extraer adelantos y viáticos filtrados por rango de fechas (obtener_adelantos_por_rango, obtener_viaticos_por_rango).
Task 24: Creada 4ta pestaña en historial_view.py llamada "Adelantos y Viáticos". Permite seleccionar fechas "Desde" y "Hasta", y renderiza dos tablas separadas con sus totales individuales.

Lecciones aprendidas:
REGLA DE NEGOCIO: Los adelantos de sueldo sí o sí deben estar atados a un empleado de la base de datos (para futuras liquidaciones). Los viáticos son gastos operativos puros y no requieren asignación.
REGLA DE CTk: Cuando se agregan campos dinámicos que aparecen/desaparecen (como el menú de empleados), es más seguro manejar las filas (grid) manualmente usando .grid() y .grid_remove() en lugar de pack, para no desplazar los botones de abajo de forma impredecible.

Estado actual del sistema:
Login: Funcional.
Apertura de Caja: Funcional.
Registro de Movimientos: Funcional (Con selector inteligente de empleados).
Resumen del Día: Funcional.
Cierre de Caja: Funcional.
Gestión de Usuarios: Funcional (Solo Admin).
Gestión de Empleados: Funcional (Solo Admin).
Exportación a Excel: Funcional.
Exportación a WhatsApp: Funcional.
Historial Diario/Semanal/Mensual: Funcional.
Reportes de Adelantos y Viáticos: Funcional.

Próximos pasos (Sesión 9):
Liquidación de sueldos semanales (Tabla que cruce Sueldo Base - Adelantos del periodo = Pago final).
Gráficas comparativas de Adelantos/Viáticos por semanas en el historial mensual.