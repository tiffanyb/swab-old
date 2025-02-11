# from gz.transport13 import Node
# from gz.msgs10.actuators_pb2 import Actuators
# import time
# 
# msg = Actuators()
# msg.velocity.append(100)
# msg.velocity.append(300)
# 
# 
# name = "r1_rover"
# 
# node = Node()
# publisher = node.advertise(f"/model/{name}/command/motor_speed", Actuators)
# if not publisher.valid():
#     print("not valid")
# 
# time.sleep(3)
# # import ipdb; ipdb.set_trace()
# publisher.publish(msg)
# print("send")
# 

import math
import subprocess

from gz.math7 import Quaterniond

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

    print("Executing:", " ".join(cmd))
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

def main():
    # Example: set "my_rover" to heading = 180 deg (yaw=180) at position (1,2,0).
    set_pose_via_service(
        model_name="r1_rover",
        x=10.0, y=2.0, z=0.0,
        yaw_deg=180.0  # 180-degree heading
    )

if __name__ == "__main__":
    main()
