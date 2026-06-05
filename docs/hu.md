# Automatización de Gestión Mora Temprana

## Descripción

Proyecto para la generación automática diaria de la cartera de Mora Temprana, asignación balanceada de operaciones a asesores de cobranza y generación del archivo de salida `ASIGNACION.csv`.

La solución procesa información proveniente de:

* CADETACACO
* CAMOROSICO
* Recblue

permitiendo identificar operaciones que ingresan en mora, excluir operaciones no elegibles y distribuir la carga de trabajo entre los asesores de cobranza.

---

# Objetivo

Automatizar el proceso de:

1. Identificación de operaciones en mora temprana.
2. Exclusión de operaciones no gestionables.
3. Ordenamiento de cartera por saldo.
4. Asignación automática de asesores.
5. Generación de archivo final para gestión de cobranzas.

---

# Fuentes de Información

## CADETACACO

Campos requeridos:

| Campo          | Columna | Descripción                 |
| -------------- | ------- | --------------------------- |
| Día Pago       | AG      | Día programado de pago      |
| Saldo Capital  | N       | Saldo pendiente del crédito |
| Estado         | AB      | Estado de la operación      |
| Tipo Operación | H       | Tipo de crédito             |

## CAMOROSICO

Campos requeridos:

| Campo       | Columna | Descripción                                   |
| ----------- | ------- | --------------------------------------------- |
| Días Atraso | S       | Días de mora calculados por el sistema origen |

## Recblue

Campos requeridos:

| Campo            | Descripción                     |
| ---------------- | ------------------------------- |
| ID Crédito       | Identificador único del crédito |
| Identificación   | Identificación del socio        |
| Número Operación | Número de operación             |

---

# Reglas de Negocio

## Identificación de Mora Temprana

Una operación entra en Mora Temprana cuando:

* El socio no realiza el pago hasta el cierre del día hábil correspondiente.
* La cuota impaga corresponde al período actual.

## Identificación de Mora Madura

Una operación corresponde a Mora Madura cuando:

* La cuota impaga pertenece a períodos anteriores.
* Continúa acumulando días de atraso.

---

# Manejo de Feriados y Fines de Semana

## Regla

Si la fecha de pago coincide con:

* Sábado
* Domingo
* Feriado

el vencimiento debe trasladarse al siguiente día hábil disponible.

### Ejemplo

Fecha original de pago: 30

30 = Sábado
31 = Domingo
01 = Lunes hábil

Fecha efectiva de vencimiento = 01

Si no paga el 01:

02 = 1 día de mora

---

# Exclusiones

No deben incluirse operaciones:

## Judiciales

Fuente:

* CADETACACO
* Columna AB

## Castigadas

Fuente:

* CADETACACO
* Columna AB

## Compra de Cartera

Fuente:

* CADETACACO
* Columna H

---

# Ordenamiento de Cartera

Las operaciones elegibles deben ordenarse:

* Por saldo capital.
* De mayor a menor.

Campo utilizado:

* CADETACACO.N

---

# Asignación Automática

## Objetivo

Distribuir la cartera de forma equilibrada entre los asesores.

## Reglas

* Asignación secuencial.
* Balanceo de carga.
* Mantener el mismo asesor durante todo el mes.
* No permitir duplicidad de asignaciones.

### Ejemplo

Operacion 1 -> Asesor A
Operacion 2 -> Asesor B
Operacion 3 -> Asesor C
Operacion 4 -> Asesor D

---

# Integración Recblue

El proceso debe obtener:

* ID Crédito
* Número Operación
* Identificación

para enriquecer la cartera final.

---

# Flujo General

1. Cargar CADETACACO.
2. Cargar CAMOROSICO.
3. Identificar operaciones en mora.
4. Aplicar reglas de días hábiles.
5. Excluir operaciones no elegibles.
6. Ordenar por saldo capital.
7. Asignar asesores.
8. Consultar Recblue.
9. Completar ID Crédito.
10. Generar archivo final.

---

# Archivo de Salida

Nombre:

ASIGNACION.csv

Campos sugeridos:

| Campo            |
| ---------------- |
| Fecha Corte      |
| ID Crédito       |
| Número Operación |
| Identificación   |
| Nombre Socio     |
| Saldo Capital    |
| Días Atraso      |
| Asesor Asignado  |

---

# Casos de Prueba

## Mora Temprana

* Pago dentro del mes actual.
* No registra pago.
* Debe ingresar en cartera.

## Mora Madura

* Cuota pertenece a un mes anterior.
* No debe formar parte de la cartera de Mora Temprana.

## Exclusiones

* Judicial.
* Castigada.
* Compra de cartera.

## Asignación

* Sin duplicidad.
* Balanceada.
* Mantener asesor durante el mes.

---

# Resultado Esperado

Generar diariamente una cartera de Mora Temprana consistente, balanceada y lista para gestión operativa por parte del Call Center de Cobranzas.
