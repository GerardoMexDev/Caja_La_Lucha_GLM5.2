"""
Punto de entrada principal del Sistema Caja La Lucha.
"""

import sys
from typing import Dict, Any
from models.database import DatabaseManager
from controllers.user_controller import UserController
from views.login_view import LoginView


class CajaLaLuchaApp:
    """Aplicación principal del sistema Caja La Lucha."""

    def __init__(self) -> None:
        """Inicializa la aplicación."""
        # Inicializar base de datos
        self.db = DatabaseManager()

        # Inicializar controladores
        self.user_controller = UserController(self.db)

        # Asegurar que existe un admin
        self.user_controller.ensure_admin_exists()

        # Usuario actual
        self.current_user: Dict[str, Any] | None = None

        # Lanzar vista de login
        self._launch_login()

    def _launch_login(self) -> None:
        """Lanza la pantalla de login."""
        self.login_view = LoginView(
            user_controller=self.user_controller,
            on_login_success=self._on_login_success
        )
        self.login_view.mainloop()

    def _on_login_success(self, user: Dict[str, Any]) -> None:
        """Callback ejecutado al login exitoso."""
        self.current_user = user
        print(f"✅ Usuario logueado: {user['nombre_usuario']} (Admin: {user['es_admin']})")
        self.login_view.destroy()
        self._launch_main_view()

    def _launch_main_view(self) -> None:
        """Lanza la vista principal del sistema."""
        # TODO: Implementar en Sesión 3
        print("🚀 Lananzando vista principal...")
        print(f"   Usuario: {self.current_user['nombre_usuario']}")


def main() -> None:
    """Función principal de la aplicación."""
    try:
        app = CajaLaLuchaApp()
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()