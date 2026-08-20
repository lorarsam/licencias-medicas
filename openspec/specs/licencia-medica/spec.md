# Licencia Medica Specification

## Purpose
Sistema para ingresar, validar y registrar licencias medicas de funcionarios chilenos.

## Requirements

### Requirement: Ingreso de datos
The system SHALL accept 7 input fields for each medical license.

#### Scenario: Ingreso manual por consola
- GIVEN a user runs solucion.py
- WHEN the program prompts for input
- THEN accept nombre_medico (str), rut_medico (str), nombre_funcionario (str), rut_funcionario (str), dias_reposo (int), fecha_emision (str DD/MM/AAAA), tipo_licencia (int 1-7)

### Requirement: Validacion de tipo de licencia
The system SHALL validate that tipo_licencia is between 1 and 7.

#### Scenario: Tipo valido
- GIVEN tipo_licencia is in range [1, 7]
- WHEN the system validates
- THEN proceed to next validation

#### Scenario: Tipo invalido
- GIVEN tipo_licencia is not in range [1, 7]
- WHEN the system validates
- THEN return "Dato invalido" with message "Tipo de licencia fuera de rango (1-7)"

### Requirement: Validacion de dias de reposo
The system SHALL validate that dias_reposo is greater than 0.

#### Scenario: Dias validos
- GIVEN dias_reposo > 0
- WHEN the system validates
- THEN proceed to next validation

#### Scenario: Dias invalidos
- GIVEN dias_reposo <= 0
- WHEN the system validates
- THEN return "Dato invalido" with message "dias de reposo invalidos"

### Requirement: Validacion de fecha de emision
The system SHALL validate that fecha_emision is not in the future.

#### Scenario: Fecha pasada o actual
- GIVEN fecha_emision <= today
- WHEN the system validates
- THEN proceed to next validation

#### Scenario: Fecha futura
- GIVEN fecha_emision > today
- WHEN the system validates
- THEN return "Rechazo - fecha invalida" with message "La fecha de emision es futura"

### Requirement: Validacion de dias maximos por tipo
The system SHALL validate that dias_reposo does not exceed the maximum for the license type.

#### Scenario: Dias dentro del maximo
- GIVEN dias_reposo <= max_dias[tipo_licencia]
- WHEN the system validates
- THEN return "Aceptada" with message "Licencia registrada correctamente"

#### Scenario: Dias excedidos
- GIVEN dias_reposo > max_dias[tipo_licencia]
- WHEN the system validates
- THEN return "Rechazo - dias excedidos" with message indicating max and entered

### Requirement: Almacenamiento en JSON
The system SHALL save each license record to datos.json.

#### Scenario: Guardar registro
- GIVEN a license has been validated
- WHEN the system saves
- THEN append record to datos.json with all input fields plus estado and motivo

### Requirement: Visualizacion con tabulate
The system SHALL display all records in a formatted table.

#### Scenario: Mostrar tabla
- GIVEN records exist in datos.json
- WHEN the user runs solucion.py
- THEN display table using tabulate with headers

### Requirement: Vista web Django
The system SHALL provide a web view at /resumen/ showing all records.

#### Scenario: Cargar pagina
- GIVEN a user accesses http://127.0.0.1:8000/resumen/
- WHEN the view loads
- THEN read datos.json and render template with records

#### Scenario: Sin registros
- GIVEN datos.json does not exist or is empty
- WHEN the view loads
- THEN display "No hay licencias medicas registradas"
