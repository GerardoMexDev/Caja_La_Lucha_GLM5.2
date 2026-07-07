"""
Vista de Gestión de Empleados.
Permite dar de alta empleados y ver su sueldo semanal.
"""

import customtkinter as ctk
from typing import Dict, Any, Callable

from controllers.empleado_controller import EmpleadoController
from utils.constants import COLOR_CARD, COLOR_TEXT, COLOR_SECONDARY, COLOR_SUCCESS, COLOR_ERROR


class EmpleadosFrame(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        empleado_controller: EmpleadoController,
        on_back: Callable[[], None],
    ) -> None:
        super().__init__(parent, fg_color="transparent")
        self.empleado_controller = empleado_controller
        self.on_back = on_back

        self._create_widgets()

    def _create_widgets(self) -> None:
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkButton(
            header, text="← Volver", width=100, height=35,
            fg_color="transparent", text_color=COLOR_TEXT,
            border_width=1, border_color="#555",
            command=self.on_back
        ).pack(side="left")

        ctk.CTkLabel(
            header, text="👥 Gestión de Empleados", font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLOR_TEXT
        ).pack(side="left", padx=20)

        # Formulario de Alta
        form_card = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=15)
        form_card.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(form_card, text="Dar de Alta Empleado", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_TEXT).pack(pady=(15, 10), anchor="w", padx=20)

        form_grid = ctk.CTkFrame(form_card, fg_color="transparent")
        form_grid.pack(fill="x", padx=20, pady=(0, 20))
        form_grid.grid_columnconfigure(0, weight=1)
        form_grid.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form_grid, text="Nombre Completo:", text_color="#bdc3c7").grid(row=0, column=0, sticky="w", pady=5, padx=(0, 10))
        self.nombre_entry = ctk.CTkEntry(form_grid, placeholder_text="Ej: Juan Pérez", height=35)
        self.nombre_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 15))

        ctk.CTkLabel(form_grid, text="Sueldo Semanal (UYU):", text_color="#bdc3c7").grid(row=0, column=1, sticky="w", pady=5)
        self.sueldo_entry = ctk.CTkEntry(form_grid, placeholder_text="Ej: 15000", height=35)
        self.sueldo_entry.grid(row=1, column=1, sticky="ew", pady=(0, 15))

        self.status_label = ctk.CTkLabel(form_grid, text="", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=2, column=0, columnspan=1, sticky="w")

        ctk.CTkButton(
            form_grid, text="➕ AGREGAR EMPLEADO", height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_SUCCESS, hover_color="#1e8449",
            command=self._agregar_empleado
        ).grid(row=2, column=1, sticky="e", pady=(0, 0))

        # Tabla de Empleados
        table_card = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=15)
        table_card.pack(fill="both", expand=True)

        ctk.CTkLabel(table_card, text="Empleados Registrados", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_TEXT).pack(pady=(15, 10), anchor="w", padx=20)

        self.table_container = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.table_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self._load_empleados()

    def _load_empleados(self) -> None:
        for widget in self.table_container.winfo_children():
            widget.destroy()

        empleados = self.empleado_controller.obtener_todos_los_empleados()

        if not empleados:
            ctk.CTkLabel(self.table_container, text="No hay empleados registrados.", text_color="#7f8c8d").pack(pady=20)
            return

        # Cabecera
        headers = [("Nombre", 300), ("Sueldo Semanal", 150), ("Estado", 100), ("Acción", 120)]
        for col, (text, w) in enumerate(headers):
            ctk.CTkLabel(self.table_container, text=text, font=ctk.CTkFont(weight="bold", size=13), text_color=COLOR_SECONDARY, width=w, anchor="w").grid(row=0, column=col, padx=5, pady=5)

        for i, emp in enumerate(empleados, start=1):
            estado_text = "✅ Activo" if emp['activo'] == 1 else "⛔ Inactivo"
            estado_color = COLOR_SUCCESS if emp['activo'] == 1 else COLOR_ERROR
            
            ctk.CTkLabel(self.table_container, text=emp['nombre'], width=300, anchor="w").grid(row=i, column=0, padx=5, pady=5)
            ctk.CTkLabel(self.table_container, text=f"$ {emp['sueldo_semanal']:,.2f}", width=150, anchor="w").grid(row=i, column=1, padx=5, pady=5)
            ctk.CTkLabel(self.table_container, text=estado_text, width=100, anchor="w", text_color=estado_color).grid(row=i, column=2, padx=5, pady=5)
            
            btn_text = "Desactivar" if emp['activo'] == 1 else "Reactivar"
            ctk.CTkButton(
                self.table_container, text=btn_text, width=100, height=28,
                fg_color="transparent", text_color="#f39c12", border_width=1, border_color="#f39c12",
                command=lambda e_id=emp['id']: self._toggle_estado(e_id)
            ).grid(row=i, column=3, padx=5, pady=5)

    def _agregar_empleado(self) -> None:
        nombre = self.nombre_entry.get().strip()
        try:
            sueldo = float(self.sueldo_entry.get().strip().replace(",", "."))
        except ValueError:
            self.status_label.configure(text="❌ Sueldo inválido.", text_color=COLOR_ERROR)
            return

        if not nombre:
            self.status_label.configure(text="❌ Ingrese un nombre.", text_color=COLOR_ERROR)
            return
        if sueldo <= 0:
            self.status_label.configure(text="❌ El sueldo debe ser mayor a 0.", text_color=COLOR_ERROR)
            return

        resultado = self.empleado_controller.crear_empleado(nombre, sueldo)
        if resultado[0]:
            self.status_label.configure(text="✅ Empleado agregado.", text_color=COLOR_SUCCESS)
            self.nombre_entry.delete(0, "end")
            self.sueldo_entry.delete(0, "end")
            self._load_empleados()
        else:
            self.status_label.configure(text=f"❌ {resultado[1]}", text_color=COLOR_ERROR)

    def _toggle_estado(self, empleado_id: int) -> None:
        self.empleado_controller.toggle_estado(empleado_id)
        self._load_empleados()