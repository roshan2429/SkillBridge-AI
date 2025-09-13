import logging
import uuid
from langchain_core.documents import Document
from langchain_openai import OpenAI
from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain, create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Responsible AI wrapper
def safe_response(text: str) -> str:
    """
    Basic responsible AI guardrails:
    - Filters unsafe words
    - Adds disclaimers when uncertain
    """
    unsafe_keywords = ["hack", "illegal", "piracy"]
    if any(word in text.lower() for word in unsafe_keywords):
        return "I’m unable to provide guidance on that topic. Please ask something related to career or learning."
    if len(text.strip()) == 0:
        return "I don’t have specific information on that, but consider exploring online courses or consulting a career coach."
    return text

# Telemetry function
def log_telemetry(query: str, response: str, metadata: dict | None = None):
    """
    Logs queries, responses, and optional metadata.
    """
    session_id = metadata.get("session_id") if metadata else str(uuid.uuid4())
    logger.info(f"[TELEMETRY] session={session_id} query='{query}' response='{response}'")

# Example agentic / multi-step workflow
def agentic_query_processing(query: str, retriever, llm) -> str:
    """
    Simplified agentic approach:
    1. Retrieve context
    2. Generate plan (multi-step reasoning)
    3. Generate final answer
    """
    try:
        # Step 1: Retrieve relevant documents
        context_docs = retriever.get_relevant_documents(query)
        context_text = "\n".join([doc.page_content for doc in context_docs])

        # Step 2: Build prompt
        system_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are SkillBridge AI, a responsible career mentor."),
            ("human", "{input}")
        ])
        prompt_text = system_prompt.format(input=f"{query}\nContext:\n{context_text}")

        # Step 3: LLM generates response
        response = llm(prompt_text)

        # Step 4: Apply responsible AI checks
        safe_text = safe_response(response)

        # Step 5: Log telemetry
        log_telemetry(query, safe_text)

        return safe_text
    except Exception as e:
        logger.error(f"Agentic processing failed: {str(e)}")
        return "I don’t have specific information on that, but consider exploring online courses or consulting a career coach."
