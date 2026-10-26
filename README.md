## Proyecto Final Clase Visualización de Datos

## Carpeta `data/`

**Archivos de entrada**

| Archivo | Descripción |
|---|---|
| `estudio_apropiacion_pdf.pdf` | Impresión de la encuesta "Lo digital empieza contigo" (Qualtrics). Es la fuente de las preguntas y de sus opciones de respuesta. |
| `template_estructura.csv` | Plantilla de referencia con el código (Q1, Q2, …) y el enunciado de cada columna. Define la estructura del dataset. |

**Archivos generados** (por `generar_dataset_sintetico.py`)

| Archivo | Descripción |
|---|---|
| `dataset_sintetico_500.csv` | 500 respuestas simuladas. Las primeras 16 columnas son metadatos de la respuesta (fechas, duración, ubicación, etc.) y el resto son las preguntas, identificadas por su código. Las respuestas van como códigos de texto. |
| `diccionario_preguntas.csv` | Código de cada columna y su descripción. |
| `diccionario_respuestas.csv` | Código y descripción de cada respuesta, solo para las preguntas con respuestas codificadas. |
| `estudio_apropiacion_pdf.ocr.json` | Caché del texto leído del PDF con OCR. Es un archivo intermedio y se puede borrar; el script lo vuelve a crear. |

Para regenerar los archivos generados: `python generar_dataset_sintetico.py`
