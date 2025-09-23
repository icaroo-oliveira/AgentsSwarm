from agno.team import Team
from agno.models.google import Gemini
from src.config.settings import settings
from src.config.setup_db import db
from .customer_support_agent import customer_support_agent
from .knowledge_agent import knowledge_agent

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