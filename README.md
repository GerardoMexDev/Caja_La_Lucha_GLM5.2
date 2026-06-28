💰 Sistema de Caja - La Lucha
Sistema de escritorio offline para el control de flujo de fondos (Caja) de la gomería "La Lucha". Desarrollado en Python con arquitectura MVC estricta.

🛠️ Tecnologías
Lenguaje: Python 3.10+
Interfaz Gráfica: CustomTkinter
Base de Datos: SQLite3 (Local, offline)
Exportación: ReportLab (PDFs) - Por instalar en futuras sesiones
📂 Estructura del Proyecto
SistemaCajaLaLucha/├── models/          # Lógica de base de datos (SQLite)├── views/           # Interfaces gráficas (CustomTkinter)├── controllers/     # Conexión entre Vistas y Models (Lógica de negocio)├── utils/           # Funciones auxiliares (formatos, validaciones)├── main.py          # Punto de entrada de la aplicación├── database.db      # (Se genera automáticamente al ejecutar)├── SESSION_LOG.md   # Bitácora de desarrollo└── requirements.txt # Dependencias del proyecto
🚀 Cómo instalar y ejecutar (Entorno Local)
Clonar o copiar el proyecto en la PC.
Crear un entorno virtual (Recomendado):
bash

python -m venv venv
Activar el entorno virtual:
Windows: venv\Scripts\activate
Mac/Linux: source venv/bin/activate
Instalar dependencias:
bash

pip install -r requirements.txt
Ejecutar la aplicación:
bash

python main.py
📜 Reglas de Desarrollo
Ver documento interno de estándares. (Código limpio, Type hints, Docstrings, separación MVC).

text


---

### Tu ritual para la próxima vez que me abras
Cuando abras un chat nuevo y quieras continuar, tu primer mensaje será: 
*"Hola, vamos a trabajar en el proyecto La Lucha. Lee esto:"* *(y me pegas el contenido del `SESSION_LOG.md`)*. Yo leeré eso y sabré exactamente en qué línea de código nos quedamos.

### 🎁 Extra: Inicialicemos Git en tu PC
Abre tu terminal (o consola/PowerShell) en la carpeta `SistemaCajaLaLucha` y ejecuta estos comandos para dejar el proyecto listo desde el día 1:

```bash
git init
git add .
git commit -m "Sesion 1: Definicion de arquitectura, requisitos y creacion de base de datos inicial"
(Si ya tienes un repositorio en GitHub creado, conéctalo con git remote add origin <tu-url> y haz git push -u origin main).