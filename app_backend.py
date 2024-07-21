from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from dotenv import load_dotenv
from prompts import main_agent_prompt
import os
from llama_index.core import PromptTemplate
from llama_orchestrator import call
import json
from sql_agent import database_read_write_agent
from analyst_sub_agent import analyst_agent
from llama_index.llms.together import TogetherLLM
from llama_index.llms.openai import OpenAI

load_dotenv()

def main_agent():
    

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

    analyst_agent1 = FunctionTool.from_defaults(fn=analyst_agent)
    orchestrator = FunctionTool.from_defaults(fn=safe_call)    
    database = FunctionTool.from_defaults(fn=database_read_write_agent)

    llm = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"),model="gpt-4")
    

    agent = ReActAgent.from_tools([orchestrator,database,analyst_agent1], llm=llm, verbose=True)

    main_agent = PromptTemplate(main_agent_prompt)

    prompt_dict = {
        "agent_worker:system_prompt": main_agent
    }

    agent.update_prompts(prompt_dict)

    print("Welcome to the ReActAgent Console Interaction. Type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() == 'exit':
            print("Exiting the program. Goodbye!")
            break

        try:
            response = agent.chat(user_input)
            print(f"\nAgent: {response}")
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("The agent is unable to process this request. Please try again or ask a different question.")

if __name__ == "__main__":
    main_agent()