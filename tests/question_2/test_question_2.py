import json
from pathlib import Path
from datetime import datetime, timedelta
from cencosud.question_2.call import Call
from cencosud.question_2.elevator import Elevator, ElevatorSystem


class TestElevatorSystem:
    n_elevators = 3
    n_floors = 10
    wait = timedelta(seconds=10)

    with open(Path.joinpath(Path(__file__).parent, "requests.json"),
              encoding="utf-8") as f:
        requests = json.load(f)["data"]

    with open(Path.joinpath(Path(__file__).parent, "system_states.txt"),
              encoding="utf-8") as f:
        system_states = f.read()

    def test_get_elevators_available(self):
        es_system = ElevatorSystem(
            n_elevators=self.n_elevators,
            n_floors=self.n_floors,
            wait=self.wait)
        elevators = [Elevator(elevator_id=elevator_id, wait=self.wait)
                     for elevator_id in range(self.n_elevators)]
        assert all(es == e for es, e in zip(es_system.elevators, elevators))

    def test_get_nearest_elevator(self):
        es_system = ElevatorSystem(
            n_elevators=self.n_elevators,
            n_floors=self.n_floors,
            wait=self.wait)
        es_system.elevators[0].floor = 10
        es_system.elevators[1].floor = 1
        es_system.elevators[2].floor = 5

        call = Call(**{
            "call_type": "out",
            "floor": 7,
            "sense": "upward",
        })
        nearest_elevator = es_system.get_nearest_elevator(
            es_system.elevators, call)
        assert nearest_elevator.elevator_id == 2

    def test_take_call(self):
        es_system = ElevatorSystem(
            n_elevators=self.n_elevators,
            n_floors=self.n_floors,
            wait=self.wait)
        call = Call(call_type="out", floor=7, sense="upward")
        es_system.take_call(call)
        assert es_system.elevators[0].queue.calls[0] == call

    def test_take_call_when_no_elevator_available(self):
        es_system = ElevatorSystem(
            n_elevators=self.n_elevators,
            n_floors=self.n_floors,
            wait=self.wait)

        call = Call(call_type="out", floor=7, sense="upward")
        for elevator in es_system.elevators:
            elevator.take_call(call)

        call = Call(call_type="out", floor=3, sense="downward")
        es_system.take_call(call)
        assert es_system.queue.calls[0] == call

    def test_update_state(self):
        es_system = ElevatorSystem(
            n_elevators=self.n_elevators,
            n_floors=self.n_floors,
            wait=self.wait)
        state = {
            0: 10,
            1: 2,
            2: 5
        }
        es_system.update_state(state, datetime(2018, 1, 1))
        system_state = {}
        for elevator in es_system.elevators:
            system_state[elevator.elevator_id] = elevator.floor
        assert system_state == state

    def test_take_request(self):
        es_system = ElevatorSystem(
            n_elevators=self.n_elevators,
            n_floors=self.n_floors,
            wait=self.wait)
        request = {
            "timestamp": "2022-05-13 08:00:00",
            "call": {
                "floor": 2,
                "sense": "upward",
                "call_type": "out"
            },
            "state": {
                "0": 5,
                "1": 3,
                "2": 10
            }
        }
        es_system.take_request(request)
        call = Call(**request["call"])
        assert es_system.elevators[1].queue.calls[0] == call

    def test_take_request_with_multiple_requests(self):
        es_system = ElevatorSystem(
            n_elevators=self.n_elevators,
            n_floors=self.n_floors,
            wait=self.wait)
        system_states = ""
        for request in self.requests:
            es_system.take_request(request)
            system_states += es_system.__str__() + "\n"
        assert system_states == self.system_states
