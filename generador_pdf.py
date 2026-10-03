"""
===============================================================================
PLANTILLA PDF EDITABLE CON LECTURA DE ARCHIVOS EXTERNOS (.TXT, .MD, .PDF)
===============================================================================
Este módulo permite generar PDFs tanto a partir de cadenas de texto en código 
como a partir de archivos ya existentes (documentos .txt, .md o archivos .pdf).
===============================================================================
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import os
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.units import cm
from reportlab.lib.colors import Color, HexColor, orange
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Flowable
from reportlab.pdfgen import canvas


# =============================================================================
# SECTOR 1: CONFIGURACIÓN GENERAL DEL DOCUMENTO
# =============================================================================

@dataclass(frozen=True)
class ConfiguracionPDF:
    """Contenedor de todos los parámetros editables del documento PDF."""

    # --- HOJA Y MÁRGENES ---
    tamano_pagina: Tuple[float, float] = A4
    margen_x: float = 1.8 * cm
    margen_y: float = 2.2 * cm
    padding_texto: float = 0.8 * cm

    # --- FUENTE Y TEXTO ---
    nombre_fuente: str = "Helvetica"
    tamano_fuente: int = 11
    interlineado: int = 17
    color_texto: Color = HexColor('#1A252C')
    alineacion_texto: int = 4                    # 0=Izq, 1=Centro, 2=Der, 4=Justificado
    espacio_entre_parrafos: float = 0.4 * cm

    # --- RECUADRO Y RELLENO ---
    color_borde: Color = HexColor('#D35400')
    color_relleno: Optional[Color] = HexColor('#FDFEFE') # None para transparente
    grosor_borde: float = 2.0
    radio_esquinas: float = 12.0

    # --- TAMAÑO FIJO SOBREESCRIBIBLE (OPCIONAL) ---
    box_ancho_personalizado: Optional[float] = None
    box_alto_personalizado: Optional[float] = None
    box_x_personalizado: Optional[float] = None
    box_y_personalizado: Optional[float] = None

    # --- CÁLCULOS GEOMÉTRICOS AUTOMÁTICOS ---
    @property
    def ancho_pagina(self) -> float:
        return self.tamano_pagina[0]

    @property
    def alto_pagina(self) -> float:
        return self.tamano_pagina[1]

    @property
    def box_x(self) -> float:
        return self.box_x_personalizado if self.box_x_personalizado is not None else self.margen_x

    @property
    def box_y(self) -> float:
        return self.box_y_personalizado if self.box_y_personalizado is not None else self.margen_y

    @property
    def box_ancho(self) -> float:
        return self.box_ancho_personalizado if self.box_ancho_personalizado is not None else self.ancho_pagina - (2 * self.margen_x)

    @property
    def box_alto(self) -> float:
        return self.box_alto_personalizado if self.box_alto_personalizado is not None else self.alto_pagina - (2 * self.margen_y)

    @property
    def frame_x(self) -> float:
        return self.box_x + self.padding_texto

    @property
    def frame_y(self) -> float:
        return self.box_y + self.padding_texto

    @property
    def frame_ancho(self) -> float:
        return self.box_ancho - (2 * self.padding_texto)

    @property
    def frame_alto(self) -> float:
        return self.box_alto - (2 * self.padding_texto)


# =============================================================================
# SECTOR 2: DIBUJO DEL FONDO EN CADA PÁGINA
# =============================================================================

class DecoradorPagina:
    """Dibuja el marco decorativo y fondo en cada página."""

    def __init__(self, config: ConfiguracionPDF):
        self._config = config

    def dibujar_fondo_decorativo(self, canvas_obj: canvas.Canvas, doc: BaseDocTemplate) -> None:
        canvas_obj.saveState()

        canvas_obj.setStrokeColor(self._config.color_borde)
        canvas_obj.setLineWidth(self._config.grosor_borde)

        hay_relleno = self._config.color_relleno is not None
        if hay_relleno:
            canvas_obj.setFillColor(self._config.color_relleno)

        if self._config.radio_esquinas > 0:
            canvas_obj.roundRect(
                self._config.box_x,
                self._config.box_y,
                self._config.box_ancho,
                self._config.box_alto,
                self._config.radio_esquinas,
                stroke=1,
                fill=1 if hay_relleno else 0
            )
        else:
            canvas_obj.rect(
                self._config.box_x,
                self._config.box_y,
                self._config.box_ancho,
                self._config.box_alto,
                stroke=1,
                fill=1 if hay_relleno else 0
            )

        canvas_obj.restoreState()


# =============================================================================
# SECTOR 3: CONSTRUCTOR Y LECTOR DE ARCHIVOS
# =============================================================================

class GeneradorDocumentoPDF:
    """Genera documentos PDF desde cadenas de texto o desde archivos externos."""

    def __init__(self, config: Optional[ConfiguracionPDF] = None):
        self.config = config or ConfiguracionPDF()
        self._decorador = DecoradorPagina(self.config)

    def generar(self, archivo_salida: str, texto_largo: str) -> None:
        """Crea el PDF a partir de una cadena de texto dada."""
        doc = BaseDocTemplate(archivo_salida, pagesize=self.config.tamano_pagina)

        frame_contenido = Frame(
            self.config.frame_x,
            self.config.frame_y,
            self.config.frame_ancho,
            self.config.frame_alto,
            id='frame_texto_principal',
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0
        )

        plantilla_recuadro = PageTemplate(
            id='plantilla_pagina_recuadro',
            frames=[frame_contenido],
            onPage=self._decorador.dibujar_fondo_decorativo
        )
        doc.addPageTemplates([plantilla_recuadro])

        hoja_estilos = getSampleStyleSheet()
        estilo_cuerpo = ParagraphStyle(
            'EstiloCuerpoPersonalizado',
            parent=hoja_estilos['Normal'],
            fontName=self.config.nombre_fuente,
            fontSize=self.config.tamano_fuente,
            leading=self.config.interlineado,
            textColor=self.config.color_texto,
            alignment=self.config.alineacion_texto
        )

        historia: List[Flowable] = []
        parrafos_crudos = texto_largo.split('\n')

        for parrafo_texto in parrafos_crudos:
            texto_limpio = parrafo_texto.strip()
            if texto_limpio:
                p = Paragraph(texto_limpio, estilo_cuerpo)
                historia.append(p)
                historia.append(Spacer(1, self.config.espacio_entre_parrafos))

        doc.build(historia)

    def generar_desde_archivo(self, ruta_archivo_entrada: str, archivo_salida: str) -> None:
        """
        Lee el contenido de un archivo externo (.txt, .md o .pdf) 
        y genera el PDF aplicándole la plantilla visual configurada.
        """
        if not os.path.exists(ruta_archivo_entrada):
            raise FileNotFoundError(f"El archivo especificado no existe: {ruta_archivo_entrada}")

        # 1. Si es un archivo PDF existente, extraemos su texto por páginas
        if ruta_archivo_entrada.lower().endswith('.pdf'):
            import pypdfium2 as pdfium
            pdf = pdfium.PdfDocument(ruta_archivo_entrada)
            bloques_texto = []
            for pagina in pdf:
                textpage = pagina.get_textpage()
                bloques_texto.append(textpage.get_text_range())
            texto_extraido = "\n\n".join(bloques_texto)

        # 2. Si es un archivo de texto plano (.txt, .md, etc.)
        else:
            with open(ruta_archivo_entrada, 'r', encoding='utf-8') as f:
                texto_extraido = f.read()

        # 3. Generar el PDF formateado
        self.generar(archivo_salida, texto_extraido)


# =============================================================================
# SECTOR 4: EJEMPLO DE USO CON ARCHIVOS EXTERNOS
# =============================================================================

if __name__ == "__main__":
    print("[+] Ejecutando demostración con lectura de archivos...")

    generador = GeneradorDocumentoPDF(config=ConfiguracionPDF())

    # --- MODO 1: USANDO UNA CADENA DE TEXTO EN CÓDIGO ---
    texto_ejemplo = "Este es un texto directo en código." * 20
    generador.generar("salida_desde_texto.pdf", texto_ejemplo)
    print("[OK] PDF desde texto generado: salida_desde_texto.pdf")

    # --- MODO 2: LEYENDO UN ARCHIVO EXTERNO (.txt, .md, o .pdf) ---
    # Ejemplo: Si tienes un archivo 'mi_documento.txt' o 'documento_base.pdf':
    # generador.generar_desde_archivo("mi_documento.txt", "pdf_estilizado.pdf")

    # Demostración usando un archivo .txt temporal
    archivo_demo_txt = "nota_ejemplo.txt"
    with open(archivo_demo_txt, "w", encoding="utf-8") as f:
        f.write("Este texto proviene de un archivo .txt externo cargado automáticamente.\n\n" * 15)

    generador.generar_desde_archivo(archivo_demo_txt, "salida_desde_archivo_txt.pdf")
    print(f"[OK] PDF procesado desde archivo '{archivo_demo_txt}': salida_desde_archivo_txt.pdf")
