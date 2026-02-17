"""
Populate Knowledge Base - Chunking Estrutural
Extrai conteúdo das páginas da InfinitePay e aplica chunking
baseado na estrutura HTML (h2, h3, FAQs), não por tamanho fixo.
"""

import re
import time
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from typing import Optional

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from hashlib import md5
from src.data.knowledge_base import knowledge_base, vector_db
from agno.knowledge.document import Document

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

# Padrões de texto de footer/legal que devem ser ignorados
FOOTER_PATTERNS = [
    r"CLOUDWALK INSTITUIÇÃO DE PAGAMENTO",
    r"correspondente bancária",
    r"Resolução CMN",
    r"Feito com amor para todos os Brasileiros",
    r"Nosso atendimento técnico e operacional",
    r"Acessar TikTok",
    r"Acessar Instagram",
    r"Acessar Youtube",
    r"Acessar Facebook",
    r"Acessar Twitter",
    r"Pesquisar conteúdo dessa página",
    r"Baixar no Google Play",
    r"Baixar na App Store",
]


def _clean_text(text: str) -> str:
    """Limpa texto extraído: remove espaços extras e chars problemáticos."""
    text = text.encode('utf-8', errors='ignore').decode('utf-8')
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _is_footer_content(text: str) -> bool:
    """Verifica se o texto é conteúdo de footer/legal que deve ser ignorado."""
    for pattern in FOOTER_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def _get_product_category(url: str) -> str:
    """Extrai a categoria do produto a partir da URL."""
    slug = url.rstrip('/').split('/')[-1]
    categories = {
        "infinitepay.io": "geral",
        "maquininha": "maquininha",
        "maquininha-celular": "infinitetap",
        "tap-to-pay": "infinitetap",
        "pdv": "pdv",
        "receba-na-hora": "recebimento",
        "gestao-de-cobranca-2": "gestao_cobranca",
        "gestao-de-cobranca": "gestao_cobranca",
        "link-de-pagamento": "link_pagamento",
        "loja-online": "loja_online",
        "boleto": "boleto",
        "conta-digital": "conta_digital",
        "conta-pj": "conta_digital",
        "pix": "pix",
        "pix-parcelado": "pix_parcelado",
        "emprestimo": "emprestimo",
        "cartao": "cartao",
        "rendimento": "rendimento",
    }
    return categories.get(slug, "geral")


def _extract_faq_chunks(soup: BeautifulSoup, url: str, category: str) -> list[dict]:
    """Extrai FAQs como chunks individuais (pergunta + resposta)."""
    chunks = []

    h3_headers = soup.find_all('h3')
    for header in h3_headers:
        question = _clean_text(header.get_text())
        if not question or len(question) < 10:
            continue

        # Percorre DOM em ordem (entra em filhos de divs) até próximo h2/h3
        answer_parts = []
        seen = set()

        el = header.next_element
        while el:
            # Para ao encontrar próximo h2 ou h3
            if isinstance(el, Tag) and el.name in ('h2', 'h3') and el != header:
                break
            if isinstance(el, NavigableString) and el.parent.name not in ('script', 'style', 'h3'):
                text = _clean_text(str(el))
                if text and len(text) > 3 and not _is_footer_content(text) and text not in seen:
                    seen.add(text)
                    answer_parts.append(text)
            el = el.next_element

        answer = ' '.join(answer_parts)

        # Só adiciona se parece uma FAQ real (tem pergunta com ?)
        if '?' in question and answer and len(answer) > 20:
            chunks.append({
                "text": f"Pergunta: {question}\nResposta: {answer}",
                "metadata": {
                    "source": "infinitepay_website",
                    "url": url,
                    "section_type": "faq",
                    "section_title": question,
                    "product_category": category,
                },
            })

    return chunks


def _extract_section_chunks(soup: BeautifulSoup, url: str, category: str) -> list[dict]:
    """Extrai seções H2 como chunks individuais."""
    chunks = []
    seen_texts = set()  # Evita duplicatas

    h2_headers = soup.find_all('h2')
    for i, header in enumerate(h2_headers):
        section_title = _clean_text(header.get_text())
        if not section_title or len(section_title) < 5:
            continue

        # Próximo H2 como limite de travessia
        next_h2 = h2_headers[i + 1] if i + 1 < len(h2_headers) else None

        # Percorre DOM em ordem (entra em filhos de divs)
        content_parts = [section_title]
        seen_in_section = {section_title}

        el = header.next_element
        while el:
            if el == next_h2:
                break
            if isinstance(el, NavigableString) and el.parent.name not in ('script', 'style'):
                text = _clean_text(str(el))
                if (text and len(text) > 3
                        and not _is_footer_content(text)
                        and text not in seen_in_section):
                    seen_in_section.add(text)
                    content_parts.append(text)
            el = el.next_element

        full_text = '\n'.join(content_parts)

        # Ignora seções muito curtas, duplicadas ou que são footer
        if len(full_text) < 30 or _is_footer_content(full_text):
            continue

        # Deduplica por hash do texto
        text_hash = hash(full_text[:200])
        if text_hash in seen_texts:
            continue
        seen_texts.add(text_hash)

        # Determina tipo de seção
        section_type = "feature"
        lower_title = section_title.lower()
        if "taxa" in lower_title:
            section_type = "taxas"
        elif "faq" in lower_title or "perguntas" in lower_title:
            section_type = "faq_intro"
        elif "mídia" in lower_title or "notícia" in lower_title:
            section_type = "midia"
        elif "depoimento" in lower_title or "confiam" in lower_title or "rede sem limites" in lower_title:
            section_type = "depoimentos"

        chunks.append({
            "text": full_text,
            "metadata": {
                "source": "infinitepay_website",
                "url": url,
                "section_type": section_type,
                "section_title": section_title,
                "product_category": category,
            },
        })

    return chunks


def _extract_hero_chunk(soup: BeautifulSoup, url: str, category: str) -> Optional[dict]:
    """Extrai o bloco hero/título principal da página."""
    h1 = soup.find('h1')
    if not h1:
        return None

    hero_text = _clean_text(h1.get_text())
    if not hero_text or len(hero_text) < 10:
        return None

    # Percorre DOM em ordem até o primeiro H2
    first_h2 = soup.find('h2')
    subtitle_parts = [hero_text]
    seen = {hero_text}
    count = 0

    el = h1.next_element
    while el and count < 8:
        if el == first_h2:
            break
        if isinstance(el, NavigableString) and el.parent.name not in ('script', 'style', 'h1'):
            text = _clean_text(str(el))
            if text and len(text) > 5 and not _is_footer_content(text) and text not in seen:
                seen.add(text)
                subtitle_parts.append(text)
                count += 1
        el = el.next_element

    return {
        "text": '\n'.join(subtitle_parts),
        "metadata": {
            "source": "infinitepay_website",
            "url": url,
            "section_type": "hero",
            "section_title": hero_text[:80],
            "product_category": category,
        },
    }


def extract_structural_chunks(url: str) -> list[dict]:
    """
    Chunking Estrutural: extrai chunks baseados na estrutura HTML.
    Cada seção H2, cada FAQ, e o hero viram chunks separados.
    Footer/legal/links sociais são descartados.
    """
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove scripts, styles, nav, footer HTML
        for tag in soup(["script", "style", "nav", "footer", "noscript", "iframe"]):
            tag.decompose()

        category = _get_product_category(url)
        chunks = []

        # 1. Hero chunk
        hero = _extract_hero_chunk(soup, url, category)
        if hero:
            chunks.append(hero)

        # 2. Section chunks (H2)
        section_chunks = _extract_section_chunks(soup, url, category)
        chunks.extend(section_chunks)

        # 3. FAQ chunks (H3 com ?)
        faq_chunks = _extract_faq_chunks(soup, url, category)
        chunks.extend(faq_chunks)

        print(f"  → {url}: {len(chunks)} chunks extraídos "
              f"(hero: {1 if hero else 0}, seções: {len(section_chunks)}, faqs: {len(faq_chunks)})")

        return chunks

    except Exception as e:
        print(f"✗ Erro ao processar {url}: {str(e)}")
        return []


def populate_knowledge_base():
    """Popula a base de conhecimento com chunking estrutural."""
    print("=" * 60)
    print("POPULANDO KNOWLEDGE BASE - Chunking Estrutural")
    print("=" * 60)

    total_chunks = 0

    # Limpa collection anterior e recria do zero
    try:
        vector_db.delete()
    except Exception:
        pass
    vector_db.create()

    for url in INFINITEPAY_URLS:
        chunks = extract_structural_chunks(url)
        if not chunks:
            continue

        # Converte chunks para Documents do Agno
        docs = []
        for chunk in chunks:
            doc = Document(
                content=chunk["text"],
                name=f"{chunk['metadata'].get('product_category', 'geral')} - {chunk['metadata'].get('section_title', '')[:50]}",
                meta_data=chunk["metadata"],
            )
            docs.append(doc)

        # Insere no vector_db diretamente (síncrono)
        try:
            content_hash = md5(url.encode()).hexdigest()
            vector_db.insert(content_hash=content_hash, documents=docs)
            print(f"  ✓ {len(docs)} chunks salvos no ChromaDB")
            total_chunks += len(docs)
        except Exception as e:
            print(f"  ✗ Erro ao salvar chunks de {url}: {str(e)[:100]}")

        # Rate limit: espera entre URLs para evitar 429
        time.sleep(2)

    print("=" * 60)
    print(f"CONCLUÍDO! Total de chunks salvos: {total_chunks}")
    print("=" * 60)


if __name__ == "__main__":
    populate_knowledge_base()