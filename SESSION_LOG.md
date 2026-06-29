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

Próximos pasos (Sesión 3):
Crear la vista principal (Dashboard) con sidebar de navegación.
Implementar apertura de caja (ingresar fondo inicial).
Agregar registro de movimientos (ingresos/egresos).