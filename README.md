# 🧩 QR Desktop Studio

QR Desktop Studio es una aplicación de escritorio desarrollada en Python para la generación de códigos QR avanzados mediante una interfaz gráfica clara, funcional y orientada a casos de uso reales.

La herramienta está diseñada para usuarios finales, instituciones educativas y empresas que requieren generar códigos QR personalizados, funcionales y listos para producción sin depender de servicios web externos.

---

## 🚀 Características principales

QR Desktop Studio incorpora plantillas inteligentes que construyen automáticamente el contenido correcto del código QR según el tipo seleccionado.

### Tipos de QR disponibles
- URL / Texto libre
- Wi-Fi (SSID, seguridad WPA/WEP/nopass, red oculta)
- vCard (Contacto)
  - Nombres
  - Apellidos
  - Teléfono
  - Correo electrónico
  - Empresa
  - Cargo
  - Sitio web
- WhatsApp  
  Enlace directo con mensaje prellenado
- Email  
  Correo destino, asunto y mensaje
- Ubicación geográfica  
  Formato geo:latitud,longitud
- Evento (iCalendar)  
  Compatible con Google Calendar, Outlook y Apple Calendar

---

## 🎨 Personalización del QR

- Vista previa del QR en tiempo real
- Ajuste del tamaño del código QR (box_size)
- Configuración del borde
- Inserción de logotipo o imagen en el centro del QR
- Corrección de errores automática al utilizar logotipo
- Exportación del código QR en formato PNG de alta calidad

---

## 🔒 Privacidad y funcionamiento

- Funcionamiento completamente offline
- No requiere conexión a internet
- No almacena ni transmite información del usuario
- No necesita cuentas ni registros

---

## 🖥️ Tecnologías utilizadas

- Python 3
- Tkinter (interfaz gráfica)
- qrcode
- Pillow (PIL)
- PyInstaller

---

## 📦 Instalación (modo desarrollo)

pip install qrcode[pil] pillow  
python qr_desktop.py

---

## 🏗️ Compilación a ejecutable (Windows)

pyinstaller --clean --noconfirm --onefile --windowed --name QRDesktopStudio qr_desktop.py

El archivo ejecutable se generará en la carpeta dist/.

---

## 📚 Casos de uso

- Generación de códigos QR para eventos y congresos
- Inventario y control de activos
- Uso educativo y académico
- Tarjetas digitales para negocios
- Señalética institucional y documentación técnica

---

## 🧠 Escalabilidad y futuras mejoras

El diseño del proyecto permite incorporar fácilmente:
- Generación masiva de códigos QR desde archivos CSV o Excel
- Historial de códigos generados
- Exportación a formatos SVG y PDF
- Modo de impresión en hojas A4
- Plantillas personalizadas por cliente o institución

---

## 👨‍💻 Autor

Desarrollado por  
EMENESES Developers  
https://emenesesdevelopers.com  

Especialistas en desarrollo de software a medida, sistemas institucionales y soluciones tecnológicas profesionales.

---

## 📄 Licencia

Este proyecto puede utilizarse con fines educativos y demostrativos.  
Para uso comercial, redistribución o personalización institucional, contactar al desarrollador.
