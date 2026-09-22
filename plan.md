# Plan - Sistema de Licencias Medicas - Eva 2

## Apartado de Negocio

### Problema

Las empresas reciben licencias medicas y deben validar manualmente sus datos. Esto puede provocar errores y retrasar la tramitacion de cada licencia.

### Solucion

SIGERH permite registrar, evaluar y administrar licencias medicas mediante una aplicacion web Django. La aplicacion conserva la regla de decision de la ES1 y almacena los registros en SQLite.

La regla `decidir()` continua siendo la unica responsable de clasificar cada licencia en uno de cuatro resultados.

### Alcance De Eva 2

- **Entra**: base de datos SQLite, modelos Django, migraciones, carga inicial desde `datos.json`, importacion de sanciones y administrador Django.
- **Entra**: operaciones CRUD, borrado logico, login, sesiones, grupos, permisos y rechazo de licencias emitidas por medicos sancionados.
- **Entra**: validacion de permisos en el servidor y proteccion CSRF para formularios POST.
- **Entra**: pruebas automatizadas de modelos, importacion, CRUD, autenticacion y autorizacion.
- **No entra**: OCR, carga de fotografias o PDF, API externa, correo y conexion con sistemas externos.
- **Compatibilidad**: `datos.json` se conserva como respaldo y fuente de migracion inicial; la aplicacion web consulta y modifica SQLite.

### MoSCoW

| Prioridad | Funcion |
|-----------|---------|
| **Must** | Mantener `decidir()` y sus cuatro resultados |
| **Must** | Configurar SQLite y crear migraciones Django |
| **Must** | Modelar una licencia mediante `LicenciaMedica` |
| **Must** | Importar los registros iniciales desde `datos.json` |
| **Must** | Administrar licencias desde `/admin/` |
| **Must** | Consultar licencias desde `/licencias/` |
| **Must** | Crear licencias desde `/licencias/crear/` |
| **Must** | Editar licencias desde `/licencias/<id>/editar/` |
| **Must** | Eliminar logicamente licencias desde `/licencias/<id>/eliminar/` |
| **Must** | Implementar login, logout y sesiones Django |
| **Must** | Implementar los roles `viewer`, `normal` y `admin` |
| **Must** | Consultar sanciones importadas y rechazar licencias durante una suspension vigente |
| **Must** | Actualizar `plan.md` e `ia.md` |
| **Should** | Mejorar reportes y filtros del listado |
| **Could** | Incorporar OCR en una etapa posterior |
| **Won't** | Guardar contrasenas en un modelo propio |
| **Won't** | Usar una API o servicio externo |
| **Won't** | Reescribir la regla de decision en las vistas |

## Apartado Tecnico

### Base De Datos

La aplicacion utiliza SQLite mediante la configuracion ORM de Django:

```text
db.sqlite3
```

El archivo local esta excluido mediante `.gitignore`. Las tablas se crean con:

```powershell
python manage.py makemigrations
python manage.py migrate
```

### Modelo `LicenciaMedica`

El modelo contiene:

- `medico`
- `rut_medico`
- `funcionario`
- `rut_funcionario`
- `dias_reposo`
- `fecha_emision`
- `tipo_licencia`
- `estado`
- `motivo`
- `fecha`
- `eliminado`
- `fecha_eliminacion`

El borrado es logico: el registro permanece en la base y deja de aparecer en el listado activo.

### Modelo `MedicoSancionado`

Las sanciones se importan desde `suseso.sqlite3` hacia el modelo `MedicoSancionado`. El
RUT se normaliza antes de comparar y cada sancion conserva su periodo de suspension,
oficio, fuente y datos originales.

La carga se ejecuta con:

```powershell
python manage.py importar_sanciones --path suseso.sqlite3
```

No existe ningun medico sancionado escrito en el codigo. La informacion proviene de la
fuente importada y puede actualizarse ejecutando nuevamente el comando.

### Regla De Decision

| # | Condicion | Resultado |
|---|-----------|-----------|
| 1 | Nombre vacio, RUT invalido, dias invalidos, fecha invalida o tipo fuera de rango | Dato invalido |
| 2 | La fecha de emision es futura | Rechazo - fecha invalida |
| 3 | Los dias superan el maximo del tipo de licencia | Rechazo - dias excedidos |
| 4 | Todos los datos son validos | Aceptada |

La regla base esta implementada en `solucion.py` y se importa mediante `decidir()` al
crear o editar. Luego, `evaluar_licencia()` realiza una verificacion adicional: si el
resultado base seria `Aceptada` y el RUT tiene una suspension vigente para la fecha de
emision, el resultado se cambia a `Rechazo - medico sancionado`.

La regla `decidir()` no fue reescrita ni duplicada.

### Rutas Web

| Ruta | Funcion |
|------|---------|
| `/login/` | Inicio de sesion |
| `/logout/` | Cierre de sesion mediante POST |
| `/licencias/` | Listado de licencias activas con filtros |
| `/licencias/crear/` | Creacion |
| `/licencias/<id>/editar/` | Actualizacion |
| `/licencias/<id>/eliminar/` | Confirmacion y borrado logico |
| `/admin/` | Administrador Django |

`/resumen/` redirige al listado nuevo para conservar la ruta anterior.

### Filtros Y Usuario Creador

Cada licencia registra el usuario que la ingreso mediante `creado_por`. El
listado filtra por busqueda de nombre o RUT, usuario creador, estado, tipo de
licencia y rango de fechas de emision. Los filtros viajan por `GET` para que
las metricas reflejen los resultados consultados.

### RUT

Los campos de RUT aceptan puntos, guion, sin formato y `k` minuscula. El
backend normaliza y guarda el formato `12.345.678-5` y el frontend aplica el
mismo formato al terminar de escribir. La validacion del RUT se mantiene en el
servidor y no depende de JavaScript.

### Respaldo De Licencias

`exportar_licencias` genera un respaldo de licencias sin contrasenas ni
sesiones; `importar_licencias` lo restaura vinculando el usuario creador si
existe en el destino. El archivo generado queda excluido del repositorio.

### Roles Y Permisos

| Rol | Consultar | Crear | Editar | Eliminar |
|-----|-----------|-------|--------|----------|
| `viewer` | Si | No | No | No |
| `normal` | Si | Si | No | No |
| `admin` | Si | Si | Si | Si |

Los grupos y permisos se configuran con:

```powershell
python manage.py crear_roles
python manage.py importar_sanciones --path suseso.sqlite3
```

Las contrasenas se administran exclusivamente mediante el sistema de usuarios de Django.

### Comandos De Verificacion

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py createsuperuser
python manage.py runserver
```

La carga inicial y la configuracion de roles se ejecutan con:

```powershell
python manage.py cargar_datos
python manage.py crear_roles
```

### Archivos Principales

| Archivo | Responsabilidad |
|---------|-----------------|
| `core/models.py` | Modelo, usuario creador y borrado logico |
| `core/forms.py` | Formularios de licencia, login y filtros |
| `core/views.py` | Login, CRUD, filtros y reutilizacion de `decidir()` |
| `core/services.py` | Verificacion de sanciones y evaluacion adicional |
| `core/constants.py` | Estado de rechazo por sancion y situacion del medico |
| `core/decorators.py` | Autorizacion por rol |
| `core/admin.py` | Configuracion del administrador |
| `core/management/commands/importar_sanciones.py` | Importacion de sanciones con `--limit` |
| `core/management/commands/cargar_datos.py` | Migracion inicial desde JSON |
| `core/management/commands/exportar_licencias.py` | Respaldo de licencias sin credenciales |
| `core/management/commands/importar_licencias.py` | Restauracion de licencias |
| `core/management/commands/crear_roles.py` | Creacion de grupos y permisos |
| `core/static/core/js/rut.js` | Formateo automatico de RUT |
| `miproyecto/settings.py` | SQLite, sesiones, autenticacion y hosts permitidos |
| `miproyecto/urls.py` | Rutas del sistema |
