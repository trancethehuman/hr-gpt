import os
import random
from dotenv import load_dotenv
from langchain.vectorstores.faiss import FAISS
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.callbacks import get_openai_callback
from langchain.callbacks.base import CallbackManager
from langchain.prompts import PromptTemplate
from langchain import LLMChain
from utils import format_sources, remove_folder
from consts import learn_more_phrases, llm_model_type
from langchain.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from consts import company_handbook_faiss_path


# Load .env variables
load_dotenv()

# LLM Initialization
openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(max_retries=3, temperature=0,  # type: ignore
                 model_name=llm_model_type)
embeddings = OpenAIEmbeddings(max_retries=2)  # type: ignore


def get_vectorstore_retriever(index_path: str):
    """
    This function returns a retriever object for a vector store index, loaded from a path (string) using
    Meta's FAISS library.
    """
    return FAISS.load_local(index_path, embeddings=embeddings).as_retriever()


def get_intro_response(query):
    """
    This function uses a generic LangChain LLM chain to generate a response to a user's question about what the user can ask and how the bot can help.
    """

    # Initialize LLM chain
    prompt_template = "As a HR AI assistant, you answer questions about the company's HR policies, how different departments operate, PTO, mat leave, work from home policies and many more. Based on this context, answer the user's question. User question: {input} \nYour answer:"
    llm_chain = LLMChain(
        llm=llm, prompt=PromptTemplate.from_template(prompt_template)
    )

    response = llm_chain(query)["text"]

    return response


def get_company_info(user_reply: str, index_path: str):
    """
    This function retrieves information about a company (using LangChain's RetrievalQA chain) based on a user's query and returns a formatted
    response with additional sources for further learning.
    """
    qa = RetrievalQA.from_llm(
        llm=llm, retriever=get_vectorstore_retriever(index_path), return_source_documents=True)

    with get_openai_callback() as cb:
        result = qa({"query": user_reply})

    # Preliminary formatted results from chain
    chat_answer = result["result"]
    formatted_sources = format_sources(result["source_documents"], 2)

    # Formatted response
    final_response = f"""{chat_answer}\n\n📖 {random.choice(learn_more_phrases)}:\n\n{formatted_sources}"""

    return final_response


def save_faiss_locally(vectorstore, path: str):
    vectorstore.save_local(path)  # type: ignore

    print(f"Vectorstore saved locally")


def load_documents_as_urls(urls: str):
    urls_list = urls.replace(" ", "").split(",")
    loader = UnstructuredURLLoader(urls=urls_list)
    loaded_documents = loader.load()

    print(f"Loaded {len(loaded_documents)} URL documents.")
    return loaded_documents


def initialize_vectorstore(input):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700, chunk_overlap=300)

    texts = ""
    if (input is not None):
        texts = text_splitter.split_documents(input)

    vectorstore = FAISS.from_documents(texts, embeddings)  # type: ignore
    print("Vectorstore created.")

    return vectorstore


def merge_with_old_vectorstore(new_vectorstore):
    old_vectorstore = FAISS.load_local(company_handbook_faiss_path, embeddings)

    old_vectorstore.merge_from(new_vectorstore)
    print("Vectorstores merged.")

    remove_folder(company_handbook_faiss_path)

    save_faiss_locally(old_vectorstore, company_handbook_faiss_path)

    return


def load_urls_and_overwrite_index(urls: str):
    # load documents from URLs
    loaded_documents = load_documents_as_urls(urls)

    # initialize vectorstore
    new_vectorstore = initialize_vectorstore(loaded_documents)

    # Merge the two indexes
    merge_with_old_vectorstore(new_vectorstore)

    # send a message back saying success
    return "Successfully updated the index with the new documents."
