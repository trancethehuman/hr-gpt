import os
from dotenv import load_dotenv
from typing import List
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from consts import llm_model_type
from ai.ai_tools import tool_describe_skills, tool_retrieve_company_info, tool_calculate_stock_options


# Load .env variables
load_dotenv()


# LLM Initialization
openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(max_retries=3, temperature=0,  # type: ignore
                 model_name=llm_model_type)


def initialize_conversational_agent(tools: List = [], is_agent_verbose: bool = True, max_iterations: int = 3, return_thought_process: bool = False):
    memory = ConversationBufferMemory(memory_key="chat_history")

    # Initialize agent
    agent = initialize_agent(
        tools, llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=is_agent_verbose, max_iterations=max_iterations, return_intermediate_steps=return_thought_process, memory=memory)

    return agent


def get_agent_response(agent, query: str, messages_history: List):
    """
    This function takes a query, a list of tools, and some optional parameters, initializes a
    conversational LangChain agent, and returns the agent's response to the query.
    """

    # Add messages to memory
    for message_dict in messages_history:
        message_value = message_dict['message']
        sender = message_dict['type']
        if (sender == 'user'):
            agent.memory.chat_memory.add_user_message(message_value)
        if (sender == 'AI'):
            agent.memory.chat_memory.add_ai_message(message_value)

    # Get results from chain
    try:
        result = agent({"input": query})
        answer = result["output"]

        # Debug agent's answer to console
        print(answer)

        # Clear the agent's memory after generating response so they don't bring that to another person
        agent.memory.chat_memory.clear()

        return answer

    except Exception:
        return "Sorry, I had trouble answering your question. Please ask again 🥹"


def initialize_retrieval_agent():
    tools = [tool_retrieve_company_info(),
             tool_describe_skills(),
             tool_calculate_stock_options()
             ]
    return initialize_conversational_agent(tools=tools)
