import sys
import os
import customtkinter as ctk
from typing import Dict, Any, Optional

from models.database import DatabaseManager
from controllers.user_controller import UserController
from controllers.caja_controller import CajaController
from controllers.movimiento_controller import MovimientoController
from controllers.empleado_controller import EmpleadoController  # NUEVO
from views.login_view import LoginFrame
from utils.constants import COLOR_BG


class CajaLaLuchaApp(ctk.CTk):
    """Ventana principal — router de navegación entre frames."""

    def __init__(self) -> None:
        super().__init__()

        # Forzar que la BD siempre esté en la raíz del proyecto
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "..", "lucha_caja.db")
        print(f">>> CONECTADO A LA BD: {db_path}")

        self.db = DatabaseManager(db_path)
        self.user_controller = UserController(self.db)
        self.caja_controller = CajaController(self.db)
        self.movimiento_controller = MovimientoController(self.db)
        self.empleado_controller = EmpleadoController(self.db)  # NUEVO
        self.user_controller.ensure_admin_exists()

        self.current_user: Optional[Dict[str, Any]] = None
        self.current_caja: Optional[Dict[str, Any]] = None
        self._active_frame: Optional[ctk.CTkFrame] = None

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=COLOR_BG)

        self._show_login()
        self.mainloop()

    # ── navegación ────────────────────────────────────────────────────────────

    def _clear_frame(self) -> None:
        if self._active_frame:
            self._active_frame.destroy()
            self._active_frame = None

    def _center(self, w: int, h: int) -> None:
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _show_login(self) -> None:
        self._clear_frame()
        self.title("Caja La Lucha — Inicio de Sesión")
        self._center(450, 550)
        self._active_frame = LoginFrame(
            parent=self,
            user_controller=self.user_controller,
            on_login_success=self._on_login_success,
        )
        self._active_frame.pack(fill="both", expand=True)

    def _on_login_success(self, user: Dict[str, Any]) -> None:
        self.current_user = user
        caja_activa = self.caja_controller.obtener_caja_activa()
        if caja_activa:
            self.current_caja = caja_activa
            self._show_dashboard()
        else:
            self._show_portal()

    def _show_portal(self) -> None:
        from views.portal_view import PortalFrame
        self._clear_frame()
        self.title("Caja La Lucha — Apertura de Jornada")
        self._center(500, 420)
        
        fondo_sugerido = self.caja_controller.obtener_ultimo_saldo_cerrado()
        
        self._active_frame = PortalFrame(
            parent=self,
            usuario=self.current_user,
            caja_controller=self.caja_controller,
            on_caja_abierta=self._on_caja_abierta,
            fondo_sugerido=fondo_sugerido,
        )
        self._active_frame.pack(fill="both", expand=True)

    def _on_caja_abierta(self, caja: Dict[str, Any]) -> None:
        self.current_caja = caja
        self._show_dashboard()

    def _show_dashboard(self) -> None:
        from views.dashboard_view import DashboardFrame
        self._clear_frame()
        self.title("Caja La Lucha — Dashboard")
        self._center(1200, 700)
        self.minsize(900, 600)
        self._active_frame = DashboardFrame(
            parent=self,
            usuario=self.current_user,
            caja=self.current_caja,
            movimiento_controller=self.movimiento_controller,
            caja_controller=self.caja_controller,
            user_controller=self.user_controller,
            empleado_controller=self.empleado_controller,  # NUEVO
            on_logout=self._on_logout,
            on_caja_cerrada=self._on_caja_cerrada,
        )
        self._active_frame.pack(fill="both", expand=True)

    def _on_caja_cerrada(self) -> None:
        self.current_user = None
        self.current_caja = None
        self.minsize(0, 0)
        self._show_login()

    def _on_logout(self) -> None:
        self.current_user = None
        self.current_caja = None
        self.minsize(0, 0)
        self._show_login()


def main() -> None:
    try:
        CajaLaLuchaApp()
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()