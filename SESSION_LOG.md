Hola, continuamos con La Lucha. Aquí tienes el log: ⚠️ REGLA DE ORO - LEER SIEMPRIMO PRIMERO
NO ASUMIR NADA. Antes de escribir cualquier código:

Pedir find . -name "*.py" -not -path "./venv/*" para ver la estructura ACTUAL.
Pedir el contenido de los archivos que se van a modificar o consumir.
Verificar nombres de clases, funciones, variables y carpetas.
Recién después de verificar TODO, escribir código.
ANTES de entregar un código, revisarlo para detectar fallas de sintaxis o atributos (ej: no usar italic=True en CTkFont).
Si hay error de código viejo que no cambia, recordar BORRAR __pycache__ con rm -rf src/views/__pycache__.
SESIÓN 1: Definición de Arquitectura y Setup Inicial
Fecha: 2024-06-28 | Estado: Completada

Lo que se hizo:

Definición de reglas MVC, Type Hints, PEP8.
Requisitos: App offline, multi-moneda (UYU, USD, BRL), lógica bancos vs caja física.
Estructura base y src/models/database.py con DatabaseManager.
Entorno virtual (venv) y requirements.txt.
Decisiones de Diseño:

Clase de BD: DatabaseManager.
Columnas tabla usuarios: nombre_usuario, contrasena, es_admin, activo.
Moneda principal: UYU (Pesos Uruguayos).
SESIÓN 2: Login y Estructura MVC
Fecha: 2024-06-28 | Estado: Completada

Lo que se hizo:

src/utils/auth.py (Hash SHA-256).
src/controllers/user_controller.py (Lógica de login, admin por defecto admin/admin123).
src/views/login_view.py (Pantalla Login como CTkFrame).
src/main.py inicial.
Lecciones aprendidas:

Todo el código va dentro de la carpeta src/.
Para ejecutar: cd src y luego python main.py.
SESIÓN 3: Dashboard, Portal y Movimientos
Fecha: 2024-07-01 | Estado: Completada

Lo que se hizo (Continuación de trabajo de otra IA):

Se estabilizó la arquitectura de Frame Swapping (Router en main.py).
Task 7: src/views/dashboard_view.py — Sidebar con navegación (Movimientos / Resumen).
Task 8: src/views/movimientos_view.py — Formulario de registro y tabla scrolleable.
Task 9: src/views/resumen_view.py — Tarjetas de UYU/USD/BRL, Efectivo vs Banco.
Correcciones importantes realizadas en esta sesión:

Se corrigió movimiento_controller.py: Se añadió lógica para leer fondo_inicial_pesos de la tabla cajas y sumarlo a efectivo_uyu en el resumen.
Se corrigió movimientos_view.py: Se eliminó el envío de es_banco al controlador (ya lo calcula él).
Se corrigió error de UI: CTkFont no usa italic=True, se eliminó el parámetro.
LECCIÓN: Si al modificar un archivo los cambios no se reflejan, borrar la caché: rm -rf src/views/__pycache__.
Próximos pasos (Sesión 4):

Implementar Cierre de Caja.
Generación de Reportes (PDF/WhatsApp).
Gestión de usuarios (Altas/Bajas).

SESIÓN 4: Cierre de Caja, Correcciones Críticas y EstabilizaciónFecha: 2024-07-02 | Estado: Completada

Lo que se hizo:

Task 10: Implementado cerrar_caja() en caja_controller.py. Actualiza estado, fechas, usuario que cierra y saldo final en la BD.
Task 11: Creado cierre_caja_view.py. Muestra resumen de monedas (UYU/USD/BRL), efectivo vs banco, campo de conteo físico y cálculo de diferencia en tiempo real (Falta/Sobra/Cuadra).
Task 12: Integrado botón "Cerrar Caja" en el sidebar de dashboard_view.py y navegación en main.py.
Feature: Implementado "Fondo inicial sugerido". Al abrir una nueva caja, se pre-carga automáticamente con el saldo final de la última caja cerrada (obtener_ultimo_saldo_cerrado en controlador, lógica en portal_view.py).
Correcciones Críticas realizadas en esta sesión:

FIX BD Duplicada: Se descubrió que al ejecutar cd src && python main.py, SQLite creaba una base de datos vacía dentro de src/ y no usaba la real del proyecto. Se solucionó en main.py usando os.path para apuntar siempre a la raíz del proyecto.
FIX Renderizado Python 3.14: El usuario utiliza Python 3.14 (Alpha), el cual tiene un bug conocido donde CustomTkinter colapsa los nuevos frames a tamaño 0x0 si se usa pack. Se solucionó cambiando el layout interno de cierre_caja_view.py a grid.
FIX Orden de creación: Se corrigió un error en portal_view.py donde se intentaba validar un campo antes de que el widget existiera en la memoria.
Lecciones aprendidas:

LECCIÓN DE ORO DE RUTAS: Nunca confiar en rutas relativas para la BD si el punto de entrada cambia de directorio. Siempre calcular BASE_DIR con os.path.dirname(os.path.abspath(__file__)).
LECCIÓN DE CTk: Si un frame se instancia sin errores pero no se ve, es un problema de layout. Cambiar pack por grid suele ser el parche definitivo.
ADVERTENCIA: Python 3.14 es inestable para UI de escritorio. Se recomienda encarecidamente usar Python 3.12.x para entorno de producción.
Estado actual del sistema:

Login: Funcional.
Apertura de Caja: Funcional (con fondo sugerido).
Registro de Movimientos: Funcional.
Resumen del Día: Funcional.
Cierre de Caja: Funcional (con conteo físico).
Ciclo completo: Probado y validado.
Próximos pasos (Sesión 5):

Generación de Reportes (PDF/WhatsApp).
Gestión de usuarios (Altas/Bajas) para el administrador.


SESIÓN 5: Gestión de Usuarios y Migración a Python 3.12Fecha: 2024-07-03 | Estado: Completada

Lo que se hizo:

Task 13: Implementado toggle_user_status() en user_controller.py. Alterna estado activo/inactivo con protección para no dejar el sistema sin admin.
Task 14: Creado usuarios_view.py. Pantalla con formulario de alta de usuarios y tabla scrolleable con acciones por usuario.
Task 15: Modificado dashboard_view.py. Se agregó botón "👥 Usuarios" en el sidebar, visible solo si es_admin == 1.
Task 16: Actualizado main.py para inyectar user_controller en el dashboard.
Decisiones de Diseño:

Se decidió posponer la generación de PDF para la próxima sesión y optar por generar Excel (usando openpyxl), por mayor estabilidad y para que el usuario lo exporte a PDF fuera del programa.
Se intentó migrar el entorno virtual a Python 3.12 para evitar los bugs de renderizado de CustomTkinter en Python 3.14, pero el entorno siguió anclado a la 3.14. El código es 100% compatible con 3.12 para cuando se realice la migración definitiva.
Lecciones aprendidas:

LECCIÓN: Al usar cat >> archivo.py << 'EOF' en Git Bash, se pueden agregar métodos al final de un archivo sin riesgo de romper la indentación del archivo original. Útil para cambios pequeños.
RECORDATORIO: El archivo nul de Windows sigue existiendo en el proyecto. Hacer git add . falla. Se debe hacer git add archivo por archivo.
Estado actual del sistema:

Login: Funcional.
Apertura de Caja: Funcional.
Registro de Movimientos: Funcional.
Resumen del Día: Funcional.
Cierre de Caja: Funcional.
Gestión de Usuarios: Funcional (Solo Admin).
Próximos pasos (Sesión 6):

Generación de Reportes en formato Excel (Instalación de openpyxl). 


SESIÓN 8 y 9 (Push combinado): Módulo de Empleados, Reportes Avanzados y Liquidación
Fecha: 2024-07-0X | Estado: Completada y Sincronizada (GitHub)

Lo que se hizo:

[REVISIÓN Y CIERRE DE SESIÓN 8]
- Revisión general de la Sesión 8 a medio terminar.
- Task 17-22: Verificadas y validadas (Diccionarios, DB, Controlador de empleados, Vista de empleados, Selector dinámico en movimientos).
- Task 23: Agregados los métodos faltantes `obtener_adelantos_por_rango` y `obtener_viaticos_por_rango` en movimiento_controller.py.
- Task 24: Creada e inyectada la 4ta pestaña "Adelantos y Viáticos" en historial_view.py. Corregida la inyección de movimiento_controller en dashboard_view.py.
- MEJORA UX: Reemplazada la selección de fecha manual (YYYY-MM-DD) por Calendarios Emergentes (tkcalendar + Toplevel) en el historial de Adelantos/Viáticos para evitar errores de tipeo del usuario.
- MEJORA DE NEGOCIO: El reporte de Adelantos ahora muestra los movimientos **agrupados por colaborador** con subtotales individuales por persona, en lugar de una lista plana.
- MEJORA UX: Agregado botón "Exportar Adelantos a Excel" (con diseño profesional: colores por sección, subtotales, bordes).
- FIX: Corregido error de layout `_tkinter.TclError: cannot use geometry manager pack inside...` al cambiar el mensaje de confirmación de Excel de `.pack()` a `.grid()`.

[SESIÓN 9 COMPLETA]
- Task 25: Creado módulo de Liquidación de Sueldos (liquidacion_view.py). 
  - Lógica en empleado_controller para calcular: Sueldo Base - Adelantos del periodo = Pago Final.
  - Tabla resumen con totales generales.
  - Exportación a Excel de la liquidación.
  - Integración en el sidebar del dashboard (Solo Admin).
- Task 26: Mejorada la pestaña Mensual en historial_view.py.
  - Nuevo método en movimiento_controller para extraer adelantos y viáticos agrupados por semana del mes.
  - Gráfico ahora es doble (Subplots): Arriba sigue la línea de Ingresos/Egresos de caja. Abajo se agregaron barras comparativas (Adelantos vs Viáticos por semana).

Lecciones aprendidas:
REGLA DE WINDOWS/GIT: En Windows, "nul" es un nombre de archivo reservado del sistema. Si se crea un archivo llamado así (ej. por un error de redirección en la terminal), Git fallará fatalmente al hacer `git add .`. Solución: `rm -f ./nul` antes de agregar.
REGLA DE CTk + CALENDARIOS: Los widgets nativos de Tkinter (como DateEntry de tkcalendar) suelen ser invisibles o romper el diseño oscuro de CustomTkinter. La mejor solución es mantener el CTkEntry y abrir un Toplevel (ventana emergente) con el Calendar al hacer clic.
REGLA DE LAYOUT FIJA: Si el contenedor base usa `.grid()`, cualquier cosa que se agregue dinámicamente después (como un label de "Operación exitosa") debe usar `.grid()` obligatoriamente, o la aplicación crashea.

Estado actual del sistema:
Login: Funcional.
Apertura de Caja: Funcional.
Registro de Movimientos: Funcional (Con selector inteligente de empleados).
Resumen del Día: Funcional.
Cierre de Caja: Funcional.
Gestión de Usuarios: Funcional (Solo Admin).
Gestión de Empleados: Funcional (Solo Admin).
Historial Diario/Semanal/Mensual: Funcional (Con gráfica doble de Caja y Gastos operativos).
Reportes de Adelantos y Viáticos: Funcional (Agrupados por empleado, con Calendario y Excel).
Liquidación de Sueldos Semanal: Funcional (Solo Admin, Cálculo automático y Excel).
Exportación a Excel: Funcional (Múltiples módulos).
Git: Sincronizado y subido a GitHub.

Próximos pasos (Sesión 10):
- Pulir detalles visuales (Ej: compactar tabla de movimientos del día).
- Agregar validaciones de seguridad (Ej: Bloquear cierre de caja si hay inconsistencias graves).
- Módulo de Proveedores o Cuentas por pagar (si aplica para el taller).
SESIÓN 10: Mejoras Visuales, Branding y Alertas de Negocio (Parcial)
Fecha: 2024-07-04 | Estado: Completada (Parcial - Pendiente Módulo Proveedores)

Lo que se hizo:

- Mejora de Branding: Integrado el logo real del negocio (`Logo_La_Lucha.png`) en la pantalla de Login, reemplazando el emoji genérico. Se almacenó en `src/assets/`.
- Leyenda de Desarrollador: Agregado "Desarrollado por MazDesign" en dos lugares:
  - Login: Flotando en el fondo azul marino (esquina inferior).
  - Dashboard: Flotando en la esquina inferior derecha usando `.place()`.
- Alerta de Caja Única Diaria: Implementado `existe_caja_cerrada_hoy()` en `caja_controller.py`. Si el usuario intenta abrir una caja y ya hubo una cerrada ese día, se muestra una advertencia roja en `portal_view.py`.
- Optimización de UI: Reducido el padding vertical del contenedor del logo en el login para una visualización más compacta.

Lecciones aprendidas:

- LECCIÓN CTk OVERLAYS: Nunca usar `ctk.CTkLabel` con `.place()` flotando sobre la interfaz si debajo hay botones. CustomTkinter crea cajas invisibles que interceptan y "roban" el evento de clic. Solución: Usar `tk.Label` nativo de la librería estándar de Python para textos overlay que no requieren interacción.

Estado actual del sistema:
- Login: Funcional (Con logo real y leyenda MazDesign).
- Apertura de Caja: Funcional (Con advertencia de caja única diaria).
- Resto de módulos: Funcionales (Con leyenda MazDesign en Dashboard).
- Módulo de Proveedores: Pendiente.

Próximos pasos (Sesión 11):
- Colocar logo en el Sidebar del Dashboard.
- Módulo de Proveedores / Cuentas por Pagar (Tabla facturas, campos: proveedor, fecha compra, monto, IVA, fecha pago).



SESIÓN 11: Mejoras Visuales, Módulo Proveedores y UX de Calendarios
Fecha: 2024-07-05 | Estado: Completada

Lo que se hizo:

- Task 27: Mejora de UI en Login. Reducido el padding excesivo del logo (de 120px a 110px, padding vertical a 0) para subir el botón de inicio de sesión. Movida la leyenda "Desarrollado por MazDesign" al borde inferior absoluto (rely=1.0) para que quede completamente en el fondo azul oscuro.
- Task 28: FIX Logo Dashboard. Corregido bug crítico donde el logo no aparecía. 
  1) La ruta calculaba mal (apuntaba a src/views/assets/ en lugar de src/assets/). Se corrigió con os.path.abspath y "..".
  2) Error de CustomTkinter: CTkImage exigía un objeto PIL.Image.Image, no un string de ruta. Se agregó Image.open() antes de instanciar.
- Task 29: FIX Footer Dashboard. Aplicada misma corrección que en Login (rely=1.0).
- Task 30: Módulo Proveedores - Multi-moneda. Agregado soporte para UYU y USD en las facturas. Nueva columna 'moneda' en BD con migración automática (ALTER TABLE). ComboBox en formulario, símbolo dinámico ($/U$S) en el cálculo de IVA en tiempo real, separación de totales en tarjetas resumen (Total UYU / Total USD) y exportación a Excel.
- Task 31: Historial - Calendarios Globales. Implementado el selector de calendario emergente (tkcalendar + Toplevel) en las pestañas Diario, Semanal y Mensual. En Mensual, se reemplazaron los dos campos manuales (Año/Mes) por un solo campo de fecha con calendario que extrae año y mes automáticamente, unificando la experiencia de usuario.

Lecciones aprendidas:

- LECCIÓN CTk IMAGE: En versiones recientes/alphas de CustomTkinter, CTkImage lanza ValueError si se le pasa un string de ruta. Siempre hacer Image.open(path) primero y pasar el objeto PIL.
- LECCIÓN RUTAS DESDE VISTAS: Al calcular rutas desde dentro de src/views/, hay que usar os.path.join(..., "..", "assets") para salir de la carpeta views. Usar os.path.abspath() para evitar ambigüedades del sistema operativo.
- LECCIÓN PLACE RELY: Para que un label flotante (overlay) quede exactamente en el borde inferior de un widget, usar rely=1.0 con anchor="s", no rely=0.98 o 0.99.

Estado actual del sistema:
- Login: Funcional (Logo optimizado, footer en borde inferior).
- Apertura de Caja: Funcional (Con advertencia de caja única diaria).
- Registro de Movimientos: Funcional (Con selector inteligente de empleados).
- Resumen del Día: Funcional.
- Cierre de Caja: Funcional (Con conteo físico).
- Gestión de Usuarios: Funcional (Solo Admin).
- Gestión de Empleados: Funcional (Solo Admin).
- Historial Diario/Semanal/Mensual: Funcional (Con calendario emergente en todas las pestañas).
- Reportes de Adelantos y Viáticos: Funcional (Agrupados por empleado, con Calendario y Excel).
- Liquidación de Sueldos Semanal: Funcional (Solo Admin, Cálculo automático y Excel).
- Gestión de Proveedores: Funcional (Solo Admin, Altas/Bajas, Facturas UYU/USD, Pago/Cancelación, Excel).
- Exportación a Excel: Funcional (Múltiples módulos).
- Git: Sincronizado y subido a GitHub.

Próximos pasos (Sesión 12):
- Validación de seguridad (Ej: Bloquear cierre de caja si hay inconsistencias graves).
- Pulir detalles visuales generales.
- Módulo de Backup de BD o configuraciones del sistema (si aplica).