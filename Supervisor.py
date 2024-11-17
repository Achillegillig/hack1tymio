from agent import Agent
from styles import styles
import streamlit as st
import random
import ell
import numpy as np
from matplotlib import pyplot as plt
import re
from ell import Message


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


class Supervisor:
    
    def __init__(self, n_agents=2, size=(4, 4)) -> None:
        # Initialize the Supervisor
        self.agents = []
        self.treasures = []
        self.conversation_hist = []
        self.size = size
        self.bot_map = np.full((10, 10), False)
        self.object_map = np.full((10, 10), False)

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

        directions = []

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
            agent.orientation, relative_direction = get_move(agent.pos, new_pos, agent.orientation)
            directions.append(relative_direction)
                
            print("Direction", relative_direction)
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

        with open("orders.txt", 'w+') as f:
            for i, direction in enumerate(directions):
                f.write(f'{direction}\n')


    def _run(self):
        # Start the game
        print('Run the game !')
        
        # Set title & styles of the page
        st.title("Conversation entre agents LLM")
        st.markdown(styles, unsafe_allow_html=True)

        # While the game is running
        while True:
            # Launch the discussion
            self._update_agent_status()
            self._launch_discussion()
            print('Discussion over. Press any key to continue...')
            input()

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



