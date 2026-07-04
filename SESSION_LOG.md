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