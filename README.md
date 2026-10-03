# Generador de PDFs con Plantilla y Recuadro Personalizable

Un generador de documentos PDF en Python utilizando **ReportLab**, diseñado para maquetar textos y documentos automáticamente dentro de un recuadro estético con paginación inteligente, tipografías editables y colores de fondo.

---

## 🚀 Características Principales

* 📐 **100% Configurable**: Modifica el tamaño de la hoja (A4, Letter), márgenes, tipografías, alineaciones e interlineados.
* 🎨 **Estilo Visual**: Personaliza el grosor y color del borde (`HexColor`), el color de relleno del fondo y la curvatura de esquinas (cuadradas o redondeadas).
* 📄 **Paginación Automática**: El motor calcula la altura útil por página y realiza saltos de página (*Page Breaks*) vertiendo el texto de forma fluida.
* 📂 **Soporte Multi-Archivo**: Genera PDFs a partir de texto directo en código o leyendo archivos externos (`.txt`, `.md`, `.pdf`).

---

## 🛠️ Instalación y Requisitos

Asegúrate de tener Python 3.8+ instalado y ejecuta:

```bash
pip install reportlab pypdfium2
```

---

## 💻 Uso Rápido

```python
from generador_pdf import GeneradorDocumentoPDF, ConfiguracionPDF
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm

# 1. Configurar aspecto visual y tipografía
config = ConfiguracionPDF(
    nombre_fuente="Helvetica",
    tamano_fuente=11,
    color_borde=HexColor('#D35400'),    # Naranja terracota
    color_relleno=HexColor('#FDFEFE'),  # Blanco marfil
    radio_esquinas=12.0,                 # Esquinas redondeadas
    margen_x=1.8 * cm,
    margen_y=2.2 * cm
)

# 2. Instanciar el generador
generador = GeneradorDocumentoPDF(config=config)

# 3. Opción A: Generar desde una cadena de texto
generador.generar("documento_salida.pdf", "Tu texto aquí...")

# 4. Opción B: Generar desde un archivo existente (.txt, .md o .pdf)
generador.generar_desde_archivo("mi_archivo.txt", "documento_salida.pdf")
```

---

## 📂 Estructura del Proyecto

* `generador_pdf.py`: Módulo principal con la arquitectura de configuración, canvas callback y generador.
* `README.md`: Documentación del repositorio.
* `requirements.txt`: Dependencias necesarias del proyecto.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.
