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
time.sleep(4)

node_id = th.first_node()
for node in th.nodes():
    print(node)

done = False

prox_left = th[node_id]["prox.ground.delta"][0]
prox_right = th[node_id]["prox.ground.delta"][1]

vars = th.variables(node_id)


print(th.variables(node_id))

def line_behavior(node_id):
    global done, prox_right, prox_left
    max_steer = 20
    speed = 50
    thresh = 50

    ground_left = th[node_id]["prox.ground.delta"][0]
    ground_right = th[node_id]["prox.ground.delta"][1]

    delta = max(abs(prox_left - ground_left), abs(prox_right - ground_right))
    print("delta", delta)
    if delta > thresh:
        th[node_id]["motor.left.target"] = 0
        th[node_id]["motor.right.target"] = 0
        done = True
        return

    tmp = max_steer * ground_left - max_steer * ground_right
    steerL = tmp // 50

    # Set motor speed and correction
    th[node_id]["motor.left.target"] = speed + steerL
    th[node_id]["motor.right.target"] = speed - steerL

    acc = th[node_id]["acc"]
    print(ground_left, ground_right)
    prox_left, prox_right = ground_left, ground_right
    #print("acc", acc)
    if th[node_id]["button.center"]:
        print("button.center")
        th[node_id]["motor.left.target"] = 0
        th[node_id]["motor.right.target"] = 0
        done = True


th.set_variable_observer(node_id, line_behavior)

while not done:
    time.sleep(0.1)
th.disconnect()


# while True:
#     th[node_id]["motor.left.target"] = 50
#     th[node_id]["motor.right.target"] = 50
#
#
#     if th[node_id]["button.center"]:
#         th[node_id]["motor.left.target"] = 0
#         th[node_id]["motor.right.target"] = 0
#
#         break
#     time.sleep(0.5)
