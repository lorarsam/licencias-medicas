from django.db import models
from django.utils import timezone

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
