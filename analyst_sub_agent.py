from dotenv import load_dotenv
import os 
from llama_index.llms.together import TogetherLLM
from prompts import planner_prompt, analyst_prompt
from  llama_index.core import PromptTemplate
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI


load_dotenv()






agent2 = ReActAgent.from_tools([], llm=OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"),model="gpt-4"))


def analyst_agent(query):
    """
    Comprehension Analyzer:
    Analyzes the user's responses to understand their comprehension of topics.
    Use this tool to analyze student comprehension.
    
    """
    analyst_agent = PromptTemplate(analyst_prompt)
    prompt_dicta = {
            "agent_worker:system_prompt" : analyst_agent
        }

    agent2.update_prompts(prompt_dicta)

    result = agent2.chat(query)
    return result