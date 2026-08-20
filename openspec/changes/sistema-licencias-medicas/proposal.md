# Proposal: Sistema de Licencias Medicas

## Summary
Implementar un sistema completo para ingresar, validar y registrar licencias medicas de funcionarios chilenos, cumpliendo con la evaluacion ES1 de Programacion Back End.

## Motivation
Las empresas reciben licencias medicas en formato papel y deben validar manualmente si los datos son correctos. Esto genera errores humanos, retraso en la tramitacion y riesgo de aceptar licencias con datos inconsistentes o fraudulentos.

## Solution
- Programa de consola (solucion.py) que pide 7 datos de la licencia
- Regla de decision con 4 resultados: aceptada, rechazo por fecha, rechazo por dias, dato invalido
- Almacenamiento en JSON (datos.json)
- Tabla formateada con tabulate
- Vista web con Django en /resumen/

## Non-goals
- Base de datos (solo JSON en ES1)
- OCR o procesamiento de imagenes
- Login o autenticacion
- API externa
- Monorepo

## Spec Changes
- ADDED: licencia-medica/spec.md - Especificacion completa del sistema

## Impact
- Criterio 1.1.1: Variables y operaciones (6 puntos)
- Criterio 1.1.2: Instrucciones y estructuras (6 puntos)
- Criterio 1.1.3: Paquete externo tabulate (6 puntos)
- Criterio 1.1.4: Django + ia.md (12 puntos)
