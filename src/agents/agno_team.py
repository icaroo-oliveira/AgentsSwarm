from agno.agent import Agent
from agno.team import Team
from agno.models.huggingface import HuggingFace
from agno.tools import tool

from src.config.settings import settings
from src.config.setup_db import db
from src.data.knowledge_base import knowledge_base

# Customer Support Tools
@tool
def get_user_account_info(user_id: str) -> str:
    """Recupera informações básicas da conta do usuário."""
    import sqlite3
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, account_status FROM user_profiles WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        name, email, status = result
        return f"Informações da conta para {name} ({user_id}): Email: {email}, Status: {status}."
    else:
        return f"Usuário {user_id} não encontrado."

@tool
def get_user_transactions(user_id: str, limit: int = 5) -> str:
    """Recupera últimas transações do usuário."""
    import sqlite3
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT date, amount, status, description FROM user_transactions WHERE user_id = ? ORDER BY date DESC LIMIT ?", (user_id, limit))
    results = cursor.fetchall()
    conn.close()
    if results:
        transactions = "\n".join([f"- {date}: R$ {amount:.2f} ({status}) - {description}" for date, amount, status, description in results])
        return f"Últimas transações para {user_id}:\n{transactions}"
    else:
        return f"Nenhuma transação encontrada para {user_id}."

# Customer Support Agent
customer_support_agent = Agent(
    name="Customer Support Agent",
    role="Agente de suporte ao cliente da InfinitePay",
    model=HuggingFace(
        id=settings.router_model,  # Usar o modelo Llama 3 do settings
        max_tokens=4096,
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
    model=HuggingFace(
        id=settings.router_model,  # Mesmo modelo Llama 3
        max_tokens=3000,
    ),
    db=db,  # Adicionar banco para Memory
    enable_user_memories=True,  # Habilitar Memory para lembrar contexto
    knowledge=knowledge_base,  # Conecta à base de conhecimento populada
    instructions="""
    Você é um especialista em produtos e serviços da InfinitePay.
    Use a base de conhecimento para responder perguntas sobre:
    - Produtos (maquininhas, PIX, cartão, empréstimos, etc.)
    - Serviços (conta digital, boleto, link de pagamento, etc.)
    - Funcionalidades e benefícios dos produtos
    - Taxas e condições

    Use a memória para lembrar detalhes da conversa do usuário.
    Sempre baseie suas respostas nas informações da base de conhecimento.
    Se não encontrar informações específicas, diga que não tem essa informação.
    Seja informativo, preciso e ajude o usuário a entender os produtos.

    Sempre responda em português brasileiro.
    """,
    markdown=True,
)

# Router Team - O Team age como router, delegando para os agentes apropriados
router_team = Team(
    name="Router Team",
    model=HuggingFace(
        id=settings.router_model,  # Mesmo modelo Llama 3
        max_tokens=3000,),
    db=db,  # Adicionar banco para Memory compartilhada
    enable_user_memories=True,  # Habilitar Memory para o Team
    members=[customer_support_agent, knowledge_agent],
    instructions="""
    Você é o Router Agent para atendimento InfinitePay.

    Sua função: analisar mensagens e decidir qual agente deve responder.

    Agentes disponíveis:
    - customer_support: Problemas de conta, suporte técnico, dificuldades com uso da plataforma
    - knowledge: Perguntas sobre produtos, serviços, funcionalidades, taxas, benefícios

    Regras de roteamento:
    1. Problemas de conta/suporte técnico/dificuldades → customer_support
    2. Perguntas sobre produtos/serviços/taxas/funcionalidades → knowledge
    3. Outras questões → responder diretamente se for simples, ou delegar apropriadamente

    Use a memória para lembrar contexto da conversa do usuário.
    Sempre responda em português brasileiro.
    Se delegar, explique brevemente por quê.
    """,
    respond_directly=False,  # Permite que o Team processe a delegação completa
    show_members_responses=True,  # Mostra respostas dos membros
    markdown=True,
)