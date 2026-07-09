"""
Vista de Login.
Pantalla principal de autenticación del sistema.
"""

import os
import customtkinter as ctk
from PIL import Image
from typing import Optional, Callable, Dict, Any
from controllers.user_controller import UserController


class LoginFrame(ctk.CTkFrame):
    """
    Ventana de login del sistema Caja La Lucha.

    Attributes:
        user_controller: Controlador de usuarios para autenticación.
        on_login_success: Callback a ejecutar al login exitoso.
        _login_attempts: Contador de intentos fallidos.
    """

    # Configuración de colores
    COLOR_PRIMARY = "#1a5276"
    COLOR_SECONDARY = "#2980b9"
    COLOR_ACCENT = "#e67e22"
    COLOR_BG = "#0f1923"
    COLOR_CARD = "#1a2332"
    COLOR_TEXT = "#ecf0f1"
    COLOR_ERROR = "#e74c3c"
    COLOR_SUCCESS = "#27ae60"

    MAX_LOGIN_ATTEMPTS = 5

    def __init__(
        self,
        parent,
        user_controller: UserController,
        on_login_success: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Inicializa el frame de login.

        Args:
            parent: Parent widget.
            user_controller: Controlador de usuarios.
            on_login_success: Función callback para login exitoso.
        """
        super().__init__(parent, fg_color=self.COLOR_BG)

        self.user_controller = user_controller
        self.on_login_success = on_login_success
        self._login_attempts = 0
        self._show_password = False

        self._create_widgets()
        self._bind_events()

    def _create_widgets(self) -> None:
        """Crea todos los widgets de la interfaz."""
        # Contenedor principal con padding
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=self.COLOR_CARD,
            corner_radius=20
        )
        self.main_frame.pack(
            padx=30,
            pady=30,
            fill="both",
            expand=True
        )

        # === LOGO/TÍTULO ===
        self._create_header()

        # === CAMPOS DE LOGIN ===
        self._create_login_fields()

        # === BOTÓN LOGIN ===
        self._create_login_button()

        # === MENSAJE DE ESTADO ===
        self._create_status_message()

        # === PIE DE PÁGINA ===
        self._create_footer()

    def _create_header(self) -> None:
        """Crea el encabezado con logo y título."""
        # Frame para el logo (círculo con ícono)
        logo_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        logo_frame.pack(pady=(7, 2))

        # Cargar imagen del logo desde assets
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.abspath(os.path.join(current_dir, "..", "assets", "Logo_La_Lucha.png"))
        
        logo_image = ctk.CTkImage(
            light_image=Image.open(logo_path),
            size=(120, 120)
        )

        self.logo_label = ctk.CTkLabel(
            logo_frame,
            image=logo_image,
            text=""
        )
        self.logo_label.pack()

        # Título principal
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="LA LUCHA - CAJA",
            font=ctk.CTkFont(
                family="Helvetica",
                size=28,
                weight="bold"
            ),
            text_color=self.COLOR_TEXT
        )
        self.title_label.pack(pady=(5, 0))

        # Subtítulo
        self.subtitle_label = ctk.CTkLabel(
            self.main_frame,
            text="Sistema de Gestión de Caja",
            font=ctk.CTkFont(
                family="Helvetica",
                size=14
            ),
            text_color="#7f8c8d"
        )
        self.subtitle_label.pack(pady=(0, 25))

        # Línea separadora
        separator = ctk.CTkFrame(
            self.main_frame,
            height=2,
            fg_color="#2c3e50"
        )
        separator.pack(fill="x", padx=40, pady=(0, 25))

    def _create_login_fields(self) -> None:
        """Crea los campos de usuario y contraseña."""
        # Frame para campos
        fields_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        fields_frame.pack(fill="x", padx=40)

        # Label y Entry para usuario
        self.username_label = ctk.CTkLabel(
            fields_frame,
            text="Usuario",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#bdc3c7",
            anchor="w"
        )
        self.username_label.pack(fill="x", pady=(0, 5))

        self.username_entry = ctk.CTkEntry(
            fields_frame,
            height=45,
            placeholder_text="Ingrese su usuario",
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            border_width=2,
            border_color="#34495e",
            fg_color="#1c2833",
            text_color=self.COLOR_TEXT,
            placeholder_text_color="#5d6d7e"
        )
        self.username_entry.pack(fill="x", pady=(0, 20))

        # Label y Entry para contraseña
        self.password_label = ctk.CTkLabel(
            fields_frame,
            text="Contraseña",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#bdc3c7",
            anchor="w"
        )
        self.password_label.pack(fill="x", pady=(0, 5))

        # Frame para contraseña y botón mostrar/ocultar
        password_frame = ctk.CTkFrame(
            fields_frame,
            fg_color="transparent"
        )
        password_frame.pack(fill="x")

        self.password_entry = ctk.CTkEntry(
            password_frame,
            height=45,
            placeholder_text="Ingrese su contraseña",
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            border_width=2,
            border_color="#34495e",
            fg_color="#1c2833",
            text_color=self.COLOR_TEXT,
            placeholder_text_color="#5d6d7e",
            show="•"
        )
        self.password_entry.pack(side="left", fill="x", expand=True)

        # Botón mostrar/ocultar contraseña
        self.toggle_password_btn = ctk.CTkButton(
            password_frame,
            text="👁",
            width=45,
            height=45,
            corner_radius=10,
            fg_color="#1c2833",
            border_width=2,
            border_color="#34495e",
            hover_color="#273746",
            command=self._toggle_password_visibility,
            font=ctk.CTkFont(size=16)
        )
        self.toggle_password_btn.pack(side="right", padx=(10, 0))

    def _create_login_button(self) -> None:
        """Crea el botón de inicio de sesión."""
        self.login_button = ctk.CTkButton(
            self.main_frame,
            text="INICIAR SESIÓN",
            height=50,
            font=ctk.CTkFont(
                family="Helvetica",
                size=16,
                weight="bold"
            ),
            corner_radius=12,
            fg_color=self.COLOR_SECONDARY,
            hover_color=self.COLOR_PRIMARY,
            command=self._handle_login
        )
        self.login_button.pack(
            fill="x",
            padx=40,
            pady=(25, 0)
        )

    def _create_status_message(self) -> None:
        """Crea el label para mensajes de estado."""
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.COLOR_TEXT,
            wraplength=350
        )
        self.status_label.pack(pady=(15, 0))

    def _create_footer(self) -> None:
        """Crea el pie de página con información del sistema."""
        import tkinter as tk
        # Se usa tk.Label nativo para que NO robe los clicks del botón de login
        tk.Label(
            self,
            text="Desarrollado por MazDesign | v1.0.0",
            bg=self.COLOR_BG,
            fg="#5d6d7e",
            font=("Helvetica", 11)
        ).place(relx=0.5, rely=0.98, anchor="s")
    def _bind_events(self) -> None:
        """Enlaza eventos de teclado."""
        # Enter en campo usuario pasa a contraseña
        self.username_entry.bind(
            "<Return>",
            lambda e: self.password_entry.focus()
        )
        # Enter en campo contraseña intenta login
        self.password_entry.bind(
            "<Return>",
            lambda e: self._handle_login()
        )

    def _toggle_password_visibility(self) -> None:
        """Alterna la visibilidad de la contraseña."""
        self._show_password = not self._show_password
        if self._show_password:
            self.password_entry.configure(show="")
            self.toggle_password_btn.configure(text="🙈")
        else:
            self.password_entry.configure(show="•")
            self.toggle_password_btn.configure(text="👁")

    def _handle_login(self) -> None:
        """Maneja el intento de login."""
        # Obtener valores
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Validaciones
        if not username:
            self._show_error("Por favor, ingrese su usuario.")
            self.username_entry.focus()
            return

        if not password:
            self._show_error("Por favor, ingrese su contraseña.")
            self.password_entry.focus()
            return

        # Verificar intentos
        if self._login_attempts >= self.MAX_LOGIN_ATTEMPTS:
            self._show_error(
                "Máximo de intentos alcanzado. "
                "El sistema se bloqueará temporalmente."
            )
            self.login_button.configure(state="disabled")
            self.after(30000, self._reset_login_attempts)
            return

        # Deshabilitar botón mientras procesa
        self.login_button.configure(state="disabled", text="VERIFICANDO...")
        self.status_label.configure(text="")

        # Usar after para permitir actualización de UI
        self.after(100, lambda: self._attempt_login(username, password))

    def _attempt_login(self, username: str, password: str) -> None:
        """
        Intenta autenticar al usuario.

        Args:
            username: Nombre de usuario.
            password: Contraseña en texto plano.
        """
        user = self.user_controller.authenticate(username, password)

        if user:
            # Login exitoso
            self._show_success(f"Bienvenido, {user['nombre_usuario']}!")
            self.login_button.configure(
                text="✓ ACCESO CONCEDIDO",
                fg_color=self.COLOR_SUCCESS
            )
            # Esperar un momento y cerrar
            self.after(800, lambda: self.on_login_success(user))
        else:
            # Login fallido
            self._login_attempts += 1
            attempts_left = self.MAX_LOGIN_ATTEMPTS - self._login_attempts

            if attempts_left > 0:
                self._show_error(
                    f"Credenciales incorrectas. "
                    f"Intentos restantes: {attempts_left}"
                )
            else:
                self._show_error("Máximo de intentos alcanzado.")

            self.login_button.configure(
                state="normal",
                text="INICIAR SESIÓN"
            )
            self.password_entry.delete(0, "end")
            self.password_entry.focus()

    def _show_error(self, message: str) -> None:
        """
        Muestra un mensaje de error.

        Args:
            message: Texto del error.
        """
        self.status_label.configure(
            text=message,
            text_color=self.COLOR_ERROR
        )

    def _show_success(self, message: str) -> None:
        """
        Muestra un mensaje de éxito.

        Args:
            message: Texto del éxito.
        """
        self.status_label.configure(
            text=message,
            text_color=self.COLOR_SUCCESS
        )

    def _reset_login_attempts(self) -> None:
        """Resetea el contador de intentos de login."""
        self._login_attempts = 0
        self.login_button.configure(
            state="normal",
            text="INICIAR SESIÓN",
            fg_color=self.COLOR_SECONDARY
        )
        self._show_success("Puede intentar nuevamente.")

    def reset_form(self) -> None:
        """Resetea el formulario de login."""
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.status_label.configure(text="")
        self.username_entry.focus()
        self._login_attempts = 0
        self.login_button.configure(
            state="normal",
            text="INICIAR SESIÓN",
            fg_color=self.COLOR_SECONDARY
        )