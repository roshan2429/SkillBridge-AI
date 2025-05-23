import requests
from langchain_core.documents import Document
import logging
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY")

if not ADZUNA_APP_ID or not ADZUNA_API_KEY:
    logger.error("Adzuna API credentials not set in .env file")
    raise ValueError("Adzuna API credentials not set")

def fetch_career_data(max_documents: int = 10) -> list[Document]:
    try:
        response = requests.get(
            "https://api.adzuna.com/v1/api/jobs/us/search/1",
            params={
                "app_id": ADZUNA_APP_ID,
                "app_key": ADZUNA_API_KEY,
                "what": "software engineer machine learning",
                "results_per_page": max_documents
            },
            timeout=5
        )
        response.raise_for_status()
        jobs = response.json().get("results", [])
        
        documents = []
        for idx, job in enumerate(jobs[:max_documents]):
            title = job.get("title", "Unknown Job")
            description = job.get("description", "No description available")
            documents.append(Document(
                page_content=f"Q: What skills are needed for {title}? A: {description}",
                metadata={"source": f"job_{idx}"}
            ))
        
        alternative_resources = [
            Document(
                page_content=(
                    "Q: What are alternative resources for learning machine learning skills?"
                    "A: Consider fast.ai for practical deep learning, DeepLearning.AI for AI certifications,"
                    "Kaggle for hands-on ML projects, or contributing to open-source projects on GitHub."
                ),
                metadata={"source": "alternative_resources"}
            )
        ]
        documents.extend(alternative_resources)
        
        logger.info(f"Fetched {len(documents)} job documents")
        return documents
    except requests.RequestException as e:
        logger.error(f"Error fetching career data: {str(e)}")
        return []