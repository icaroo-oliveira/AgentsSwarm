import os
import chromadb
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.chroma import ChromaDb
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.knowledge.reader.website_reader import WebsiteReader

from src.config.settings import settings

# Configurar o Embedder (Google gemini-embedding-001 via API key gratuita)
embedder = GeminiEmbedder(
    id=settings.embedder_model,  # gemini-embedding-001
    dimensions=768,
    api_key=settings.google_api_key,
)

# Configurar o Vector DB (ChromaDB via HTTP - container Docker)
chroma_host = os.getenv("CHROMA_HOST", settings.chroma_host)
chroma_port = int(os.getenv("CHROMA_PORT", settings.chroma_port))

vector_db = ChromaDb(
    collection="infinitepay_kb",
    embedder=embedder,
)
# Injeta HttpClient para conectar ao ChromaDB remoto (Docker)
vector_db._client = chromadb.HttpClient(host=chroma_host, port=chroma_port)

# Configurar Website Reader
website_reader = WebsiteReader()

# Knowledge Base instance
knowledge_base = Knowledge(
    name="InfinitePay Knowledge Base",
    description="Base de conhecimento da InfinitePay com RAG usando ChromaDB",
    vector_db=vector_db,
    readers={"website": website_reader},
)
