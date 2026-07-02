⚠️ REGLA DE ORO - LEER SIEMPRIMO PRIMERO
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