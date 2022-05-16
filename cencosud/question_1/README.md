# Pregunta 1

## Descripción

Para responder las preguntas del enunciado se creó la clase `HumanResources` la cual permite establecer una conexión con la base datos y realizar consultas. Siendo sus métodos los siguientes:

- `__init__`: Establece conexión con una base de datos MySQL.
- `create_db`: Crea la base de datos hhrr.
- `create_tbl_personas`: Crea la tabla personas.
- `create_tbl_conyuges`: Crea la tabla conyuges.
- `create_tbl_hijos`: Crea la tabla hijos.
- `truncate_db(sample)`: Trunca las tablas de hhrr con los datos en `sample`.
- `create_pupulated_db(sample)`: Utiliza todos los métodos anteriores en orden.
- `get_avg_children_per_marriage`: Obtiene la cantidad de hijos promedio por cada matrimonio.
- `get_person_with_max_number_grandchildren`: Retorna la persona con la mayor cantidad de nietos en la base de datos.

Adicionalmente se creó la clase `HumanResourcesGenerator` para generar muestras aleatorias para popular la tabla `personas`, `conyuges` y `hijos`.

## Cantidad de hijos promedio por cada matrimonio

En primer lugar, se realizan dos **inner joins** entre la tabla `conyuges` e `hijos` con el objetivo de hallar los padres de cada hijo que estan en un matrimonio, obteniéndose por resultado las tablas `first_parent` y `second_parent`. En segundo lugar, se realiza un **inner join** entre esas dos tablas para obtener los padres de un hijo que son parte del mismo matrimonio, siendo `marriages_and_children` la tabla resultante. En tercer lugar, se cuenta la cantidad de hijos por matrimonio agrupando por **id**, obteniéndose por resultado la tabla `count_children_by_marriage`. Finalmente, se realiza un **left join** entre `conyuges` y `count_children_by_marriage`, así el promedio es sobre el universo de todos los matrimonios.

```
WITH
  first_parent AS (
    SELECT
      c.id,
      c.id_persona_1,
      c.id_persona_2,
      h.id_hijo
    FROM hhrr.conyuges AS c
    INNER JOIN hhrr.hijos AS h
    ON c.id_persona_1 = h.id_padre),
  second_parent AS (
    SELECT
      c.id,
      c.id_persona_1,
      c.id_persona_2,
      h.id_hijo
    FROM hhrr.conyuges AS c
    INNER JOIN hhrr.hijos AS h
    ON c.id_persona_2 = h.id_padre),
  marriages_and_children AS (
    SELECT
      fp.id,
      fp.id_hijo
    FROM first_parent AS fp
    INNER JOIN second_parent AS sp
    ON fp.id_persona_1 = sp.id_persona_1
      AND fp.id_persona_2 = sp.id_persona_2
      AND fp.id_hijo = sp.id_hijo),
  count_children_by_marriage AS (
    SELECT
      id,
      count(*) AS num_children
    FROM marriages_and_children
    GROUP BY id
  )
SELECT
  AVG(IFNULL(chbm.num_children, 0)) avg_per_marriage
FROM hhrr.conyuges AS c
LEFT JOIN count_children_by_marriage AS chbm
ON c.id = chbm.id
```

En caso que esta consulta sea recurrente, una forma de reducir el tiempo de consulta es crear una tabla intermedia entre `conyuges` e `hijos`, tablas que tienen una relación N-M. Sea la tabla `conyuges_hijos`, con los campos ["id", "conyuges_id", "hijo_id"], siendo 1-N la relación `conyuges-conyuges_hijos` y `hijos-conyuges_hijos`. Así pasamos de una cardinalidad N-M a dos de 1-N.


## La persona con la mayor cantidad de nietos en la base de datos

En primer lugar, se realiza un **inner join** entre la tabla `hijos` consigo misma, obteniéndose una tabla intermedia que relaciona abuelos con sus nietos. En segundo lugar, se obtiene la cantidad de nietos por abuelo al agrupar por su **id**, obteniéndose la tabla `count_grandchildren_by_person`. En tercer lugar, se calcula el máximo número de nietos a partir de `count_grandchildren_by_person`, se calcula el argumento máximo usando un **where** sobre la misma tabla y se limita el resultado a una fila en caso de que el máximo no es único. Por último, se realiza un **where** con la tabla personas para recuparar toda la información del argumento máximo. 

```
WITH
  count_grandchildren_by_person AS (
    SELECT
      grandparents.id_padre,
      count(*) AS num_grandchildren
    FROM hhrr.hijos AS grandparents
    INNER JOIN hhrr.hijos AS parents
    ON grandparents.id_hijo = parents.id_padre
    GROUP BY grandparents.id_padre),
  person_with_max_number_grandchildren AS (
    SELECT
        id_padre
    FROM count_grandchildren_by_person
    WHERE num_grandchildren = (
      SELECT
        MAX(num_grandchildren)
      FROM count_grandchildren_by_person)
    LIMIT 1)
SELECT *
FROM hhrr.personas
WHERE id = (
  SELECT id_padre
  FROM person_with_max_number_grandchildren)

```

Esta consulta se puede optimizar de manera similar a la consulta anterior, ya que la tabla `hijos` tiene una relación N-M consigo misma. Creando una tabla adicional en donde el campo `id_padre` está en la posición `id_hijo` siempre y cuando exista su padre.


## Uso
```
from datetime import datetime, timedelta
from cencosud.question_1.random_generator import HumanResourcesGenerator
from cencosud.question_1.human_resources import HumanResources

n_personas = 1000
n_conyuges = 50
n_hijos = 120
min_date = datetime(1900, 1, 1)
max_date = datetime(2022, 1, 1)
seed = 0

# create random sample
hrg = HumanResourcesGenerator(n_personas, n_conyuges, n_hijos,
    min_date, max_date, seed)
hrg.sample()

# create hhrr db and populate it with random data 
hr = HumanResources()
hr.create_populated_db(hrg)

# answer 
hr.get_avg_children_per_marriage()
hr.get_person_with_max_number_grandchildren()
```
