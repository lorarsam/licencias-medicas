from django.db import models
from django.utils import timezone

from core.constants import ESTADO_RECHAZO_SANCION
from solucion import (
    ESTADO_ACEPTADA,
    ESTADO_INVALIDO,
    ESTADO_RECHAZO_DIAS,
    ESTADO_RECHAZO_FECHA,
    TIPOS_LICENCIA,
)


TIPOS_LICENCIA_CHOICES = tuple(
    (codigo, datos["nombre"])
    for codigo, datos in TIPOS_LICENCIA.items()
)

ESTADO_CHOICES = (
    (ESTADO_ACEPTADA, ESTADO_ACEPTADA),
    (ESTADO_RECHAZO_FECHA, ESTADO_RECHAZO_FECHA),
    (ESTADO_RECHAZO_DIAS, ESTADO_RECHAZO_DIAS),
    (ESTADO_RECHAZO_SANCION, ESTADO_RECHAZO_SANCION),
    (ESTADO_INVALIDO, ESTADO_INVALIDO),
)


class LicenciaMedica(models.Model):
    medico = models.CharField(max_length=120)
    rut_medico = models.CharField(max_length=12)
    funcionario = models.CharField(max_length=120)
    rut_funcionario = models.CharField(max_length=12)
    dias_reposo = models.IntegerField()
    fecha_emision = models.DateField()
    tipo_licencia = models.PositiveSmallIntegerField(
        choices=TIPOS_LICENCIA_CHOICES,
    )
    estado = models.CharField(
        max_length=40,
        choices=ESTADO_CHOICES,
    )
    motivo = models.TextField()
    fecha = models.DateTimeField(default=timezone.now, editable=False)
    eliminado = models.BooleanField(default=False)
    fecha_eliminacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-fecha",)

    def __str__(self):
        return f"{self.funcionario} - {self.fecha_emision:%d/%m/%Y}"

    def soft_delete(self):
        self.eliminado = True
        self.fecha_eliminacion = timezone.now()
        self.save(update_fields=("eliminado", "fecha_eliminacion"))


class MedicoSancionado(models.Model):
    rut_medico = models.CharField(max_length=20)
    nombre_medico = models.CharField(max_length=240)
    numero_oficio = models.CharField(max_length=80, blank=True)
    fecha_oficio = models.DateField(null=True, blank=True)
    monto_multa_utm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    suspension_dias = models.PositiveIntegerField(null=True, blank=True)
    inicio_suspension = models.DateField(null=True, blank=True)
    fin_suspension = models.DateField(null=True, blank=True)
    fuente_url = models.URLField(max_length=500)
    fecha_carga = models.DateTimeField(default=timezone.now, editable=False)
    datos_origen = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-inicio_suspension", "nombre_medico")
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "rut_medico",
                    "numero_oficio",
                    "inicio_suspension",
                    "fin_suspension",
                ),
                name="unique_sancion_medico_periodo",
            ),
        )

    def __str__(self):
        return f"{self.nombre_medico} - {self.rut_medico}"
