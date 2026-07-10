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
    """

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
        super().__init__(parent, fg_color=self.COLOR_BG)

        self.user_controller = user_controller
        self.on_login_success = on_login_success
        self._login_attempts = 0
        self._show_password = False

        self._create_widgets()
        self._bind_events()

    def _create_widgets(self) -> None:
        # Contenedor principal con padding reducido arriba
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=self.COLOR_CARD,
            corner_radius=20
        )
        self.main_frame.pack(
            padx=30,
            pady=(20, 45),  # Menos arriba, más abajo para dejar espacio al footer
            fill="both",
            expand=True
        )

        self._create_header()
        self._create_login_fields()
        self._create_login_button()
        self._create_status_message()
        self._create_footer()

    def _create_header(self) -> None:
        # Frame para el logo — padding mínimo
        logo_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        logo_frame.pack(pady=(0, 0))  # Sin padding extra

        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.abspath(os.path.join(current_dir, "..", "assets", "Logo_La_Lucha.png"))

        logo_image = ctk.CTkImage(
            light_image=Image.open(logo_path),
            size=(110, 110)  # Ligeramente más chico
        )

        self.logo_label = ctk.CTkLabel(
            logo_frame,
            image=logo_image,
            text=""
        )
        self.logo_label.pack()

        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="LA LUCHA - CAJA",
            font=ctk.CTkFont(
                family="Helvetica",
                size=26,
                weight="bold"
            ),
            text_color=self.COLOR_TEXT
        )
        self.title_label.pack(pady=(2, 0))

        self.subtitle_label = ctk.CTkLabel(
            self.main_frame,
            text="Sistema de Gestión de Caja",
            font=ctk.CTkFont(
                family="Helvetica",
                size=13
            ),
            text_color="#7f8c8d"
        )
        self.subtitle_label.pack(pady=(0, 12))

        separator = ctk.CTkFrame(
            self.main_frame,
            height=2,
            fg_color="#2c3e50"
        )
        separator.pack(fill="x", padx=40, pady=(0, 15))

    def _create_login_fields(self) -> None:
        fields_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        fields_frame.pack(fill="x", padx=40)

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
        self.username_entry.pack(fill="x", pady=(0, 15))

        self.password_label = ctk.CTkLabel(
            fields_frame,
            text="Contraseña",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#bdc3c7",
            anchor="w"
        )
        self.password_label.pack(fill="x", pady=(0, 5))

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
            pady=(18, 0)
        )

    def _create_status_message(self) -> None:
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.COLOR_TEXT,
            wraplength=350
        )
        self.status_label.pack(pady=(12, 0))

    def _create_footer(self) -> None:
        import tkinter as tk
        # rely=1.0 lo pone en el borde inferior absoluto (fondo azul)
        tk.Label(
            self,
            text="Desarrollado por MazDesign | v1.0.0",
            bg=self.COLOR_BG,
            fg="#5d6d7e",
            font=("Helvetica", 11)
        ).place(relx=0.5, rely=1.0, anchor="s")

    def _bind_events(self) -> None:
        self.username_entry.bind(
            "<Return>",
            lambda e: self.password_entry.focus()
        )
        self.password_entry.bind(
            "<Return>",
            lambda e: self._handle_login()
        )

    def _toggle_password_visibility(self) -> None:
        self._show_password = not self._show_password
        if self._show_password:
            self.password_entry.configure(show="")
            self.toggle_password_btn.configure(text="🙈")
        else:
            self.password_entry.configure(show="•")
            self.toggle_password_btn.configure(text="👁")

    def _handle_login(self) -> None:
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username:
            self._show_error("Por favor, ingrese su usuario.")
            self.username_entry.focus()
            return

        if not password:
            self._show_error("Por favor, ingrese su contraseña.")
            self.password_entry.focus()
            return

        if self._login_attempts >= self.MAX_LOGIN_ATTEMPTS:
            self._show_error(
                "Máximo de intentos alcanzado. "
                "El sistema se bloqueará temporalmente."
            )
            self.login_button.configure(state="disabled")
            self.after(30000, self._reset_login_attempts)
            return

        self.login_button.configure(state="disabled", text="VERIFICANDO...")
        self.status_label.configure(text="")

        self.after(100, lambda: self._attempt_login(username, password))

    def _attempt_login(self, username: str, password: str) -> None:
        user = self.user_controller.authenticate(username, password)

        if user:
            self._show_success(f"Bienvenido, {user['nombre_usuario']}!")
            self.login_button.configure(
                text="✓ ACCESO CONCEDIDO",
                fg_color=self.COLOR_SUCCESS
            )
            self.after(800, lambda: self.on_login_success(user))
        else:
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
        self.status_label.configure(
            text=message,
            text_color=self.COLOR_ERROR
        )

    def _show_success(self, message: str) -> None:
        self.status_label.configure(
            text=message,
            text_color=self.COLOR_SUCCESS
        )

    def _reset_login_attempts(self) -> None:
        self._login_attempts = 0
        self.login_button.configure(
            state="normal",
            text="INICIAR SESIÓN",
            fg_color=self.COLOR_SECONDARY
        )
        self._show_success("Puede intentar nuevamente.")

    def reset_form(self) -> None:
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
