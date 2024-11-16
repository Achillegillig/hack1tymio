from thymiodirect import Connection
from thymiodirect import Thymio
from thymiodirect.thymio_serial_ports import ThymioSerialPort

import time
import os

thymio_serial_ports = ThymioSerialPort.get_ports()
serial_port = thymio_serial_ports[0].device

print(serial_port)

use_tcp = False
host = None
tcp_port = None
speed = 100

th = Thymio(use_tcp=use_tcp,
                    serial_port=serial_port,
                    host=host, tcp_port=tcp_port,
                    refreshing_coverage={
                        "prox.horizontal",
                        "button.center",
                        "prox.ground.delta"
                    },
                   )
def on_comm_error(error):

    # loss of connection: display error and exit
    print(error)
    os._exit(1) # forced exit despite coroutines

th.on_comm_error = on_comm_error

th.connect()

# wait 2-3 sec until robots are known
time.sleep(2)

node_id = th.first_node()
for node in th.nodes():
    print(node)


def line_behavior(node_id):
    global done, prox_right, prox_left, line_moving
    max_steer = 10

    ground_left = th[node_id]["prox.ground.delta"][0]
    ground_right = th[node_id]["prox.ground.delta"][1]

    # Set motor speed and correction
    tmp = max_steer * ground_left - max_steer * ground_right
    steerL = tmp // 50
    th[node_id]["motor.left.target"] = speed + steerL
    th[node_id]["motor.right.target"] = speed - steerL

    # print(ground_left, ground_right)

    # Exit with center button at any time
    if th[node_id]["button.center"]:
        print("button.center")
        th[node_id]["motor.left.target"] = 0
        th[node_id]["motor.right.target"] = 0
        done = True

def request_llm():
    return "RIGHT"

def rotate(node_id, rotation_order="RIGHT"):
    if rotation_order == "RIGHT":
        th[node_id]["motor.left.target"] = speed
        th[node_id]["motor.right.target"] = -speed
    else:
        th[node_id]["motor.left.target"] = -speed
        th[node_id]["motor.right.target"] = speed

    stop_rotation = False
    time.sleep(2.20)
    print("Rotation done !")

    th[node_id]["motor.left.target"] = speed
    th[node_id]["motor.right.target"] = speed

def intersection(node_id, prox_left, prox_right):

    ground_left = th[node_id]["prox.ground.delta"][0]
    ground_right = th[node_id]["prox.ground.delta"][1]

    thresh = 300
    # Check if intersection has been reached
    delta = max(prox_left - ground_left , prox_right - ground_right)
    print("delta", delta , "ground_left", ground_left, "prox_left", prox_left, "ground_right", ground_right, "prox_right", prox_right)

    prox_left, prox_right = ground_left, ground_right

    if delta > thresh:
        print("Intersection detected !")
        # th.set_variable_observer(node_id, rotate) # a changer rihgt/left

        th[node_id]["motor.left.target"] = speed
        th[node_id]["motor.right.target"] = speed
        time.sleep(1.9)
        return True
    return False


def play(node_id):

    # line_behavior(node_id)
    th.set_variable_observer(node_id, line_behavior)

    ground_left = th[node_id]["prox.ground.delta"][0]
    ground_right = th[node_id]["prox.ground.delta"][1]

    while not intersection(node_id, ground_left, ground_right):
        ground_left = th[node_id]["prox.ground.delta"][0]
        ground_right = th[node_id]["prox.ground.delta"][1]
        time.sleep(0.1)

    th.set_variable_observer(node_id, lambda node_id: None)
    rotation_order = request_llm()
    rotate(node_id, rotation_order)




if __name__ == "__main__":

    # Set global variables
    done = False
    line_moving = True
    prox_left = th[node_id]["prox.ground.delta"][0]
    prox_right = th[node_id]["prox.ground.delta"][1]

    # th.set_variable_observer(node_id, play)
    compteur = 0
    while not done:
        time.sleep(0.1)

        for node_id in th.nodes():


            print("compteur", compteur)
            for node_id in th.nodes():
                play(node_id)

            #         th.set_variable_observer(node_id, line_behavior)
            #     while line_moving:
            #         time.sleep(0.1)
            #     th.set_variable_observer(node_id, lambda node_id: None)
            #     rotation_order = request_llm()
            #     rotate(node_id, rotation_order)
            #     line_moving = True
            # except KeyboardInterrupt:
            #     print("KeyboardInterrupt detected. Stopping Thymio...")
            #     th[node_id]["motor.left.target"] = 0
            #     th[node_id]["motor.right.target"] = 0
            #     done = True
            #     time.sleep(0.5)
            # except Exception as e:
            #     print("Exception caught!", e)
            #     th[node_id]["motor.left.target"] = 0
            #     th[node_id]["motor.right.target"] = 0
            #     done = True

    th.disconnect()
