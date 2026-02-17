"""
Consulta direta ao ChromaDB para avaliar qualidade dos chunks.
Sem uso de LLM - apenas busca vetorial.
"""
import chromadb
from agno.knowledge.embedder.google import GeminiEmbedder
from dotenv import load_dotenv
import os
import time

load_dotenv()

client = chromadb.HttpClient(host='localhost', port=8001)
col = client.get_collection('infinitepay_kb')

embedder = GeminiEmbedder(id='gemini-embedding-001', dimensions=768)

def query(text, n=3):
    """Faz query vetorial e retorna top-n resultados."""
    # Gera embedding da query
    resp = embedder.get_embedding(text)
    if not resp:
        print(f"ERRO: embedding falhou para '{text}'")
        return
    
    # resp pode ser lista direta ou objeto com .embedding
    emb = resp if isinstance(resp, list) else resp.embedding
    
    results = col.query(
        query_embeddings=[emb],
        n_results=n,
        include=['documents', 'metadatas', 'distances']
    )
    
    print(f"\n{'='*70}")
    print(f"QUERY: \"{text}\"")
    print(f"{'='*70}")
    
    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        meta = results['metadatas'][0][i]
        dist = results['distances'][0][i]
        
        print(f"\n  [{i+1}] Score (distância): {dist:.4f}")
        print(f"      URL: {meta.get('url', '?')}")
        print(f"      Tipo: {meta.get('section_type', '?')} | Categoria: {meta.get('product_category', '?')}")
        print(f"      Título: {meta.get('section_title', '?')[:80]}")
        print(f"      Texto: {doc[:200]}...")
    
    return results


# ========== CONSULTAS DE TESTE ==========

print("\n" + "#"*70)
print("# CONSULTAS DIRETAS NO CHROMADB - SEM LLM")
print("#"*70)

# 1. Consulta sobre taxas da maquininha
query("quais são as taxas da maquininha?")
time.sleep(1)

# 2. Consulta sobre Pix
query("como funciona o pix na InfinitePay?")
time.sleep(1)

# 3. Consulta sobre conta digital
query("quero abrir uma conta digital")
time.sleep(1)

# 4. Consulta sobre empréstimo
query("como pegar empréstimo para minha empresa?")
time.sleep(1)

# 5. Consulta sobre link de pagamento
query("como criar um link de pagamento?")
time.sleep(1)

# 6. Consulta sobre cartão
query("qual o limite do cartão InfinitePay?")
time.sleep(1)

# 7. Consulta sobre rendimento
query("meu dinheiro rende na conta?")
time.sleep(1)

# 8. Consulta sobre boleto
query("posso gerar boleto pela InfinitePay?")

print("\n\n" + "#"*70)
print("# FIM DAS CONSULTAS")
print("#"*70)
