#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_dataset_sintetico.py
============================
Genera un CSV con N registros sintéticos (500 por defecto) para la encuesta
"Lo digital empieza contigo" (Qualtrics), a partir de:

  * data/estudio_apropiacion_pdf.pdf  -> impresión de la encuesta (sin capa de texto: se usa OCR)
  * data/template_estructura.csv      -> guía estructural (fila 1 = códigos Qn, fila 2 = texto de la pregunta)

Flujo del script
----------------
  1. Lee el template y obtiene la lista de columnas (código + enunciado).
  2. Lee el PDF (capa de texto si existe; si no, OCR con RapidOCR) y alinea cada pregunta
     del template con el flujo de texto del PDF.
  3. Clasifica cada pregunta:
       choice        -> opciones visibles en el PDF (radio buttons)
       dropdown      -> enunciado SIN opciones visibles (lista desplegable): se le asigna un
                        código único DDnn; sus respuestas válidas se definen en el diccionario
                        DROPDOWN_OPTIONS (sección de configuración)
       likert        -> matriz de escala de 7 puntos (totalmente en desacuerdo ... de acuerdo)
       differential  -> diferencial semántico de 7 puntos entre dos polos ("A:B")
       open_text     -> pregunta abierta (se rellena con OPEN_TEXT_DEFAULT = "Prueba")
  4. Genera N respuestas coherentes (variables latentes correlacionadas, ítems invertidos,
     dependencias edad -> antigüedad, experiencia -> frecuencia de uso, etc.).
  5. Exporta tres CSV: los datos (encabezado = código de pregunta), el diccionario de preguntas
     (código, descripción) y el diccionario de respuestas (código/descripción de cada respuesta).

Dependencias:  pip install numpy pymupdf rapidocr-onnxruntime
Uso:           python generar_dataset_sintetico.py
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import random
import re
import string
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import numpy as np

try:  # PyMuPDF: las versiones nuevas se importan como "pymupdf", las viejas como "fitz"
    import pymupdf
except ImportError:  # pragma: no cover
    import fitz as pymupdf

# ──────────────────────────────────────────────────────────────────────────────
# 1. CONFIGURACIÓN
# ──────────────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
DEFAULT_PDF = ROOT / "data" / "estudio_apropiacion_pdf.pdf"
DEFAULT_TEMPLATE = ROOT / "data" / "template_estructura.csv"
DEFAULT_OUTPUT = ROOT / "data" / "dataset_sintetico_500.csv"             # datos (solo códigos de pregunta)
DEFAULT_Q_DICT = ROOT / "data" / "diccionario_preguntas.csv"             # código de pregunta -> descripción
DEFAULT_A_DICT = ROOT / "data" / "diccionario_respuestas.csv"            # pregunta + código/descripción de respuesta
DEFAULT_OCR_CACHE = ROOT / "data" / "estudio_apropiacion_pdf.ocr.json"

N_ROWS = 500          # número de registros a generar
SEED = 42             # semilla para que el resultado sea reproducible
LIKERT_POINTS = 7     # puntos de las escalas Likert y de los diferenciales semánticos
OCR_DPI = 150         # resolución con la que se rasteriza cada página para el OCR

# Parámetros del análisis del PDF (las distancias son fracciones del alto de página)
MIN_TEXT_LINES = 50       # si la capa de texto trae menos líneas, se asume PDF escaneado -> OCR
MIN_STEM_SCORE = 0.50     # cobertura mínima de tokens para dar un enunciado por localizado
WINDOW_SLACK = 4          # holgura de la ventana deslizante al buscar un enunciado
MAX_OPTION_GAP = 0.066    # separación vertical máxima entre enunciado/opción y la opción siguiente
MAX_OPTION_CHARS = 45     # una opción de radio es corta; un párrafo introductorio no
HEADER_FRAC = 0.03        # franja superior de cada página que se descarta (fecha y título del navegador)
FOOTER_FRAC = 0.05        # franja inferior que se descarta (URL y nº de página)

P_SPECIAL = 0.03          # prob. de elegir "Prefiero no responder" / "Otro" cuando existen
OPEN_TEXT_DEFAULT = "Prueba"  # valor de todas las preguntas abiertas

# Etiquetas de la escala Likert de 7 puntos (código 1..7), tal como aparecen en el PDF
LIKERT_LABELS = ["Totalmente en desacuerdo", "En desacuerdo", "Parcialmente en desacuerdo", "Neutral",
                 "Parcialmente de acuerdo", "De acuerdo", "Totalmente de acuerdo"]

# Ítems redactados en sentido negativo (se invierten: 8 - x). Se comparan contra el texto normalizado.
REVERSE_PATTERNS = [
    r"aporta poco valor", r"confusa e impredecible", r"poco respaldo", r"complicado identificar",
    r"prefiero mantener un procedimiento", r"me preocupa perder control", r"necesito comprobar beneficios",
    r"no suele formar parte", r"poco probable que incorpore", r"necesito apoyo frecuente",
    r"poco claros desde el inicio", r"poco agradable", r"poco clara para saber",
    r"volumen del audio fue incomodo", r"ruido del entorno me suele traer", r"hizo mas dificil",
    r"poco control sobre la navegacion", r"mentalmente abrumadora",
]

# Reglas para decidir cómo se simula cada pregunta de selección (texto normalizado -> tipo)
FIELD_RULES = [
    (r"acepto participar", "consent"),
    (r"participado en una experiencia", "participation"),
    (r"que edad", "age"),
    (r"cuanto tiempo llevas", "tenure"),
    (r"nivel de experiencia utilizando", "digital_level"),
    (r"con que frecuencia utilizas", "digital_level"),
    (r"con que frecuencia participas", "training_freq"),
]

# ► PARAMETRIZACIÓN DE LISTAS DESPLEGABLES ◄
# Clave = código de la columna; valor = respuestas válidas, en el orden en que se codifican (1, 2, 3...).
# En Q8, Q11 y Q12 (escalas ordinales) escribe las opciones de MENOR a MAYOR.
# El script detecta los desplegables en el PDF y exige que cada uno esté definido aquí.
DROPDOWN_OPTIONS = {
    # Q6: ¿En qué área prestas tus servicios?
    "Q6": ["Dirección Corporativa de Relacionamiento Institucional y Comunicaciones",
           "Dirección Corporativa de Auditoría Interna",
           "Dirección Corporativa de Cumplimiento",
           "Vicepresidencia Corporativa Jurídica y Secretaría General",
           "Vicepresidencia Comercial y de Mercadeo",
           "Vicepresidencia Administrativa y Servicios",
           "Vicepresidencia Corporativa de Transformación Territorial y HSE",
           "Vicepresidencia Corporativa de Estrategia y Nuevos Negocios",
           "Vicepresidencia Corporativa de Ciencia, Tecnología e Innovación",
           "Vicepresidencia Corporativa de Finanzas y Valor Sostenible",
           "Vicepresidencia Corporativa de Talento Organizacional",
           "Vicepresidencia Ejecutiva de Hidrocarburos",
           "Vicepresidencia de Exploración, Desarrollo y Producción",
           "Vicepresidencia de Refinación y Procesos Industriales",
           "Vicepresidencia Ejecutiva de Energías para la Transición",
           "Gerencia General de Planeación y Logística Operativa"],
    # Q7: ¿Cuál de estas opciones describe mejor tu servicio actual?
    "Q7": ["Aprendiz", "Técnico/Operativo", "Profesional/Especialista", "Líder/Coordinador",
           "Jefatura/Gerencia"],
    # Q8: ¿Cuánto tiempo llevas prestando tus servicios para la Empresa?   (ordinal)
    "Q8": ["Menos de 1 año", "Entre 1 y 3 años", "Entre 4 y 7 años", "Entre 8 y 15 años", "Más de 15 años"],
    # Q11: ¿Con qué frecuencia utilizas herramientas digitales para realizar tus actividades laborales?   (ordinal)
    "Q11": ["Nunca", "Al menos una vez al año", "Varias veces al año", "Mensualmente", "Semanalmente",
            "Varias veces a la semana"],
    # Q12: ¿Con qué frecuencia participas en capacitaciones o procesos de aprendizaje ...?   (ordinal)
    "Q12": ["Nunca", "Al menos una vez al año", "Varias veces al año", "Mensualmente", "Semanalmente",
            "Varias veces a la semana"],
    # Q13: Selecciona una categoría de soluciones digitales en la cual hayas tenido un proceso de aprendizaje reciente
    "Q13": ["Soluciones Digitales Exploración, Desarrollo, Producción",
            "Soluciones Digitales Refinación, Comercial",
            "Soluciones Digitales Corporativas",
            "Soluciones Digitales Energías para la Transición"],
    # Q14: ¿Cuál fue la modalidad principal de tu experiencia de aprendizaje?
    "Q14": ["Presencial", "Acompañamiento en el puesto", "Virtual sincrónica (en vivo)",
            "Virtual asincrónica (a tu ritmo)", "Autoaprendizaje (a tu ritmo)",
            "Híbrida (presencial y virtual)", "Otra"],
}

# Correcciones de acentos del OCR para las opciones (el OCR del PDF pierde las tildes y la ñ)
OPTION_FIXES = {"anos": "años", "mas": "más", "hibrida": "Híbrida"}

# Ítems de la matriz Q30: 1-4 miden sensibilidad sensorial, 5-10 autorregulación (constructos distintos)
CONSTRUCT_OVERRIDES = {"Q30": [(1, 4, "Q30S"), (5, 10, "Q30R")]}
# Correlación de cada constructo con la apropiación digital general del encuestado (por defecto 0.6)
CONSTRUCT_RHO = {"Q30S": 0.0, "Q30R": 0.45, "PREF": 0.0, "AUTO": 0.4}  # PREF/AUTO: latentes de los diferenciales
DEFAULT_RHO = 0.6

# Cargas (preferencia sensorial, sensibilidad, autonomía) de cada diferencial semántico, en orden de aparición
DIFFERENTIAL_LOADINGS = [(0.5, -0.4, 0.0), (0.5, -0.3, 0.0), (0.5, -0.2, 0.1), (0.5, -0.4, 0.0),
                         (0.0, 0.0, 0.7), (0.0, 0.0, 0.6), (0.0, 0.0, 0.0), (0.1, 0.0, 0.2)]

# Palabras vacías: no se usan al alinear enunciados (inflan el solapamiento entre preguntas parecidas)
STOPWORDS = set("a al con de del el en es la las lo los me mi mis o para por que se su sus te tu tus un una y".split())

# Metadatos de respuesta (estilo Qualtrics) que se anteponen a las preguntas: (nombre de columna, descripción)
META_COLUMNS = [
    ("Start Date", "Fecha de inicio de la respuesta"),
    ("End Date", "Fecha de finalización de la respuesta"),
    ("Response Type", "Tipo de respuesta (1 por defecto)"),
    ("IP Address", "Dirección IP del respondiente (anonimizada)"),
    ("Progress", "Porcentaje de avance de la encuesta"),
    ("Duration (in seconds)", "Tiempo que tomó diligenciar la encuesta, en segundos"),
    ("Finished", "Indicador de encuesta finalizada (1 = sí)"),
    ("Recorded Date", "Fecha en que se registró la respuesta"),
    ("Response ID", "Identificador único de la respuesta"),
    ("Recipient Last Name", "Apellido del destinatario (anonimizado)"),
    ("Recipient First Name", "Nombre del destinatario (anonimizado)"),
    ("Recipient Email", "Correo del destinatario (anonimizado)"),
    ("Location Latitude", "Latitud aproximada del respondiente (Bogotá)"),
    ("Location Longitude", "Longitud aproximada del respondiente (Bogotá)"),
    ("Distribution Channel", "Canal de distribución de la encuesta"),
    ("User Language", "Idioma de la encuesta"),
]
DURATION_MEDIAN_S = 600               # duración mediana de la encuesta (segundos)
DURATION_RANGE_S = (240, 1800)        # mínimo y máximo plausibles (segundos)
BOGOTA_LAT = (4.55, 4.82)             # rango de latitud de Bogotá
BOGOTA_LON = (-74.20, -74.01)         # rango de longitud de Bogotá

SPECIAL_RE = re.compile(r"prefiero no responder|^otro\b|^otra\b")

# ──────────────────────────────────────────────────────────────────────────────
# 2. UTILIDADES DE TEXTO
# ──────────────────────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    """Minúsculas, sin tildes ni signos. El OCR lee '¿' como 'i' pegada a la mayúscula siguiente."""
    text = re.sub(r"\bi(?=[A-ZÁÉÍÓÚÑ])", "", text)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def tokens(text: str) -> list[str]:
    """Tokens significativos (sin palabras vacías) usados para alinear enunciados."""
    return [t for t in normalize(text).split() if t not in STOPWORDS]


def clean_template_text(text: str) -> str:
    """Quita los '?' sobrantes que dejaron los emojis al guardar el template en cp1252."""
    text = re.sub(r"\s*\?{2,}", "", text)      # "...escena ?? - ..." / "????El cuerpo"
    text = re.sub(r"\s+\?\s+-\s+", " - ", text)  # "adelante ? - La solución"
    return re.sub(r"^\?+", "", text).strip()


def restore_accents(option: str) -> str:
    """Repara las tildes que el OCR pierde en las opciones (años, más, Sí, Híbrida)."""
    if option.strip().lower() == "si":
        return "Sí"
    return " ".join(OPTION_FIXES.get(w.lower(), w) for w in option.split())


def phi(z: float) -> float:
    """Función de distribución acumulada normal estándar."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


# ──────────────────────────────────────────────────────────────────────────────
# 3. LECTURA DEL TEMPLATE
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Column:
    """Una columna del CSV de salida (una variable de la encuesta)."""
    code: str                 # Q15_2
    text: str                 # enunciado completo (fila 2 del template)
    group: str                # Q15
    item_idx: int             # 2   (0 si la pregunta no tiene sub-ítems)
    stem: str                 # enunciado general de la matriz (o la pregunta completa)
    item: str                 # afirmación del ítem ("" si no aplica)
    poles: tuple[str, str] | None = None   # polos de un diferencial semántico
    qtype: str = "unknown"
    options: list[str] = field(default_factory=list)
    dd_code: str | None = None             # código único DDnn de los desplegables
    reverse: bool = False
    construct: str = ""
    pdf_page: int | None = None            # página del PDF donde se localizó

    @property
    def norm(self) -> str:
        return normalize(self.text)


def read_template(path: Path) -> list[Column]:
    """Lee códigos (fila 1) y enunciados (fila 2). El template viene en cp1252, no en UTF-8."""
    raw = path.read_bytes()
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        content = raw.decode("cp1252", errors="replace")
    rows = list(csv.reader(io.StringIO(content)))
    if len(rows) < 2 or len(rows[0]) != len(rows[1]):
        raise ValueError("El template debe tener al menos 2 filas con el mismo número de columnas.")

    columns: list[Column] = []
    for code, text in zip(rows[0], rows[1]):
        code, text = code.strip(), clean_template_text(text)
        group, _, idx = code.partition("_")
        stem, sep, item = text.partition(" - ")
        stem = re.sub(r"\s+\?\s*$", "", stem).strip()   # emoji residual al final del enunciado
        col = Column(code=code, text=text, group=group, item_idx=int(idx) if idx else 0,
                     stem=stem if sep else text, item=item.strip() if sep else "")
        # Un ítem "Polo A:Polo B" es un diferencial semántico
        parts = [p.strip() for p in col.item.split(":")]
        if col.item_idx and len(parts) == 2 and all(parts):
            col.poles = (parts[0], parts[1])
        col.reverse = any(re.search(p, col.norm) for p in REVERSE_PATTERNS)
        col.construct = group_construct(col)
        columns.append(col)
    return columns


def group_construct(col: Column) -> str:
    """Constructo latente al que pertenece un ítem (normalmente su grupo Qn)."""
    for lo, hi, name in CONSTRUCT_OVERRIDES.get(col.group, []):
        if lo <= col.item_idx <= hi:
            return name
    return col.group


# ──────────────────────────────────────────────────────────────────────────────
# 4. LECTURA DEL PDF (capa de texto u OCR)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class PdfLine:
    page: int      # nº de página (1-based)
    y: float       # coordenada vertical de la línea
    x: float       # coordenada horizontal
    height: float  # alto de la página en las mismas unidades que y
    text: str

    @property
    def yf(self) -> float:
        return self.y / self.height


def _text_layer_lines(doc) -> list[PdfLine]:
    """Líneas de la capa de texto nativa del PDF (vacía si el PDF es una imagen)."""
    lines = []
    for pno, page in enumerate(doc, start=1):
        for block in page.get_text("dict")["blocks"]:
            for ln in block.get("lines", []):
                txt = "".join(s["text"] for s in ln["spans"]).strip()
                if txt:
                    lines.append(PdfLine(pno, ln["bbox"][1], ln["bbox"][0], page.rect.height, txt))
    return lines


def _ocr_lines(doc, pdf_path: Path, cache_path: Path) -> list[PdfLine]:
    """OCR página por página con RapidOCR. El resultado se guarda en caché (el OCR tarda minutos)."""
    stamp = {"size": pdf_path.stat().st_size, "mtime": int(pdf_path.stat().st_mtime), "dpi": OCR_DPI}
    if cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        if cached.get("stamp") == stamp:
            print(f"  · OCR recuperado de caché: {cache_path.name}")
            return [PdfLine(**d) for d in cached["lines"]]
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        sys.exit("El PDF no tiene capa de texto y falta el OCR. Instala:  pip install rapidocr-onnxruntime")

    engine = RapidOCR()
    lines: list[PdfLine] = []
    for pno, page in enumerate(doc, start=1):
        print(f"  · OCR página {pno}/{len(doc)}", end="\r", flush=True)
        pix = page.get_pixmap(dpi=OCR_DPI)
        result, _ = engine(pix.tobytes("png"))
        for box, txt, _conf in result or []:
            lines.append(PdfLine(pno, float(box[0][1]), float(box[0][0]), float(pix.height), txt.strip()))
    print(" " * 40, end="\r")
    cache_path.write_text(json.dumps({"stamp": stamp, "lines": [l.__dict__ for l in lines]},
                                     ensure_ascii=False), encoding="utf-8")
    return lines


def read_pdf_stream(pdf_path: Path, cache_path: Path) -> list[PdfLine]:
    """Devuelve las líneas del PDF en orden de lectura, sin encabezados, pies de página ni ruido."""
    doc = pymupdf.open(pdf_path)
    lines = _text_layer_lines(doc)
    if len(lines) < MIN_TEXT_LINES:
        print("  · El PDF no tiene capa de texto: se aplica OCR.")
        lines = _ocr_lines(doc, pdf_path, cache_path)

    noise = re.compile(r"qualtrics|https?://|^\d+\s*/\s*\d+$|^\d{1,2}/\d{1,2}/\d{2}", re.I)
    kept = [l for l in lines
            if HEADER_FRAC < l.yf < 1 - FOOTER_FRAC and not noise.search(l.text)]
    # Orden de lectura: página, banda vertical (tolera pequeñas diferencias de y) y luego x
    kept.sort(key=lambda l: (l.page, round(l.yf / 0.012), l.x))
    return kept


# ──────────────────────────────────────────────────────────────────────────────
# 5. ANÁLISIS DE LA ENCUESTA: ALINEACIÓN TEMPLATE <-> PDF Y CLASIFICACIÓN
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Block:
    """Conjunto de columnas que comparten enunciado en el PDF (una matriz o una pregunta suelta)."""
    columns: list[Column]
    search_text: str                    # texto que se busca en el PDF
    start_line: int | None = None       # índice (en el flujo del PDF) donde empieza el enunciado
    end_line: int | None = None
    score: float = 0.0


class SurveyAnalyzer:
    """Localiza cada pregunta del template dentro del PDF y deduce su tipo y sus opciones."""

    def __init__(self, columns: list[Column], lines: list[PdfLine]):
        self.columns, self.lines = columns, lines
        self.stream = [(t, i) for i, l in enumerate(lines) for t in tokens(l.text)]
        self.blocks = self._build_blocks()

    # -- agrupación -----------------------------------------------------------
    def _build_blocks(self) -> list[Block]:
        """Agrupa columnas consecutivas del mismo grupo (Q15_1, Q15_2, Q15_3 -> un bloque)."""
        blocks: list[Block] = []
        for col in self.columns:
            if blocks and col.item_idx and blocks[-1].columns[-1].group == col.group and not col.poles:
                blocks[-1].columns.append(col)
            else:
                # Un diferencial se ubica por sus polos (únicos); el resto, por su enunciado
                blocks.append(Block([col], col.item if col.poles else col.stem))
        return blocks

    # -- búsqueda del enunciado en el flujo del PDF ---------------------------
    def _locate(self, text: str, start: int):
        """Ventana deslizante: busca el tramo del PDF con mayor solapamiento de tokens con `text`."""
        need = Counter(tokens(text))
        m, width = sum(need.values()), sum(need.values()) + WINDOW_SLACK
        if not m:
            return None
        win, overlap, best_score, best_end = Counter(), 0, 0.0, -1
        for end in range(start, len(self.stream)):
            tok = self.stream[end][0]
            if win[tok] < need.get(tok, 0):
                overlap += 1
            win[tok] += 1
            left = end - width
            if left >= start:                      # sale el token más antiguo de la ventana
                old = self.stream[left][0]
                win[old] -= 1
                if win[old] < need.get(old, 0):
                    overlap -= 1
            if overlap / m > best_score:           # '>' estricto: gana la coincidencia más temprana
                best_score, best_end = overlap / m, end
        if best_score < MIN_STEM_SCORE:
            return None
        # Se recorre hacia atrás desde el final para fijar el inicio exacto del enunciado,
        # cortando cuando aparecen varios tokens seguidos ajenos al enunciado.
        remaining, first, miss = Counter(need), best_end, 0
        for k in range(best_end, max(start, best_end - width) - 1, -1):
            tok = self.stream[k][0]
            if remaining[tok] > 0:
                remaining[tok] -= 1
                first, miss = k, 0
            else:
                miss += 1
                if miss > 2:
                    break
        return self.stream[first][1], self.stream[best_end][1], best_score, best_end + 1, first

    # -- opciones visibles de una pregunta de selección ------------------------
    def _visible_options(self, block: Block, region_end: int) -> list[str]:
        """Líneas contiguas bajo el enunciado = opciones de radio. Un salto vertical grande corta."""
        options, prev = [], self.lines[block.end_line]
        for ln in self.lines[block.end_line + 1: region_end + 1]:
            same_page = ln.page == prev.page and 0 < ln.yf - prev.yf <= MAX_OPTION_GAP
            next_page = ln.page == prev.page + 1 and ln.yf <= 0.09 and prev.yf >= 0.75
            text = re.sub(r"^\W+", "", ln.text).strip()
            if not (same_page or next_page) or not text or len(text) > MAX_OPTION_CHARS:
                break
            options.append(restore_accents(text))
            prev = ln
        # La encuesta repite a veces una opción (p. ej. "40 a 49 años" en Q3): se conserva una sola vez
        return list(dict.fromkeys(options))

    # -- proceso principal -----------------------------------------------------
    def analyze(self) -> None:
        cursor, anchors = 0, []                    # anchors: inicio (en tokens) de cada bloque localizado
        for blk in self.blocks:                    # 1) localizar cada enunciado en orden de lectura
            hit = self._locate(blk.search_text, cursor)
            if not hit and len(anchors) >= 2:
                # El PDF puede mostrar dos ítems de una misma pregunta en distinto orden que el template:
                # se reintenta desde dos bloques atrás sin mover el cursor.
                hit = self._locate(blk.search_text, anchors[-2])
            if hit:
                blk.start_line, blk.end_line, blk.score, nxt, first = hit
                cursor, anchors = max(cursor, nxt), anchors + [first]
                for col in blk.columns:
                    col.pdf_page = self.lines[blk.start_line].page

        seen_matrix = False
        for n, blk in enumerate(self.blocks):      # 2) clasificar y extraer opciones
            first = blk.columns[0]
            nxt = next((b.start_line for b in self.blocks[n + 1:] if b.start_line is not None), None)
            region_end = (nxt - 1) if nxt is not None else len(self.lines) - 1

            if first.poles:
                kind = "differential"
            elif first.item_idx:
                kind = "likert"
            elif seen_matrix:
                kind = "open_text"                 # preguntas sueltas tras las matrices = respuesta abierta
            else:
                options = (self._visible_options(blk, region_end) if blk.end_line is not None else [])
                kind = "choice" if len(options) >= 2 else "dropdown"
                for col in blk.columns:
                    col.options = options
            seen_matrix = seen_matrix or bool(first.item_idx)
            for col in blk.columns:
                col.qtype = kind

    def report(self) -> None:
        """Resumen legible del análisis (una línea por pregunta o matriz)."""
        print(f"\n  {'Columnas':<14}{'Tipo':<14}{'Pág.':<6}{'Detalle'}")
        for blk in self.blocks:
            c = blk.columns[0]
            label = c.code if len(blk.columns) == 1 else f"{c.code}..{blk.columns[-1].code}"
            page = c.pdf_page or "?"
            if c.qtype == "choice":
                detail = f"{len(c.options)} opciones: " + " | ".join(c.options)
            elif c.qtype == "dropdown":
                detail = "SIN opciones visibles -> lista desplegable"
            elif c.qtype == "likert":
                detail = f"{len(blk.columns)} ítems" + ("" if blk.score else "  (enunciado no localizado)")
            elif c.qtype == "differential":
                detail = f"polos: {c.poles[0]}  <->  {c.poles[1]}"
            else:
                detail = "respuesta abierta"
            print(f"  {label:<14}{c.qtype:<14}{str(page):<6}{detail[:110]}")
        located = sum(b.start_line is not None for b in self.blocks)
        print(f"\n  Preguntas del template localizadas en el PDF: {located}/{len(self.blocks)}")


# ──────────────────────────────────────────────────────────────────────────────
# 6. PARAMETRIZACIÓN DE LOS DESPLEGABLES (desde el diccionario DROPDOWN_OPTIONS)
# ──────────────────────────────────────────────────────────────────────────────

def apply_dropdown_options(columns: list[Column], options: dict[str, list[str]]) -> None:
    """Asigna un código único DDnn a cada desplegable detectado y carga sus respuestas desde el diccionario."""
    dropdowns = [c for c in columns if c.qtype == "dropdown"]
    print(f"\n=== Desplegables detectados: {len(dropdowns)} ===")
    missing = []
    for n, col in enumerate(dropdowns, start=1):
        col.dd_code = f"DD{n:02d}"
        opts = list(dict.fromkeys(o.strip() for o in options.get(col.code, []) if o.strip()))
        if len(opts) < 2:
            missing.append(col)
            continue
        col.options = opts
        print(f"  [{col.dd_code}] {col.code}: {len(opts)} opciones -> {' | '.join(opts)}"[:150])
    if missing:
        lista = "\n".join(f"  - {c.code} ({c.dd_code}): {c.text}" for c in missing)
        sys.exit("Faltan opciones (mínimo 2) en DROPDOWN_OPTIONS para:\n" + lista)
    unused = set(options) - {c.code for c in dropdowns}
    if unused:
        print(f"  Aviso: claves de DROPDOWN_OPTIONS que no son desplegables y se ignoran: {sorted(unused)}")


# ──────────────────────────────────────────────────────────────────────────────
# 7. GENERACIÓN DE DATOS SINTÉTICOS
# ──────────────────────────────────────────────────────────────────────────────


class SyntheticGenerator:
    """Simula respondientes con variables latentes para que las respuestas sean coherentes entre sí."""

    def __init__(self, columns: list[Column], seed: int):
        self.columns = columns
        self.rng = np.random.default_rng(seed)
        self.rules = {c.code: self._field_rule(c) for c in columns if c.qtype in ("choice", "dropdown")}
        self._cat_weights: dict[str, np.ndarray] = {}
        self.ctx: dict = {}

    @staticmethod
    def _field_rule(col: Column) -> str:
        for pattern, rule in FIELD_RULES:
            if re.search(pattern, col.norm):
                return rule
        return "categorical"

    # -- API pública ----------------------------------------------------------
    def generate(self, n: int) -> list[list]:
        rows = []
        for _ in range(n):
            self._new_respondent()
            row = {}
            for col in self.columns:                      # resto de preguntas
                if col.qtype != "open_text":
                    row[col.code] = self._answer(col)
            for col in self.columns:                      # preguntas abiertas: texto fijo
                if col.qtype == "open_text":
                    row[col.code] = OPEN_TEXT_DEFAULT
            rows.append([row[c.code] for c in self.columns])
        return rows

    # -- estado del encuestado --------------------------------------------------
    def _new_respondent(self) -> None:
        self.ctx = {"g": self.rng.normal(), "age_z": self.rng.normal(), "participated": True,
                    "traits": {}, "diff_i": 0}

    def _trait(self, key: str) -> float:
        """Rasgo latente de un constructo: correlacionado (rho) con la apropiación digital general."""
        traits = self.ctx["traits"]
        if key not in traits:
            rho = CONSTRUCT_RHO.get(key, DEFAULT_RHO)
            traits[key] = rho * self.ctx["g"] + math.sqrt(1 - rho ** 2) * self.rng.normal()
        return traits[key]

    def _answer(self, col: Column) -> int:
        if col.qtype in ("choice", "dropdown"):
            return self._choice(col)
        if col.qtype == "likert":
            return self._likert(col)
        return self._differential()

    # -- preguntas de selección -------------------------------------------------
    def _bell(self, k: int, center: float = 0.5) -> np.ndarray:
        """Pesos en forma de campana sobre una escala ordinal de k niveles."""
        idx = np.arange(k)
        w = np.exp(-0.5 * ((idx - center * (k - 1)) / max(0.8, k / 3.5)) ** 2)
        return w / w.sum()

    def _ordinal(self, k: int, z: float, center: float = 0.5) -> int:
        """Nivel ordinal (0..k-1) a partir de un puntaje latente z: monótono en z."""
        cum = np.cumsum(self._bell(k, center))
        return int(min(np.searchsorted(cum, phi(z), side="right"), k - 1))

    def _choice(self, col: Column) -> int:
        """Devuelve el código numérico (1..k) de la opción elegida, como exporta Qualtrics."""
        rule, opts, g, rng = self.rules[col.code], col.options, self.ctx["g"], self.rng
        if rule == "consent":
            return 1                                      # todos aceptan participar
        if rule == "participation":                       # Sí / No / No estoy seguro
            w = np.array([0.85] + [0.15 / (len(opts) - 1)] * (len(opts) - 1))
            pick = int(rng.choice(len(opts), p=w))
            self.ctx["participated"] = pick == 0
            return pick + 1

        special = [i for i, o in enumerate(opts) if SPECIAL_RE.search(normalize(o))]
        ladder = [i for i in range(len(opts)) if i not in special]
        if special and ladder and rng.random() < P_SPECIAL:   # "Prefiero no responder" / "Otro"
            return int(rng.choice(special)) + 1
        k = len(ladder)

        if rule == "age":
            pos = self._ordinal(k, self.ctx["age_z"], center=0.35)
        elif rule == "tenure":                            # más edad -> más antigüedad
            pos = self._ordinal(k, 0.55 * self.ctx["age_z"] + 0.835 * rng.normal(), center=0.35)
        elif rule == "digital_level":                     # más apropiación -> más experiencia/uso
            pos = self._ordinal(k, 0.65 * g + 0.76 * rng.normal())
        elif rule == "training_freq":                     # haber participado -> más capacitación
            bonus = 0.6 if self.ctx["participated"] else -0.6
            pos = self._ordinal(k, (0.4 * g + bonus + 0.7 * rng.normal()) / 1.1, center=0.4)
        else:                                             # categórica: pesos aleatorios fijos por columna
            if col.code not in self._cat_weights:
                self._cat_weights[col.code] = rng.dirichlet([6.0] * k)
            pos = int(rng.choice(k, p=self._cat_weights[col.code]))
        return ladder[pos] + 1

    # -- escalas Likert y diferenciales ------------------------------------------
    def _likert(self, col: Column) -> int:
        raw = 4.7 + 1.1 * self._trait(col.construct) + self.rng.normal(0, 0.9)
        favorable = int(np.clip(round(raw), 1, LIKERT_POINTS))      # puntuación "a favor"
        return LIKERT_POINTS + 1 - favorable if col.reverse else favorable

    def _differential(self) -> int:
        i = self.ctx["diff_i"]
        self.ctx["diff_i"] += 1
        l_pref, l_sens, l_auto = DIFFERENTIAL_LOADINGS[i] if i < len(DIFFERENTIAL_LOADINGS) else (0, 0, 0)
        latent = (l_pref * self._trait("PREF") + l_sens * self._trait("Q30S")
                  + l_auto * self._trait("AUTO"))
        return int(np.clip(round(4 + 1.2 * latent + self.rng.normal(0, 1.3)), 1, LIKERT_POINTS))


# ──────────────────────────────────────────────────────────────────────────────
# 8. EXPORTACIÓN Y VALIDACIÓN
# ──────────────────────────────────────────────────────────────────────────────

def generate_metadata(n: int, seed: int) -> list[list]:
    """Genera los campos de metadatos (fechas, duración, ID, ubicación en Bogotá...) de n respuestas."""
    rng = np.random.default_rng(seed + 1)          # generador aparte: no altera las respuestas de la encuesta
    rid = random.Random(seed + 2)
    today = date.today().isoformat()               # fecha fija de hoy para todos los registros
    alphabet = string.ascii_letters + string.digits
    used: set[str] = set()
    rows = []
    for _ in range(n):
        while True:                                 # ID tipo "R_6EfM7vgHxjmzwz9", sin repetidos
            response_id = "R_" + "".join(rid.choices(alphabet, k=15))
            if response_id not in used:
                used.add(response_id)
                break
        duration = int(np.clip(rng.lognormal(math.log(DURATION_MEDIAN_S), 0.4), *DURATION_RANGE_S))
        rows.append([today, today, "1", "XXXXXXXXX", 100, duration, "1", today, response_id,
                     "XXXXX", "YYYYY", "xxxxxxx@",
                     round(float(rng.uniform(*BOGOTA_LAT)), 6), round(float(rng.uniform(*BOGOTA_LON)), 6),
                     "preview", "ES"])
    return rows


def _write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    """Escribe un CSV en UTF-8 con BOM para que Excel respete las tildes.
    QUOTE_NONNUMERIC: todo valor de tipo str (p. ej. los códigos de respuesta "1", "2"...) va entre comillas,
    y solo los números reales (Progress, Duration, latitud/longitud) se escriben sin comillas."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_NONNUMERIC)
        w.writerow(header)
        w.writerows(rows)


def export_data(path: Path, columns: list[Column], rows: list[list], meta_rows: list[list]) -> None:
    """CSV de datos: una sola fila de encabezado (metadatos + código de pregunta), luego los registros."""
    header = [name for name, _ in META_COLUMNS] + [c.code for c in columns]
    _write_csv(path, header, [m + [str(v) for v in r] for m, r in zip(meta_rows, rows)])   # códigos de respuesta como texto


def export_question_dictionary(path: Path, columns: list[Column]) -> None:
    """Diccionario 1: código de la pregunta y su descripción (todas las columnas)."""
    _write_csv(path, ["codigo_pregunta", "descripcion_pregunta"],
               [list(m) for m in META_COLUMNS] + [[c.code, c.text] for c in columns])


def answer_labels(col: Column) -> list[tuple[int, str]]:
    """Pares (código, descripción) de respuesta de una columna; vacío si no aplica (preguntas abiertas)."""
    if col.qtype in ("choice", "dropdown"):
        return list(enumerate(col.options, start=1))
    if col.qtype == "likert":
        return list(enumerate(LIKERT_LABELS, start=1))
    if col.qtype == "differential":          # solo los extremos de la escala tienen etiqueta
        return [(1, col.poles[0]), (LIKERT_POINTS, col.poles[1])]
    return []


def export_answer_dictionary(path: Path, columns: list[Column]) -> int:
    """Diccionario 2: pregunta + código y descripción de cada respuesta (solo donde hay respuestas codificadas)."""
    rows = [[c.code, c.text, str(code), label] for c in columns for code, label in answer_labels(c)]
    _write_csv(path, ["codigo_pregunta", "descripcion_pregunta", "codigo_respuesta", "descripcion_respuesta"], rows)
    return len(rows)


def validate(columns: list[Column], rows: list[list], n_expected: int) -> None:
    """Comprobaciones básicas de calidad antes de dar por buena la salida."""
    assert len(rows) == n_expected, f"Se esperaban {n_expected} registros y hay {len(rows)}"
    for j, col in enumerate(columns):
        vals = [r[j] for r in rows]
        if col.qtype in ("choice", "dropdown"):
            assert all(1 <= v <= len(col.options) for v in vals), f"{col.code}: código fuera de rango"
        elif col.qtype in ("likert", "differential"):
            assert all(1 <= v <= LIKERT_POINTS for v in vals), f"{col.code}: valor fuera de escala"
    print(f"  Validación OK: {len(rows)} registros x {len(columns)} columnas.")


# ──────────────────────────────────────────────────────────────────────────────
# 9. PROGRAMA PRINCIPAL
# ──────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Genera un CSV sintético a partir del PDF de la encuesta.")
    ap.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    ap.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="CSV de datos")
    ap.add_argument("--questions-dict", type=Path, default=DEFAULT_Q_DICT, help="CSV código -> descripción de pregunta")
    ap.add_argument("--answers-dict", type=Path, default=DEFAULT_A_DICT, help="CSV de códigos de respuesta")
    ap.add_argument("--rows", type=int, default=N_ROWS, help="número de registros (por defecto 500)")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--ocr-cache", type=Path, default=DEFAULT_OCR_CACHE)
    return ap.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):                 # consola de Windows en UTF-8
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()

    print("1) Leyendo template ...")
    columns = read_template(args.template)
    print(f"   {len(columns)} columnas ({columns[0].code} ... {columns[-1].code})")

    print("2) Leyendo y analizando el PDF ...")
    lines = read_pdf_stream(args.pdf, args.ocr_cache)
    analyzer = SurveyAnalyzer(columns, lines)
    analyzer.analyze()
    analyzer.report()

    print("\n3) Parametrización de desplegables (DROPDOWN_OPTIONS) ...")
    apply_dropdown_options(columns, DROPDOWN_OPTIONS)

    print(f"\n4) Generando {args.rows} registros sintéticos ...")
    rows = SyntheticGenerator(columns, args.seed).generate(args.rows)
    validate(columns, rows, args.rows)

    print("\n5) Exportando archivos ...")
    export_data(args.output, columns, rows, generate_metadata(args.rows, args.seed))
    export_question_dictionary(args.questions_dict, columns)
    n_answers = export_answer_dictionary(args.answers_dict, columns)
    print(f"   Datos ({len(rows)} registros):            {args.output}")
    print(f"   Diccionario de preguntas ({len(META_COLUMNS) + len(columns)}):    {args.questions_dict}")
    print(f"   Diccionario de respuestas ({n_answers} filas): {args.answers_dict}")


if __name__ == "__main__":
    main()
