from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

from core.models import ESTADO_CHOICES, LicenciaMedica
from solucion import (
    ATRIBUTOS_FORMULARIO,
    AYUDAS_FORMULARIO,
    ETIQUETAS_FORMULARIO,
    FORMATO_FECHA_HTML,
    LARGO_MAXIMO_NOMBRE,
    LARGO_MAXIMO_RUT,
    MENSAJE_CAMPO_REQUERIDO,
    MENSAJE_ENTERO_INVALIDO,
    MENSAJE_FECHA_WEB_INVALIDA,
    MENSAJE_OPCION_INVALIDA,
    OPCION_TIPO_INICIAL,
    TIPOS_LICENCIA,
    formatear_rut,
)


ERRORES_REQUERIDO = {"required": MENSAJE_CAMPO_REQUERIDO}
OPCIONES_TIPO_LICENCIA = (
    ("", OPCION_TIPO_INICIAL),
    *((codigo, f"{codigo} - {datos['nombre']}")
      for codigo, datos in TIPOS_LICENCIA.items()),
)


class LicenciaMedicaForm(forms.ModelForm):
    medico = forms.CharField(
        label=ETIQUETAS_FORMULARIO["nombre_medico"],
        max_length=LARGO_MAXIMO_NOMBRE,
        widget=forms.TextInput(attrs=ATRIBUTOS_FORMULARIO["nombre_medico"]),
        error_messages=ERRORES_REQUERIDO,
    )
    rut_medico = forms.CharField(
        label=ETIQUETAS_FORMULARIO["rut_medico"],
        max_length=LARGO_MAXIMO_RUT,
        help_text=AYUDAS_FORMULARIO["rut_medico"],
        widget=forms.TextInput(attrs=ATRIBUTOS_FORMULARIO["rut_medico"]),
        error_messages=ERRORES_REQUERIDO,
    )
    funcionario = forms.CharField(
        label=ETIQUETAS_FORMULARIO["nombre_funcionario"],
        max_length=LARGO_MAXIMO_NOMBRE,
        widget=forms.TextInput(attrs=ATRIBUTOS_FORMULARIO["nombre_funcionario"]),
        error_messages=ERRORES_REQUERIDO,
    )
    rut_funcionario = forms.CharField(
        label=ETIQUETAS_FORMULARIO["rut_funcionario"],
        max_length=LARGO_MAXIMO_RUT,
        help_text=AYUDAS_FORMULARIO["rut_funcionario"],
        widget=forms.TextInput(attrs=ATRIBUTOS_FORMULARIO["rut_funcionario"]),
        error_messages=ERRORES_REQUERIDO,
    )
    dias_reposo = forms.IntegerField(
        label=ETIQUETAS_FORMULARIO["dias_reposo"],
        widget=forms.NumberInput(attrs=ATRIBUTOS_FORMULARIO["dias_reposo"]),
        error_messages={
            "required": MENSAJE_CAMPO_REQUERIDO,
            "invalid": MENSAJE_ENTERO_INVALIDO,
        },
    )
    fecha_emision = forms.DateField(
        label=ETIQUETAS_FORMULARIO["fecha_emision"],
        help_text=AYUDAS_FORMULARIO["fecha_emision"],
        input_formats=(FORMATO_FECHA_HTML,),
        widget=forms.DateInput(
            format=FORMATO_FECHA_HTML,
            attrs=ATRIBUTOS_FORMULARIO["fecha_emision"],
        ),
        error_messages={
            "required": MENSAJE_CAMPO_REQUERIDO,
            "invalid": MENSAJE_FECHA_WEB_INVALIDA,
        },
    )
    tipo_licencia = forms.TypedChoiceField(
        label=ETIQUETAS_FORMULARIO["tipo_licencia"],
        choices=OPCIONES_TIPO_LICENCIA,
        coerce=int,
        widget=forms.Select(attrs=ATRIBUTOS_FORMULARIO["tipo_licencia"]),
        error_messages={
            "required": MENSAJE_CAMPO_REQUERIDO,
            "invalid_choice": MENSAJE_OPCION_INVALIDA,
        },
    )

    class Meta:
        model = LicenciaMedica
        fields = (
            "medico",
            "rut_medico",
            "funcionario",
            "rut_funcionario",
            "dias_reposo",
            "fecha_emision",
            "tipo_licencia",
        )

    def clean_rut_medico(self):
        return formatear_rut(self.cleaned_data["rut_medico"])

    def clean_rut_funcionario(self):
        return formatear_rut(self.cleaned_data["rut_funcionario"])


class FiltroLicenciaForm(forms.Form):
    q = forms.CharField(
        label="Buscar",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "control",
                "placeholder": "Nombre o RUT",
                "autocomplete": "off",
            }
        ),
    )
    estado = forms.ChoiceField(
        label="Estado",
        required=False,
        choices=(("", "Todos"), *ESTADO_CHOICES),
        widget=forms.Select(attrs={"class": "control"}),
    )
    tipo_licencia = forms.ChoiceField(
        label="Tipo de licencia",
        required=False,
        choices=(
            ("", "Todos"),
            *((codigo, f"{codigo} - {datos['nombre']}")
              for codigo, datos in TIPOS_LICENCIA.items()),
        ),
        widget=forms.Select(attrs={"class": "control"}),
    )
    creado_por = forms.ModelChoiceField(
        label="Ingresada por",
        required=False,
        queryset=get_user_model().objects.none(),
        empty_label="Todos",
        widget=forms.Select(attrs={"class": "control"}),
    )
    fecha_desde = forms.DateField(
        label="Fecha desde",
        required=False,
        input_formats=(FORMATO_FECHA_HTML,),
        widget=forms.DateInput(
            format=FORMATO_FECHA_HTML,
            attrs={"class": "control", "type": "date"},
        ),
    )
    fecha_hasta = forms.DateField(
        label="Fecha hasta",
        required=False,
        input_formats=(FORMATO_FECHA_HTML,),
        widget=forms.DateInput(
            format=FORMATO_FECHA_HTML,
            attrs={"class": "control", "type": "date"},
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["creado_por"].queryset = get_user_model().objects.filter(
            is_active=True,
        ).order_by("username")


class InicioSesionForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(
            attrs={
                "class": "control",
                "autocomplete": "username",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label="Contrasena",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "control",
                "autocomplete": "current-password",
            }
        ),
    )
