# Spec Delta: licencia-medica

## ADDED

### Requirement: Ingreso de datos
The system SHALL accept 7 input fields for each medical license.

#### Scenario: Ingreso manual por consola
- GIVEN a user runs solucion.py
- WHEN the program prompts for input
- THEN accept nombre_medico (str), rut_medico (str), nombre_funcionario (str), rut_funcionario (str), dias_reposo (int), fecha_emision (str DD/MM/AAAA), tipo_licencia (int 1-7)

### Requirement: Validacion de tipo de licencia
The system SHALL validate that tipo_licencia is between 1 and 7.

#### Scenario: Tipo invalido
- GIVEN tipo_licencia is not in range [1, 7]
- WHEN the system validates
- THEN return "Dato invalido" with message "Tipo de licencia fuera de rango (1-7)"

### Requirement: Validacion de dias de reposo
The system SHALL validate that dias_reposo is greater than 0.

#### Scenario: Dias invalidos
- GIVEN dias_reposo <= 0
- WHEN the system validates
- THEN return "Dato invalido" with message "dias de reposo invalidos"

### Requirement: Validacion de fecha de emision
The system SHALL validate that fecha_emision is not in the future.

#### Scenario: Fecha futura
- GIVEN fecha_emision > today
- WHEN the system validates
- THEN return "Rechazo - fecha invalida" with message "La fecha de emision es futura"

### Requirement: Validacion de dias maximos por tipo
The system SHALL validate that dias_reposo does not exceed the maximum for the license type.

| Tipo | Maximo dias |
|------|-------------|
| 1 | 30 |
| 2 | 2 |
| 3 | 180 |
| 4 | 180 |
| 5 | 365 |
| 6 | 365 |
| 7 | 84 |

#### Scenario: Dias excedidos
- GIVEN dias_reposo > max_dias[tipo_licencia]
- WHEN the system validates
- THEN return "Rechazo - dias excedidos"

### Requirement: Almacenamiento en JSON
The system SHALL save each license record to datos.json.

### Requirement: Visualizacion con tabulate
The system SHALL display all records in a formatted table using tabulate.

### Requirement: Vista web Django
The system SHALL provide a web view at /resumen/ showing all records.
