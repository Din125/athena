from dotenv import load_dotenv
from llama_agents import (
    AgentService,
    ControlPlaneServer,
    SimpleMessageQueue,
    AgentOrchestrator,
)
from llama_index.core.agent import ReActAgent
from llama_agents import LocalLauncher
import asyncio
from prompts import planner_prompt
from llama_index.core import PromptTemplate
import os
import uuid
from llama_index.llms.together import TogetherLLM
from llama_index.llms.openai import OpenAI

load_dotenv()

message_queue = SimpleMessageQueue()
control_plane = ControlPlaneServer(
    message_queue=message_queue,
    orchestrator=AgentOrchestrator(llm=OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"),model="gpt-4"))
)

def create_agent_service():
    agent = ReActAgent.from_tools([],llm=OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"),model="gpt-4"))
    planner_agent = PromptTemplate(planner_prompt)
    prompt_dictp = {
        "agent_worker:system_prompt": planner_agent
    }
    agent.update_prompts(prompt_dictp)
    
    return AgentService(
        agent=agent,
        message_queue=message_queue,
        description="You're an Expert Educational planning agent. You always provide a plan.",
        service_name=f"Educational_Planner_{uuid.uuid4().hex}",  # Add unique identifier
    )

def call(task):
    """
    This tool communicates with a control plane that manages a sub-agent:
    Study Plan Creator: Creates personalized study plans based on what needs to be studied, breaking it down into daily tasks.
    """
    agent_service = create_agent_service()  # Create a new agent service for each call
    launcher = LocalLauncher(
        [agent_service],
        control_plane,
        message_queue,
    )

    try:
        result = launcher.launch_single(task)
    except ValueError as e:
        if "signal only works in main thread" in str(e):
            # Fallback to running without signal handling
            async def run_without_signal():
                return await launcher.alaunch_single(task)
            result = asyncio.run(run_without_signal())
        else:
            raise

    print("Llama orchestrator : ", result)
    return result