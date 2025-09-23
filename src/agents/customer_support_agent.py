from agno.agent import Agent
from agno.models.google import Gemini
from src.tools.customer_support_tools import get_user_account_info, get_user_transactions
from src.config.settings import settings
from src.config.setup_db import db

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

        IMPORTANTE: Sempre use as ferramentas disponíveis (get_user_account_info e get_user_transactions) para recuperar informações do usuário ANTES de responder. Não diga que vai delegar ou solicitar informações; execute as tools diretamente e forneça os dados.

        O user_id do usuário é fornecido no início da mensagem (ex: "User ID: client789"). Use esse user_id nas ferramentas para recuperar dados específicos.

        Para perguntas sobre transações ou gastos/ganhos: Use get_user_transactions para obter o histórico e calcule/resuma os valores.

        Use a memória para lembrar detalhes importantes da conversa.
        Seja empático, profissional e resolva o problema do usuário.

        Sempre responda em português brasileiro.
        """,
    tools=[get_user_account_info, get_user_transactions],
    markdown=True,
)