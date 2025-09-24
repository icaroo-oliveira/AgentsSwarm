from agno.knowledge.knowledge import Knowledge
from agno.vectordb.chroma import ChromaDb
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.knowledge.reader.website_reader import WebsiteReader
# from agno.knowledge.chunking import FixedSizeChunking  # Não disponível

from src.config.settings import settings

# Configurar o Embedder (SentenceTransformer para eficiência)
embedder = SentenceTransformerEmbedder(id=settings.embedder_model)

# Configurar o Vector DB (ChromaDB local)
vector_db = ChromaDb(
    collection="infinitepay_kb",  # Coleção específica para InfinitePay
    path=settings.vector_store_path,  # Path do settings: ./src/data/vector_store
    persistent_client=True,  # Persistir dados
    embedder=embedder,  # Passar embedder para ChromaDb
)

# Configurar Website Reader
website_reader = WebsiteReader()

# Knowledge Base instance usando Knowledge (como no exemplo)
knowledge_base = Knowledge(
    name="InfinitePay Knowledge Base",
    description="Base de conhecimento da InfinitePay com RAG usando ChromaDB",
    vector_db=vector_db,
    readers={"website": website_reader},  # Adicionar website reader
)
