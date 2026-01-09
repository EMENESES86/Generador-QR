import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_H
import os
import urllib.parse
from datetime import datetime

# -----------------------
# Builders (plantillas)
# -----------------------

def build_url_text(payload: dict) -> str:
    # usa "text" tal cual
    return (payload.get("text") or "").strip()

def build_wifi(payload: dict) -> str:
    """
    Formato estándar:
    WIFI:T:WPA;S:MiRed;P:Clave;H:false;;
    """
    ssid = (payload.get("ssid") or "").strip()
    password = payload.get("password") or ""
    security = payload.get("security") or "WPA"
    hidden = payload.get("hidden") or False

    if not ssid:
        raise ValueError("Wi-Fi: SSID es obligatorio.")

    # Si no hay password, normalmente se usa T:nopass
    if security == "nopass":
        return f"WIFI:T:nopass;S:{ssid};H:{str(hidden).lower()};;"

    return f"WIFI:T:{security};S:{ssid};P:{password};H:{str(hidden).lower()};;"

def build_vcard(payload: dict) -> str:
    """
    vCard 3.0 simple.
    """
    first = (payload.get("first") or "").strip()
    last = (payload.get("last") or "").strip()
    phone = (payload.get("phone") or "").strip()
    email = (payload.get("email") or "").strip()
    org = (payload.get("org") or "").strip()
    title = (payload.get("title") or "").strip()
    url = (payload.get("url") or "").strip()

    if not (first or last):
        raise ValueError("vCard: Nombre o Apellido es obligatorio.")

    fn = (first + " " + last).strip()

    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN:{fn}",
        f"N:{last};{first};;;",
    ]
    if org:
        lines.append(f"ORG:{org}")
    if title:
        lines.append(f"TITLE:{title}")
    if phone:
        lines.append(f"TEL;TYPE=CELL:{phone}")
    if email:
        lines.append(f"EMAIL:{email}")
    if url:
        lines.append(f"URL:{url}")
    lines.append("END:VCARD")
    return "\n".join(lines)

def build_whatsapp(payload: dict) -> str:
    """
    wa.me con texto prellenado:
    https://wa.me/5939xxxxxxx?text=Hola%20...
    """
    phone = (payload.get("phone") or "").strip()
    text = payload.get("text") or ""

    if not phone:
        raise ValueError("WhatsApp: Teléfono es obligatorio (con código país, solo números).")

    # limpiar: deja dígitos
    phone_digits = "".join(ch for ch in phone if ch.isdigit())
    if not phone_digits:
        raise ValueError("WhatsApp: Teléfono inválido.")

    q = urllib.parse.quote(text)
    if q:
        return f"https://wa.me/{phone_digits}?text={q}"
    return f"https://wa.me/{phone_digits}"

def build_email(payload: dict) -> str:
    """
    mailto:correo?subject=...&body=...
    """
    to = (payload.get("to") or "").strip()
    subject = payload.get("subject") or ""
    body = payload.get("body") or ""

    if not to:
        raise ValueError("Email: Para (correo) es obligatorio.")

    params = {}
    if subject:
        params["subject"] = subject
    if body:
        params["body"] = body

    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    if query:
        return f"mailto:{to}?{query}"
    return f"mailto:{to}"

def build_geo(payload: dict) -> str:
    """
    geo:lat,long
    """
    lat = (payload.get("lat") or "").strip()
    lon = (payload.get("lon") or "").strip()

    if not lat or not lon:
        raise ValueError("Ubicación: Latitud y Longitud son obligatorias.")

    # validación suave
    try:
        float(lat); float(lon)
    except:
        raise ValueError("Ubicación: Latitud/Longitud deben ser números (ej: -1.249, -78.616).")

    return f"geo:{lat},{lon}"

def build_ical(payload: dict) -> str:
    """
    iCalendar VEVENT básico.
    Fechas: YYYY-MM-DD
    Horas: HH:MM (24h)
    """
    summary = (payload.get("summary") or "").strip()
    location = (payload.get("location") or "").strip()
    description = (payload.get("description") or "").strip()

    date_start = (payload.get("date_start") or "").strip()
    time_start = (payload.get("time_start") or "").strip()
    date_end = (payload.get("date_end") or "").strip()
    time_end = (payload.get("time_end") or "").strip()

    if not summary:
        raise ValueError("Evento: Título es obligatorio.")
    if not (date_start and time_start and date_end and time_end):
        raise ValueError("Evento: Fecha/Hora inicio y fin son obligatorias.")

    # Convertir a formato UTC "YYYYMMDDTHHMMSSZ" (sin zona real, pero compatible)
    def to_utc_like(d, t):
        dt = datetime.strptime(f"{d} {t}", "%Y-%m-%d %H:%M")
        return dt.strftime("%Y%m%dT%H%M%SZ")

    dtstart = to_utc_like(date_start, time_start)
    dtend = to_utc_like(date_end, time_end)
    dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    uid = f"{int(datetime.utcnow().timestamp())}@qrdesktop"

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//QR Desktop//ES//",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART:{dtstart}",
        f"DTEND:{dtend}",
        f"SUMMARY:{summary}",
    ]
    if location:
        lines.append(f"LOCATION:{location}")
    if description:
        # iCal evita saltos sin escapar, lo dejamos simple
        safe_desc = description.replace("\n", "\\n")
        lines.append(f"DESCRIPTION:{safe_desc}")

    lines += [
        "END:VEVENT",
        "END:VCALENDAR"
    ]
    return "\n".join(lines)

TEMPLATES = {
    "URL / Texto": {
        "fields": [("Contenido", "text")],
        "builder": build_url_text,
    },
    "Wi-Fi": {
        "fields": [("SSID", "ssid"), ("Contraseña", "password")],
        "builder": build_wifi,
        "extras": "wifi",
    },
    "vCard (Contacto)": {
        "fields": [
            ("Nombres", "first"),
            ("Apellidos", "last"),
            ("Teléfono", "phone"),
            ("Email", "email"),
            ("Empresa", "org"),
            ("Cargo", "title"),
            ("Web", "url"),
        ],
        "builder": build_vcard,
    },
    "WhatsApp": {
        "fields": [("Teléfono (código país)", "phone"), ("Mensaje", "text")],
        "builder": build_whatsapp,
    },
    "Email": {
        "fields": [("Para", "to"), ("Asunto", "subject"), ("Mensaje", "body")],
        "builder": build_email,
    },
    "Ubicación": {
        "fields": [("Latitud", "lat"), ("Longitud", "lon")],
        "builder": build_geo,
    },
    "Evento (iCalendar)": {
        "fields": [
            ("Título", "summary"),
            ("Lugar", "location"),
            ("Descripción", "description"),
            ("Fecha inicio (YYYY-MM-DD)", "date_start"),
            ("Hora inicio (HH:MM)", "time_start"),
            ("Fecha fin (YYYY-MM-DD)", "date_end"),
            ("Hora fin (HH:MM)", "time_end"),
        ],
        "builder": build_ical,
    }
}


class QRDesktopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QR Desktop Studio")
        self.geometry("980x600")
        self.minsize(980, 600)

        self.logo_path = None
        self.qr_img_pil = None
        self.qr_img_tk = None

        self.type_var = tk.StringVar(value="URL / Texto")
        self.box_var = tk.IntVar(value=10)
        self.border_var = tk.IntVar(value=4)

        # wifi extras
        self.wifi_security_var = tk.StringVar(value="WPA")
        self.wifi_hidden_var = tk.BooleanVar(value=False)

        self.fields_vars = {}   # key -> StringVar

        self._build_ui()
        self._render_form()

    def _build_ui(self):
        # Layout principal
        outer = ttk.Frame(self, padding=12)
        outer.pack(fill="both", expand=True)

        left = ttk.Frame(outer)
        left.pack(side="left", fill="y")

        right = ttk.Frame(outer)
        right.pack(side="right", fill="both", expand=True, padx=(12, 0))

        # ---- Left: configuración ----
        ttk.Label(left, text="Tipo de QR:").pack(anchor="w")
        self.type_combo = ttk.Combobox(
            left,
            textvariable=self.type_var,
            values=list(TEMPLATES.keys()),
            state="readonly",
            width=34
        )
        self.type_combo.pack(anchor="w", pady=(0, 10))
        self.type_combo.bind("<<ComboboxSelected>>", lambda e: self._render_form())

        ttk.Separator(left).pack(fill="x", pady=10)

        ttk.Label(left, text="Configuración:").pack(anchor="w")

        row1 = ttk.Frame(left)
        row1.pack(anchor="w", pady=(6, 0))
        ttk.Label(row1, text="box_size:").pack(side="left")
        ttk.Spinbox(row1, from_=4, to=30, textvariable=self.box_var, width=6).pack(side="left", padx=8)

        row2 = ttk.Frame(left)
        row2.pack(anchor="w", pady=(6, 0))
        ttk.Label(row2, text="border:").pack(side="left")
        ttk.Spinbox(row2, from_=1, to=10, textvariable=self.border_var, width=6).pack(side="left", padx=18)

        ttk.Separator(left).pack(fill="x", pady=10)

        # Logo
        ttk.Label(left, text="Logo (opcional):").pack(anchor="w")
        logo_row = ttk.Frame(left)
        logo_row.pack(anchor="w", pady=(6, 0))
        ttk.Button(logo_row, text="Elegir...", command=self.choose_logo).pack(side="left")
        ttk.Button(logo_row, text="Quitar", command=self.clear_logo).pack(side="left", padx=8)
        self.logo_label = ttk.Label(left, text="(sin logo)")
        self.logo_label.pack(anchor="w", pady=(6, 10))

        ttk.Separator(left).pack(fill="x", pady=10)

        # Botones
        ttk.Button(left, text="Generar QR", command=self.generate_qr).pack(anchor="w", fill="x")
        ttk.Button(left, text="Guardar PNG...", command=self.save_png).pack(anchor="w", fill="x", pady=8)

        # ---- Right: formulario + preview ----
        self.form_card = ttk.Labelframe(right, text="Datos", padding=12)
        self.form_card.pack(fill="x")

        self.form_area = ttk.Frame(self.form_card)
        self.form_area.pack(fill="x")

        self.extra_area = ttk.Frame(self.form_card)
        self.extra_area.pack(fill="x", pady=(10, 0))

        ttk.Label(right, text="Vista previa:").pack(anchor="w", pady=(12, 0))
        self.preview = ttk.Label(right)
        self.preview.pack(fill="both", expand=True)

        self.payload_label = ttk.Label(right, text="", foreground="#444", wraplength=620, justify="left")
        self.payload_label.pack(anchor="w", pady=(10, 0))

    def _clear_container(self, container):
        for w in container.winfo_children():
            w.destroy()

    def _render_form(self):
        tname = self.type_var.get()
        tpl = TEMPLATES[tname]

        # limpiar
        self._clear_container(self.form_area)
        self._clear_container(self.extra_area)
        self.fields_vars = {}

        # campos dinámicos
        for i, (label, key) in enumerate(tpl["fields"]):
            ttk.Label(self.form_area, text=label + ":").grid(row=i, column=0, sticky="w", pady=4)
            var = tk.StringVar()
            self.fields_vars[key] = var

            # Textbox grande para campos tipo "Mensaje" / "Descripción"
            if key in ("text", "body", "description"):
                entry = tk.Text(self.form_area, height=4, width=62)
                entry.grid(row=i, column=1, sticky="we", pady=4, padx=(8, 0))
                # vínculo manual: guardamos widget en var para leer luego
                self.fields_vars[key] = entry
            else:
                ttk.Entry(self.form_area, textvariable=var, width=64).grid(row=i, column=1, sticky="we", pady=4, padx=(8, 0))

        self.form_area.grid_columnconfigure(1, weight=1)

        # extras por tipo (Wi-Fi)
        if tpl.get("extras") == "wifi":
            ttk.Label(self.extra_area, text="Seguridad:").grid(row=0, column=0, sticky="w", pady=4)
            sec = ttk.Combobox(
                self.extra_area,
                textvariable=self.wifi_security_var,
                values=["WPA", "WEP", "nopass"],
                state="readonly",
                width=15
            )
            sec.grid(row=0, column=1, sticky="w", pady=4, padx=(8, 0))

            chk = ttk.Checkbutton(self.extra_area, text="Red oculta", variable=self.wifi_hidden_var)
            chk.grid(row=0, column=2, sticky="w", pady=4, padx=12)

    def _get_payload(self) -> dict:
        payload = {}

        for key, v in self.fields_vars.items():
            if isinstance(v, tk.Text):
                payload[key] = v.get("1.0", "end").strip()
            else:
                payload[key] = v.get().strip()

        # wifi extras
        if self.type_var.get() == "Wi-Fi":
            payload["security"] = self.wifi_security_var.get()
            payload["hidden"] = bool(self.wifi_hidden_var.get())

        return payload

    def choose_logo(self):
        path = filedialog.askopenfilename(
            title="Seleccionar logo",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp"), ("Todos", "*.*")]
        )
        if path:
            self.logo_path = path
            self.logo_label.config(text=os.path.basename(path))

    def clear_logo(self):
        self.logo_path = None
        self.logo_label.config(text="(sin logo)")

    def generate_qr(self):
        tname = self.type_var.get()
        tpl = TEMPLATES[tname]
        payload = self._get_payload()

        try:
            data = tpl["builder"](payload)
        except Exception as e:
            messagebox.showwarning("Datos incompletos", str(e))
            return

        if not data:
            messagebox.showwarning("Falta contenido", "No hay datos para generar el QR.")
            return

        box_size = int(self.box_var.get())
        border = int(self.border_var.get())

        # si hay logo, subir corrección de errores
        err = ERROR_CORRECT_H if self.logo_path else ERROR_CORRECT_L

        qr = qrcode.QRCode(
            version=None,
            error_correction=err,
            box_size=box_size,
            border=border
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        if self.logo_path:
            try:
                img = self._apply_logo(img, self.logo_path)
            except Exception as e:
                messagebox.showerror("Error con el logo", f"No se pudo aplicar el logo.\n\nDetalle: {e}")
                return

        self.qr_img_pil = img
        self._update_preview(img)
        self.payload_label.config(text=f"Contenido final codificado:\n{data}")

    def _apply_logo(self, qr_img: Image.Image, logo_path: str) -> Image.Image:
        logo = Image.open(logo_path).convert("RGBA")

        qr_w, qr_h = qr_img.size
        logo_size = int(qr_w * 0.18)  # 18% del QR
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

        pos = ((qr_w - logo_size) // 2, (qr_h - logo_size) // 2)

        # fondo blanco alrededor del logo
        pad = 7
        bg = Image.new("RGBA", (logo_size + pad*2, logo_size + pad*2), (255, 255, 255, 255))
        bg_pos = (pos[0] - pad, pos[1] - pad)

        qr_rgba = qr_img.convert("RGBA")
        qr_rgba.paste(bg, bg_pos, bg)
        qr_rgba.paste(logo, pos, logo)

        return qr_rgba.convert("RGB")

    def _update_preview(self, img: Image.Image):
        # adapta al panel sin deformar
        w = self.preview.winfo_width() or 680
        h = self.preview.winfo_height() or 360

        preview_img = img.copy()
        preview_img.thumbnail((w, h), Image.LANCZOS)

        self.qr_img_tk = ImageTk.PhotoImage(preview_img)
        self.preview.config(image=self.qr_img_tk)

    def save_png(self):
        if self.qr_img_pil is None:
            messagebox.showinfo("Nada que guardar", "Primero genera un QR.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
            title="Guardar QR como PNG"
        )
        if not path:
            return

        try:
            self.qr_img_pil.save(path, format="PNG")
            messagebox.showinfo("Guardado", f"QR guardado en:\n{path}")
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))


if __name__ == "__main__":
    app = QRDesktopApp()
    app.mainloop()
    
    
