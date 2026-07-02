"""
Formulario de registro de movimientos y tabla del día.
"""

import customtkinter as ctk
from typing import Dict, Any, Callable

from controllers.movimiento_controller import MovimientoController
from utils.constants import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT, COLOR_BG,
    COLOR_CARD, COLOR_TEXT, COLOR_ERROR, COLOR_SUCCESS
)

CATEGORIAS = [
    "servicio_taller", "venta", "pago_credito", 
    "compra_tiendas", "adelanto_sueldo", "deposito_bancario_ext"
]

METODOS_PAGO = ["Efectivo", "Tarjeta Débito", "Tarjeta Crédito", "Transferencia", "Cheque"]
MONEDAS = ["UYU", "USD", "BRL"]


class MovimientosFrame(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        caja: Dict[str, Any],
        movimiento_controller: MovimientoController,
        on_movement_added: Callable[[], None],
    ) -> None:
        super().__init__(parent, fg_color="transparent")
        self.caja = caja
        self.movimiento_controller = movimiento_controller
        self.on_movement_added = on_movement_added

        self._create_form()
        self._create_table()

    def _create_form(self) -> None:
        form_card = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=15)
        form_card.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            form_card, text="Nuevo Movimiento", font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXT
        ).pack(pady=(15, 15), anchor="w", padx=20)

        form_grid = ctk.CTkFrame(form_card, fg_color="transparent")
        form_grid.pack(fill="x", padx=20, pady=(0, 20))
        
        form_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.tipo_var = ctk.StringVar(value="ingreso")
        self.monto_var = ctk.StringVar()
        self.moneda_var = ctk.StringVar(value="UYU")
        self.metodo_var = ctk.StringVar(value="Efectivo")

        ctk.CTkLabel(form_grid, text="Tipo:", text_color="#bdc3c7", font=ctk.CTkFont(size=13)).grid(row=0, column=0, sticky="w", pady=5)
        self.tipo_menu = ctk.CTkOptionMenu(form_grid, values=["ingreso", "egreso"], variable=self.tipo_var, width=150)
        self.tipo_menu.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 15))

        ctk.CTkLabel(form_grid, text="Monto:", text_color="#bdc3c7", font=ctk.CTkFont(size=13)).grid(row=0, column=1, sticky="w", pady=5)
        self.monto_entry = ctk.CTkEntry(form_grid, textvariable=self.monto_var, placeholder_text="0.00", height=35, width=150)
        self.monto_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 15))

        ctk.CTkLabel(form_grid, text="Moneda:", text_color="#bdc3c7", font=ctk.CTkFont(size=13)).grid(row=0, column=2, sticky="w", pady=5)
        self.moneda_menu = ctk.CTkOptionMenu(form_grid, values=MONEDAS, variable=self.moneda_var, width=150)
        self.moneda_menu.grid(row=1, column=2, sticky="ew", padx=(0, 10), pady=(0, 15))

        ctk.CTkLabel(form_grid, text="Método Pago:", text_color="#bdc3c7", font=ctk.CTkFont(size=13)).grid(row=0, column=3, sticky="w", pady=5)
        self.metodo_menu = ctk.CTkOptionMenu(form_grid, values=METODOS_PAGO, variable=self.metodo_var, width=150)
        self.metodo_menu.grid(row=1, column=3, sticky="ew", pady=(0, 15))

        self.categoria_var = ctk.StringVar(value=CATEGORIAS[0])
        self.motivo_var = ctk.StringVar()

        ctk.CTkLabel(form_grid, text="Categoría:", text_color="#bdc3c7", font=ctk.CTkFont(size=13)).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        self.cat_menu = ctk.CTkOptionMenu(form_grid, values=CATEGORIAS, variable=self.categoria_var, width=320)
        self.cat_menu.grid(row=3, column=0, columnspan=2, sticky="ew", padx=(0, 10), pady=(0, 15))

        ctk.CTkLabel(form_grid, text="Motivo / Detalle:", text_color="#bdc3c7", font=ctk.CTkFont(size=13)).grid(row=2, column=2, columnspan=2, sticky="w", pady=5)
        self.motivo_entry = ctk.CTkEntry(form_grid, textvariable=self.motivo_var, placeholder_text="Ej: Reparación neumáticos", height=35, width=320)
        self.motivo_entry.grid(row=3, column=2, columnspan=2, sticky="ew", pady=(0, 15))

        self.btn_registrar = ctk.CTkButton(
            form_grid, text="REGISTRAR MOVIMIENTO", height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_SUCCESS, hover_color="#1e8449",
            command=self._registrar_movimiento
        )
        self.btn_registrar.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(5, 0))

        self.status_label = ctk.CTkLabel(form_grid, text="", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=5, column=0, columnspan=4, pady=(5, 0))

    def _create_table(self) -> None:
        table_card = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=15)
        table_card.pack(fill="both", expand=True)

        ctk.CTkLabel(
            table_card, text="Movimientos de Hoy", font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXT
        ).pack(pady=(15, 10), anchor="w", padx=20)

        self.table_container = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.table_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self._load_movimientos()

    def _load_movimientos(self) -> None:
        for widget in self.table_container.winfo_children():
            widget.destroy()

        movimientos = self.movimiento_controller.obtener_movimientos_del_dia(self.caja['id'])

        if not movimientos:
            ctk.CTkLabel(self.table_container, text="No hay movimientos registrados hoy.", text_color="#7f8c8d").pack(pady=20)
            return

        headers = ["Hora", "Tipo", "Categoría", "Motivo", "Monto", "Pago"]
        for col, text in enumerate(headers):
            ctk.CTkLabel(
                self.table_container, text=text, font=ctk.CTkFont(weight="bold", size=13),
                text_color=COLOR_ACCENT, width=120, anchor="w"
            ).grid(row=0, column=col, padx=5, pady=5)

        for row_idx, mov in enumerate(movimientos, start=1):
            hora = mov['created_at'].split(' ')[1] if ' ' in mov['created_at'] else mov['created_at']
            tipo_text = "✅ Ingreso" if mov['tipo'] == 'ingreso' else "🔴 Egreso"
            color_tipo = COLOR_SUCCESS if mov['tipo'] == 'ingreso' else COLOR_ERROR
            
            signo = "+" if mov['tipo'] == 'ingreso' else "-"
            monto_str = f"{signo} {mov['monto']:,.2f} {mov['moneda']}"

            vals = [hora, tipo_text, mov['categoria'], mov['motivo'], monto_str, mov['metodo_pago']]
            
            for col, text in enumerate(vals):
                lbl = ctk.CTkLabel(
                    self.table_container, text=text, font=ctk.CTkFont(size=12),
                    text_color=color_tipo if col == 1 else COLOR_TEXT, 
                    width=120, anchor="w"
                )
                lbl.grid(row=row_idx, column=col, padx=5, pady=2, sticky="w")

    def _registrar_movimiento(self) -> None:
        try:
            monto = float(self.monto_var.get().strip().replace(",", "."))
        except ValueError:
            self.status_label.configure(text="❌ Monto inválido.", text_color=COLOR_ERROR)
            return

        if monto <= 0:
            self.status_label.configure(text="❌ El monto debe ser mayor a 0.", text_color=COLOR_ERROR)
            return

        if not self.motivo_var.get().strip():
            self.status_label.configure(text="❌ Ingrese un motivo.", text_color=COLOR_ERROR)
            return

        self.btn_registrar.configure(state="disabled", text="Guardando...")

        try:
            resultado = self.movimiento_controller.registrar_movimiento(
                caja_id=self.caja['id'],
                tipo=self.tipo_var.get(),
                categoria=self.categoria_var.get(),
                motivo=self.motivo_var.get().strip(),
                monto=monto,
                moneda=self.moneda_var.get(),
                metodo_pago=self.metodo_var.get()
            )
            
            if resultado[0]:
                self.status_label.configure(text="✅ Movimiento guardado.", text_color=COLOR_SUCCESS)
                self.monto_entry.delete(0, "end")
                self.motivo_entry.delete(0, "end")
                self._load_movimientos()
                self.after(500, self.on_movement_added)
            else:
                self.status_label.configure(text=f"❌ {resultado[1]}", text_color=COLOR_ERROR)

        except Exception as e:
            self.status_label.configure(text=f"❌ Error al guardar: {str(e)}", text_color=COLOR_ERROR)
        finally:
            self.btn_registrar.configure(state="normal", text="REGISTRAR MOVIMIENTO")