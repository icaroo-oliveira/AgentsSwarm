import asyncio
import sys
import os

# Add project root to Python path
sys.path.append('.')

from src.agents.agno_team import router_team, knowledge_agent
from agno.utils.pprint import pprint_run_response

response = knowledge_agent.run("Quais são as taxas do PIX na InfinitePay?")
pprint_run_response(response, markdown=True)

# async def test_knowledge_agent():
#     """Teste direto do knowledge agent."""
#     try:
#         print("Testando Knowledge Agent diretamente...")
#         response = await knowledge_agent.arun("Quais são as taxas do PIX na InfinitePay?")
#         print(f"Resposta do Knowledge Agent: {response}")
#         print("\n" + "="*50 + "\n")
#     except Exception as e:
#         print(f"Erro no Knowledge Agent: {e}")
#         import traceback
#         traceback.print_exc()

# # Comentado para focar no teste do Knowledge Agent
# """
# async def test_router_team():
#     "Teste do router team completo."
#     try:
#         print("Testando Router Team...")
#         response = await router_team.arun("Quais são as taxas do PIX na InfinitePay?")
#         print(f"Resposta do Router Team: {response}")
#     except Exception as e:
#         print(f"Erro no Router Team: {e}")
#         import traceback
#         traceback.print_exc()
# """

# async def main():
#     """Executa todos os testes."""
#     await test_knowledge_agent()
#     # Comentado para focar no teste do Knowledge Agent
#     # await test_router_team()

# if __name__ == "__main__":
#     asyncio.run(main())