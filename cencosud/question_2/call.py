from datetime import datetime
from typing import Union
from pydantic import BaseModel, PositiveInt, constr


class Call(BaseModel):
    """
    Data structure to manage calls made from inside or outside an elevator.

    Parameters
    ----------
    call_type : str
        Can take value "in" or "out". A "in" call is made from inside a
        specific elevator. On the other hand, a "out" call is made from
        outside without an elevator in specific.
    floor : int
        Refers to destination floor. Must be positive integer.
    sense : str
        Can take value "upward" or "downward". When is a "in" call refers to
        the sense of the destinity respect to the elevator current position.
        When is a "out" call refers to the sense of the next possible "in"
        call.
    not_attended : bool, default=True
        True if the call has been attended False otherwise.
    timestamp : datetime, default=None
        Call timestamp.
    elevator_id : int, default=None
        Elevator who take the "in" call. Optional when is a "out" call.
    """
    call_type: constr(regex="^in$|^out$")
    floor: PositiveInt
    sense: constr(regex="^upward$|^downward$")
    not_attended: bool = True
    timestamp: datetime = None
    elevator_id: Union[int, None] = None

    def __eq__(self, other) -> bool:
        return (
            self.call_type == other.call_type and
            self.floor == other.floor and
            self.sense == other.sense and
            self.timestamp == other.timestamp and
            self.elevator_id == other.elevator_id
        )
    def __call__(self, timestamp) -> None:
        if self.not_attended:
            self.timestamp = timestamp
            self.not_attended = False
