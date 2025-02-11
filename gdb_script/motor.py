from gz.transport13 import Node
from gz.msgs10.actuators_pb2 import Actuators
import time

publisher = None
a_node = Node()
def set(value): 
    if publisher is not None:
        msg = Actuators()
        msg.velocity.append(float(value * 2000) )
        msg.velocity.append(float(value * 2000) )
        time.sleep(2)
        publisher.publish(msg)
        print(f"Send Throttle Value {value} to Gazebo")
    else:
        print("Error with Motor publisher")


def init(rover_name):
    global publisher
    publisher = a_node.advertise(f"/model/{rover_name}/command/motor_speed", Actuators)
    if not publisher.valid():
        print("motor publisher is not valid")
