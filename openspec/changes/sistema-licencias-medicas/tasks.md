# Tasks: Sistema de Licencias Medicas

## Implementation Tasks

- [x] Crear estructura de carpetas del proyecto
- [x] Implementar solucion.py con constantes TIPOS_LICENCIA, ARCHIVO_JSON, FORMATO_FECHA
- [x] Implementar funciones: cargar(), guardar(), validar_rut(), parsear_fecha(), decidir()
- [x] Implementar main() con input() para 7 campos
- [x] Implementar mostrar_tabulate() con tabulate
- [x] Configurar Django con python-decouple y .env
- [x] Crear vista core/views.py que importa desde solucion.py
- [x] Crear template core/templates/resumen.html
- [x] Crear plan.md con apartado negocio y tecnico
- [x] Crear ia.md con documentacion de uso de IA
- [x] Probar los 4 resultados de la regla de decision
- [x] Probar Django runserver y vista /resumen/
- [x] Configurar OpenSpec con project context
- [x] Crear spec licencia-medica/spec.md

## Verification Tasks
- [x] Ejecutar python solucion.py y probar los 4 casos
- [x] Ejecutar python manage.py runserver y verificar /resumen/
- [x] Verificar que datos.json se crea y guarda registros
- [x] Verificar que tabulate muestra tabla formateada
