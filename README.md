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

## Base de datos y usuario demo

```powershell
python manage.py migrate
python manage.py crear_usuario_demo --password Eva2backend
```

El comando es seguro de repetir y deja configurados los permisos de consulta,
creacion, edicion y eliminacion de licencias para el usuario demo.

## Ejecutar

```powershell
python manage.py runserver
```

Ingresa en <http://127.0.0.1:8000/login/> con:

```text
Usuario: Docente
Clave: Eva2backend
```

La base SQLite local y las claves del entorno no se incluyen en el repositorio.
