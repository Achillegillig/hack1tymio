from agent import Agent
from styles import styles
import streamlit as st
import random
import ell
import numpy as np
from message_processing import process_response_item


class Supervisor:
    
    def __init__(self, n_agents=5, size=(10, 10)) -> None:
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
        self.goal_pos_mat = np.zeros((10,10))
        
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
            self.goal_pos_mat[goal_pos] = agent.color

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
                response = ell.user([f'{agent.name}:', message])
                hist = process_response_item(response)["COMMUNICATE"]
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


