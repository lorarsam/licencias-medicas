## MODIFIED Requirements

### Requirement: Ingreso de datos
The system SHALL accept seven input fields for each medical license.

#### Scenario: Ingreso manual por consola
- **WHEN** the user runs solucion.py without arguments
- **THEN** the system requests names and RUTs for the doctor and employee, rest days, issue date, and license type

#### Scenario: Ejecucion cancelada
- **WHEN** the user interrupts the program while it is requesting data
- **THEN** the system finishes with a cancellation message and without a traceback

### Requirement: Validacion de tipo de licencia
The system SHALL validate that the license type is between 1 and 7.

#### Scenario: Tipo valido
- **WHEN** the license type is in the range from 1 to 7
- **THEN** the system continues with the remaining validations

#### Scenario: Tipo invalido
- **WHEN** the license type is outside the range from 1 to 7
- **THEN** the system returns "Dato invalido" with the message "Tipo de licencia fuera de rango (1-7)"

### Requirement: Validacion de dias de reposo
The system SHALL validate that rest days are a positive integer.

#### Scenario: Dias validos
- **WHEN** rest days are greater than zero
- **THEN** the system continues with the remaining validations

#### Scenario: Dias invalidos
- **WHEN** rest days are zero or negative
- **THEN** the system returns "Dato invalido" with the message "dias de reposo invalidos"

### Requirement: Validacion de fecha de emision
The system SHALL validate the issue date using DD/MM/YYYY format and reject future dates.

#### Scenario: Formato invalido
- **WHEN** the issue date does not use a valid DD/MM/YYYY date
- **THEN** the system returns "Dato invalido"

#### Scenario: Fecha pasada o actual
- **WHEN** the issue date is today or an earlier date
- **THEN** the system continues with the remaining validations

#### Scenario: Fecha futura
- **WHEN** the issue date is later than the current date
- **THEN** the system returns "Rechazo - fecha invalida" with the message "La fecha de emision es futura"

### Requirement: Validacion de dias maximos por tipo
The system SHALL reject a license when its rest days exceed the configured maximum for its type.

#### Scenario: Dias dentro del maximo
- **WHEN** rest days do not exceed the maximum for the license type
- **THEN** the system returns "Aceptada" after all other validations pass

#### Scenario: Dias excedidos
- **WHEN** rest days exceed the maximum for the license type
- **THEN** the system returns "Rechazo - dias excedidos" and reports the configured maximum

### Requirement: Almacenamiento en JSON
The system SHALL append each processed license to datos.json with its input, status, and reason.

#### Scenario: Guardar registro
- **WHEN** the console finishes processing a license
- **THEN** the system preserves previous records and writes the new record to datos.json

### Requirement: Visualizacion con tabulate
The system SHALL display all stored records as a formatted console table using tabulate.

#### Scenario: Mostrar tabla
- **WHEN** records exist after processing a license
- **THEN** the system displays a table with headers and all records

### Requirement: Vista web Django
The system SHALL provide one web view at /resumen/ that reuses the decision rule and displays the JSON records.

#### Scenario: Cargar pagina
- **WHEN** the user accesses /resumen/ and datos.json exists
- **THEN** the view recalculates each result with the shared rule and renders all records

#### Scenario: Sin registros
- **WHEN** the user accesses /resumen/ and datos.json does not exist or contains no records
- **THEN** the page displays "No hay licencias medicas registradas"
