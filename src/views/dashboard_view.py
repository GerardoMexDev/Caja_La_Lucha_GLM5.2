"""
Frame principal del Dashboard.
Contiene el sidebar de navegación y el área de contenido dinámico.
"""

import customtkinter as ctk
from typing import Dict, Any, Callable, Optional

from controllers.movimiento_controller import MovimientoController
from utils.constants import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT, COLOR_BG,
    COLOR_CARD, COLOR_TEXT, COLOR_ERROR
)


class DashboardFrame(ctk.CTkFrame):
    """Contenedor principal con sidebar y área de contenido."""

    def __init__(
        self,
        parent,
        usuario: Dict[str, Any],
        caja: Dict[str, Any],
        movimiento_controller: MovimientoController,
        on_logout: Callable[[], None],
    ) -> None:
        super().__init__(parent, fg_color=COLOR_BG)
        self.usuario = usuario
        self.caja = caja
        self.movimiento_controller = movimiento_controller
        self.on_logout = on_logout
        
        self._content_frame: Optional[ctk.CTkFrame] = None

        self._create_widgets()
        self._show_movimientos()  # Vista por defecto al entrar

    def _create_widgets(self) -> None:
        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(
            self, width=250, corner_radius=0, fg_color=COLOR_CARD
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Header Sidebar
        ctk.CTkLabel(
            self.sidebar, text="💰 LA LUCHA",
            font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_ACCENT
        ).pack(pady=(30, 5))

        ctk.CTkLabel(
            self.sidebar, text=f"Caja #{self.caja['id']} Abierta",
            font=ctk.CTkFont(size=12), text_color="#bdc3c7"
        ).pack(pady=(0, 20))

        # Separador
        ctk.CTkFrame(self.sidebar, height=2, fg_color="#2c3e50").pack(fill="x", padx=20, pady=10)

        # Botones de navegación
        self.btn_movimientos = ctk.CTkButton(
            self.sidebar, text="📝 Movimientos", height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY,
            corner_radius=10, command=self._show_movimientos
        )
        self.btn_movimientos.pack(fill="x", padx=20, pady=(20, 10))

        self.btn_resumen = ctk.CTkButton(
            self.sidebar, text="📊 Resumen del Día", height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent", text_color=COLOR_TEXT,
            border_width=2, border_color="#34495e", hover_color="#1c2833",
            corner_radius=10, command=self._show_resumen
        )
        self.btn_resumen.pack(fill="x", padx=20, pady=10)

        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="both", expand=True)

        # Info usuario y logout
        ctk.CTkLabel(
            self.sidebar, text=f"👤 {self.usuario['nombre_usuario']}",
            font=ctk.CTkFont(size=13), text_color="#bdc3c7"
        ).pack(pady=(0, 10))

        self.btn_logout = ctk.CTkButton(
            self.sidebar, text="🚪 Cerrar Sesión", height=40,
            font=ctk.CTkFont(size=13),
            fg_color=COLOR_ERROR, hover_color="#c0392b",
            corner_radius=10, command=self.on_logout
        )
        self.btn_logout.pack(fill="x", padx=20, pady=(0, 30))

        # --- ÁREA DE CONTENIDO ---
        self.content_area = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0)
        self.content_area.pack(side="right", fill="both", expand=True)

    def _clear_content(self) -> None:
        if self._content_frame:
            self._content_frame.destroy()
            self._content_frame = None

    def _reset_sidebar_buttons(self) -> None:
        """Deja los botones del sidebar en su estado por defecto."""
        self.btn_movimientos.configure(fg_color=COLOR_SECONDARY, text_color="white", border_width=0)
        self.btn_resumen.configure(fg_color="transparent", text_color=COLOR_TEXT, border_width=2, border_color="#34495e")

    def _show_movimientos(self) -> None:
        from views.movimientos_view import MovimientosFrame
        self._clear_content()
        self._reset_sidebar_buttons()
        
        # Resaltar botón activo
        self.btn_movimientos.configure(fg_color="transparent", text_color=COLOR_ACCENT, border_width=2, border_color=COLOR_ACCENT)
        
        self._content_frame = MovimientosFrame(
            parent=self.content_area,
            caja=self.caja,
            movimiento_controller=self.movimiento_controller,
            on_movement_added=self._on_movement_added
        )
        self._content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def _show_resumen(self) -> None:
        from views.resumen_view import ResumenFrame
        self._clear_content()
        self._reset_sidebar_buttons()
        
        # Resaltar botón activo
        self.btn_resumen.configure(fg_color="transparent", text_color=COLOR_ACCENT, border_width=2, border_color=COLOR_ACCENT)
        
        self._content_frame = ResumenFrame(
            parent=self.content_area,
            caja=self.caja,
            movimiento_controller=self.movimiento_controller
        )
        self._content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def _on_movement_added(self) -> None:
        """Callback cuando se agrega un movimiento para refrescar la tabla."""
        # Por ahora simplemente re-renderiza la vista. Se puede optimizar después.
        self._show_movimientos()