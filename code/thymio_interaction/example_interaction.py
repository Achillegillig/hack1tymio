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

# wait 2-3 sec until robots are known
time.sleep(4)

node_id = th.first_node()

for node in th.nodes():
    print(node)
# print(node_id)

print(th[node_id]["prox.horizontal"])


nodelist = list(th.nodes())
while True:
    th[nodelist[0]]["motor.left.target"] = 50
    th[nodelist[1]]["motor.left.target"] = 50

    if th[node_id]["button.center"]:
        th[nodelist[0]]["motor.left.target"] = 0
        th[nodelist[1]]["motor.left.target"] = 0

        break
    time.sleep(0.5)
