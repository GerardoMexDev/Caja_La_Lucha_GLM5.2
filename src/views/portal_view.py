"""
Frame de apertura de jornada.
Se muestra cuando no hay caja activa al iniciar sesión.
"""

import customtkinter as ctk
from datetime import datetime
from typing import Dict, Any, Callable

from controllers.caja_controller import CajaController
from utils.constants import (
    COLOR_ACCENT, COLOR_BG, COLOR_CARD, COLOR_TEXT,
    COLOR_ERROR, COLOR_SUCCESS
)

_DIAS = {
    'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado',
    'Sunday': 'Domingo',
}


class PortalFrame(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        usuario: Dict[str, Any],
        caja_controller: CajaController,
        on_caja_abierta: Callable[[Dict[str, Any]], None],
    ) -> None:
        super().__init__(parent, fg_color=COLOR_BG)
        self.usuario = usuario
        self.caja_controller = caja_controller
        self.on_caja_abierta = on_caja_abierta
        self._create_widgets()

    def _create_widgets(self) -> None:
        card = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=20)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.88)

        ctk.CTkLabel(card, text="💰", font=ctk.CTkFont(size=50), text_color=COLOR_ACCENT).pack(pady=(30, 5))

        ctk.CTkLabel(
            card, text="INICIO DE JORNADA",
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack()

        now = datetime.now()
        dia_en = now.strftime("%A")
        dia_es = _DIAS.get(dia_en, dia_en)
        fecha_str = f"{dia_es} {now.strftime('%d/%m/%Y')}"
        ctk.CTkLabel(
            card,
            text=f"Hola, {self.usuario['nombre_usuario']} 👋\n{fecha_str}",
            font=ctk.CTkFont(size=14),
            text_color="#bdc3c7",
            justify="center",
        ).pack(pady=(10, 15))

        ctk.CTkFrame(card, height=2, fg_color="#2c3e50").pack(fill="x", padx=40, pady=(0, 20))

        ctk.CTkLabel(
            card, text="Fondo Inicial de Caja (UYU)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#bdc3c7",
        ).pack()

        self.fondo_entry = ctk.CTkEntry(
            card,
            height=50,
            placeholder_text="$ 0.00",
            font=ctk.CTkFont(size=18),
            corner_radius=10,
            border_width=2,
            border_color="#34495e",
            fg_color="#1c2833",
            text_color=COLOR_TEXT,
            justify="center",
        )
        self.fondo_entry.pack(fill="x", padx=60, pady=(8, 0))
        self.fondo_entry.bind("<KeyRelease>", self._validate_fondo)

        self.open_btn = ctk.CTkButton(
            card,
            text="ABRIR CAJA Y COMENZAR",
            height=50,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=12,
            fg_color="#34495e",
            state="normal",
            command=self._abrir_caja,
        )
        self.open_btn.pack(fill="x", padx=60, pady=(20, 0))

        self.status_label = ctk.CTkLabel(
            card, text="",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT,
        )
        self.status_label.pack(pady=(10, 0))

    def _validate_fondo(self, event=None) -> None:
        value = self.fondo_entry.get().strip().replace(",", ".")
        try:
            fondo = float(value)
            if fondo >= 0:
                self.open_btn.configure(state="normal", fg_color=COLOR_SUCCESS)
                return
        except ValueError:
            pass
        self.open_btn.configure(state="disabled", fg_color="#2c3e50")

    def _abrir_caja(self) -> None:
        value = self.fondo_entry.get().strip().replace(",", ".")
        try:
            fondo = float(value)
        except ValueError:
            self.status_label.configure(text="Ingrese un monto válido.", text_color=COLOR_ERROR)
            return

        self.open_btn.configure(state="disabled", text="Abriendo...")
        caja = self.caja_controller.abrir_caja(self.usuario['id'], fondo)
        self.after(300, lambda: self.on_caja_abierta(caja))
