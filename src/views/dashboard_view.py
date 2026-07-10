"""
Frame principal del Dashboard.
Contiene el sidebar de navegación y el área de contenido dinámico.
"""

import os
import customtkinter as ctk
from PIL import Image
from typing import Dict, Any, Callable, Optional

from controllers.movimiento_controller import MovimientoController
from controllers.caja_controller import CajaController
from controllers.user_controller import UserController
from controllers.empleado_controller import EmpleadoController
from controllers.proveedor_controller import ProveedorController
from utils.constants import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT, COLOR_BG,
    COLOR_CARD, COLOR_TEXT, COLOR_ERROR
)

_ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets"))
_LOGO_PATH = os.path.join(_ASSETS_DIR, "Logo_La_Lucha.png")
_LOGO_IMAGE = None
if os.path.exists(_LOGO_PATH):
    _LOGO_PIL = Image.open(_LOGO_PATH)
    _LOGO_IMAGE = ctk.CTkImage(light_image=_LOGO_PIL, dark_image=_LOGO_PIL, size=(60, 60))


class DashboardFrame(ctk.CTkFrame):
    """Contenedor principal con sidebar y área de contenido."""

    def __init__(
        self,
        parent,
        usuario: Dict[str, Any],
        caja: Dict[str, Any],
        movimiento_controller: MovimientoController,
        caja_controller: CajaController,
        user_controller: UserController,
        empleado_controller: EmpleadoController,
        proveedor_controller: ProveedorController,
        on_logout: Callable[[], None],
        on_caja_cerrada: Callable[[], None],
    ) -> None:
        super().__init__(parent, fg_color=COLOR_BG)
        self.usuario = usuario
        self.caja = caja
        self.movimiento_controller = movimiento_controller
        self.caja_controller = caja_controller
        self.user_controller = user_controller
        self.empleado_controller = empleado_controller
        self.proveedor_controller = proveedor_controller
        self.on_logout = on_logout
        self.on_caja_cerrada = on_caja_cerrada

        self._content_frame: Optional[ctk.CTkFrame] = None

        self._create_widgets()
        self._show_movimientos()

    def _create_widgets(self) -> None:
        self.sidebar = ctk.CTkFrame(
            self, width=250, corner_radius=0, fg_color=COLOR_CARD
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        if _LOGO_IMAGE:
            ctk.CTkLabel(self.sidebar, image=_LOGO_IMAGE, text="").pack(pady=(20, 0))
        ctk.CTkLabel(
            self.sidebar, text="LA LUCHA",
            font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_ACCENT
        ).pack(pady=(4, 2))

        ctk.CTkLabel(
            self.sidebar, text=f"Caja #{self.caja['id']} Abierta",
            font=ctk.CTkFont(size=12), text_color="#bdc3c7"
        ).pack(pady=(0, 12))

        ctk.CTkFrame(self.sidebar, height=2, fg_color="#2c3e50").pack(fill="x", padx=20, pady=5)

        self.btn_movimientos = ctk.CTkButton(
            self.sidebar, text="📝 Movimientos", height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY,
            corner_radius=10, command=self._show_movimientos
        )
        self.btn_movimientos.pack(fill="x", padx=20, pady=(12, 8))

        self.btn_resumen = ctk.CTkButton(
            self.sidebar, text="📊 Resumen del Día", height=42,
            font=ctk.CTkFont(size=13),
            fg_color="transparent", text_color=COLOR_TEXT,
            border_width=2, border_color="#34495e", hover_color="#1c2833",
            corner_radius=10, command=self._show_resumen
        )
        self.btn_resumen.pack(fill="x", padx=20, pady=8)

        self.btn_historial = ctk.CTkButton(
            self.sidebar, text="📅 Historial", height=38,
            font=ctk.CTkFont(size=13),
            fg_color="transparent", text_color=COLOR_TEXT,
            border_width=2, border_color="#34495e", hover_color="#1c2833",
            corner_radius=10, command=self._show_historial
        )
        self.btn_historial.pack(fill="x", padx=20, pady=8)

        if self.usuario['es_admin'] == 1:
            ctk.CTkFrame(self.sidebar, height=1, fg_color="#2c3e50").pack(fill="x", padx=20, pady=(10, 5))
            ctk.CTkLabel(
                self.sidebar, text="ADMINISTRACIÓN",
                font=ctk.CTkFont(size=10, weight="bold"), text_color="#7f8c8d"
            ).pack(pady=(0, 8))

            self.btn_empleados = ctk.CTkButton(
                self.sidebar, text="👨‍🔧 Empleados", height=36,
                font=ctk.CTkFont(size=12),
                fg_color="transparent", text_color=COLOR_TEXT,
                border_width=1, border_color="#34495e", hover_color="#1c2833",
                corner_radius=8, command=self._show_empleados
            )
            self.btn_empleados.pack(fill="x", padx=20, pady=4)

            self.btn_proveedores = ctk.CTkButton(
                self.sidebar, text="📦 Proveedores", height=36,
                font=ctk.CTkFont(size=12),
                fg_color="transparent", text_color=COLOR_TEXT,
                border_width=1, border_color="#34495e", hover_color="#1c2833",
                corner_radius=8, command=self._show_proveedores
            )
            self.btn_proveedores.pack(fill="x", padx=20, pady=4)

            self.btn_usuarios = ctk.CTkButton(
                self.sidebar, text="👥 Usuarios", height=36,
                font=ctk.CTkFont(size=12),
                fg_color="transparent", text_color=COLOR_TEXT,
                border_width=1, border_color="#34495e", hover_color="#1c2833",
                corner_radius=8, command=self._show_usuarios
            )
            self.btn_usuarios.pack(fill="x", padx=20, pady=4)

            self.btn_liquidacion = ctk.CTkButton(
                self.sidebar, text="💵 Liquidación", height=36,
                font=ctk.CTkFont(size=12),
                fg_color="transparent", text_color=COLOR_TEXT,
                border_width=1, border_color="#34495e", hover_color="#1c2833",
                corner_radius=8, command=self._show_liquidacion
            )
            self.btn_liquidacion.pack(fill="x", padx=20, pady=4)

        ctk.CTkFrame(self.sidebar, height=2, fg_color="#2c3e50").pack(fill="x", padx=20, pady=(10, 5))

        self.btn_cerrar_caja = ctk.CTkButton(
            self.sidebar, text="🔒 Cerrar Caja", height=38,
            font=ctk.CTkFont(size=13),
            fg_color="#7f8c8d", hover_color="#95a5a6",
            corner_radius=10, command=self._show_cierre_caja
        )
        self.btn_cerrar_caja.pack(fill="x", padx=20, pady=(0, 8))

        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.sidebar, text=f"👤 {self.usuario['nombre_usuario']}",
            font=ctk.CTkFont(size=13), text_color="#bdc3c7"
        ).pack(pady=(0, 8))

        self.btn_logout = ctk.CTkButton(
            self.sidebar, text="🚪 Cerrar Sesión", height=38,
            font=ctk.CTkFont(size=13),
            fg_color=COLOR_ERROR, hover_color="#c0392b",
            corner_radius=10, command=self.on_logout
        )
        self.btn_logout.pack(fill="x", padx=20, pady=(0, 25))

        self.content_area = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0)
        self.content_area.pack(side="right", fill="both", expand=True)

        import tkinter as tk
        tk.Label(
            self, text="Desarrollado por MazDesign",
            font=("Segoe UI", 9), fg="#34495e", bg=self.cget("fg_color")
        ).place(relx=0.99, rely=1.0, anchor="se")

    def _clear_content(self) -> None:
        if self._content_frame:
            self._content_frame.destroy()
            self._content_frame = None

    def _reset_sidebar_buttons(self) -> None:
        self.btn_movimientos.configure(fg_color=COLOR_SECONDARY, text_color="white", border_width=0)
        self.btn_resumen.configure(fg_color="transparent", text_color=COLOR_TEXT, border_width=2, border_color="#34495e")
        self.btn_historial.configure(fg_color="transparent", text_color=COLOR_TEXT, border_width=2, border_color="#34495e")
        self.btn_cerrar_caja.configure(fg_color="#7f8c8d", text_color="white", border_width=0)

        if hasattr(self, 'btn_empleados'):
            self.btn_empleados.configure(fg_color="transparent", text_color=COLOR_TEXT, border_width=1, border_color="#34495e")
        if hasattr(self, 'btn_proveedores'):
            self.btn_proveedores.configure(fg_color="transparent", text_color=COLOR_TEXT, border_width=1, border_color="#34495e")
        if hasattr(self, 'btn_usuarios'):
            self.btn_usuarios.configure(fg_color="transparent", text_color=COLOR_TEXT, border_width=1, border_color="#34495e")
        if hasattr(self, 'btn_liquidacion'):
            self.btn_liquidacion.configure(fg_color="transparent", text_color=COLOR_TEXT, border_width=1, border_color="#34495e")

    def _highlight_btn(self, btn: ctk.CTkButton) -> None:
        btn.configure(fg_color="transparent", text_color=COLOR_ACCENT, border_width=2, border_color=COLOR_ACCENT)

    def _show_movimientos(self) -> None:
        from views.movimientos_view import MovimientosFrame
        self._clear_content()
        self._reset_sidebar_buttons()
        self._highlight_btn(self.btn_movimientos)
        self._content_frame = MovimientosFrame(
            parent=self.content_area, caja=self.caja,
            movimiento_controller=self.movimiento_controller,
            empleado_controller=self.empleado_controller,
            on_movement_added=self._on_movement_added
        )
        self._content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def _show_resumen(self) -> None:
        from views.resumen_view import ResumenFrame
        self._clear_content()
        self._reset_sidebar_buttons()
        self._highlight_btn(self.btn_resumen)
        self._content_frame = ResumenFrame(
            parent=self.content_area, caja=self.caja,
            movimiento_controller=self.movimiento_controller
        )
        self._content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def _show_historial(self) -> None:
        from views.historial_view import HistorialFrame
        self._clear_content()
        self._reset_sidebar_buttons()
        self._highlight_btn(self.btn_historial)
        self._content_frame = HistorialFrame(
            parent=self.content_area,
            caja_controller=self.caja_controller,
            movimiento_controller=self.movimiento_controller
        )
        self._content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def _show_empleados(self) -> None:
        from views.empleados_view import EmpleadosFrame
        self._clear_content()
        self._reset_sidebar_buttons()
        self._highlight_btn(self.btn_empleados)
        self._content_frame = EmpleadosFrame(
            parent=self.content_area,
            empleado_controller=self.empleado_controller,
            on_back=self._show_movimientos
        )
        self._content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def _show_proveedores(self) -> None:
        from views.proveedores_view import ProveedoresFrame
        self._clear_content()
        self._reset_sidebar_buttons()
        self._highlight_btn(self.btn_proveedores)
        self._content_frame = ProveedoresFrame(
            parent=self.content_area,
            proveedor_controller=self.proveedor_controller,
            on_back=self._show_movimientos
        )
        self._content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def _show_liquidacion(self) -> None:
        from views.liquidacion_view import LiquidacionFrame
        self._clear_content()
        self._reset_sidebar_buttons()
        self._highlight_btn(self.btn_liquidacion)
        self._content_frame = LiquidacionFrame(
            parent=self.content_area,
            empleado_controller=self.empleado_controller,
            on_back=self._show_movimientos
        )
        self._content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def _show_usuarios(self) -> None:
        from views.usuarios_view import UsuariosFrame
        self._clear_content()
        self._reset_sidebar_buttons()
        self._highlight_btn(self.btn_usuarios)
        self._content_frame = UsuariosFrame(
            parent=self.content_area,
            user_controller=self.user_controller,
            usuario_actual=self.usuario,
            on_back=self._show_movimientos
        )
        self._content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def _show_cierre_caja(self) -> None:
        from views.cierre_caja_view import CierreCajaFrame
        self._clear_content()
        self._reset_sidebar_buttons()
        self._highlight_btn(self.btn_cerrar_caja)
        self._content_frame = CierreCajaFrame(
            parent=self.content_area, caja=self.caja,
            usuario=self.usuario, caja_controller=self.caja_controller,
            on_caja_cerrada=self.on_caja_cerrada
        )
        self._content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def _on_movement_added(self) -> None:
        self._show_movimientos()
