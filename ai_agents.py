import os
from dotenv import load_dotenv
from typing import List
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from consts import llm_model_type


# Load .env variables
load_dotenv()


# LLM Initialization
openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(max_retries=3, temperature=0,  # type: ignore
                 model_name=llm_model_type)


def get_agent_zero_shot_response(query: str, tools: List, messages_history: List, is_agent_verbose: bool = True, max_iterations: int = 3, return_thought_process: bool = False):
    """
    This function takes a query, a list of tools, and some optional parameters, initializes a
    conversational LangChain agent, and returns the agent's response to the query.
    """
    memory = ConversationBufferMemory(
        memory_key="chat_history")

    # Add messages to memory
    for message_dict in messages_history:
        message_value = message_dict['message']
        sender = message_dict['type']
        if (sender == 'user'):
            memory.chat_memory.add_user_message(message_value)
        if (sender == 'AI'):
            memory.chat_memory.add_ai_message(message_value)

    # Initialize agent
    agent = initialize_agent(
        tools, llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=is_agent_verbose, max_iterations=max_iterations, return_intermediate_steps=return_thought_process,  memory=memory)

    result = agent({"input": query})
    answer = result["output"]

    # Debug agent's answer
    print(answer)

    return answer
