# ia.md - Uso de IA en el proyecto

## Herramienta utilizada
OpenCode (modelo big-pickle) para planificacion y generacion de codigo.

## Consulta realizada
Se pidio a la IA que leyera las instrucciones ES1 de Programacion Back End y creara un plan completo para resolver el problema de "Sistema de Licencias Medicas", incluyendo la priorizacion MoSCoW y la verificacion de compliance contra la rubrica.

## Respuesta de la IA
La IA genero:
1. Un plan.md con apartado de negocio y tecnico
2. La estructura de archivos completa
3. La regla de decision con 4 resultados
4. El codigo de solucion.py con constantes (sin hardcodear)
5. La vista Django que importa desde solucion.py
6. Verificacion de compliance: 30/30 puntos posibles

## Correcciones realizadas por el estudiante
- Se ajustaron los maximos de dias por tipo de licencia segun legislacion chilena vigente
- Se agrego validacion de RUT con formato basico
- Se ensure_ascii=False en json.dump para caracteres especiales del espanol
- Se verifico que la vista Django reutiliza la logica de solucion.py (no la reescribe)
