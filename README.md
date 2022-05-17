# Evaluación Data Scientist Cencosud

## Pregunta 1

En [cencosud/question_1](cencosud/question_1) se tiene el código fuente que responde a la pregunta "Cantidad de hijos promedio por cada matrimonio" y "La persona con la mayor cantidad de nietos en la base de datos".  Además, la carpeta cuenta con un README en el que se describe la implementación y se responden preguntas adicionales del enunciado. Por último en la carpeta [tests/question_1](tests/question_1) se tienen algunos tests unitarios con datos simulados.

## Pregunta 2

En [cencosud/question_2](cencosud/question_2) se tiene el código fuente con la implementación de un sistema que gestiona llamadas a ascensores. En la misma carpeta hay un README que detalla la implementación. Por último, en la carpeta [tests/question_2](tests/question_2) se tienen algunos tests unitarios con datos simulados.

## Pregunta 3
En [cencosud/question_3/time_serie_analysis.ipynb](cencosud/question_3/time_serie_analysis.ipynb) se tiene el jupyter notebook con el código y las respuestas de la pregunta. Para una mejor visualización del notebook visitar el siguiente [link](https://nbviewer.org/github/dgarridoa/cencosud/blob/main/cencosud/question_3/time_serie_analysis.ipynb).

## Ejecución
Para poder ejecutar el código se recomienda instalar la última versión de [docker](https://docs.docker.com/get-docker/). Luego, con el siguiente comando en la raíz del proyecto se puede crear la imagen y levantar el contenedor.

```
docker compose up --build

```

El comando anterior levanta un contenedor con MySQL para la pregunta 1, luego un contenedor con Python en donde ejecuta los tests unitarios de las pregunta 1 y 2, finalmente levanta una instancia de jupyter lab que puede ser accedida en [http://localhost:8888](http://localhost:8888).
