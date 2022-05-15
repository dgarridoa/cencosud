from datetime import datetime, timedelta
from cencosud.question_2.call import Call


class ElevatorQueue:
    """
    Data structure to manage an elevator queue.

    Attributes
    ----------
    is_empty : bool
        True if no pending calls, else False.
    calls : list[Call]
        List with pending calls.
    """
    def __init__(self):
        self.is_empty = True
        self.calls = []

    def __eq__(self, other):
        return all(sc == oc for sc, oc in zip(self.calls, other.calls))

    def sort(self, reverse: bool):
        """
        Sorts pending calls by priority using their floor values.

        Parameters
        ----------
        reverse: bool
            When is True sorts calls in descending order by call.floor.
            When is False sorts calls in ascending order by call.floor.
        """
        self.calls.sort(key=lambda x: x.floor, reverse=reverse)

    def append(self, call: Call):
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

    def pop(self):
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


class Elevator:
    """
    Class to represent an elevator and manage its queue.

    Attributes
    ----------
    elevator_id :int
        Unique identifier.
    floor : int
        Floor where is located.
    sense : str
        Sense where is moving.
    queue : ElevatorQueue
        Pending calls.
    wait : timedelta
        Seconds that the elevator waits before clean its queue. The
        implications of this is that an elevator that took an out call wait for
        the in call, if no in call received the elevator is able to take other
        calls.
    """
    def __init__(self, elevator_id: int, wait: timedelta):
        self.elevator_id = elevator_id
        self.floor = 1
        self.sense = ""
        self.queue = ElevatorQueue()
        self.wait = wait
        self.timestamp = None

    def __eq__(self, other):
        return (
            self.elevator_id == other.elevator_id and
            self.floor == other.floor and
            self.sense == other.sense and
            self.queue == other.queue and
            self.wait == self.wait and
            self.timestamp == other.timestamp
        )

    def is_available_to_take_in_call(self, call: Call):
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
        is_available = self.elevator_id == call.elevator_id
        return is_available

    def is_available_to_take_out_call(self, call: Call):
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
            last_call = self.queue.calls[-1]
            if self.sense != last_call.sense:
                is_available = False
            elif (self.sense == "upward" and
                  self.floor <= call.floor and
                  last_call.sense == call.sense):
                is_available = True
            elif (self.sense == "downward" and
                  self.floor >= call.floor and
                  last_call.sense == call.sense):
                is_available = True
            else:
                is_available = False
        return is_available

    def is_available_to_take_call(self, call: Call):
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

    def take_call(self, call: Call):
        """
        Add call to elevator queue. This method don't validate if the elevator
        is available to take the call.

        Parameters
        ----------
        call : Call
            Pending call.
        """
        self.sense = "upward" if self.floor <= call.floor else "downward"
        self.queue.append(call)

    def remove_answered_calls(self):
        """
        Remove calls answered from elevator queue. When sense is "upward"
        remove calls under the current elevator floor. When sense is
        "downward" remove calls above the current elevator floor.
        Unset elevator sense when is empty.
        """
        if not self.queue.is_empty:
            call_floor = self.queue.calls[-1].floor
            up_answered = (self.sense == "upward" and
                           self.floor >= call_floor)
            down_answered = (self.sense == "downward" and
                             self.floor <= call_floor)
            if up_answered or down_answered:
                self.queue.pop()
                self.remove_answered_calls()
        else:
            self.sense = ""

    def update_position(self, position: int, timestamp: datetime):
        """
        Update elevator floor. Also remove answered calls when is appropriate.
        When the last_call is "in" the delta time between timestamp and
        last_call.timestamp should be greather than self.wait.

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
            if not (last_call.call_type == "in" and
                    self.wait >= timestamp - last_call.timestamp):
                self.remove_answered_calls()


class ElevatorSystem:
    """
    Class to manage calls in an elevator system.

    Attributes
    ----------
    n_elevators : int
        Number of elevators that the system manages.
    n_floors : int
        Number of floors that the system has.
    wait : timedelta
        Seconds that an elevator waits before clean its queue. The
        implications of this is that an elevator that took an out call wait for
        the in call, if no in call received the elevator is able to take other
        calls.
    elevators : list[Elevator]
        List of elevators that make up the system.
    """
    def __init__(self, n_elevators: int, n_floors: int, wait: timedelta):
        self.n_elevators = n_elevators
        self.n_floors = n_floors
        self.wait = wait
        self.elevators = [Elevator(elevator_id, wait)
                          for elevator_id in range(n_elevators)]
        self.queue = ElevatorQueue()

    def get_elevators_available(self, call: Call):
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

    def get_nearest_elevator(self, elevators, call):
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

    def take_call(self, call: Call):
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

    def update_state(self, state: dict, timestamp: datetime):
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
        for elevator in self.elevators:
            elevator.update_position(state[elevator.elevator_id], timestamp)
        if not self.queue.is_empty:
            call = self.queue.pop()
            self.take_call(call)

    def take_request(self, request: dict):
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
        timestamp = datetime.strptime(request["timestamp"],
                                      "%Y-%m-%d %H:%M:%S")
        state = {int(key): value for key, value in request["state"].items()}
        self.update_state(state, timestamp)
        if request.get("call"):
            call_data = request["call"]
            call_data["timestamp"] = timestamp
            call = Call(**call_data)
            if call.floor > self.n_floors:
                raise ValueError(
                    "Call can not come from a floor greather than n_floors")
            self.take_call(call)

    def __str__(self):
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
