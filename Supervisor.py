from agent import Agent
from styles import styles
import streamlit as st
import random
import ell
import time
from thymiodirect import Thymio
from thymiodirect.thymio_serial_ports import ThymioSerialPort



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
    
    def __init__(self, n_agents=5, size=(10, 10), speed=100) -> None:
        # Initialize the Supervisor
        self.agents = []
        self.treasures = []
        self.conversation_hist = []
        self.size = size
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
            available_positions.remove(pos)

            # Assign random goal position
            goal_pos = random.choice(available_positions)
            available_positions.remove(goal_pos)

            # Create agent
            agent = Agent(None, i, f'Thymio{i+1}', pos, goal_pos)
            self.agents.append(agent)

    def _launch_discussion(self, round=2):
        # For each round
        for _ in range(round):

            # For each agent
            for i, agent in enumerate(self.agents):

                # If it's the first agent
                if i == 0:
                    self.conversation_hist.append(ell.user(f"{agent.name}, you are the first to communicate!"))

                # Generate the message
                message = agent.act(self.conversation_hist)

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
                self.conversation_hist.append(ell.user([f'{agent.name}:', message]))
    
    def _run(self):
        # Start the game
        # print('Run the game !')
        
        # # Set title & styles of the page
        # st.title("Conversation entre agents LLM")
        # st.markdown(styles, unsafe_allow_html=True)
        assert len(self.agents) == len(th.nodes())
        for agent, node in zip(self.agents, th.nodes()):
            agent.link_thymio(node)
            print(f"Agent {agent.name} linked to node {node}")
        global prox_right, prox_left

        # While the game is running
        while True:
            # Launch the discussion
            #self._launch_discussion()
            # get orders from supervisor
            # returns LEFT, RIGHT, UP, DOWN, STOP (référentiel de la carte)
            # Interpret in robot space
            print('Discussion over. Press any key to continue...')
            input()
            # Init positions
            for agent in self.agents:
                print(f"Agent {agent.name}:{agent.node_id}, going to init node")
                prox_right, prox_left = th[agent.node_id]["prox.ground.delta"]
                self.play(agent.node_id)

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
    global done, prox_right, prox_left
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
    
