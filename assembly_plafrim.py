import streamlit as st
import os
import dotenv
import ell
dotenv.load_dotenv()

class Assembly:
    def __init__(self, model=os.getenv('MODEL')) -> None:
        self.agents = []
        self.model = model
        self.conversation_hist = []

    def launch_round(self):
        for i, agent in enumerate(self.agents):
            if i == 0:
                self.conversation_hist.append(ell.user(f"{agent.name}, you are the first to communicate!"))

            message = agent.act(self.conversation_hist)
            agent_class = f"agent{agent.id + 1}"
            st.markdown(f"""
                <div class="chat-container">
                    <div class="message-bubble {agent_class}">
                        <div class="agent-name">{agent.name}</div>
                        {message.content[-1].text}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            self.conversation_hist.append(ell.user([f'{agent.name}:', message]))