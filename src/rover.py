from __future__ import annotations

from dataclasses import dataclass, field
from logging import Logger, NullHandler, getLogger
from math import pi
from threading import Lock

from gz.transport13 import Node, Publisher, SubscribeOptions
from gz.math7 import Quaterniond
from gz.msgs10.actuators_pb2 import Actuators
from gz.msgs10.boolean_pb2 import Boolean
from gz.msgs10.entity_factory_pb2 import EntityFactory
from gz.msgs10.pose_v_pb2 import Pose_V

import attack
import automaton

def _pose_logger() -> Logger:
    logger = getLogger("rover.PoseHandler")
    logger.addHandler(NullHandler())

    return logger


@dataclass()
class PoseHandler:
    _name: str = field() 
    _lock: Lock = field(default_factory=Lock, init=False)
    _heading: float = field(default=0.0, init=False)
    _roll: float = field(default=0.0, init=False)
    _position: tuple[float, float, float] = field(default=(0.0, 0.0, 0.0), init=False)
    _clock: float = field(default=0.0, init=False)
    _logger: Logger = field(default_factory=_pose_logger, init=False)

    def __call__(self, msg: Pose_V):
        for pose in msg.pose:
            if pose.name == self._name:
                self._logger.debug(f"Received pose: {pose}")

                time = msg.header.stamp.sec + msg.header.stamp.nsec / 1e9
                q = Quaterniond(
                    pose.orientation.w,
                    pose.orientation.x,
                    pose.orientation.y,
                    pose.orientation.z,
                )

                with self._lock:
                    euler = q.euler()
                    self._heading = euler.z()
                    self._roll = euler.y()
                    self._position = (pose.position.x, pose.position.y, pose.position.z)
                    self._clock = time

                break

    @property
    def clock(self) -> float:
        with self._lock:
            return self._clock

    @property
    def heading(self) -> float:
        with self._lock:
            return self._heading * (180 / pi)

    @property
    def roll(self) -> float:
        with self._lock:
            return self._roll

    @property
    def position(self) -> tuple[float, float, float]:
        with self._lock:
            return self._position


@dataclass()
class Rover(automaton.Vehicle):
    _node: Node = field()
    _motors: Publisher = field()
    _pose: PoseHandler = field()
    _magnet: attack.Magnet = field()
    _velocity: float = field(default=0.0, init=False)
    _omega: float = field(default=0.0, init=False)

    @property
    def clock(self) -> float:
        return self._pose.clock

    @property
    def position(self) -> tuple[float, float, float]:
        return self._pose.position

    @property
    def heading(self) -> float:
        return self._pose.heading

    @property
    def roll(self) -> float:
        return self._pose.roll

    @property
    def omega(self) -> float:
        return self._omega

    @omega.setter
    def omega(self, target: float):
        if target != self._omega:
            msg = Actuators()
            msg.velocity.append(target)
            msg.velocity.append(target)

            self._motors.publish(msg)
            self._omega = target

    @property
    def velocity(self) -> float:
        return self._velocity

    @velocity.setter
    def velocity(self, target: float):
        if target != self._velocity:
            msg = Actuators()
            msg.velocity.append(-target)
            msg.velocity.append(target)

            self._motors.publish(msg)
            self._velocity = target


class RoverError(Exception):
    pass


class TransportError(RoverError):
    pass


def spawn(world: str, *, name: str = "r1_rover", magnet: attack.Magnet | None) -> Rover:
    logger = getLogger("rover")
    logger.addHandler(NullHandler())
    logger.setLevel('DEBUG')

    node = Node()
    msg = EntityFactory()
    # TODO: VERY HACKY HARDCODED PATH
    # msg.sdf_filename = "/app/resources/models/r1_rover/model.sdf"
    msg.sdf_filename = "/app/resources/models/rover_ackermann/model.sdf"
    msg.name = name
    msg.allow_renaming = False
    res, rep = node.request(f"/world/{world}/create", msg, EntityFactory, Boolean, timeout=1000)

    if not res:
        raise TransportError("Failed to send Gazebo message for rover creation")

    if not rep.data:
        raise RoverError("Could not create rover Gazebo model")

    print("Created rover model in gazebo world")
    motors = node.advertise(f"/model/{name}/command/motor_speed", Actuators)

    if not motors.valid():
        raise TransportError("Could not register publisher for motor control")

    logger.debug("Created motor topic publisher")

    pose = PoseHandler(name)
    pose_options = SubscribeOptions()
    pose_options.msgs_per_sec = 10

    if not node.subscribe(Pose_V, f"/world/{world}/pose/info", pose, pose_options):
        raise TransportError()

    if magnet is None:
        magnet = attack.StationaryMagnet(0.0)

    return Rover(node, motors, pose, magnet)

def remove(world: str, *, name: str = "r1_rover"):
    node = Node()
    msg = EntityFactory()
    # msg.sdf_filename = "r1_rover/model.sdf"
    msg.name = name
    msg.allow_renaming = False
    res, rep = node.request(f"/world/{world}/remove", msg, EntityFactory, Boolean, timeout=1000)

    if not res:
        raise TransportError("Failed to send Gazebo message for rover creation")

    if not rep.data:
        raise RoverError("Could not create rover Gazebo model")
