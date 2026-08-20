# ia.md - Uso de IA en el proyecto

## Herramienta utilizada
OpenCode (modelo big-pickle) para planificacion y generacion de codigo.

## Consulta realizada
Se pidio a la IA que leyera las instrucciones ES1 de Programacion Back End y creara un plan completo para resolver el problema de "Sistema de Licencias Medicas", incluyendo la priorizacion MoSCoW y la verificacion de compliance contra la rubrica.

## Respuesta de la IA
La IA genero:
1. Un plan.md con apartado de negocio y tecnico
2. La estructura de archivos completa
3. La regla de decision con 4 resultados
4. El codigo de solucion.py con constantes (sin hardcodear)
5. La vista Django que importa desde solucion.py
6. Verificacion de compliance: 30/30 puntos posibles

## Funcionalidad OCR agregada (Should)
Se agrego soporte para leer licencias medicas directamente desde PDF:

### Tipos de PDF soportados
- **PDF con texto seleccionable**: Usa PyPDF2 para extraer texto directo
- **PDF escaneado (imagen)**: Usa PyMuPDF + pytesseract (Tesseract OCR) para reconocimiento de caracteres

### Funciones agregadas
- `extraer_texto_pypdf2(ruta_pdf)`: Lee PDF con texto seleccionable
- `extraer_texto_ocr(ruta_pdf)`: Convierte PDF a imagen y aplica OCR
- `detectar_tipo_pdf(ruta_pdf)`: Detecta automaticamente el tipo de PDF
- `parsear_texto_licencia(texto)`: Extrae los 7 campos con regex
- `procesar_pdf(ruta_pdf)`: Orquesta todo el proceso

### Uso
```bash
# Modo manual (original)
python solucion.py

# Modo PDF (nuevo)
python solucion.py "licencia.pdf"
```

### Dependencias nuevas
- PyPDF2: Extraccion de texto de PDFs
- pytesseract: Wrapper de Tesseract OCR
- Pillow: Manipulacion de imagenes
- PyMuPDF: Conversion de PDF a imagenes
- Tesseract-OCR: Motor OCR (instalador Windows)

## Correcciones realizadas por el estudiante
- Se ajustaron los maximos de dias por tipo de licencia segun legislacion chilena vigente
- Se agrego validacion de RUT con formato basico
- Se ensure_ascii=False en json.dump para caracteres especiales del espanol
- Se verifico que la vista Django reutiliza la logica de solucion.py (no la reescribe)
