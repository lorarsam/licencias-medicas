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
    main()
