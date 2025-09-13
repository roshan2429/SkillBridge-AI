from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import OpenAI
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from ai_agent import agentic_query_processing
import os
import uuid
import logging
from fetch_data import fetch_career_data
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

app = FastAPI(
    title="SkillBridge AI",
    description="AI-powered career mentorship chatbot using job market and learning resource data",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Initialize RAG pipeline
try:
    career_data = fetch_career_data()
    if not career_data:
        logger.warning("No career data retrieved; relying on LLM fallback")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True
    )
    docs = text_splitter.split_documents(career_data) if career_data else []
    
    vectorstore = Chroma.from_documents(
        documents=docs or [Document(page_content="No external data available.", metadata={"source": "empty"})],
        embedding=OpenAIEmbeddings(api_key=OPENAI_API_KEY),
        collection_name=f"career_collection_{uuid.uuid4()}",
        persist_directory="./chroma_db"
    )
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 3, "score_threshold": 0.5}
    )
    
    llm = OpenAI(
        api_key=OPENAI_API_KEY,
        temperature=0.4,
        max_tokens=500
    )
except Exception as e:
    logger.error(f"Failed to initialize RAG pipeline: {str(e)}")
    raise RuntimeError(f"Initialization failed: {str(e)}")

system_prompt = (
    "You are SkillBridge AI, a career mentorship assistant. You provide concise, actionable advice on skill development,job preparation, and career planning based on job market data and learning resources. "
    "For greetings like 'hi' or 'hello', respond with: 'Hello! How can I assist you with your career goals today?' "
    "For follow-up queries about alternative resources (e.g., 'other recommendations'), exclude previously mentioned resources (Coursera, Udemy, freeCodeCamp) and suggest alternatives like fast.ai, DeepLearning.AI, Kaggle, or GitHub open-source projects. "
    "If no relevant data is available or the query is unclear, respond: 'I don’t have specific information on that, but consider exploring online courses or consulting a career coach.'"
    "\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

class QueryRequest(BaseModel):
    query: str
    chat_history: list = [] 

class QueryResponse(BaseModel):
    answer: str
    status: str
    error: str | None = None

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        query_lower = request.query.strip().lower()
        if query_lower in ["hi", "hello", "hey"]:
            return QueryResponse(
                answer="Hello! How can I assist you with your career goals today?",
                status="success",
                error=None
            )
        
        if "other recommendations" in query_lower or "already familiar" in query_lower:
            previous_resources = ["coursera", "udemy", "freecodecamp"]
            alternative_resources = (
                "To develop skills for a Software Engineer, Machine Learning role, consider these alternatives: "
                "1. fast.ai for practical deep learning courses. "
                "2. DeepLearning.AI for specialized AI certifications. "
                "3. Kaggle competitions to build hands-on ML projects. "
                "4. Contributing to open-source ML projects on GitHub. "
                "These can help you gain practical experience and stand out."
            )
            return QueryResponse(
                answer=alternative_resources,
                status="success",
                error=None
            )
        
        response = rag_chain.invoke({"input": request.query})
        answer = response["answer"]
        if not answer.strip() or "no relevant information" in answer.lower():
            answer = "I don’t have specific information on that, but consider exploring online courses or consulting a career coach."
        return QueryResponse(
            answer=answer,
            status="success",
            error=None
        )
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        return QueryResponse(
            answer="I don’t have specific information on that, but consider exploring online courses or consulting a career coach.",
            status="error",
            error=str(e)
        )

@app.post("/agent-query", response_model=QueryResponse)
async def process_agent_query(request: QueryRequest):
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        answer = agentic_query_processing(request.query, retriever, llm)

        return QueryResponse(
            answer=answer,
            status="success",
            error=None
        )
    except Exception as e:
        logger.error(f"Agentic query failed: {str(e)}")
        return QueryResponse(
            answer="I don’t have specific information on that, but consider exploring online courses or consulting a career coach.",
            status="error",
            error=str(e)
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")