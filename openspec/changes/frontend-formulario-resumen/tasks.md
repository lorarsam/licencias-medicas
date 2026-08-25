## 1. Constantes y formulario

- [x] 1.1 Centralizar textos funcionales, etiquetas, formatos, parametros y atributos reutilizables en constantes y verificar que no se dupliquen reglas ni valores de dominio fuera de `solucion.py`.
- [x] 1.2 Crear el formulario Django de siete campos con opciones derivadas de `TIPOS_LICENCIA` y fecha normalizada con `FORMATO_FECHA`, y verificar conversiones validas y errores por campo mediante pruebas.

## 2. Flujo web

- [x] 2.1 Habilitar la proteccion CSRF en la configuracion y verificar que un POST sin token sea rechazado sin escribir registros.
- [x] 2.2 Ampliar la vista de resumen para procesar POST mediante `crear_registro()`, `cargar()` y `guardar()`, aplicar POST/Redirect/GET y verificar los cuatro resultados con pruebas de integracion.
- [x] 2.3 Preparar registros, nombres de tipo, clases de estado y conteos para el template usando constantes compartidas, y verificar el contexto con registros y sin registros.

## 3. Interfaz responsiva

- [x] 3.1 Crear un template base y una hoja de estilos estatica con propiedades CSS centralizadas, y verificar que Django encuentre y sirva el recurso.
- [x] 3.2 Refactorizar `resumen.html` con formulario accesible, errores por campo, confirmacion, indicadores y tabla responsiva, y verificar el contenido para estados con datos y vacio.
- [x] 3.3 Verificar manualmente `/resumen/` en anchos de escritorio y movil, confirmando que el formulario sea utilizable y que la tabla no desborde la pagina.

## 4. Verificacion final

- [x] 4.1 Ejecutar la suite Django y `python manage.py check`, corregir cualquier fallo y registrar que ambas verificaciones terminan correctamente.
- [x] 4.2 Revisar el cambio contra la especificacion y buscar valores funcionales duplicados o hardcodeados en vistas, formularios y templates; verificar que catalogos, estados, formatos y mensajes tengan una unica fuente.
