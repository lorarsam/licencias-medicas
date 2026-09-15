# Plan - Sistema de Licencias Medicas - Eva 2

## Apartado de Negocio

### Problema

Las empresas reciben licencias medicas y deben validar manualmente sus datos. Esto puede provocar errores y retrasar la tramitacion de cada licencia.

### Solucion

SIGERH permite registrar, evaluar y administrar licencias medicas mediante una aplicacion web Django. La aplicacion conserva la regla de decision de la ES1 y almacena los registros en SQLite.

La regla `decidir()` continua siendo la unica responsable de clasificar cada licencia en uno de cuatro resultados.

### Alcance De Eva 2

- **Entra**: base de datos SQLite, modelo Django, migraciones, carga inicial desde `datos.json`, administrador Django, operaciones CRUD, borrado logico, login, sesiones, grupos y permisos.
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

### Regla De Decision

| # | Condicion | Resultado |
|---|-----------|-----------|
| 1 | Nombre vacio, RUT invalido, dias invalidos, fecha invalida o tipo fuera de rango | Dato invalido |
| 2 | La fecha de emision es futura | Rechazo - fecha invalida |
| 3 | Los dias superan el maximo del tipo de licencia | Rechazo - dias excedidos |
| 4 | Todos los datos son validos | Aceptada |

La regla esta implementada en `solucion.py` y las vistas la importan mediante `decidir()` al crear o editar.

### Rutas Web

| Ruta | Funcion |
|------|---------|
| `/login/` | Inicio de sesion |
| `/logout/` | Cierre de sesion mediante POST |
| `/licencias/` | Listado de licencias activas |
| `/licencias/crear/` | Creacion |
| `/licencias/<id>/editar/` | Actualizacion |
| `/licencias/<id>/eliminar/` | Confirmacion y borrado logico |
| `/admin/` | Administrador Django |

`/resumen/` redirige al listado nuevo para conservar la ruta anterior.

### Roles Y Permisos

| Rol | Consultar | Crear | Editar | Eliminar |
|-----|-----------|-------|--------|----------|
| `viewer` | Si | No | No | No |
| `normal` | Si | Si | No | No |
| `admin` | Si | Si | Si | Si |

Los grupos y permisos se configuran con:

```powershell
python manage.py crear_roles
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
| `core/models.py` | Modelo y borrado logico |
| `core/forms.py` | Formularios de licencia y login |
| `core/views.py` | Login, CRUD y reutilizacion de `decidir()` |
| `core/decorators.py` | Autorizacion por rol |
| `core/admin.py` | Configuracion del administrador |
| `core/management/commands/cargar_datos.py` | Migracion inicial desde JSON |
| `core/management/commands/crear_roles.py` | Creacion de grupos y permisos |
| `miproyecto/settings.py` | SQLite, sesiones y autenticacion |
| `miproyecto/urls.py` | Rutas del sistema |
