#!/usr/bin/env python3
"""
Teste específico para o Customer Support Agent
Testa as funcionalidades de memória e tools do agente de suporte ao cliente
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agno_team import customer_support_agent
from src.config.setup_db import setup_mock_data

def test_customer_support_agent():
    """Testa o Customer Support Agent com diferentes cenários"""

    print("🚀 Iniciando teste do Customer Support Agent")
    print("=" * 50)

    setup_mock_data()
    print("✅ Banco de dados configurado")

    # Cenários de teste
    test_cases = [
        {
            "message": "Não consigo fazer login na minha conta",
            "user_id": "client789",
            "expected": "problema de login"
        },
        {
            "message": "Por que minha transferência não foi processada?",
            "user_id": "client789",
            "expected": "problema de transferência"
        },
        {
            "message": "Quero ver minhas últimas transações",
            "user_id": "client123",
            "expected": "consultar transações"
        },
        {
            "message": "Minha conta está bloqueada, o que faço?",
            "user_id": "client456",
            "expected": "conta bloqueada"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Teste {i}: {test_case['message']}")
        print("-" * 40)

        try:
            response = customer_support_agent.run(test_case['message'], user_id=test_case['user_id'])

            print(f"👤 Usuário: {test_case['user_id']}")
            print(f"💬 Mensagem: {test_case['message']}")
            print(f"🤖 Resposta: {response.content}")
            print("✅ Teste executado com sucesso")
            print(f"💬 Mensagem: {test_case['message']}")
            print(f"🤖 Resposta: {response.content}")
            print("✅ Teste executado com sucesso")
            print(f"💬 Mensagem: {test_case['message']}")
            print(f"🤖 Resposta: {response.content}")
            print("✅ Teste executado com sucesso")

        except Exception as e:
            print(f"❌ Erro no teste {i}: {str(e)}")

    print("\n" + "=" * 50)
    print("🏁 Testes do Customer Support Agent concluídos")

if __name__ == "__main__":
    test_customer_support_agent()