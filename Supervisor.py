from agent import Agent
from styles import styles
import streamlit as st
import random
import ell
import numpy as np
from message_processing import process_response_item


class Supervisor:
    
    def __init__(self, n_agents=5, size=(10, 10), colors = ["blue", "green", "red","yellow", "purple"]) -> None:
        # Initialize the Supervisor
        self.agents = []
        self.treasures = []
        self.conversation_hist = []
        self.size = size

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
        #self.goal_pos_mat = np.zeros((10,10))
        self.bot_map = np.full((10, 10), False)
        self.object_map = np.full((10, 10), False)
        # self.object_map = metttre les 4 couleurs sur le plateau
        
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
            agent = Agent(None, i, f'Thymio{i+1}', pos, goal_pos, color = self.colors[i])
            self.agents.append(agent)
            if agent.color != "purple" : # Le violet est le traître et n'a pas d'objectif
                self.object_map[goal_pos] = agent.color
        
        for i in range(3): # Ajout des pièges
            trap_pos = random.choice(available_positions)
            available_positions.remove(trap_pos)
            self.object_map[trap_pos] = "trap"


    def _launch_discussion(self, round=2):
        # For each round
        for _ in range(round):
            self.update_agent_status()

            # For each agent
            for i, agent in enumerate(self.agents):

                # If it's the first agent
                if i == 0:
                    self.conversation_hist.append(ell.user(f"{agent.name}, you are the first to communicate!"))

                # Generate the message
                if agent.name in self.immobilisation :
                    self.immobilisation[agent.name] = self.immobilisation[agent.name] -1
                    if self.immobilisation[agent.name] == 0:
                        del self.immobilisation[agent.name]
                        agent.status = "free to move"
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
                response = ell.user([f'{agent.name}:', message])
                hist = process_response_item(response)["MESSAGE"]
                #self.conversation_hist.append(ell.user([f'{agent.name}:', message]))
                self.conversation_hist.append(ell.user([f'{agent.name}:', hist]))
    
    def _run(self):
        # Start the game
        print('Run the game !')
        
        # Set title & styles of the page
        st.title("Conversation entre agents LLM")
        st.markdown(styles, unsafe_allow_html=True)

        # While the game is running
        while True:
            # Launch the discussion
            self._launch_discussion()
            print('Discussion over. Press any key to continue...')
            input()

    def update_agent_status(self):
        for agent in self.agents :
            event = self.object_map[agent.pos]
            if event :
                if event == "trap":
                    agent.status = "immobilised"
                    self.immobilisation[agent.name] = 3
                    agent.trigger_event = "trap"
                elif event == agent.color: # L'agent a trouvé son trésor
                    agent.goal_achieved = True
                    agent.trigger_event = event + " treasure"
                else : # L'agent a trouvé le trésor d'un autre
                    agent.trigger_event = event + " treasure"
            # agent.event_message(f"""You reached a cell with a trap. You canno't move for the next 3 turns""")
            else :
                agent.trigger_event = "None"


            x = agent.pos[0]
            y = self.pos[1]
            agent.neighbour = dict()
            
            p_neighbourg_x = np.array([x-1, x+1])
            p_neighbourg_y = np.array([y-1, y+1])

            for x_pos in p_neighbourg_x :
                for y_pos in p_neighbourg_y:
                    if y>= 0 and y <10 and y>= 0 and y <10 : # 10 est une valeur arbitraire en fonction de la taille du quadrillage
                        if self.object_map[x_pos, y_pos] != False:
                            agent.vision[np.array([x_pos, y_pos])] = "object"
                        elif self.bot_map[x_pos, y_pos] != False:
                            agent.vision[ np.array([x_pos, y_pos])] ="tymio"
                        else : 
                            agent.vision[ np.array([x_pos, y_pos])] ="empty"

