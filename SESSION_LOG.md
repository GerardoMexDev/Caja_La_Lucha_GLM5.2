Registro de Sesiones - Sistema Caja La Lucha
Este archivo sirve como memoria para la IA y el desarrollador. Se debe leer al inicio de cada nueva sesión de chat.

SESIÓN 1: Definición de Arquitectura y Negocio
Fecha: [Fecha de hoy]Estado del Proyecto: Inicio (Fase de Diseño y DB)

Lo que se hizo:
Se definieron las "Reglas de Buenas Prácticas" (Documento 1): Patrón MVC, Type Hints, PEP8, Docstrings, UI/UX profesional.
Se definieron los "Requisitos Funcionales" (Documento 2): App de escritorio offline, multi-moneda (ARS, USD, BRL), lógica de bancos vs caja física, roles de usuario, alertas de fondo mínimo, reportes PDF/WhatsApp.
Se diseñó la estructura de carpetas del proyecto (MVC estricto).
Se creó el primer código: models/database.py con la creación de tablas (usuarios, cajas, movimientos).
Decisions de Diseño Tomadas:
No hay tabla de productos, se ingresa motivo y monto manualmente.
Fondo de caja inicial solo en Pesos (ARS).
Todo método de pago que no sea "Efectivo" se marca con es_banco = 1 para separar las cuentas.
Al cerrar caja, el saldo final en pesos pasará a ser el fondo inicial de la próxima automáticamente.
Cajas pasadas solo se editan con contraseña de Admin.
Próximos pasos (Sesión 2):
 Probar la creación de la base de datos localmente.
 Crear el Controlador de Usuarios (controllers/user_controller.py) para el login.
 Crear la primera Vista: Pantalla de Login (views/login_view.py) con CustomTkinter.
 Configurar archivo requirements.txt.