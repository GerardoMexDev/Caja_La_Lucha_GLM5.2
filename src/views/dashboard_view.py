"""
Frame principal del Dashboard.
Contiene el sidebar de navegación y el área de contenido dinámico.
"""

import customtkinter as ctk
from typing import Dict, Any, Callable, Optional

from controllers.movimiento_controller import MovimientoController
from controllers.caja_controller import CajaController
from controllers.user_controller import UserController
from controllers.empleado_controller import EmpleadoController  # NUEVO
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
        caja_controller: CajaController,
        user_controller: UserController,
        empleado_controller: EmpleadoController,  # NUEVO
        on_logout: Callable[[], None],
        on_caja_cerrada: Callable[[], None],
    ) -> None:
        super().__init__(parent, fg_color=COLOR_BG)
        self.usuario = usuario
        self.caja = caja
        self.movimiento_controller = movimiento_controller
        self.caja_controller = caja_controller
        self.user_controller = user_controller
        self.empleado_controller = empleado_controller  # NUEVO
        self.on_logout = on_logout
        self.on_caja_cerrada = on_caja_cerrada
        
        self._content_frame: Optional[ctk.CTkFrame] = None

        self._create_widgets()
        self._show_movimientos()

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

        self.btn_historial = ctk.CTkButton(
            self.sidebar, text="📅 Historial", height=40,
            font=ctk.CTkFont(size=13),
            fg_color="transparent", text_color=COLOR_TEXT,
            border_width=2, border_color="#34495e", hover_color="#1c2833",
            corner_radius=10, command=self._show_historial
        )
        self.btn_historial.pack(fill="x", padx=20, pady=10)

        # SECCIÓN ADMIN
        if self.usuario['es_admin'] == 1:
            self.btn_empleados = ctk.CTkButton(
                self.sidebar, text="👨‍🔧 Empleados", height=40,
                font=ctk.CTkFont(size=13),
                fg_color="transparent", text_color=COLOR_TEXT,
                border_width=2, border_color="#34495e", hover_color="#1c2833",
                corner_radius=10, command=self._show_empleados
            )
            self.btn_empleados.pack(fill="x", padx=20, pady=10)

            self.btn_usuarios = ctk.CTkButton(
                self.sidebar, text="👥 Usuarios", height=40,
                font=ctk.CTkFont(size=13),
                fg_color="transparent", text_color=COLOR_TEXT,
                border_width=2, border_color="#34495e", hover_color="#1c2833",
                corner_radius=10, command=self._show_usuarios
            )
            self.btn_usuarios.pack(fill="x", padx=20, pady=10)

            self.btn_liquidacion = ctk.CTkButton(
                self.sidebar, text="💵 Liquidación", height=40,
                font=ctk.CTkFont(size=13),
                fg_color="transparent", text_color=COLOR_TEXT,
                border_width=2, border_color="#34495e", hover_color="#1c2833",
                corner_radius=10, command=self._show_liquidacion
            )
            self.btn_liquidacion.pack(fill="x", padx=20, pady=10)

        # Separador antes de acciones finales
        ctk.CTkFrame(self.sidebar, height=2, fg_color="#2c3e50").pack(fill="x", padx=20, pady=(15, 10))

        self.btn_cerrar_caja = ctk.CTkButton(
            self.sidebar, text="🔒 Cerrar Caja", height=40,
            font=ctk.CTkFont(size=13),
            fg_color="#7f8c8d", hover_color="#95a5a6",
            corner_radius=10, command=self._show_cierre_caja
        )
        self.btn_cerrar_caja.pack(fill="x", padx=20, pady=(0, 10))

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
        self.btn_historial.configure(fg_color="transparent", text_color=COLOR_TEXT, border_width=2, border_color="#34495e")
        self.btn_cerrar_caja.configure(fg_color="#7f8c8d", text_color="white", border_width=0)
        
        if hasattr(self, 'btn_empleados'):
            self.btn_empleados.configure(fg_color="transparent", text_color=COLOR_TEXT, border_width=2, border_color="#34495e")
        if hasattr(self, 'btn_usuarios'):
            self.btn_usuarios.configure(fg_color="transparent", text_color=COLOR_TEXT, border_width=2, border_color="#34495e")
        if hasattr(self, 'btn_liquidacion'):
            self.btn_liquidacion.configure(fg_color="transparent", text_color=COLOR_TEXT, border_width=2, border_color="#34495e")
        

    def _show_movimientos(self) -> None:
        from views.movimientos_view import MovimientosFrame
        self._clear_content()
        self._reset_sidebar_buttons()
        
        self.btn_movimientos.configure(fg_color="transparent", text_color=COLOR_ACCENT, border_width=2, border_color=COLOR_ACCENT)
        
        # NUEVO: Inyectamos el empleado_controller
        self._content_frame = MovimientosFrame(
            parent=self.content_area,
            caja=self.caja,
            movimiento_controller=self.movimiento_controller,
            empleado_controller=self.empleado_controller,  # NUEVO
            on_movement_added=self._on_movement_added
        )
        self._content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def _show_resumen(self) -> None:
        from views.resumen_view import ResumenFrame
        self._clear_content()
        self._reset_sidebar_buttons()
        
        self.btn_resumen.configure(fg_color="transparent", text_color=COLOR_ACCENT, border_width=2, border_color=COLOR_ACCENT)
        
        self._content_frame = ResumenFrame(
            parent=self.content_area,
            caja=self.caja,
            movimiento_controller=self.movimiento_controller
        )
        self._content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def _show_historial(self) -> None:
        from views.historial_view import HistorialFrame
        self._clear_content()
        self._reset_sidebar_buttons()

        self.btn_historial.configure(fg_color="transparent", text_color=COLOR_ACCENT, border_width=2, border_color=COLOR_ACCENT)

        self._content_frame = HistorialFrame(
            parent=self.content_area,
            caja_controller=self.caja_controller,
            movimiento_controller=self.movimiento_controller
        )
        self._content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # NUEVA: Navegación a Empleados
    def _show_empleados(self) -> None:
        from views.empleados_view import EmpleadosFrame
        self._clear_content()
        self._reset_sidebar_buttons()

        if hasattr(self, 'btn_empleados'):
            self.btn_empleados.configure(fg_color="transparent", text_color=COLOR_ACCENT, border_width=2, border_color=COLOR_ACCENT)

        self._content_frame = EmpleadosFrame(
            parent=self.content_area,
            empleado_controller=self.empleado_controller,
            on_back=self._show_movimientos
        )
        self._content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def _show_liquidacion(self) -> None:
        from views.liquidacion_view import LiquidacionFrame
        self._clear_content()
        self._reset_sidebar_buttons()

        if hasattr(self, 'btn_liquidacion'):
            self.btn_liquidacion.configure(fg_color="transparent", text_color=COLOR_ACCENT, border_width=2, border_color=COLOR_ACCENT)

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

        if hasattr(self, 'btn_usuarios'):
            self.btn_usuarios.configure(fg_color="transparent", text_color=COLOR_ACCENT, border_width=2, border_color=COLOR_ACCENT)

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

        self.btn_cerrar_caja.configure(
            fg_color="transparent", text_color=COLOR_ACCENT,
            border_width=2, border_color=COLOR_ACCENT
        )

        self._content_frame = CierreCajaFrame(
            parent=self.content_area,
            caja=self.caja,
            usuario=self.usuario,
            caja_controller=self.caja_controller,
            on_caja_cerrada=self.on_caja_cerrada
        )
        self._content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def _on_movement_added(self) -> None:
        """Callback cuando se agrega un movimiento para refrescar la tabla."""
        self._show_movimientos()