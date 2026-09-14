# Uso de IA en el proyecto

## Herramienta y finalidad
Use OpenCode para ordenar el plan y revisar el proyecto contra las instrucciones de la evaluacion ES1. La consulta concreta fue: "Revisa nuevamente las instrucciones y confirmame si falta algo por hacer o si esta todo listo para evaluar".

## Respuesta recibida
La herramienta confirmo que Django, JSON y `tabulate` funcionaban, pero detecto tres riesgos: la consulta de IA no estaba analizada en mis palabras, las entradas no numericas no se guardaban y la regla no mostraba el operador `and` mencionado en el checklist.

## Revision personal y correccion
Al principio no entendi por que usar `or` no bastaba si la decision ya funcionaba. Revise el ejemplo del criterio 1.1.2 y comprendi que debia demostrar una combinacion con `and`; por eso lo use para comprobar que ambos nombres sean validos. Tambien conserve las entradas no numericas como datos invalidos para que pasen por la misma regla, se guarden en JSON y aparezcan en la tabla, sin agregar OCR, base de datos ni otras funciones fuera del MVP.
