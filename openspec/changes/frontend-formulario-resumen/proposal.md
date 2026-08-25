## Why

El sistema solo permite ingresar licencias desde la consola, lo que limita el uso de la vista web a una consulta pasiva. Se requiere completar el flujo web para registrar licencias y revisar inmediatamente el resultado sin duplicar reglas ni valores en la capa de presentacion.

## What Changes

- Ampliar `/resumen/` con un formulario para los siete datos de una licencia medica.
- Procesar el formulario con Django y reutilizar `crear_registro()`, `cargar()` y `guardar()` desde `solucion.py`.
- Mantener los cuatro resultados existentes y mostrar el registro procesado en el resumen.
- Separar los estilos del template y entregar una interfaz responsiva para escritorio y dispositivos moviles.
- Proteger los envios POST con CSRF y aplicar el patron POST/Redirect/GET.
- Centralizar textos, rutas, formatos, clases de estado y opciones funcionales en constantes; no duplicar reglas de negocio en formularios, vistas o templates.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `licencia-medica`: ampliar la vista web para ingresar, validar, guardar y visualizar licencias medicas mediante un formulario Django.

## Impact

- Codigo Django: `core/forms.py`, `core/views.py`, `miproyecto/urls.py` y `miproyecto/settings.py`.
- Presentacion: templates de `core/templates/` y nuevos estilos bajo `core/static/`.
- Dominio y persistencia: se reutilizan `solucion.py` y `datos.json` sin introducir base de datos ni API.
- Pruebas: cobertura del formulario, flujo POST, estados de decision y renderizado del resumen.
