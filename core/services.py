from datetime import date

from core.constants import ESTADO_RECHAZO_SANCION
from core.models import MedicoSancionado
from solucion import ESTADO_ACEPTADA, decidir, parsear_fecha


def normalizar_rut(rut):
    if not isinstance(rut, str):
        return ""
    return rut.replace(".", "").replace("-", "").replace(" ", "").upper()


def buscar_sancion_activa(rut_medico, fecha_emision):
    rut_normalizado = normalizar_rut(rut_medico)
    if not rut_normalizado or not isinstance(fecha_emision, date):
        return None

    return MedicoSancionado.objects.filter(
        rut_medico=rut_normalizado,
        inicio_suspension__lte=fecha_emision,
        fin_suspension__gte=fecha_emision,
    ).first()


def evaluar_licencia(
    medico,
    rut_medico,
    funcionario,
    rut_funcionario,
    dias_reposo,
    fecha_emision,
    tipo_licencia,
):
    estado, motivo = decidir(
        medico,
        rut_medico,
        funcionario,
        rut_funcionario,
        dias_reposo,
        fecha_emision,
        tipo_licencia,
    )
    sancion = None
    fecha = parsear_fecha(fecha_emision)
    if estado == ESTADO_ACEPTADA:
        sancion = buscar_sancion_activa(rut_medico, fecha)
        if sancion:
            periodo = (
                f"{sancion.inicio_suspension:%d/%m/%Y} al "
                f"{sancion.fin_suspension:%d/%m/%Y}"
            )
            motivo = (
                f"El medico {sancion.nombre_medico} esta sancionado para emitir "
                f"licencias durante el periodo {periodo}."
            )
            if sancion.numero_oficio:
                motivo += f" Oficio: {sancion.numero_oficio}."
            estado = ESTADO_RECHAZO_SANCION

    return estado, motivo, sancion
