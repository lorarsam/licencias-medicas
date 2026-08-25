## MODIFIED Requirements

### Requirement: Vista web Django
The system SHALL provide a web view at /resumen/ for entering a medical license and reviewing all stored records.

#### Scenario: Cargar pagina
- **WHEN** a user accesses http://127.0.0.1:8000/resumen/ and stored records exist
- **THEN** the system displays the seven-field input form and all records with their license type, status, and reason

#### Scenario: Sin registros
- **WHEN** a user accesses http://127.0.0.1:8000/resumen/ and no stored records exist
- **THEN** the system displays the input form and the message "No hay licencias medicas registradas"

## ADDED Requirements

### Requirement: Ingreso web de licencia medica
The system SHALL accept the seven medical license fields through the web view and SHALL process them with the same decision rules used by the console flow.

#### Scenario: Envio valido del formulario
- **WHEN** a user submits values that can be converted to the required input types
- **THEN** the system evaluates one of the four decision results, stores the complete record, and returns the user to the updated summary

#### Scenario: Error de conversion del formulario
- **WHEN** a user submits a missing value or a value that cannot be converted to its required input type
- **THEN** the system does not store a partial record and displays errors next to the affected fields

### Requirement: Envio web seguro y repetible
The system MUST protect form submissions against cross-site request forgery and MUST prevent a browser refresh from submitting the same record again.

#### Scenario: Envio protegido exitoso
- **WHEN** a user submits the form with a valid anti-forgery token
- **THEN** the system processes the request and redirects to the summary using a GET request

#### Scenario: Envio sin proteccion
- **WHEN** a client submits the form without a valid anti-forgery token
- **THEN** the system rejects the request and does not write a record

### Requirement: Presentacion web responsiva
The system SHALL keep the form and license information usable on desktop and mobile viewports.

#### Scenario: Visualizacion en pantalla estrecha
- **WHEN** the summary is displayed on a mobile-width viewport
- **THEN** form controls remain readable and records can be reviewed without overflowing the page
