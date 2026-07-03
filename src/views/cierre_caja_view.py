import customtkinter as ctk
from typing import Dict, Any, Callable
from controllers.caja_controller import CajaController
from utils.constants import COLOR_ACCENT, COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_SECONDARY, COLOR_SUCCESS, COLOR_ERROR

class CierreCajaFrame(ctk.CTkFrame):
    def __init__(self, parent, caja: Dict[str, Any], usuario: Dict[str, Any], caja_controller: CajaController, on_caja_cerrada: Callable[[], None]) -> None:
        super().__init__(parent, fg_color=COLOR_BG)
        self.caja = caja
        self.usuario = usuario
        self.caja_controller = caja_controller
        self.on_caja_cerrada = on_caja_cerrada
        self._efectivo_esperado = 0.0
        self._create_widgets()

    def _create_widgets(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        saldo = self.caja_controller.calcular_saldo_actual(self.caja['id'])
        self._efectivo_esperado = saldo['efectivo_uyu']
        
        cont = ctk.CTkScrollableFrame(self, fg_color="transparent")
        cont.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        

        fc = ctk.CTkFrame(cont, fg_color=COLOR_CARD, corner_radius=12)
        fc.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(fc, text="Fondo Inicial", font=ctk.CTkFont(size=13), text_color="#bdc3c7").pack(pady=(12, 2), padx=15, anchor="w")
        ctk.CTkLabel(fc, text=f"$ {saldo['fondo_inicial']:,.2f} UYU", font=ctk.CTkFont(size=24, weight="bold"), text_color=COLOR_TEXT).pack(padx=15, anchor="w", pady=(0, 12))

        mf = ctk.CTkFrame(cont, fg_color="transparent")
        mf.pack(fill="x", pady=(0, 15))
        mf.grid_columnconfigure((0, 1, 2), weight=1)

        for i, (lbl, d, col) in enumerate([("UYU", saldo['totales']['UYU'], COLOR_SECONDARY), ("USD", saldo['totales']['USD'], "#27ae60"), ("BRL", saldo['totales']['BRL'], "#8e44ad")]):
            c = ctk.CTkFrame(mf, fg_color=COLOR_CARD, corner_radius=12)
            c.grid(row=0, column=i, padx=(0 if i==0 else 8, 0 if i==2 else 8), sticky="nsew")
            ctk.CTkLabel(c, text=lbl, font=ctk.CTkFont(size=14, weight="bold"), text_color=col).pack(pady=(12, 5), padx=12, anchor="w")
            ctk.CTkLabel(c, text=f"Ingresos: ${d['ingresos']:,.2f}", font=ctk.CTkFont(size=12), text_color=COLOR_SUCCESS).pack(padx=12, anchor="w")
            ctk.CTkLabel(c, text=f"Egresos: ${d['egresos']:,.2f}", font=ctk.CTkFont(size=12), text_color=COLOR_ERROR).pack(padx=12, anchor="w")
            ctk.CTkLabel(c, text=f"Saldo: ${d['saldo']:,.2f}", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_TEXT).pack(padx=12, anchor="w", pady=(2, 12))

        bf = ctk.CTkFrame(cont, fg_color="transparent")
        bf.pack(fill="x", pady=(0, 15))
        bf.grid_columnconfigure((0, 1), weight=1)

        ce = ctk.CTkFrame(bf, fg_color=COLOR_CARD, corner_radius=12)
        ce.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        ctk.CTkLabel(ce, text="EFECTIVO EN CAJA", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_SUCCESS).pack(pady=(12, 5), padx=15, anchor="w")
        ctk.CTkLabel(ce, text=f"$ {saldo['efectivo_uyu']:,.2f}", font=ctk.CTkFont(size=26, weight="bold"), text_color=COLOR_TEXT).pack(padx=15, anchor="w", pady=(0, 12))

        cb = ctk.CTkFrame(bf, fg_color=COLOR_CARD, corner_radius=12)
        cb.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        ctk.CTkLabel(cb, text="BANCO", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_SECONDARY).pack(pady=(12, 5), padx=15, anchor="w")
        ctk.CTkLabel(cb, text=f"$ {saldo['banco_uyu']:,.2f}", font=ctk.CTkFont(size=26, weight="bold"), text_color=COLOR_TEXT).pack(padx=15, anchor="w", pady=(0, 12))

        ctk.CTkFrame(cont, height=2, fg_color="#2c3e50").pack(fill="x", pady=(10, 15))

        cc = ctk.CTkFrame(cont, fg_color=COLOR_CARD, corner_radius=12)
        cc.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(cc, text="Conteo Fisico de Efectivo", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_TEXT).pack(pady=(15, 10), padx=15, anchor="w")
        ctk.CTkLabel(cc, text="Ingrese el dinero real que hay en la caja:", font=ctk.CTkFont(size=12), text_color="#bdc3c7").pack(padx=15, anchor="w")

        self.conteo_var = ctk.StringVar()
        self.conteo_entry = ctk.CTkEntry(cc, textvariable=self.conteo_var, placeholder_text="$ 0.00", height=45, font=ctk.CTkFont(size=16), corner_radius=8)
        self.conteo_entry.pack(fill="x", padx=15, pady=(8, 5))
        self.conteo_entry.bind("<KeyRelease>", self._calcular_diferencia)

        self.diferencia_label = ctk.CTkLabel(cc, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.diferencia_label.pack(padx=15, anchor="w", pady=(0, 15))

        self.btn_confirmar = ctk.CTkButton(cont, text="CONFIRMAR CIERRE DE CAJA", height=50, font=ctk.CTkFont(size=15, weight="bold"), fg_color=COLOR_ERROR, hover_color="#c0392b", corner_radius=12, command=self._confirmar_cierre)
        self.btn_confirmar.pack(fill="x", pady=(5, 0))

        self.status_label = ctk.CTkLabel(cont, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=(8, 0))

    def _calcular_diferencia(self, event=None) -> None:
        try:
            c = float(self.conteo_var.get().strip().replace(",", "."))
            d = c - self._efectivo_esperado
            if abs(d) < 0.01: self.diferencia_label.configure(text="Cuadra perfecto", text_color=COLOR_SUCCESS)
            elif d > 0: self.diferencia_label.configure(text=f"Sobra: $ {d:,.2f}", text_color=COLOR_ACCENT)
            else: self.diferencia_label.configure(text=f"Falta: $ {abs(d):,.2f}", text_color=COLOR_ERROR)
        except ValueError: self.diferencia_label.configure(text="")

    def _confirmar_cierre(self) -> None:
        self.btn_confirmar.configure(state="disabled", text="Cerrando caja...")
        try:
            self.caja_controller.cerrar_caja(caja_id=self.caja['id'], usuario_id=self.usuario['id'])
            self.status_label.configure(text="Caja cerrada correctamente.", text_color=COLOR_SUCCESS)
            self.btn_confirmar.configure(text="CAJA CERRADA", fg_color="#2c3e50")
            self.after(1000, self.on_caja_cerrada)
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color=COLOR_ERROR)
            self.btn_confirmar.configure(state="normal", text="CONFIRMAR CIERRE DE CAJA")