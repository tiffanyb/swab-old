import math
import time
import subprocess
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

pose_handler = None
g_x = 0
g_y = 0
g_z = 0
a_node = Node()
def euler_to_quaternion(roll_deg, pitch_deg, yaw_deg):
    """
    Convert Euler angles in degrees to a (x, y, z, w) quaternion.
    Rotation order is roll (X), pitch (Y), yaw (Z).
    """
    roll  = math.radians(roll_deg)
    pitch = math.radians(pitch_deg)
    yaw   = math.radians(yaw_deg)

    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)

    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy
    return (x, y, z, w)

def set_pose_via_service(
    model_name="r1_rover",
    x=0.0, y=0.0, z=0.0,
    roll_deg=0.0, pitch_deg=0.0, yaw_deg=180.0,
    service="/world/default/set_pose"
):
    """
    Call the /world/default/set_pose service in Ignition Gazebo to set a model's pose.
    We'll build a text-based request for 'ignition.msgs.Pose' and pass it to 'ign service'.
    """

    # Convert Euler angles to quaternion
    (qx, qy, qz, qw) = euler_to_quaternion(roll_deg, pitch_deg, yaw_deg)

    # Build the request in text format (protobuf) for ignition.msgs.Pose
    request_text = f"""name: "{model_name}"
position:
  {{x: {x},
  y: {y},
  z: {z}}},
orientation:
  {{x: {qx},
  y: {qy},
  z: {qz},
  w: {qw}}}
"""

    # Construct the command to call 'ign service'
    cmd = [
        "gz", "service",
        "-s", service,
        "--reqtype", "gz.msgs.Pose",
        "--reptype", "gz.msgs.Boolean",
        "--timeout", "2000",  # ms
        "--req", request_text
    ]

    # print("Executing:", " ".join(cmd))
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Service call output:")
        print(result.stdout.strip())
        if result.stderr.strip():
            print("Errors/Warnings:", result.stderr.strip())
    except subprocess.CalledProcessError as e:
        print("Failed to call service.")
        print("Return code:", e.returncode)
        print("Stdout:", e.stdout)
        print("Stderr:", e.stderr)


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

def get_current_pose():
    global pose_handler
    return pose_handler.position

def init(world, rover_name):
    global pose_handler
    pose_handler = PoseHandler(rover_name)
    pose_options = SubscribeOptions()
    pose_options.msgs_per_sec = 5

    if not a_node.subscribe(Pose_V, f"/world/{world}/pose/info", pose_handler, pose_options):
        print("pose subscription failed!")
    else:
        print("pose subscription succeed!")

def set(rover_name, value, check_position=False, maxturn=None):
    global g_x
    global g_y
    global g_z
    turn = False
    while True:
        x, y, z = get_current_pose()
        if check_position:
            if abs(g_x - x) > 2 or abs(g_y - y) > 2 or abs(g_z - z) > 2:
                g_x = x
                g_y = y
                g_z = z
                turn = True
                break
        if g_x != x or g_y != y or g_z != z:
            g_x = x
            g_y = y
            g_z = z
            break
        time.sleep(2)
    print(f"Current position: x: {x}, y: {y}, z: {z}")
    # Example: set "my_rover" to heading = 180 deg (yaw=180) at position (1,2,0).
    if turn:
        set_pose_via_service(
        model_name=rover_name,
        x=x, y=y, z=z,
        yaw_deg=maxturn)  # 180-degree heading
    else:
        set_pose_via_service(
        model_name=rover_name,
        x=x, y=y, z=z,
        yaw_deg=value  # 180-degree heading
    )

if __name__ == "__main__":
    node = Node()
    init(node, 'default', 'r1_rover')
    try:
        while True:
            time.sleep(0.1)
            print(get_current_pose())
            print("===================================")
    except KeyboardInterrupt:
        pass
