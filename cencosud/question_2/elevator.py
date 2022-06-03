from datetime import datetime, timedelta
from cencosud.question_2.call import Call
from typing import List, Dict
from pydantic import BaseModel, NonNegativeInt, PositiveInt, constr, validate_arguments


class ElevatorQueue(BaseModel):
    """
    Data structure to manage an elevator queue.

    Parameters
    ----------
    is_empty : bool, default=True
        True if no pending calls, else False.
    calls : List[Call], default=[]
        List with pending calls.
    """
    is_empty: bool = True
    calls: List[Call] = []

    def __eq__(self, other) -> bool:
        return all(sc == oc for sc, oc in zip(self.calls, other.calls))

    def sort(self, reverse: bool) -> None:
        """
        Sorts pending calls by priority using their floor values.

        Parameters
        ----------
        reverse: bool
            When is True sorts calls in descending order by call.floor.
            When is False sorts calls in ascending order by call.floor.
        """
        self.calls.sort(key=lambda x: x.floor, reverse=reverse)

    def append(self, call: Call) -> None:
        """
        Add call to the list of pending calls in the appropriate order.

        Parameters
        ----------
        call: Call
            Add call to the list self.calls.
        """
        reverse = call.sense == "upward"
        self.calls.append(call)
        self.sort(reverse=reverse)
        self.is_empty = False

    def pop(self) -> Call:
        """
        Remove call with the highest priority.

        Returns
        -------
        call : Call
        """
        call = self.calls.pop()
        if not self.calls:
            self.is_empty = True
        return call


class Elevator(BaseModel):
    """
    Class to represent an elevator and manage its queue.

    Parameters
    ----------
    elevator_id :int
        Unique identifier. Must be non negative integer.
    floor : int, default=1
        Floor where is located. Must be a positive integer.
    sense : str
        Sense where is moving. Can take value "upward", "downward" or empty "".
    queue : ElevatorQueue
        Pending calls.
    wait : timedelta, default=timedelta(seconds=10)
        Seconds that the elevator waits before clean a ready to clean out call
        from its queue. The implications of this is that an elevator that took
        an out call wait for the in call, if no in call received the elevator
        is able to take other calls.
    timestamp : datetime, default=None
        Current timestamp.
    """
    elevator_id: NonNegativeInt
    floor: PositiveInt = 1
    sense: constr(regex="^upward$|^downward$|") = ""
    queue: ElevatorQueue = ElevatorQueue()
    wait: timedelta = timedelta(seconds=10)
    timestamp: datetime = None

    def __eq__(self, other) -> bool:
        return (
            self.elevator_id == other.elevator_id and
            self.floor == other.floor and
            self.sense == other.sense and
            self.queue == other.queue and
            self.wait == self.wait and
            self.timestamp == other.timestamp
        )

    def is_available_to_take_in_call(self, call: Call) -> bool:
        """
        Test if Elevator is able to take a "in" call.

        Paramaters
        ----------
        call : Call
            Call object with call.call_type == "in".

        Returns
        -------
        is_available : bool
            True if the Elevetar is able to take the call, otherwise False.
        """
        if self.queue.is_empty:
            is_available = False
        else:
            last_call = self.queue.calls[-1]
            is_available = (
                self.elevator_id == call.elevator_id and
                last_call.sense == call.sense
            )
        return is_available

    def is_available_to_take_out_call(self, call: Call) -> bool:
        """
        Test if Elevator is able to take a "out" call.

        Paramaters
        ----------
        call : Call
            Call object with call.call_type == "out".

        Returns
        -------
        is_available : bool
            True if the Elevetar is able to take the call, otherwise False.
        """
        if self.queue.is_empty:
            is_available = True
        else:
            is_available = (
                self.sense == call.sense and
                (self.sense == "upward" and self.floor <= call.floor) or
                (self.sense == "downward" and self.floor >= call.floor)
            )
        return is_available

    def is_available_to_take_call(self, call: Call) -> bool:
        """
        Test if Elevator is able to take a call.

        Paramaters
        ----------
        call : Call
            Pending call.

        Returns
        -------
        is_available : bool
            True if the Elevetar is able to take the call, otherwise False.
        """
        if call.call_type == "in":
            is_available = self.is_available_to_take_in_call(call)
        else:
            is_available = self.is_available_to_take_out_call(call)
        return is_available

    def take_call(self, call: Call) -> None:
        """
        Add call to elevator queue. This method don't validate if the elevator
        is available to take the call.

        Parameters
        ----------
        call : Call
            Pending call.
        """
        if call.call_type == "in":
            self.remove_answered_calls()
        self.sense = "upward" if self.floor <= call.floor else "downward"
        self.queue.append(call)

    def remove_answered_calls(self) -> None:
        """
        Remove calls answered from elevator queue. When sense is "upward"
        remove calls under the current elevator floor. When sense is
        "downward" remove calls above the current elevator floor.
        Unset elevator sense when is empty.
        """
        if not self.queue.is_empty:
            call_floor = self.queue.calls[-1].floor
            is_answered = (
                (self.sense == "upward" and self.floor >= call_floor) or
                (self.sense == "downward" and self.floor <= call_floor)
            )
            if is_answered:
                self.queue.pop()
                self.remove_answered_calls()
        else:
            self.sense = ""

    def update_position(self, position: int, timestamp: datetime) -> None:
        """
        Update elevator floor. Also remove answered calls when is appropriate.
        When not the last_call is "out" and the delta time between timestamp
        and last_call.timestamp is equal or lower than than self.wait.

        Paremeters
        ----------
        position : int
            Floor where the elevator is located.
        timestamp : datetime
            Last timestamp.
        """
        self.floor = position
        if not self.queue.is_empty:
            last_call = self.queue.calls[-1]
            if self.floor == last_call.floor:
                last_call(timestamp)
            if (not last_call.not_attended and
                    (last_call.call_type == "in" or
                     self.wait < timestamp - last_call.timestamp)):
                self.remove_answered_calls()


class ElevatorSystem(BaseModel):
    """
    Class to manage calls in an elevator system.

    Parameters
    ----------
    n_elevators : int
        Number of elevators that the system manages. Must be a positive
        integer.
    n_floors : int
        Number of floors that the system has. Must be a positive integer.
    wait : timedelta, default=timedelta(seconds=10)
        Seconds that the elevator waits before clean a ready to clean out call
        from its queue. The implications of this is that an elevator that took
        an out call wait for the in call, if no in call received the elevator
        is able to take other calls.
    elevators : List[Elevator]
        List of elevators that make up the system.
    queue : ElevatorQueue,
        Queue with calls pending assignment.
    """
    n_elevators: PositiveInt
    n_floors: PositiveInt
    wait: timedelta = timedelta(seconds=10)
    elevators: List[Elevator] = []
    queue: ElevatorQueue = ElevatorQueue()

    def __init__(self, **data) -> None:
        super().__init__(**data)
        self.elevators = [Elevator(elevator_id=elevator_id, wait=self.wait)
                          for elevator_id in range(self.n_elevators)]

    def get_elevators_available(self, call: Call) -> List[Elevator]:
        """
        Get elevators that are available to take call.

        Parameters
        ----------
        call : Call
            Call to evaluate.

        Returns
        -------
        elevators_available : List[Elevator]
            List of elevators available to take call.
        """
        elevators_available = []
        for elevator in self.elevators:
            if elevator.is_available_to_take_call(call):
                elevators_available.append(elevator)
        return elevators_available

    def get_nearest_elevator(
        self,
        elevators: List[Elevator],
        call: Call
    ) -> Elevator:
        """
        Get the nearest elevator to a call.
        When is more than one return the first.

        Parameters
        ----------
        elevators : List[Elevator]
            List of elevators to evaluate.
        call : Call
            Call to evaluate.

        Returns
        -------
        nearest_elevator : Elevator
            Nearest elevator to call.
        """
        minimum_distance = self.n_floors
        nearest_elevator = elevators[0]
        for elevator in elevators:
            distance = abs(elevator.floor - call.floor)
            if distance < minimum_distance:
                nearest_elevator = elevator
                minimum_distance = distance
        return nearest_elevator

    def take_call(self, call: Call) -> None:
        """
        Assign call to an available elevator. When there are elevators
        available, the nearest one is assigned; otherwise the call is entered
        into self.queue.

        Parameters
        ----------
        call : Call
            Call to assign to an available elevator.
        """
        elevators = self.get_elevators_available(call)
        if elevators:
            nearest_elevator = self.get_nearest_elevator(elevators, call)
            nearest_elevator.take_call(call)
        else:
            self.queue.append(call)

    @validate_arguments
    def update_state(self, state: Dict[int, int], timestamp: datetime) -> None:
        """
        Update elevator positions and assign self.queue calls if elevators are
        available.

        Parameters
        ----------
        state : dict
            Dictionary with elevator positions with the structure
            {elevator_id : floor}.
        timestamp : datetime
            The time of the state.
        """
        for elevator_id in range(self.n_elevators):
            elevator = self.elevators[elevator_id]
            elevator.update_position(state[elevator_id], timestamp)
        if not self.queue.is_empty:
            call = self.queue.pop()
            self.take_call(call)

    @validate_arguments
    def take_request(self, request: Dict) -> None:
        """
        Take request to update elevator positions and assign call if call data
        is sent.

        Parameters
        ----------
        request : dict
            Dictionary with the content of request.
            {
                timestamp: "yyyy-mm-dd hh:mm:ss",
                call : {floor, sense, elevator_id, call_type}
                state: {elevator_1: floor_1, .., elevator_N: floor_N}
            }
            The key call is optional.
        """
        self.update_state(request["state"], request["timestamp"])
        if request.get("call"):
            call = Call(**request["call"])
            if call.floor > self.n_floors:
                raise ValueError(
                    "Call can not come from a floor greather than n_floors")
            self.take_call(call)

    def __str__(self) -> str:
        """
        Print the queue of each elevator.
        """
        string = ""
        for i, elevator in enumerate(self.elevators):
            calls_string = ""
            if not elevator.queue.is_empty:
                calls_string = ", ".join([
                    str(call.floor) for call in elevator.queue.calls])
            calls_string = "[" + calls_string + "]"
            string += f"{i}: {calls_string}\n"
        return string
