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
        import pymupdf
        from PIL import Image
        import io

        pytesseract.pytesseract.tesseract_cmd = RUTA_TESSERACT

        doc = pymupdf.open(ruta_pdf)
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
    import re
    BANDERAS = re.IGNORECASE | re.DOTALL

    medico = None
    rut_medico = None
    funcionario = None
    rut_funcionario = None
    tipo = None
    dias = None
    fecha = None

    for patron in [
        r"Profesional\s*:\s*(.+?)(?:\n|Rut|$)",
        r"PROFESIONAL\s*:\s*(.+?)(?:\n|RUT|$)",
        r"DOCTOR[A]?\s*:\s*(.+?)(?:\n|$)",
    ]:
        m = re.search(patron, texto, BANDERAS)
        if m:
            medico = m.group(1).strip()
            break

    if not medico:
        m = re.search(
            r"RUN\s*[-:]?\s*(\d[\d\.\-]*\d).*?([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{2,})",
            texto, BANDERAS,
        )
        if m:
            rut_medico = m.group(1).strip()
            nombre = m.group(2).strip()
            nombre = re.sub(r"\s*RUT\s*$", "", nombre, flags=re.IGNORECASE)
            medico = nombre

    if not medico:
        m = re.search(r"TOSE\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+?)\s+RUT", texto)
        if m:
            medico = m.group(1).strip()

    for patron in [
        r"Profesional.*?Rut\s*:\s*(\d[\d\.\-]*\d)",
        r"PROFESIONAL.*?RUN\s*[-:]?\s*(\d[\d\.\-]*\d)",
        r"RUN\s*[-:]?\s*(\d[\d\.\-]*\d)",
    ]:
        m = re.search(patron, texto, BANDERAS)
        if m:
            rut_medico = m.group(1).strip()
            break

    if not rut_medico:
        m = re.search(r"(\d{6,8})\s*\|", texto)
        if m:
            rut_medico = m.group(1).strip()

    for patron in [
        r"Datos Trabajador.*?Nombre\s*:\s*(.+?)(?:\n|Rut)",
        r"DATOS TRABAJADOR.*?NOMBRES?\s*(.+?)(?:\n|RUT)",
        r"TRABAJADOR.*?NOMBRE[S]?\s*(.+?)(?:\n|RUN|RUT)",
    ]:
        m = re.search(patron, texto, BANDERAS)
        if m:
            funcionario = m.group(1).strip()
            break

    for patron in [
        r"Datos Trabajador.*?Rut\s*:\s*(\d[\d\.\-]*\d)",
        r"DATOS TRABAJADOR.*?RUN\s*[-:]?\s*(\d[\d\.\-]*\d)",
    ]:
        m = re.search(patron, texto, BANDERAS)
        if m:
            rut_funcionario = m.group(1).strip()
            break

    if not rut_funcionario:
        m = re.search(r"RUN\s*[-:]?\s*(\d[\d\.\-]*\d)", texto, BANDERAS)
        if m and rut_medico and m.group(1).strip() != rut_medico:
            rut_funcionario = m.group(1).strip()

    if not rut_funcionario:
        todos_ruts = re.findall(r"\b(\d{7,10})\b", texto)
        for r in todos_ruts:
            if r != rut_medico and r != "2026051674":
                rut_funcionario = r
                break

    for patron in [
        r"Tipo Licencia\s*:\s*(\d)",
        r"TIPO\s*(?:DE\s*)?LICENCIA\s*:\s*(\d)",
        r"TIPO\s*=\s*(\d)",
    ]:
        m = re.search(patron, texto, BANDERAS)
        if m:
            tipo = int(m.group(1))
            break

    if not tipo:
        m = re.search(r"CONTINUACION", texto, BANDERAS)
        if m:
            tipo = 1

    for patron in [
        r"N[°º]?\s*D[ií]as?\s*:\s*(\d+)",
        r"(\d+)\s*DIAS?\s*PREVIOS",
    ]:
        m = re.search(patron, texto, BANDERAS)
        if m:
            dias = int(m.group(1))
            break

    for patron in [
        r"Fecha\s*(?:Otorgamiento|Inicio)\s*:\s*(\d{2})[-/](\d{2})[-/](\d{4})",
        r"DESDE\s*:\s*(\d{2})[-/](\d{2})[-/](\d{4})",
        r"FECHA\s*INICIO\s*REPOSO\s*(\d{2})(\d{2})(\d{4})",
    ]:
        m = re.search(patron, texto, BANDERAS)
        if m:
            fecha = f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
            if not dias:
                hasta = re.search(r"HASTA\s*:\s*(\d{2})[-/](\d{2})[-/](\d{4})", texto, BANDERAS)
                if hasta:
                    try:
                        fi = datetime.strptime(fecha, "%d/%m/%Y")
                        ff = datetime.strptime(f"{hasta.group(1)}/{hasta.group(2)}/{hasta.group(3)}", "%d/%m/%Y")
                        dias = (ff - fi).days
                    except Exception:
                        pass
            break

    if not fecha:
        todas_fechas = re.findall(r"(\d{2})[-/](\d{2})[-/](\d{4})", texto)
        if len(todas_fechas) >= 1:
            fecha = f"{todas_fechas[0][0]}/{todas_fechas[0][1]}/{todas_fechas[0][2]}"
        if not dias and len(todas_fechas) >= 2:
            try:
                fi = datetime.strptime(f"{todas_fechas[0][0]}/{todas_fechas[0][1]}/{todas_fechas[0][2]}", "%d/%m/%Y")
                ff = datetime.strptime(f"{todas_fechas[1][0]}/{todas_fechas[1][1]}/{todas_fechas[1][2]}", "%d/%m/%Y")
                dias = (ff - fi).days
            except Exception:
                pass

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

    campos_faltantes = []
    if not datos[0]:
        campos_faltantes.append("medico")
    if not datos[1]:
        campos_faltantes.append("rut_medico")
    if not datos[4]:
        campos_faltantes.append("dias")
    if not datos[5]:
        campos_faltantes.append("fecha")
    if not datos[6]:
        campos_faltantes.append("tipo")

    if campos_faltantes:
        print("Error: No se pudieron extraer campos esenciales del PDF")
        print(f"Campos faltantes: {', '.join(campos_faltantes)}")
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
