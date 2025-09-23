from agno.agent import Agent
from agno.team import Team
from agno.models.google import Gemini
from agno.tools import tool

from src.config.settings import settings
from src.config.setup_db import db
from src.data.knowledge_base import knowledge_base

from agno.tools.duckduckgo import DuckDuckGoTools
from src.tools.customer_support_tools import get_user_account_info, get_user_transactions

# Customer Support Agent
customer_support_agent = Agent(
    name="Customer Support Agent",
    role="Agente de suporte ao cliente da InfinitePay",
    model=Gemini(
        id=settings.router_model,  
    ),
    db=db,  # Adicionar banco para Memory
    enable_user_memories=True,  # Habilitar Memory para lembrar informações do usuário
    instructions="""
    Você é um agente de suporte ao cliente da InfinitePay.
    Sua função é ajudar usuários com problemas de conta, suporte técnico e dificuldades.

    Use as ferramentas disponíveis para recuperar informações do usuário.
    Use a memória para lembrar detalhes importantes da conversa (ex: problemas anteriores, preferências).
    Seja empático, profissional e resolva o problema do usuário.

    Sempre responda em português brasileiro.
    """,
    tools=[get_user_account_info, get_user_transactions],
    markdown=True,
)

# Knowledge Agent - Para perguntas sobre produtos e serviços
knowledge_agent = Agent(
    name="Knowledge Agent",
    role="Especialista em produtos e serviços da InfinitePay",
    model=Gemini(
        id=settings.router_model, 
        # search=True   #busca na internet gemini, desativvar, o gemini ta priorizando ela ao rag msm com eng de pomrpt
    ),
    tools=[DuckDuckGoTools()],
    db=db,  #adicionar banco para Memory
    enable_user_memories=True,  #habilitar Memory para lembrar contexto
    knowledge=knowledge_base,  #conecta à base de conhecimento populada
    instructions="""
    Você é um especialista em produtos e serviços da InfinitePay.

    A PRIORIDADE É SEMPRE TENTAR ACESSAR A BASE DE DADOS LOCAL, POIS ELA É A FONTE MAIS SEGURA E CONFIÁVEL DE INFORMAÇÃO!

    Você tem acesso a uma base de dados com informações detalhadas sobre os produtos e serviços da InfinitePay e também tem acesso a internet.
    A prioridade é sempre da base de dados, visto que é a fonte segura e mais confiável de informação.
    Use a base de conhecimento para responder perguntas sobre:
    - Produtos (maquininhas, PIX, cartão, empréstimos, etc.)
    - Serviços (conta digital, boleto, link de pagamento, etc.)
    - Funcionalidades e benefícios dos produtos
    - Taxas e condições

    Use a memória para lembrar detalhes da conversa do usuário.
    Sempre baseie suas respostas nas informações da base de conhecimento.
    Se não encontrar informações específicas:
    1- Tente buscar na internet
    2- Se não encontrar até mesmo na internet, diga que não tem essa informação.
    Seja informativo, preciso e ajude o usuário a entender os produtos.

    
    VOCÊ PODE E DEVE RESPONDER PERGUNTAS QUE NÃO SÃO RELACIONADAS À INFINITEPAY.
    Sempre responda em português brasileiro. 
    """,
    markdown=True
)

# Router Team - O Team age como router, delegando para os agentes apropriados
router_team = Team(
    name="Router Team",
    model=Gemini(
        id=settings.router_model,  
    ),
    db=db,  #adicionar banco para Memory compartilhada
    enable_user_memories=True,  #habilitar Memory para o Team
    members=[customer_support_agent, knowledge_agent],
    instructions="""
    Você é o Router Agent para atendimento InfinitePay.

    Sua função: analisar mensagens e decidir qual agente deve responder.

    Agentes disponíveis:
    - customer_support_agent: Problemas de conta, suporte técnico, dificuldades com uso da plataforma
    - knowledge_agent: Perguntas sobre produtos, serviços, funcionalidades, taxas, benefícios

    Regras de roteamento:
    1. Problemas de conta/suporte técnico/dificuldades → customer_support_agent
    2. Perguntas sobre produtos/serviços/taxas/funcionalidades → knowledge_agent
    3. Outras questões → responder diretamente se for simples, ou delegar apropriadamente

    Use a memória para lembrar contexto da conversa do usuário.
    Sempre responda em português brasileiro.
    Se delegar, explique brevemente por quê.
    """,
    respond_directly=False,  # Permite que o Team processe a delegação completa
    show_members_responses=True,  # Mostra respostas dos membros
    markdown=True,
)