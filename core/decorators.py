from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def requiere_rol(*roles):
    def decorador(view_func):
        @wraps(view_func)
        @login_required(login_url="login")
        def wrapper(request, *args, **kwargs):
            tiene_rol = request.user.is_superuser or request.user.groups.filter(
                name__in=roles,
            ).exists()
            if tiene_rol:
                return view_func(request, *args, **kwargs)

            messages.error(request, "No tienes permiso para esta accion.")
            return redirect("lista")

        return wrapper

    return decorador
