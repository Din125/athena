import streamlit as st
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from dotenv import load_dotenv
from prompts import main_agent_prompt
import os
from llama_index.core import PromptTemplate
from llama_orchestrator import call
import json
from sql_agent import database_read_write_agent
from llama_index.llms.together import TogetherLLM
from llama_index.llms.openai import OpenAI

load_dotenv()

def safe_call(input_dict):
    """
    This tool communicates with a control plane that manages one sub-agent:
    a. Study Plan Creator: Creates personalized study plans based on what needs to be studied, breaking it down into daily tasks.
    """
    try:
        # Convert the input dictionary to a JSON string
        input_json = json.dumps(input_dict)
        return call(input_json)
    except Exception as e:
        return f"Error in call function: {str(e)}"

@st.cache_resource
def initialize_agent():
    orchestrator = FunctionTool.from_defaults(fn=safe_call)
    database = FunctionTool.from_defaults(fn=database_read_write_agent)
    
    llm = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"),model="gpt-4")
    
    agent = ReActAgent.from_tools([orchestrator, database], llm=llm, verbose=True)
    main_agent = PromptTemplate(main_agent_prompt)
    prompt_dict = {
        "agent_worker:system_prompt": main_agent
    }
    agent.update_prompts(prompt_dict)
    return agent

def main():
    st.title("AI Study Assistant")
    st.write("Welcome to the AI Study Assistant. Ask questions or request study plans!")

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Get user input
    user_input = st.chat_input("You:")

    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Get AI response
        agent = initialize_agent()
        with st.spinner("Thinking..."):
            try:
                response = agent.chat(user_input)
                # Add AI response to chat history
                st.session_state.messages.append({"role": "assistant", "content": str(response)})
                with st.chat_message("assistant"):
                    st.markdown(str(response))
            except Exception as e:
                error_message = f"An error occurred: {str(e)}\nThe agent is unable to process this request. Please try again or ask a different question."
                st.session_state.messages.append({"role": "assistant", "content": error_message})
                with st.chat_message("assistant"):
                    st.markdown(error_message)

if __name__ == "__main__":
    main()