import asyncio
import requests
from bs4 import BeautifulSoup

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


from src.data.knowledge_base import knowledge_base

# Lista de URLs do InfinitePay para extrair conteúdo
INFINITEPAY_URLS = [
    "https://www.infinitepay.io",
    "https://www.infinitepay.io/maquininha",
    "https://www.infinitepay.io/maquininha-celular",
    "https://www.infinitepay.io/tap-to-pay",
    "https://www.infinitepay.io/pdv",
    "https://www.infinitepay.io/receba-na-hora",
    "https://www.infinitepay.io/gestao-de-cobranca-2",
    "https://www.infinitepay.io/gestao-de-cobranca",
    "https://www.infinitepay.io/link-de-pagamento",
    "https://www.infinitepay.io/loja-online",
    "https://www.infinitepay.io/boleto",
    "https://www.infinitepay.io/conta-digital",
    "https://www.infinitepay.io/conta-pj",
    "https://www.infinitepay.io/pix",
    "https://www.infinitepay.io/pix-parcelado",
    "https://www.infinitepay.io/emprestimo",
    "https://www.infinitepay.io/cartao",
    "https://www.infinitepay.io/rendimento",
]

def extract_content_from_url(url: str) -> str:
    """Extrai conteúdo textual de uma URL usando requests e BeautifulSoup."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # Força codificação UTF-8
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove scripts e estilos
        for script in soup(["script", "style"]):
            script.decompose()

        # Extrai texto do corpo
        text = soup.get_text(separator=' ', strip=True)

        # Limpa caracteres problemáticos e codifica em UTF-8
        text = text.encode('utf-8', errors='ignore').decode('utf-8')

        # Remove caracteres não-ASCII para evitar problemas de codificação
        import re
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)

        # Limita tamanho se necessário
        return text[:10000]  # Limite para evitar textos muito longos
    except Exception as e:
        print(f"Erro ao extrair {url}: {str(e)}")
        return ""

async def populate_knowledge_base():
    """Popula a base de conhecimento com conteúdo das URLs do InfinitePay."""
    print("Iniciando população da base de conhecimento...")
    
    for url in INFINITEPAY_URLS:
        content = extract_content_from_url(url)
        if content:
            try:
                print(f"Adicionando conteúdo de: {url}")
                await knowledge_base.add_content_async(
                    text_content=content,
                    name=f"InfinitePay - {url.split('/')[-1] or 'home'}",
                    metadata={"source": "infinitepay_website", "url": url}
                )
                print(f"✓ Conteúdo adicionado: {url}")
            except Exception as e:
                print(f"✗ Erro ao adicionar {url}: {str(e)}")
        else:
            print(f"✗ Sem conteúdo para {url}")

    print("População da base de conhecimento concluída!")

if __name__ == "__main__":
    asyncio.run(populate_knowledge_base())