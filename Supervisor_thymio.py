from agent import Agent
from styles import styles
import streamlit as st
import random
import ell
import numpy as np
from matplotlib import pyplot as plt
import re
from ell import Message
import time
from thymiodirect import Thymio
from thymiodirect.thymio_serial_ports import ThymioSerialPort

prox_left = None
prox_right = None


def process_response_item(response: Message):
    message = dict()
    message["THOUGHTS"] = response.text.split("MESSAGE" + ":")[0]
    message["MESSAGE"] = response.text.split("MESSAGE" + ":")[1].split("ACTION" + ":")[0]
    message["ACTION"] =  response.text.split("ACTION"+ ":")[1]
    return message

def get_move(pos, new_pos, agent_direction):
    absolute_direction = ""
    if pos[0] == new_pos[0] and pos[1] == new_pos[1] + 1:
        absolute_direction = "DOWN"
    elif pos[0] == new_pos[0] and pos[1] == new_pos[1] - 1:
        absolute_direction = "UP"
    elif pos[0] == new_pos[0] + 1 and pos[1] == new_pos[1]:
        absolute_direction = "LEFT"
    elif pos[0] == new_pos[0] - 1 and pos[1] == new_pos[1]:
        absolute_direction = "RIGHT"
    else:
        raise ValueError("Invalid move")
    
    MVT = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    relative_index = MVT.index(absolute_direction)

    dico = {
        "UP": ["UP", "DOWN", "LEFT", "RIGHT"],
        "DOWN": ["DOWN", "UP", "RIGHT", "LEFT"],
        "LEFT": ["RIGHT", "LEFT", "UP", "DOWN"],
        "RIGHT": ["LEFT", "RIGHT", "DOWN", "UP"]
    }
    relative_direction = dico[agent_direction][relative_index]
    return absolute_direction, relative_direction

def init_thymio():
    thymio_serial_ports = ThymioSerialPort.get_ports()
    serial_port = thymio_serial_ports[0].device
    th = Thymio(use_tcp=False,
                    serial_port=serial_port,
                    host=None,
                    refreshing_coverage={
                        "prox.horizontal",
                        "button.center",
                        "prox.ground.delta"
                    },
                   )
    th.connect(delay=3, progress=lambda : print("Connecting to Thymio..."))
    time.sleep(4)
    for node in th.nodes():
        print(node)
    return th

th = init_thymio()

class Supervisor:
    
    def __init__(self, n_agents=2, size=(4, 4), speed=100) -> None:
        # Initialize the Supervisor
        self.agents = []
        self.treasures = []
        self.conversation_hist = []
        self.size = size
        self.bot_map = np.full((10, 10), False)
        self.object_map = np.full((10, 10), False)
        self.speed = speed

        # Initialize the agents
        self._init_agents(n_agents)

        # Print informations
        self._display_infos()

        # Start the game
        self._run()

    

    def _display_infos(self):
        # Display the informations
        print('Agent   | Position |  Goal Position  |')
        for agent in self.agents:
            print(f'{agent.name} |  {agent.pos}  |     {agent.goal_pos}')

        # Wait for the user to press a key (time to init the game)
        print('Press any key to begin the game...')
        input()


    def _init_agents(self, n_agents):
        # Get all available positions
        available_positions = [(i, j) for i in range(self.size[0]) for j in range(self.size[1])]
        
        # Create agents
        for i in range(n_agents):
            # Assign a random position
            pos = random.choice(available_positions)
            self.bot_map[pos] = True 
            available_positions.remove(pos)

            # Assign random goal position
            goal_pos = random.choice(available_positions)
            available_positions.remove(goal_pos)

            # Create agent
            agent = Agent(None, i, f'Thymio{i+1}', pos, goal_pos)
            self.agents.append(agent)

    def _launch_discussion(self, round=1):
        # For each round
        for _ in range(round):

            # For each agent
            for i, agent in enumerate(self.agents):

                # If it's the first agent
                if i == 0:
                    self.conversation_hist.append(ell.user(f"{agent.name}, you are the first to communicate!"))

                # Generate the message
                print("POS", agent.pos)
                print("Allowed", agent.allowed_move)
                message = agent.act(len(self.agents), self.conversation_hist)
                extraction = process_response_item(message)
                command = extraction["ACTION"]
                new_pos = tuple(int(v) for v in re.findall(r'\d+', command))
                self.bot_map[agent.pos] = False
                self.bot_map[new_pos] = True
                
                # Calcul du mvt à envoyer au BOT
                agent.orientation, agent.direction = get_move(agent.pos, new_pos, agent.orientation)
                agent.pos = new_pos

                # Display the message
                agent_class = f"agent{agent.id + 1}"
                st.markdown(f"""
                    <div class="chat-container">
                        <div class="message-bubble {agent_class}">
                            <div class="agent-name">{agent.name}</div>
                            {message.content[-1].text}
                        </div>
                    </div>
                """, unsafe_allow_html=True)


                # Add the message to the conversation history
                #response = ell.user([f'{agent.name}:', message])
                hist = extraction["MESSAGE"]
                self.conversation_hist.append(ell.user([f'{agent.name}:', hist]))
    
    def _run(self):
        global prox_left, prox_right

        # Start the game
        print('Run the game !')
        
        # # Set title & styles of the page
        st.title("Conversation entre agents LLM")
        st.markdown(styles, unsafe_allow_html=True)

        # Initialize the Thymio
        assert len(self.agents) == len(th.nodes())
        for agent, node in zip(self.agents, th.nodes()):
            agent.link_thymio(node)
            print(f"Agent {agent.name} linked to node {node}")

        # While the game is running
        while True:
            # Launch the discussion
            self._update_agent_status()
            self._launch_discussion()

            # Interpret in robot space
            print('Discussion over. Press any key to continue...')
            input()

            # Init positions
            for agent in self.agents:
                prox_left = th[node_id]["prox.ground.delta"][0]
                prox_right = th[node_id]["prox.ground.delta"][1]
                print(f"Agent {agent.name}:{agent.node_id}, going to init node")
                prox_right, prox_left = th[agent.node_id]["prox.ground.delta"]
                self.play(agent.node_id)

            # Interpret in robot space
            for agent in self.agents:
                prox_left = th[node_id]["prox.ground.delta"][0]
                prox_right = th[node_id]["prox.ground.delta"][1]
                node_id = agent.node_id
                # Init sensor values
                prox_right, prox_left = th[agent.node_id]["prox.ground.delta"]

                self.rotate(node_id, agent.direction)
                th[node_id]["motor.left.target"] = 0
                th[node_id]["motor.right.target"] = 0

                self.play(node_id)
                th[node_id]["motor.left.target"] = 0
                th[node_id]["motor.right.target"] = 0

    def _update_agent_status(self):
        for agent in self.agents :
            agent.vision = {}
            agent.allowed_move = []
            event = self.object_map[agent.pos]
            if event :
                if event == "trap":
                    agent.status = "immobilised"
                    self.immobilisation[agent.name] = 3
                    agent.vision[agent.pos] = "trap"
                elif event == agent.color: # L'agent a trouvé son trésor
                    agent.goal_achieved = True
                    agent.vision[agent.pos] = event + " treasure"
                else : # L'agent a trouvé le trésor d'un autre
                    agent.vision[agent.pos] = event + " treasure"

            x = agent.pos[0]
            y = agent.pos[1]
            agent.neighbour = dict()

            # Compute all available moves
            available_moves = []
            if x - 1 >= 0:
                available_moves.append((x - 1, y))
            if x + 1 < self.size[0]:
                available_moves.append((x + 1, y))
            if y - 1 >= 0:
                available_moves.append((x, y - 1))
            if y + 1 < self.size[1]:
                available_moves.append((x, y + 1))

            # Update the vision of the agent
            for (x_pos, y_pos) in available_moves:
                if self.object_map[x_pos, y_pos] != False:
                    agent.vision[(x_pos, y_pos)] = "object"
                    agent.allowed_move.append((x_pos, y_pos))
                elif self.bot_map[(x_pos, y_pos)] != False:
                    agent.vision[(x_pos, y_pos)] ="tymio"
                else : 
                    agent.vision[(x_pos, y_pos)] ="empty"
                    agent.allowed_move.append((x_pos, y_pos))

            for agent in self.agents:
                order_robot_space = "RIGHT"
                node_id = agent.node_id

                # Init sensor values
                prox_right, prox_left = th[agent.node_id]["prox.ground.delta"]


                self.rotate(node_id, order_robot_space)
                th[node_id]["motor.left.target"] = 0
                th[node_id]["motor.right.target"] = 0

                self.play(node_id)
                th[node_id]["motor.left.target"] = 0
                th[node_id]["motor.right.target"] = 0
            


    def rotate(self, node_id, rotation_order="RIGHT"):
        if rotation_order == "RIGHT":
            th[node_id]["motor.left.target"] = self.speed
            th[node_id]["motor.right.target"] = -self.speed
        else:
            th[node_id]["motor.left.target"] = -self.speed
            th[node_id]["motor.right.target"] = self.speed

        time.sleep(2.20)
        print("Rotation done !")

        th[node_id]["motor.left.target"] = self.speed
        th[node_id]["motor.right.target"] = self.speed


    def intersection(self, node_id, prox_left, prox_right):

        ground_left = th[node_id]["prox.ground.delta"][0]
        ground_right = th[node_id]["prox.ground.delta"][1]

        thresh = 300
        # Check if intersection has been reached
        delta = max(prox_left - ground_left , prox_right - ground_right)
        print("delta", delta , "ground_left", ground_left, "prox_left", prox_left, "ground_right", ground_right, "prox_right", prox_right)

        if delta > thresh:
            print("Intersection detected !")
            # th.set_variable_observer(node_id, rotate) # a changer rihgt/left

            # Avoid correction at intersection
            th[node_id]["motor.left.target"] = self.speed
            th[node_id]["motor.right.target"] = self.speed
            time.sleep(1.9) # We need to wait a bit before rotating to get a good angle
            th[node_id]["motor.left.target"] = 0
            th[node_id]["motor.right.target"] = 0
            return True
        return False

    def play(self, node_id):
        th.set_variable_observer(node_id, line_behavior)
        print("Playing ", node_id)

        ground_left = th[node_id]["prox.ground.delta"][0]
        ground_right = th[node_id]["prox.ground.delta"][1]


        # TODO Take a decision from buffered values
        # TODO cooldown intersection
        while not self.intersection(node_id, ground_left, ground_right):
            ground_left = th[node_id]["prox.ground.delta"][0]
            ground_right = th[node_id]["prox.ground.delta"][1]
            time.sleep(0.1)

        th.set_variable_observer(node_id, lambda node_id: None)


def line_behavior(node_id, speed=100):
    global prox_left, prox_right
    max_steer = 10

    ground_left = th[node_id]["prox.ground.delta"][0]
    ground_right = th[node_id]["prox.ground.delta"][1]

    # Set motor speed and correction
    tmp = max_steer * ground_left - max_steer * ground_right
    steerL = tmp // speed
    th[node_id]["motor.left.target"] = speed + steerL
    th[node_id]["motor.right.target"] = speed - steerL
    print("Motor left", th[node_id]["motor.left.target"], "Motor right", th[node_id]["motor.right.target"] , "steerL", steerL)
    prox_left, prox_right = th[node_id]["prox.ground.delta"]

if __name__ == "__main__":
    s = Supervisor(n_agents=2, size=(10,10))
    s._run()
    