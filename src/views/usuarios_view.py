import customtkinter as ctk
from typing import Dict, Any, Callable, List
from controllers.user_controller import UserController
from utils.constants import COLOR_ACCENT, COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_SECONDARY, COLOR_SUCCESS, COLOR_ERROR


class UsuariosFrame(ctk.CTkFrame):
    def __init__(self, parent, user_controller: UserController, usuario_actual: Dict[str, Any], on_back: Callable[[], None]) -> None:
        super().__init__(parent, fg_color=COLOR_BG)
        self.user_controller = user_controller
        self.usuario_actual = usuario_actual
        self.on_back = on_back
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._create_widgets()

    def _create_widgets(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        ctk.CTkButton(header, text="<- Volver", width=100, height=35, fg_color="transparent", border_width=1, border_color="#5d6d7e", text_color=COLOR_TEXT, hover_color="#1c2833", command=self.on_back).pack(side="left")

        ctk.CTkLabel(header, text="GESTION DE USUARIOS", font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_ACCENT).pack(side="left", padx=20)

        form = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=10)
        form.grid(row=1, column=0, sticky="nsew", pady=(0, 15))
        form.grid_columnconfigure((1, 2, 3), weight=1)

        ctk.CTkLabel(form, text="Nuevo Usuario:", font=ctk.CTkFont(size=13), text_color="#bdc3c7").grid(row=0, column=0, padx=(15, 5), pady=15)
        
        self.entry_user = ctk.CTkEntry(form, placeholder_text="Nombre usuario", height=35, width=150)
        self.entry_user.grid(row=0, column=1, padx=5, pady=15)

        self.entry_pass = ctk.CTkEntry(form, placeholder_text="Contrasena", show="*", height=35, width=150)
        self.entry_pass.grid(row=0, column=2, padx=5, pady=15)

        self.chk_admin = ctk.CTkCheckBox(form, text="Admin", font=ctk.CTkFont(size=13))
        self.chk_admin.grid(row=0, column=3, padx=5, pady=15)

        self.btn_crear = ctk.CTkButton(form, text="CREAR", width=100, height=35, fg_color=COLOR_SUCCESS, command=self._crear_usuario)
        self.btn_crear.grid(row=0, column=4, padx=(5, 15), pady=15)

        self.status_lbl = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=12))
        self.status_lbl.grid(row=1, column=0, columnspan=5, padx=15, pady=(0, 10), sticky="w")

        self.table_container = ctk.CTkScrollableFrame(self, fg_color=COLOR_CARD, corner_radius=10)
        self.table_container.grid(row=2, column=0, sticky="nsew")
        self.table_container.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        self._load_users()

    def _load_users(self) -> None:
        for w in self.table_container.winfo_children(): w.destroy()

        headers = ["ID", "Usuario", "Rol", "Estado", "Accion"]
        for col, h in enumerate(headers):
            ctk.CTkLabel(self.table_container, text=h, font=ctk.CTkFont(weight="bold", size=13), text_color=COLOR_ACCENT).grid(row=0, column=col, padx=10, pady=10)

        users: List[Dict[str, Any]] = self.user_controller.get_all_users()
        for i, u in enumerate(users, start=1):
            ctk.CTkLabel(self.table_container, text=str(u['id']), text_color=COLOR_TEXT).grid(row=i, column=0, padx=10, pady=5)
            ctk.CTkLabel(self.table_container, text=u['nombre_usuario'], text_color=COLOR_TEXT).grid(row=i, column=1, padx=10, pady=5)
            
            rol = "Admin" if u['es_admin'] == 1 else "Cajero"
            ctk.CTkLabel(self.table_container, text=rol, text_color=COLOR_SECONDARY).grid(row=i, column=2, padx=10, pady=5)
            
            estado_txt = "Activo" if u['activo'] == 1 else "Inactivo"
            estado_color = COLOR_SUCCESS if u['activo'] == 1 else COLOR_ERROR
            ctk.CTkLabel(self.table_container, text=estado_txt, text_color=estado_color).grid(row=i, column=3, padx=10, pady=5)

            puede_toggle = not (u['id'] == self.usuario_actual['id'])
            estado_btn = "Desactivar" if u['activo'] == 1 else "Activar"
            color_btn = COLOR_ERROR if u['activo'] == 1 else COLOR_SUCCESS
            fg = "transparent" if u['activo'] == 1 else color_btn
            border = 1 if u['activo'] == 1 else 0
            txt_color = color_btn if u['activo'] == 1 else "white"

            btn = ctk.CTkButton(self.table_container, text=estado_btn, width=100, height=30, fg_color=fg, text_color=txt_color, border_width=border, border_color=COLOR_ERROR, state="normal" if puede_toggle else "disabled", command=lambda uid=u['id']: self._toggle_user(uid))
            btn.grid(row=i, column=4, padx=10, pady=5)

    def _crear_usuario(self) -> None:
        user = self.entry_user.get().strip()
        pwd = self.entry_pass.get().strip()
        if not user or not pwd:
            self.status_lbl.configure(text="Error: Usuario y contrasena requeridos.", text_color=COLOR_ERROR)
            return
        es_admin = 1 if self.chk_admin.get() else 0
        self.btn_crear.configure(state="disabled", text="Creando...")
        resultado = self.user_controller.create_user(user, pwd, es_admin)
        if resultado[0]:
            self.status_lbl.configure(text=f"OK: {resultado[1]}", text_color=COLOR_SUCCESS)
            self.entry_user.delete(0, "end")
            self.entry_pass.delete(0, "end")
            self.chk_admin.deselect()
            self._load_users()
        else:
            self.status_lbl.configure(text=f"Error: {resultado[1]}", text_color=COLOR_ERROR)
        self.btn_crear.configure(state="normal", text="CREAR")

    def _toggle_user(self, user_id: int) -> None:
        resultado = self.user_controller.toggle_user_status(user_id)
        if not resultado[0]:
            self.status_lbl.configure(text=f"Error: {resultado[1]}", text_color=COLOR_ERROR)
        self._load_users()
