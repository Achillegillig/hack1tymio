from thymiodirect import Connection
from thymiodirect import Thymio
from thymiodirect.thymio_serial_ports import ThymioSerialPort

import time

thymio_serial_ports = ThymioSerialPort.get_ports()
serial_port = thymio_serial_ports[0].device

print(serial_port)

use_tcp = False
host = None
tcp_port = None

# th = Thymio(serial_port=serial_port,
#             on_connect=lambda node_id:print(f"{node_id} is connected"))

th = Thymio(use_tcp=use_tcp,
                    serial_port=serial_port,
                    host=host, tcp_port=tcp_port,
                    refreshing_coverage={"prox.horizontal", "button.center"},
                   )

th.connect()

node_id = th.first_node()

print(th.nodes())

# print(node_id)

print(th[node_id]["prox.horizontal"])

if th[node_id]["button.center"]:
    print("button.center")
    done = True

# for i in range(0, 7):
#     th[id]["motor.left.target"] = 50
#     time.sleep(0.5)
