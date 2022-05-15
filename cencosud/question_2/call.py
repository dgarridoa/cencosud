from datetime import datetime


class Call:
    """
    Data structure to manage calls made from inside or outside an elevator.

    Atributes
    ----------
    call_type : str
        Can take value "in" or "out". A "in" call is made from inside a
        specific elevator. On the other hand, a "out" call is made from
        outside without an elevator in specific.
    floor : int
        Refers to destination floor.
    sense : str
        Can take value "upward" or "downward". When is a "in" call refers to
        the sense of the destinity respect to the elevator current position.
        When is a "out" call refers to the sense of the next possible "in"
        call.
    timestamp : datetime
        Call timestamp.
    elevator_id : int
        Elevator who take the "in" call. Optional when is a "out" call.
    """
    def __init__(
       self,
       call_type: str,
       floor: int,
       sense: str,
       timestamp: datetime,
       elevator_id: int = -1,
    ):
        if call_type not in ("in", "out"):
            raise ValueError("'in' or 'out' call_type are aceptables.")
        if sense not in ("upward", "downward"):
            raise ValueError("'upward' or 'downward' sense are aceptables.")
        self.call_type = call_type
        self.floor = floor
        self.sense = sense
        self.timestamp = timestamp
        self.elevator_id = elevator_id

    def __eq__(self, other):
        return (
            self.call_type == other.call_type and
            self.floor == other.floor and
            self.sense == other.sense and
            self.timestamp == other.timestamp and
            self.elevator_id == other.elevator_id
        )
