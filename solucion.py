import json
import os
from datetime import datetime, date
from tabulate import tabulate

ARCHIVO_JSON = "datos.json"

TIPOS_LICENCIA = {
    1: {"nombre": "Enfermedad o accidente comun", "max_dias": 30},
    2: {"nombre": "Medicina preventiva", "max_dias": 2},
    3: {"nombre": "Licencia pre y postnatal", "max_dias": 180},
    4: {"nombre": "Enfermedad grave del nino menor de un anio", "max_dias": 180},
    5: {"nombre": "Accidente del trabajo o del trayecto", "max_dias": 365},
    6: {"nombre": "Enfermedad profesional", "max_dias": 365},
    7: {"nombre": "Patologias del embarazo", "max_dias": 84},
}

FORMATO_FECHA = "%d/%m/%Y"


def cargar():
    if os.path.exists(ARCHIVO_JSON):
        with open(ARCHIVO_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def guardar(registros):
    with open(ARCHIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(registros, f, indent=2, ensure_ascii=False)


def validar_rut(rut):
    if not rut or not rut.strip():
        return False
    rut_limpio = rut.replace(".", "").replace("-", "").strip()
    if len(rut_limpio) < 2:
        return False
    return rut_limpio[:-1].isdigit()


def parsear_fecha(fecha_str):
    try:
        return datetime.strptime(fecha_str, FORMATO_FECHA).date()
    except ValueError:
        return None


def validar_tipo_licencia(tipo):
    return tipo in TIPOS_LICENCIA


def calcular_max_dias(tipo):
    return TIPOS_LICENCIA[tipo]["max_dias"]


def decidir(nombre_medico, rut_medico, nombre_funcionario, rut_funcionario,
            dias_reposo, fecha_emision_str, tipo_licencia):
    if not validar_tipo_licencia(tipo_licencia) or dias_reposo <= 0:
        return "Dato invalido", "Tipo de licencia fuera de rango (1-7) o dias de reposo invalidos"

    fecha_emision = parsear_fecha(fecha_emision_str)
    if fecha_emision is None:
        return "Dato invalido", "Formato de fecha invalido (use DD/MM/AAAA)"

    if not validar_rut(rut_medico) or not validar_rut(rut_funcionario):
        return "Dato invalido", "RUT del medico o funcionario con formato invalido"

    if fecha_emision > date.today():
        return "Rechazo - fecha invalida", "La fecha de emision es futura, no puede registrarse"

    max_dias = calcular_max_dias(tipo_licencia)
    if dias_reposo > max_dias:
        return "Rechazo - dias excedidos", f"Maximo {max_dias} dias para tipo {tipo_licencia}, se ingresaron {dias_reposo}"

    return "Aceptada", "Licencia registrada correctamente"


def mostrar_tabulate(registros):
    if registros:
        print(tabulate(registros, headers="keys", tablefmt="grid"))
    else:
        print("No hay registros de licencias medicas.")


RUTA_TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def buscar_patron(texto, patron):
    import re
    match = re.search(patron, texto, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def extraer_texto_pypdf2(ruta_pdf):
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(ruta_pdf)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text() or ""
        return texto
    except Exception as e:
        print(f"Error PyPDF2: {e}")
        return ""


def extraer_texto_ocr(ruta_pdf):
    try:
        import pytesseract
        import fitz
        from PIL import Image
        import io

        pytesseract.pytesseract.tesseract_cmd = RUTA_TESSERACT

        doc = fitz.open(ruta_pdf)
        texto_completo = ""

        for pagina in doc:
            pix = pagina.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            texto_completo += pytesseract.image_to_string(img, lang="spa") + "\n"

        doc.close()
        return texto_completo
    except Exception as e:
        print(f"Error OCR: {e}")
        return ""


def parsear_texto_licencia(texto):
    medico = buscar_patron(texto, r"Profesional\s*:\s*(.+?)(?:\n|Rut|$)")
    if not medico:
        medico = buscar_patron(texto, r"APELLIDO PATERNO\s*(.+?)(?:\n|APELLIDO MATERNO)")

    rut_medico = buscar_patron(texto, r"Profesional.*?Rut\s*:\s*(\d[\d\.\-]*\d)")
    if not rut_medico:
        rut_medico = buscar_patron(texto, r"RUN\s*[-:]?\s*(\d[\d\.\-]*\d)")

    funcionario = buscar_patron(texto, r"Datos Trabajador.*?Nombre\s*:\s*(.+?)(?:\n|Rut)")
    if not funcionario:
        funcionario = buscar_patron(texto, r"DATOS TRABAJADOR.*?NOMBRES?\s*(.+?)(?:\n|RUT)")

    rut_funcionario = buscar_patron(texto, r"Datos Trabajador.*?Rut\s*:\s*(\d[\d\.\-]*\d)")

    tipo_str = buscar_patron(texto, r"Tipo Licencia\s*:\s*(\d)")
    tipo = int(tipo_str) if tipo_str else None

    dias_str = buscar_patron(texto, r"N[°º]?\s*D[ií]as?\s*:\s*(\d+)")
    dias = int(dias_str) if dias_str else None

    import re
    fecha_grupo = re.search(r"Fecha\s*(?:Otorgamiento|Inicio)\s*:\s*(\d{2})[-/](\d{2})[-/](\d{4})", texto, re.IGNORECASE)
    if fecha_grupo:
        fecha = f"{fecha_grupo.group(1)}/{fecha_grupo.group(2)}/{fecha_grupo.group(3)}"
    else:
        fecha = None

    return medico, rut_medico, funcionario, rut_funcionario, dias, fecha, tipo


def detectar_tipo_pdf(ruta_pdf):
    texto = extraer_texto_pypdf2(ruta_pdf)
    if texto and len(texto.strip()) > 100:
        return "texto", texto
    return "escaneado", extraer_texto_ocr(ruta_pdf)


def procesar_pdf(ruta_pdf):
    if not os.path.exists(ruta_pdf):
        print(f"Error: No se encontro el archivo {ruta_pdf}")
        return None

    tipo_pdf, texto = detectar_tipo_pdf(ruta_pdf)
    print(f"Tipo de PDF detectado: {tipo_pdf}")

    if not texto or len(texto.strip()) < 50:
        print("Error: No se pudo extraer texto del PDF")
        return None

    datos = parsear_texto_licencia(texto)

    if not all(datos):
        print("Error: No se pudieron extraer todos los datos del PDF")
        print(f"Datos encontrados: medico={datos[0]}, rut_medico={datos[1]}, "
              f"funcionario={datos[2]}, rut_funcionario={datos[3]}, "
              f"dias={datos[4]}, fecha={datos[5]}, tipo={datos[6]}")
        return None

    medico, rut_medico, funcionario, rut_funcionario, dias, fecha, tipo = datos

    estado, motivo = decidir(
        medico, rut_medico, funcionario, rut_funcionario,
        dias, fecha, tipo
    )

    registro = {
        "medico": medico,
        "rut_medico": rut_medico,
        "funcionario": funcionario,
        "rut_funcionario": rut_funcionario,
        "dias_reposo": dias,
        "fecha_emision": fecha,
        "tipo_licencia": tipo,
        "estado": estado,
        "motivo": motivo,
        "fuente": "PDF",
    }

    registros = cargar()
    registros.append(registro)
    guardar(registros)

    print(f"\nPDF procesado: {os.path.basename(ruta_pdf)}")
    print(f"Medico: {medico} (RUT: {rut_medico})")
    print(f"Funcionario: {funcionario} (RUT: {rut_funcionario})")
    print(f"Dias: {dias} | Fecha: {fecha} | Tipo: {tipo}")
    print(f"Resultado: {estado}")
    print(f"Detalle: {motivo}\n")

    mostrar_tabulate(registros)
    return registro


def pedir_datos():
    nombre_medico = input("Nombre del medico: ").strip()
    rut_medico = input("RUT del medico (ej: 12.345.678-9): ").strip()
    nombre_funcionario = input("Nombre del funcionario: ").strip()
    rut_funcionario = input("RUT del funcionario (ej: 12.345.678-9): ").strip()
    dias_reposo = int(input("Dias de reposo: "))
    fecha_emision = input("Fecha de emision (DD/MM/AAAA): ").strip()
    tipo_licencia = int(input("Tipo de licencia (1-7): "))
    return nombre_medico, rut_medico, nombre_funcionario, rut_funcionario, dias_reposo, fecha_emision, tipo_licencia


def main():
    registros = cargar()

    nombre_medico, rut_medico, nombre_funcionario, rut_funcionario, dias_reposo, fecha_emision, tipo_licencia = pedir_datos()

    estado, motivo = decidir(
        nombre_medico, rut_medico, nombre_funcionario, rut_funcionario,
        dias_reposo, fecha_emision, tipo_licencia
    )

    registro = {
        "medico": nombre_medico,
        "rut_medico": rut_medico,
        "funcionario": nombre_funcionario,
        "rut_funcionario": rut_funcionario,
        "dias_reposo": dias_reposo,
        "fecha_emision": fecha_emision,
        "tipo_licencia": tipo_licencia,
        "estado": estado,
        "motivo": motivo,
    }

    print(f"\nResultado: {estado}")
    print(f"Detalle: {motivo}\n")

    registros.append(registro)
    guardar(registros)
    print("Registro guardado en datos.json\n")

    mostrar_tabulate(registros)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        procesar_pdf(sys.argv[1])
    else:
        main()
