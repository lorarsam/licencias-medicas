# Uso De IA En El Proyecto

## Herramienta Utilizada

Se utilizo OpenCode como herramienta de inteligencia artificial para analizar el proyecto, revisar las instrucciones de `Migracion-ES1-a-Eva2.pdf`, proponer la arquitectura de Eva 2 y apoyar la implementacion y verificacion del codigo.

## Consultas Realizadas

Las consultas principales fueron:

1. "En base a este proyecto, ahora hay que hacer lo siguiente: configurar una base de datos, utilizar el administrador de Django, implementar CRUD, sesiones y seguridad."
2. "Lee `Migracion-ES1-a-Eva2.pdf` y comprueba las instrucciones y pasos a seguir."
3. "Dime los pasos a seguir segun las instrucciones."
4. "Planifiquemos etapa 1."
5. "Planifica la creacion del modelo LicenciaMedica, las migraciones de SQLite y los roles viewer, normal y admin sin duplicar decidir()."
6. "Procede con la etapa 1", seguida de solicitudes para implementar la migracion de datos, el administrador, el CRUD y la autenticacion por roles.
7. "El medico ingresado es un medico sancionado; debe mostrarse un aviso y rechazarse la licencia sin hardcodear personas."

## Orientaciones Recibidas

La herramienta identifico que la version ES1 no tenia modelos Django, SQLite, administrador, CRUD completo, autenticacion ni sesiones. Tambien indico que la funcion `decidir()` debia conservarse y reutilizarse desde las vistas sin copiar su cadena de condiciones.

Las orientaciones tecnicas principales fueron:

- Crear el modelo `LicenciaMedica` a partir de los campos de `datos.json`.
- Usar SQLite y migraciones Django.
- Importar los datos existentes antes de abandonar JSON como fuente web.
- Registrar el modelo en `admin.py` con columnas, filtros y buscador.
- Separar las operaciones CRUD en vistas independientes.
- Usar borrado logico con `eliminado` y `fecha_eliminacion`.
- Usar usuarios, sesiones y grupos incluidos en Django.
- Aplicar permisos en el servidor y no solamente ocultar botones en las plantillas.
- Probar accesos directos a las rutas protegidas.
- Consultar una fuente de sanciones por RUT normalizado y periodo de suspension.

## Correcciones Y Decisiones Personales

No se copiaron todas las sugerencias de forma automatica. Se realizaron estas correcciones:

- La IA propuso inicialmente agregar OCR por fotografia o PDF, pero el documento de Eva 2 no lo exige. Se dejo fuera del alcance obligatorio para priorizar SQLite, Admin, CRUD, login y roles.
- Se mantuvo un unico modelo `LicenciaMedica` en vez de crear modelos separados para medico y funcionario, porque el PDF indica transformar las claves existentes en campos del modelo.
- No se creo un modelo propio de contrasenas. Se utilizo `django.contrib.auth` y las sesiones incorporadas en Django.
- No se dejaron permisos solo en las plantillas. Las vistas usan `requiere_rol()` para validar el acceso en el servidor.
- No se duplico la cadena de `if/elif` de la regla. Crear y editar llaman a `decidir()` desde `solucion.py`.
- El borrado fisico sugerido para un CRUD comun se reemplazo por borrado logico, de acuerdo con el modelo solicitado en el PDF.
- La importacion desde `datos.json` se implemento como comando Django transaccional e idempotente para evitar duplicados.
- Para las sanciones no se escribio ningun medico en el codigo. Se importo la base `suseso.sqlite3` al modelo `MedicoSancionado` y se comparan RUT y fechas mediante el ORM.
- La comprobacion de sanciones se implemento como una capa posterior a `decidir()`, conservando los cuatro resultados originales cuando la licencia no esta sancionada.

## Verificacion Realizada

La suite de pruebas verifica:

- SQLite y migraciones.
- Importacion inicial e idempotencia.
- Administrador Django.
- Login y logout.
- Sesiones.
- Permisos de `viewer`, `normal` y `admin`.
- Creacion, consulta, edicion y borrado logico.
- CSRF en operaciones POST.
- Reutilizacion de `decidir()` y sus cuatro resultados.
- Rechazo de licencias cuando el medico esta sancionado durante la fecha de emision.

La implementacion se verifico con:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

La implementacion de sanciones se verifico con datos importados desde `suseso.sqlite3`,
incluyendo coincidencias con RUT escrito con puntos y guion, limites inclusivos del
periodo de suspension y medicos sin sancion vigente.
