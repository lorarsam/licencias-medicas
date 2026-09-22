import json
from datetime import date, datetime
from pathlib import Path

from tabulate import tabulate


BASE_DIR = Path(__file__).resolve().parent
NOMBRE_ARCHIVO_JSON = "datos.json"
ARCHIVO_JSON = BASE_DIR / NOMBRE_ARCHIVO_JSON
FORMATO_FECHA = "%d/%m/%Y"
FORMATO_FECHA_HTML = "%Y-%m-%d"
MASCARA_FECHA = "DD/MM/AAAA"
CODIFICACION = "utf-8"
FORMATO_TABLA = "grid"
LARGO_MAXIMO_NOMBRE = 120
LARGO_MAXIMO_RUT = 12

RUTA_RESUMEN = "resumen/"
NOMBRE_RUTA_RESUMEN = "resumen"
PLANTILLA_RESUMEN = "resumen.html"
RUTA_ESTILOS = "core/css/app.css"
METODO_POST = "POST"
PARAMETRO_REGISTRO_GUARDADO = "guardada"
VALOR_PARAMETRO_ACTIVO = "1"

ESTADO_INVALIDO = "Dato invalido"
ESTADO_RECHAZO_FECHA = "Rechazo - fecha invalida"
ESTADO_RECHAZO_DIAS = "Rechazo - dias excedidos"
ESTADO_ACEPTADA = "Aceptada"

CLASES_ESTADO = {
    ESTADO_ACEPTADA: "aceptada",
    ESTADO_RECHAZO_FECHA: "rechazada",
    ESTADO_RECHAZO_DIAS: "rechazada",
    ESTADO_INVALIDO: "invalido",
}
CLASE_ESTADO_DESCONOCIDO = "invalido"

MENSAJE_NOMBRES_INVALIDOS = "Nombre del medico o funcionario vacio"
MENSAJE_RUT_INVALIDO = "RUT del medico o funcionario invalido"
MENSAJE_FECHA_INVALIDA = f"Formato de fecha invalido (use {MASCARA_FECHA})"
MENSAJE_DIAS_INVALIDOS = "dias de reposo invalidos"
MENSAJE_TIPO_INVALIDO = "Tipo de licencia fuera de rango (1-7)"
MENSAJE_FECHA_FUTURA = "La fecha de emision es futura"
MENSAJE_ACEPTADA = "Licencia registrada correctamente"
MENSAJE_CANCELADO = "Ejecucion cancelada por el usuario"
MENSAJE_SIN_REGISTROS = "No hay registros de licencias medicas."
MENSAJE_REGISTRO_GUARDADO = f"Registro guardado en {NOMBRE_ARCHIVO_JSON}"
NOMBRE_TIPO_DESCONOCIDO = "Desconocido"
MENSAJE_CAMPO_REQUERIDO = "Este campo es obligatorio."
MENSAJE_ENTERO_INVALIDO = "Ingrese un numero entero."
MENSAJE_FECHA_WEB_INVALIDA = f"Ingrese una fecha valida en formato {MASCARA_FECHA}."
MENSAJE_OPCION_INVALIDA = "Seleccione un tipo de licencia valido."
OPCION_TIPO_INICIAL = "Seleccione un tipo de licencia"
CLASE_CONTROL_FORMULARIO = "control"
CLASE_INDICADOR_TOTAL = "total"

PROMPTS = {
    "nombre_medico": "Nombre del medico: ",
    "rut_medico": "RUT del medico (ej: 12.345.678-5): ",
    "nombre_funcionario": "Nombre del funcionario: ",
    "rut_funcionario": "RUT del funcionario (ej: 12.345.678-5): ",
    "dias_reposo": "Dias de reposo: ",
    "fecha_emision": "Fecha de emision (DD/MM/AAAA): ",
    "tipo_licencia": "Tipo de licencia (1-7): ",
}

ETIQUETAS_FORMULARIO = {
    "nombre_medico": "Nombre del medico",
    "rut_medico": "RUT del medico",
    "nombre_funcionario": "Nombre del funcionario",
    "rut_funcionario": "RUT del funcionario",
    "dias_reposo": "Dias de reposo",
    "fecha_emision": "Fecha de emision",
    "tipo_licencia": "Tipo de licencia",
}

AYUDAS_FORMULARIO = {
    "rut_medico": "Formato sugerido: 12.345.678-5",
    "rut_funcionario": "Formato sugerido: 11.111.111-1",
    "fecha_emision": f"Formato requerido: {MASCARA_FECHA}",
}

ATRIBUTOS_FORMULARIO = {
    "nombre_medico": {
        "class": CLASE_CONTROL_FORMULARIO,
        "placeholder": "Ej. Dra. Ana Perez",
        "autocomplete": "off",
    },
    "rut_medico": {
        "class": CLASE_CONTROL_FORMULARIO,
        "placeholder": "12.345.678-5",
        "autocomplete": "off",
        "data-rut": "true",
    },
    "nombre_funcionario": {
        "class": CLASE_CONTROL_FORMULARIO,
        "placeholder": "Ej. Luis Gonzalez",
        "autocomplete": "off",
    },
    "rut_funcionario": {
        "class": CLASE_CONTROL_FORMULARIO,
        "placeholder": "11.111.111-1",
        "autocomplete": "off",
        "data-rut": "true",
    },
    "dias_reposo": {
        "class": CLASE_CONTROL_FORMULARIO,
        "placeholder": "Ej. 7",
        "inputmode": "numeric",
    },
    "fecha_emision": {
        "class": CLASE_CONTROL_FORMULARIO,
        "type": "date",
    },
    "tipo_licencia": {
        "class": CLASE_CONTROL_FORMULARIO,
    },
}

TEXTOS_WEB = {
    "idioma": "es",
    "titulo_pagina": "SIGERH | Licencias medicas",
    "saltar_contenido": "Saltar al contenido principal",
    "marca": "SIGERH",
    "marca_inicial": "S",
    "area": "Personas y cumplimiento",
    "titulo_principal": "Gestion de licencias medicas",
    "descripcion_principal": (
        "Evalua antecedentes, aplica las reglas vigentes y conserva un registro "
        "claro para el equipo de personas."
    ),
    "seccion_formulario": "Registrar una licencia",
    "seccion_formulario_numero": "01",
    "descripcion_formulario": (
        "Ingrese los antecedentes del medico, del funcionario y del reposo."
    ),
    "campos_obligatorios": "Todos los campos son obligatorios.",
    "boton_guardar": "Evaluar y registrar",
    "error_formulario": "Revise los campos marcados antes de continuar.",
    "confirmacion": "Licencia evaluada y registrada correctamente.",
    "indicador_total": "Total",
    "indicador_aceptadas": "Aceptadas",
    "indicador_rechazadas": "Rechazadas",
    "indicador_invalidas": "Datos invalidos",
    "boton_crear": "Crear licencia",
    "accion_editar": "Editar",
    "accion_eliminar": "Eliminar",
    "seccion_registros": "Registro de licencias",
    "seccion_registros_numero": "02",
    "descripcion_registros": "Resultados calculados con las reglas centralizadas del sistema.",
    "sin_registros": "No hay licencias medicas registradas",
    "sin_registros_detalle": "Los registros procesados desde este formulario apareceran aqui.",
    "sin_registros_marca": "0",
    "tabla_etiqueta": "Listado de licencias medicas",
    "usuario_creador": "Ingresada por",
    "pie": f"Persistencia local en {NOMBRE_ARCHIVO_JSON}",
}

ENCABEZADOS_TABLA = {
    "medico": "Medico tratante",
    "rut_medico": "RUT del medico",
    "funcionario": "Funcionario",
    "rut_funcionario": "RUT del funcionario",
    "dias_reposo": "Dias",
    "fecha_emision": "Fecha",
    "tipo_licencia": "Tipo de licencia",
    "estado": "Estado",
    "motivo": "Motivo",
    "acciones": "Acciones",
    "situacion_medico": "Situacion medico",
}

TIPOS_LICENCIA = {
    1: {"nombre": "Enfermedad o accidente comun", "max_dias": 30},
    2: {"nombre": "Medicina preventiva", "max_dias": 2},
    3: {"nombre": "Licencia pre y postnatal", "max_dias": 180},
    4: {"nombre": "Enfermedad grave del nino menor de un anio", "max_dias": 180},
    5: {"nombre": "Accidente del trabajo o del trayecto", "max_dias": 365},
    6: {"nombre": "Enfermedad profesional", "max_dias": 365},
    7: {"nombre": "Patologias del embarazo", "max_dias": 84},
}

FACTORES_RUT = (2, 3, 4, 5, 6, 7)
MODULO_RUT = 11
RESULTADO_DV_K = 10
RESULTADO_DV_CERO = 11
DIGITO_RUT_K = "K"
DIGITO_RUT_CERO = "0"


def cargar():
    if not ARCHIVO_JSON.exists():
        return []

    try:
        with ARCHIVO_JSON.open("r", encoding=CODIFICACION) as archivo:
            return json.load(archivo)
    except json.JSONDecodeError:
        return []


def guardar(registros):
    with ARCHIVO_JSON.open("w", encoding=CODIFICACION) as archivo:
        json.dump(registros, archivo, indent=2, ensure_ascii=False)


def validar_rut(rut):
    if not isinstance(rut, str):
        return False

    rut_limpio = rut.replace(".", "").replace("-", "").strip().upper()
    if len(rut_limpio) < 2:
        return False

    cuerpo = rut_limpio[:-1]
    digito_ingresado = rut_limpio[-1]
    if not cuerpo.isdigit() or not (
        digito_ingresado.isdigit() or digito_ingresado == DIGITO_RUT_K
    ):
        return False

    total = 0
    for indice, digito in enumerate(reversed(cuerpo)):
        factor = FACTORES_RUT[indice % len(FACTORES_RUT)]
        total += int(digito) * factor

    resultado = MODULO_RUT - (total % MODULO_RUT)
    if resultado == RESULTADO_DV_CERO:
        digito_calculado = DIGITO_RUT_CERO
    elif resultado == RESULTADO_DV_K:
        digito_calculado = DIGITO_RUT_K
    else:
        digito_calculado = str(resultado)

    return digito_ingresado == digito_calculado


def parsear_fecha(fecha_str):
    if not isinstance(fecha_str, str):
        return None

    try:
        return datetime.strptime(fecha_str, FORMATO_FECHA).date()
    except ValueError:
        return None


def validar_tipo_licencia(tipo):
    return tipo in TIPOS_LICENCIA


def calcular_max_dias(tipo):
    return TIPOS_LICENCIA[tipo]["max_dias"]


def convertir_entero(valor):
    try:
        return int(valor)
    except ValueError:
        return valor


def normalizar_rut(rut):
    if not isinstance(rut, str):
        return ""
    return rut.replace(".", "").replace("-", "").replace(" ", "").upper()


def formatear_rut(rut):
    rut_limpio = normalizar_rut(rut)
    if len(rut_limpio) < 2:
        return rut_limpio

    cuerpo, digito_verificador = rut_limpio[:-1], rut_limpio[-1]
    if not cuerpo.isdigit() or not (
        digito_verificador.isdigit() or digito_verificador == DIGITO_RUT_K
    ):
        return rut_limpio

    grupos = []
    while cuerpo:
        grupos.append(cuerpo[-3:])
        cuerpo = cuerpo[:-3]
    return ".".join(reversed(grupos)) + f"-{digito_verificador}"


def obtener_motivo_invalido(nombre_medico, rut_medico, nombre_funcionario,
                            rut_funcionario, dias_reposo, fecha_emision,
                            tipo_licencia):
    nombres_validos = (
        isinstance(nombre_medico, str)
        and bool(nombre_medico.strip())
        and isinstance(nombre_funcionario, str)
        and bool(nombre_funcionario.strip())
    )
    if not nombres_validos:
        return MENSAJE_NOMBRES_INVALIDOS
    elif not validar_rut(rut_medico) or not validar_rut(rut_funcionario):
        return MENSAJE_RUT_INVALIDO
    elif not isinstance(dias_reposo, int) or dias_reposo <= 0:
        return MENSAJE_DIAS_INVALIDOS
    elif not validar_tipo_licencia(tipo_licencia):
        return MENSAJE_TIPO_INVALIDO
    elif fecha_emision is None:
        return MENSAJE_FECHA_INVALIDA
    else:
        return None


def decidir(nombre_medico, rut_medico, nombre_funcionario, rut_funcionario,
            dias_reposo, fecha_emision_str, tipo_licencia):
    fecha_emision = parsear_fecha(fecha_emision_str)
    motivo_invalido = obtener_motivo_invalido(
        nombre_medico, rut_medico, nombre_funcionario, rut_funcionario,
        dias_reposo, fecha_emision, tipo_licencia,
    )

    if motivo_invalido:
        return ESTADO_INVALIDO, motivo_invalido
    elif fecha_emision > date.today():
        return ESTADO_RECHAZO_FECHA, MENSAJE_FECHA_FUTURA
    elif dias_reposo > calcular_max_dias(tipo_licencia):
        max_dias = calcular_max_dias(tipo_licencia)
        motivo = f"Maximo {max_dias} dias para tipo {tipo_licencia}, se ingresaron {dias_reposo}"
        return ESTADO_RECHAZO_DIAS, motivo
    else:
        return ESTADO_ACEPTADA, MENSAJE_ACEPTADA


def crear_registro(nombre_medico, rut_medico, nombre_funcionario, rut_funcionario,
                   dias_reposo, fecha_emision, tipo_licencia):
    rut_medico = formatear_rut(rut_medico)
    rut_funcionario = formatear_rut(rut_funcionario)
    estado, motivo = decidir(
        nombre_medico, rut_medico, nombre_funcionario, rut_funcionario,
        dias_reposo, fecha_emision, tipo_licencia,
    )
    return {
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


def mostrar_tabulate(registros):
    if registros:
        print(tabulate(registros, headers="keys", tablefmt=FORMATO_TABLA))
    else:
        print(MENSAJE_SIN_REGISTROS)


def pedir_datos():
    nombre_medico = input(PROMPTS["nombre_medico"]).strip()
    rut_medico = input(PROMPTS["rut_medico"]).strip()
    nombre_funcionario = input(PROMPTS["nombre_funcionario"]).strip()
    rut_funcionario = input(PROMPTS["rut_funcionario"]).strip()
    dias_reposo = convertir_entero(input(PROMPTS["dias_reposo"]).strip())
    fecha_emision = input(PROMPTS["fecha_emision"]).strip()
    tipo_licencia = convertir_entero(input(PROMPTS["tipo_licencia"]).strip())
    return (
        nombre_medico, rut_medico, nombre_funcionario, rut_funcionario,
        dias_reposo, fecha_emision, tipo_licencia,
    )


def main():
    datos = pedir_datos()
    registro = crear_registro(*datos)
    registros = cargar()
    registros.append(registro)
    guardar(registros)

    print(f"\nResultado: {registro['estado']}")
    print(f"Detalle: {registro['motivo']}\n")
    print(f"{MENSAJE_REGISTRO_GUARDADO}\n")
    mostrar_tabulate(registros)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{MENSAJE_CANCELADO}")
