"""
Vista de Resumen del Día.
Muestra totales por moneda, efectivo vs banco y últimos movimientos.
"""

import customtkinter as ctk
from typing import Dict, Any

from controllers.movimiento_controller import MovimientoController
from utils.constants import (
    COLOR_ACCENT, COLOR_BG, COLOR_CARD, COLOR_TEXT,
    COLOR_SECONDARY, COLOR_SUCCESS, COLOR_ERROR
)


class ResumenFrame(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        caja: Dict[str, Any],
        movimiento_controller: MovimientoController,
    ) -> None:
        super().__init__(parent, fg_color="transparent")
        self.caja = caja
        self.movimiento_controller = movimiento_controller

        self._create_widgets()

    def _create_widgets(self) -> None:
        resumen = self.movimiento_controller.obtener_resumen_del_dia(self.caja['id'])
        
        # --- TARJETAS SUPERIORES (Monedas) ---
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 20))
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        monedas = [
            ("🇺🇾 UYU (Pesos)", resumen['UYU'], COLOR_SECONDARY),
            ("💵 USD (Dólares)", resumen['USD'], "#27ae60"),
            ("🇧🇷 BRL (Reales)", resumen['BRL'], "#8e44ad"),
        ]

        for i, (titulo, datos, color) in enumerate(monedas):
            card = ctk.CTkFrame(cards_frame, fg_color=COLOR_CARD, corner_radius=15)
            card.grid(row=0, column=i, padx=(0 if i==0 else 10, 0 if i==2 else 10), sticky="nsew")

            ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=14, weight="bold"), text_color=color).pack(pady=(15, 5), padx=15, anchor="w")
            
            saldo_str = f"${datos['saldo']:,.2f}"
            ctk.CTkLabel(card, text=saldo_str, font=ctk.CTkFont(size=28, weight="bold"), text_color=COLOR_TEXT).pack(padx=15, anchor="w")
            
            ctk.CTkFrame(card, height=2, fg_color="#2c3e50").pack(fill="x", padx=15, pady=10)
            
            ctk.CTkLabel(card, text=f"➕ Ingresos: ${datos['ingresos']:,.2f}", font=ctk.CTkFont(size=12), text_color="#2ecc71").pack(anchor="w", padx=15)
            ctk.CTkLabel(card, text=f"➖ Egresos: ${datos['egresos']:,.2f}", font=ctk.CTkFont(size=12), text_color="#e74c3c").pack(anchor="w", padx=15, pady=(0, 15))


        # --- TARJETAS INFERIORES (Físico vs Banco) ---
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="both", expand=True)
        bottom_frame.grid_columnconfigure((0, 1), weight=1)

        # Tarjeta Efectivo Físico
        card_efectivo = ctk.CTkFrame(bottom_frame, fg_color=COLOR_CARD, corner_radius=15)
        card_efectivo.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        ctk.CTkLabel(card_efectivo, text="💵 EFECTIVO EN CAJA", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_SUCCESS).pack(pady=(20, 10), padx=20, anchor="w")
        ctk.CTkLabel(card_efectivo, text=f"${resumen['efectivo_uyu']:,.2f}", font=ctk.CTkFont(size=32, weight="bold"), text_color=COLOR_TEXT).pack(padx=20, anchor="w")
        ctk.CTkLabel(card_efectivo, text="Dinero físico real que hay en la caja", font=ctk.CTkFont(size=12), text_color="#7f8c8d").pack(padx=20, anchor="w", pady=(5, 20))

        # Tarjeta Banco
        card_banco = ctk.CTkFrame(bottom_frame, fg_color=COLOR_CARD, corner_radius=15)
        card_banco.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        ctk.CTkLabel(card_banco, text="🏦 DINERO EN BANCO", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_SECONDARY).pack(pady=(20, 10), padx=20, anchor="w")
        ctk.CTkLabel(card_banco, text=f"${resumen['banco_uyu']:,.2f}", font=ctk.CTkFont(size=32, weight="bold"), text_color=COLOR_TEXT).pack(padx=20, anchor="w")
        ctk.CTkLabel(card_banco, text="Tarjetas, transferencias y cheques", font=ctk.CTkFont(size=12), text_color="#7f8c8d").pack(padx=20, anchor="w", pady=(5, 20))

        # Pie de página
        ctk.CTkLabel(
            self, 
            text=f"Fondo inicial de caja: ${resumen['fondo_inicial']:,.2f} UYU",
            font=ctk.CTkFont(size=12), text_color="#5d6d7e"
        ).pack(pady=(15, 0))