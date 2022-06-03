# Pregunta 2

## Descripción

El sistema de gestión de ascensores asume que existe otro sistema el cual se comunica con este a través de requests. Cada request informa al sistema la posición actual de los elevadores y opcionalmente solicitan el ingreso de una llamada. 

Cuando la llamada es de tipo **"in"** (desde el interior de un elevador) debe llevar la `id` del elevador desde el que se realiza la petición. Estas llamadas son ignoradas si no van en el mismo sentido al que se dirige el elevador.

Cuando la llamada es de tipo **"out"** (desde afuera de los elevadores) se asigna al elevador disponible más cercano. Si no hay elevadores disponibles la llamada se ingresa a una cola, de esta manera cada vez que se actualicen las posiciones de los elevadores el sistema intentará nuevamente asignar la llamada. Un elevador se considera disponible si está vacío, o si la llamada actual tiene el mismo sentido que el ascensor y si es **"upward"** (**"downward"**) en una posición igual o superior (inferior) a la posición actual del ascensor. Adicionalmente, se asume que una llamada **"downward"** desde el piso 1 o una **"upward"** desde el piso 10 no son request que el sistema deba gestionar. Por último, el parámetro `wait` controla los segundos que debe esperar el elevador antes de limpiar de su cola una llamada tipo **"out"** a pesar que el elevador ha llegado a su destino, esto con el objetivo de priorizar una llamada entrante tipo **"in"** por sobre una **"out"**.

`ElevatorSystem` es la clase que gestiona las llamadas y las posiciones de los elevadores. Para esto crea instancias de la clase `Elevator` para gestionar de manera interna las colas de cada elevador, verificar si estan disponibles para tomar una llamada y asignarlas. Cada elevador cuenta con una instancia de `ElevatorQueue`, una estructura de datos que facilita agregar, eliminar y ordenar llamadas. Por último, esta la clase `Call`, una estructura de datos que facilita la gestión de los datos de una llamada.

## Uso

En la carpeta de **tests/question_2** el archivo **requests.json** representa una instancia de requests consecutivas. El archivo **system_states.txt** las posiciones de los elevadores y sus colas tras procesar cada una de esas requests.


```
from datetime import timedelta
from cencosud.question_2.elevator import ElevatorSystem

n_elevators = 10
n_floors = 10
wait = timedelta(seconds=10)
es = ElevatorSystem(n_elevators=n_elevators, n_floors=n_floors, wait=wait)

# update elevator positions and take out call
es.take_request({
    "timestamp": "2022-05-13 08:00:00",
    "call": {
        "floor": 1,
        "sense": "upward",
        "call_type": "out"
    },
    "state": {
        "0": 1,
        "1": 1,
        "2": 1
    }
})

# update elevator positions and take in call
es.take_request(
{
    "timestamp": "2022-05-13 08:00:05",
    "call": {
        "floor": 4,
        "sense": "upward",
        "elevator_id": 0,
        "call_type": "in"
    },
    "state": {
        "0": 1,
        "1": 1,
        "2": 1
    }
 })

# update elevator positions
es.take_request({
    "timestamp": "2022-05-13 08:00:10",
    "state": {
        "0": 2,
        "1": 1,
        "2": 1
    }
 })
```
