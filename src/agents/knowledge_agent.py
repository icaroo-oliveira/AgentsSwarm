from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from src.config.settings import settings
from src.config.setup_db import db
from src.data.knowledge_base import knowledge_base

# Knowledge Agent - Para perguntas sobre produtos e serviços
knowledge_agent = Agent(
    name="Knowledge Agent",
    role="Especialista em produtos e serviços da InfinitePay",
    model=Gemini(
        id=settings.router_model,
    ),
    tools=[DuckDuckGoTools()],
    db=db,  # adicionar banco para Memory
    enable_user_memories=True,  # habilitar Memory para lembrar contexto
    knowledge=knowledge_base,  # conecta à base de conhecimento populada
    instructions="""
    Você é um agente inteligente especialista em produtos e serviços da InfinitePay, mas também capaz de responder perguntas gerais.

    **PARA PERGUNTAS RELACIONADAS À INFINITEPAY:**
    - Sempre busque primeiro na base de conhecimento local (RAG) para obter informações precisas e confiáveis.
    - Só use a ferramenta de busca na web (DuckDuckGoTools) se não encontrar informações relevantes na base local.
    - Exemplos: taxas, produtos, serviços, funcionalidades da InfinitePay.

    **PARA PERGUNTAS NÃO RELACIONADAS À INFINITEPAY:**
    - Não busque na base local, pois ela é específica para InfinitePay.
    - Use diretamente a ferramenta de busca na web para informações atualizadas ou gerais.
    - Exemplos: notícias, esportes, eventos atuais.

    Use a memória para lembrar detalhes da conversa do usuário.
    Seja informativo, preciso e ajude o usuário a entender os produtos.
    Sempre responda em português brasileiro.
    """,
    markdown=True,
    debug_mode=True
)