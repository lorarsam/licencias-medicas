# SIGERH

Sistema Django para registrar y evaluar licencias medicas.

## Instalacion

Requiere Python 3.12 o superior.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Completa `SECRET_KEY` en `.env`. No publiques el archivo `.env` ni claves reales.
El valor `ALLOWED_HOSTS` de `.env` lista los hosts permitidos; agrega la IP del
computador si se accede desde otro equipo.

## Base de datos y usuario demo

```powershell
python manage.py migrate
python manage.py crear_usuario_demo --password Eva2backend
```

El comando es seguro de repetir y deja configurados los permisos de consulta,
creacion, edicion y eliminacion de licencias para el usuario demo.

## Sanciones de SUSESO

`suseso.sqlite3` contiene un snapshot publico de sanciones obtenido mediante
scraping de la pagina oficial de SUSESO y se incluye en el repositorio. La
fuente publica es:

https://www.suseso.gob.cl/609/w3-propertyvalue-799701.html

Importa las sanciones con:

```powershell
python manage.py importar_sanciones --path suseso.sqlite3
```

Para probar solo con un subconjunto:

```powershell
python manage.py importar_sanciones --path suseso.sqlite3 --limit 10
```

La importacion carga o actualiza `MedicoSancionado` sin eliminar las licencias
existentes. Si el medico tiene una suspension vigente en la fecha de emision, la
licencia se rechaza con el estado `Rechazo - medico sancionado`. El snapshot
puede actualizarse re-ejecutando el importador con una version mas reciente de
la base.

## Respaldo y restauracion de licencias

`db.sqlite3` queda fuera del repositorio. Para conservar el historial al cambiar
de equipo, exporta las licencias (sin contrasenas ni sesiones) y restaurarlas en
el nuevo equipo:

```powershell
python manage.py exportar_licencias --path licencias_respaldo.json
python manage.py importar_licencias --path licencias_respaldo.json
```

El respaldo conserva el nombre del usuario creador; si ese usuario no existe en el
nuevo equipo, la licencia se restaura sin vincularlo. El archivo de respaldo esta
excluido del repositorio.

## Uso compartido entre computadores

Se debe ejecutar una sola instancia de Django en el computador anfitrion:

```powershell
python manage.py runserver 0.0.0.0:8000
```

El otro computador accede con `http://IP_DEL_ANFITRION:8000`. Agrega esa IP a
`ALLOWED_HOSTS` en `.env` y limita el acceso a la red interna. No se debe ejecutar
una copia local por equipo ni abrir `db.sqlite3` desde una carpeta compartida.

## Ingreso de RUT

Los campos de RUT aceptan puntos, guion, sin formato y `k` minuscula. Al terminar
de escribir, el campo se formatea automaticamente como `12.345.678-5`. La
validacion siempre se aplica en el servidor, incluso sin JavaScript.

## Filtros del listado

El listado permite buscar por nombre o RUT, filtrar por usuario creador, estado,
tipo de licencia y rango de fechas de emision. Cada licencia registra el usuario
que la ingreso.

## Ejecutar

```powershell
python manage.py runserver
```

Ingresa en <http://127.0.0.1:8000/login/> con:

```text
Usuario: Docente
Clave: Eva2backend
```

La base SQLite local, el respaldo y las claves del entorno no se incluyen en el
repositorio.
