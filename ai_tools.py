import os
from dotenv import load_dotenv
from langchain.agents import Tool
from langchain.chat_models import ChatOpenAI
from ai_functions import get_company_info, get_intro_response
from consts import company_handbook_faiss_path, llm_model_type


# Load .env variables
load_dotenv()


# LLM Initialization
openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(max_retries=3, temperature=0,  # type: ignore
                 model_name=llm_model_type)


def tool_describe_skills():
    """
    This function creates a LangChain agent's tool that uses a generic LLM chain to introduce itself and give user suggestions for what it can do.
    """

    return Tool(name="Who are you", func=lambda query: get_intro_response(query), description=f"""useful for questions like 'what can I ask', 'what can you do', 'what else can you do'. Action Input is the user's query.""", return_direct=True)  # type: ignore


def tool_retrieve_company_info():
    """
    This function creates a LangChain agent's tool that uses QARetrieval chain to retrieve information from the company handbook based on a FAISS vectorstore.
    """
    return Tool(name="Company Guidelines", func=lambda query: get_company_info(user_reply=query, index_path=company_handbook_faiss_path), description=f"""useful for questions about GitLab's polices, work from home, IT,  CEO, product, meeting conduct,, diversity and inclusion (DEI), career progression, management tips, sales process, finance, HR, accounting, team events, 1 on 1 guidelines, coaching tips and finance. Pass user's response directly to this tool""", return_direct=True)  # type: ignore
