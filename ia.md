# Uso de IA en el proyecto

## Herramienta y finalidad
Use OpenCode para ordenar el plan y revisar el proyecto contra las instrucciones de la evaluacion ES1. La consulta concreta fue: "Vuelve a verificar que se cumplan los requisitos y soluciona el problema al correr solucion.py".

## Respuesta recibida
La herramienta explico que `KeyboardInterrupt` aparecia porque el programa fue detenido mientras `input()` esperaba el nombre del medico. Tambien detecto que la regla no usaba `if/elif/else` y que el OCR estaba programado aunque el plan lo clasificaba como Should y fuera de alcance.

## Correccion aplicada
Decidi dejar un MVP estricto. Se retiro OCR, se centralizaron las reglas en constantes, se escribieron los cuatro resultados con `if/elif/else` y se manejo la cancelacion sin mostrar un traceback. Tambien se hizo que la vista Django reutilice `decidir()` en vez de duplicar la regla.
