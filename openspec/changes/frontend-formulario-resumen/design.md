## Context

La aplicacion usa Django con templates renderizados en servidor y persiste una lista de registros en `datos.json`. `solucion.py` ya concentra catalogos, formatos, estados, mensajes y funciones de validacion y persistencia; la vista actual solo carga esa lista y aplica nuevamente la decision antes de renderizarla. Ver `proposal.md` para la motivacion y `specs/licencia-medica/spec.md` para el comportamiento esperado.

## Goals / Non-Goals

**Goals:**

- Conservar una unica fuente para reglas, catalogos, formatos y textos funcionales.
- Incorporar el formulario al endpoint existente sin separar frontend y backend.
- Evitar reenvios accidentales y escrituras parciales.
- Mantener una interfaz accesible y responsiva sin incorporar dependencias.

**Non-Goals:**

- Resolver escrituras concurrentes sobre JSON.
- Incorporar una API, framework JavaScript, autenticacion o base de datos.
- Cambiar los siete campos ni las cuatro decisiones del dominio.

## Decisions

### Mantener renderizado del lado servidor

Se usaran Django Forms, templates y archivos estaticos. Esto evita una API y un proceso de compilacion que no aportan valor al alcance academico. Una SPA fue descartada por aumentar dependencias y duplicar contratos de validacion.

### Unificar ingreso y consulta en `/resumen/`

La vista existente respondera GET con el formulario y los registros, y POST con la validacion y escritura. Despues de guardar aplicara POST/Redirect/GET hacia el mismo resumen. Separar el formulario en otra ruta agregaria navegacion y una segunda plantilla sin una necesidad funcional.

### Usar el formulario como adaptador, no como regla de negocio

El formulario convertira enteros, fechas y la seleccion del tipo. Las opciones se generaran desde `TIPOS_LICENCIA`, la fecha se normalizara usando `FORMATO_FECHA` y el registro se creara exclusivamente con `crear_registro()`. Las validaciones de RUT, dias, fecha futura y maximos permaneceran en `solucion.py`.

### Centralizar valores de interfaz

Los textos funcionales, etiquetas, ayudas, atributos reutilizables y nombres de template o parametros se declararan como constantes. El template recibira esos valores en contexto en vez de repetir estados, tipos o mensajes. Los colores y medidas se organizaran como propiedades personalizadas CSS para evitar valores visuales dispersos.

### Mantener JSON y confirmar mediante redireccion

Un POST valido cargara la lista, agregara el resultado de `crear_registro()` y llamara a `guardar()`. La redireccion incluira solo una marca de confirmacion no sensible; el estado real se mostrara desde el registro persistido.

### Presentacion sin JavaScript obligatorio

El formulario usara HTML semantico, errores del servidor y un contenedor con desplazamiento horizontal para la tabla. La experiencia principal no dependera de JavaScript, reduciendo superficie de fallos y pruebas.

## Risks / Trade-offs

- [Dos solicitudes pueden sobrescribir `datos.json`] -> Mantener el sistema para uso local y documentar que una operacion multiusuario requiere base de datos.
- [La capa web puede duplicar validaciones del dominio] -> Limitar Django Forms a conversion, presencia y adaptacion de formato; probar que `crear_registro()` decide el estado.
- [El template puede volver a introducir valores funcionales literales] -> Entregar textos y opciones desde constantes y revisar las ocurrencias durante la verificacion.
- [Una tabla amplia puede ser incomoda en movil] -> Usar un contenedor accesible con desplazamiento horizontal y celdas legibles.

## Migration Plan

1. Incorporar constantes de presentacion sin cambiar los registros existentes.
2. Agregar el formulario y habilitar proteccion CSRF.
3. Actualizar la vista conservando el GET actual y agregando el flujo POST.
4. Refactorizar el template y mover estilos a `core/static/`.
5. Ejecutar pruebas automaticas y verificar manualmente escritorio y movil.

La reversa consiste en retirar el formulario y restaurar la vista GET previa; el formato de `datos.json` no cambia.
