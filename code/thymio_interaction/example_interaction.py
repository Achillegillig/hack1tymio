from thymiodirect import Connection
from thymiodirect import Thymio

port = Connection.serial_default_port()

print(port)

th = Thymio(serial_port=port,
            on_connect=lambda node_id:print(f"{node_id} is connected"))
th.connect()

id = th.first_node()
print(id)

print(th[id]["prox.horizontal"])

th[id]["leds.top"] = [0, 0, 32]
