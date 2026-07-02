SESIÓN 1: Definición de Arquitectura y Setup Inicial
Fecha: 2024-06-28Estado: Completada

⚠️ REGLA DE ORO - LEER SIEMPRE PRIMERO
NO ASUMIR NADA. Antes de escribir cualquier código:

Pedir find . -type f para ver la estructura ACTUAL del proyecto.
Pedir el contenido de los archivos que se van a modificar.
Verificar nombres de clases, funciones, variables y carpetas.
Recién después de verificar TODO, escribir código.
Antes de entregar un codigo revisarlo para detectar fallas

Lo que se hizo:

Se definieron las "Reglas de Buenas Prácticas": Patrón MVC, Type Hints, PEP8, Docstrings, UI/UX profesional.
Se definieron los "Requisitos Funcionales": App offline, multi-moneda (ARS, USD, BRL), lógica de bancos vs caja física, alertas de fondo mínimo, reportes PDF/WhatsApp, edición de cajas pasadas solo con Admin.
Se creó la estructura de carpetas del proyecto (models, views, controllers, utils) dentro de src/.
Se crearon los archivos base: README.md, SESSION_LOG.md, .gitignore.
Se escribió el primer código: src/models/database.py con la clase DatabaseManager y creación de tablas (usuarios, cajas, movimientos).
Se creó y activó el entorno virtual (venv).
Se creó el archivo requirements.txt con customtkinter==5.2.2.
Se hizo el primer commit y push a GitHub.
Decisiones de Diseño Tomadas:

No hay tabla de productos, se ingresa motivo y monto manualmente.
Fondo de caja inicial solo en Pesos (ARS).
Todo método de pago que no sea "Efectivo" se marca con es_banco = 1.
Al cerrar caja, el saldo final en pesos pasará a ser el fondo inicial de la próxima automáticamente.
Cajas pasadas solo se editan con contraseña de Admin.
La clase de BD se llama DatabaseManager (no Database).
Nombres de columnas en tabla usuarios: nombre_usuario, contrasena, es_admin, activo.
SESIÓN 2: Login y Estructura MVC
Fecha: 2024-06-28Estado: Completada

Lo que se hizo:

Se creó src/utils/auth.py con hash SHA-256 y verificación de contraseñas.
Se creó src/controllers/user_controller.py con lógica de autenticación, creación de usuarios y auto-creación de admin por defecto.
Se creó src/views/login_view.py con pantalla de login profesional usando CustomTkinter.
Se creó src/main.py como punto de entrada de la aplicación.
Se instaló customtkinter en el venv.
Se corrigió estructura de carpetas (todo queda dentro de src/).
Login funcional probado con credenciales admin/admin123.
Características del Login implementadas:

Validación de campos vacíos.
Hash de contraseñas con SHA-256.
Protección contra timing attacks (hmac.compare_digest).
Límite de 5 intentos con bloqueo temporal (30 seg).
Botón mostrar/ocultar contraseña.
Navegación con tecla Enter.
Creación automática de admin si no existe.
UI profesional con colores corporativos.
Feedback visual (éxito/error).
Lecciones aprendidas:

Siempre verificar la estructura actual antes de escribir código.
No asumir nombres de clases, archivos o carpetas.
La clase de BD es DatabaseManager, no Database.
Los archivos están dentro de src/, no en la raíz.

SESIÓN 3: Dashboard, Portal de Jornada y Movimientos
Fecha: 2026-07-01 — Estado: EN PROGRESO (Tasks 1-6 completadas, faltan 7-9)

Decisiones de diseño tomadas:

La moneda principal es PESOS URUGUAYOS (UYU), no ARS. Se corrigió el DEFAULT en database.py.
Monedas soportadas: UYU, USD, BRL.
Arquitectura de ventana única con frame swapping (CTk router en main.py). Sin múltiples ventanas CTk.
Flujo post-login: si no hay caja abierta → PortalFrame; si ya hay caja abierta → DashboardFrame directo.
Colores secundarios de UI (#bdc3c7, #2c3e50, #34495e, #1c2833) pueden hardcodearse en las vistas. Los 8 colores de marca van en utils/constants.py.
es_banco se calcula automáticamente: 1 si metodo_pago != 'Efectivo', 0 si Efectivo.
Sidebar minimalista: solo Movimientos y Resumen del Día (sin Cierre de Caja en esta sesión).

Lo que se hizo (Tasks completadas con subagent-driven development):

Task 1: src/utils/constants.py con 8 colores de marca. DB corregida (ARS→UYU). pytest instalado y configurado.
Task 2: src/controllers/caja_controller.py — abrir_caja(), obtener_caja_activa(), calcular_saldo_actual(). 4 tests pasando.
Task 3: src/controllers/movimiento_controller.py — registrar_movimiento(), obtener_movimientos_del_dia(), obtener_resumen_del_dia(). 11 tests pasando (4+7).
Task 4: src/views/login_view.py migrado de LoginView(CTk) a LoginFrame(CTkFrame). Solo 3 cambios mecánicos.
Task 5: src/main.py refactorizado. CajaLaLuchaApp hereda CTk, actúa como router con _show_login(), _show_portal(), _show_dashboard().
Task 6: src/views/portal_view.py — PortalFrame con campo de fondo inicial, validación en tiempo real, botón habilitado solo con float >= 0.

Pendiente para retomar (Sesión 4 o continuación Sesión 3):

Task 7: src/views/dashboard_view.py — DashboardFrame con sidebar (Movimientos / Resumen del Día).
Task 8: src/views/movimientos_view.py — formulario de registro + tabla del día.
Task 9: src/views/resumen_view.py — totales por moneda, efectivo vs banco, últimos movimientos.

Archivos del plan y spec en:
  docs/superpowers/specs/2026-07-01-sesion3-dashboard-design.md
  docs/superpowers/plans/2026-07-01-sesion3-dashboard.md
  .superpowers/sdd/progress.md (ledger de tasks completadas)