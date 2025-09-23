# Agent Swarm - Sistema Multi-Agente com Agno

## Descrição

Este projeto implementa um sistema de agentes inteligentes (Agent Swarm) usando o framework Agno. O sistema processa mensagens de usuários através de três tipos de agentes especializados: Router Agent, Knowledge Agent e Customer Support Agent. A aplicação é containerizada com Docker e expõe uma API REST para interação.

## Arquitetura do Agent Swarm

### Agentes Implementados

1. **Router Agent**
   - **Função**: Ponto de entrada principal para todas as mensagens.
   - **Responsabilidades**: Analisa o conteúdo da mensagem e decide qual agente especializado deve processá-la.
   - **Decisões**: Baseadas em análise de intenção e contexto da mensagem.

2. **Knowledge Agent** 
   - **Função**: Responde perguntas sobre produtos e serviços da InfinitePay.
   - **Tecnologia**: Usa Retrieval Augmented Generation (RAG) para respostas baseadas em dados do site oficial.
   - **Ferramentas**: Busca web para perguntas gerais, RAG para conhecimento específico.

3. **Customer Support Agent**
   - **Função**: Fornece suporte ao cliente, recuperando dados específicos do usuário.
   - **Ferramentas**: Duas ferramentas implementadas para consultar perfil e transações do usuário.
   - **Banco de Dados**: SQLite com dados mockados para simulação.

### Fluxo de Processamento de Mensagem

1. **Recebimento**: API recebe POST em `/chat` com JSON contendo `message` e `user_id`.
2. **Roteamento**: Router Agent analisa a mensagem e seleciona o agente apropriado.
3. **Processamento**: Agente selecionado executa sua lógica (RAG, consultas DB, etc.).
4. **Resposta**: Sistema retorna JSON com resposta, agente usado, confiança e metadados.
5. **Memória**: Dados de conversa são armazenados para contexto futuro.

### Design Choices

- **Framework Agno**: Escolhido por sua simplicidade em criar agentes e integrações com LLMs.
- **FastAPI**: Para API REST rápida e documentada automaticamente.
- **ChromaDB**: Vector store leve e eficiente para RAG.
- **Docker**: Containerização para portabilidade e isolamento.
- **SQLite**: Banco simples para dados mockados de usuários.

## Como Construir, Configurar e Executar

### Pré-requisitos

- Docker e Docker Compose instalados
- Chave da API Google Gemini (gratuita, para modelos de LLM) (aistudio.google.com/app/apikey)

### Configuração

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/icaro-oliveira/MultiAgent.git
   cd MultiAgent
   ```

2. **Configure variáveis de ambiente**:
   Crie um arquivo `.env` na raiz do projeto:
   ```
   GOOGLE_API_KEY=sua_chave_aqui
   LOG_LEVEL=INFO
   ```
   **Exponha a variável de ambiente**
   setx GOOGLE_API_KEY sua_chave_aqui

3. **Popule a base de conhecimento** (para Knowledge Agent):
   ```bash
   python src/data/populate_kb.py
   ```

4. **Configure o banco de dados de usuários** (para Customer Support Agent):
   O script `src/config/setup_db.py` cria tabelas e insere dados mockados automaticamente ao iniciar a aplicação. Se quiser executar manualmente:
   ```bash
   python -c "from src.config.setup_db import setup_mock_data; setup_mock_data()"
   ```

### Execução com Docker Compose (Recomendado)

```bash
docker-compose up --build
```

A aplicação estará disponível em `http://localhost:8000`.

### Execução Manual com Docker

```bash
# Build da imagem
docker build -t agent-swarm .

# Execução
docker run -p 8000:8000 \
  -e HUGGINGFACEHUB_API_TOKEN=seu_token \
  -v $(pwd)/src/data/vector_store:/app/src/data/vector_store \
  agent-swarm
```

### Verificação de Saúde

Acesse `http://localhost:8000/health` para verificar se a aplicação está rodando.

### API Endpoints

- `GET /health`: Verificação de saúde
- `POST /chat`: Processamento de mensagens
  - Body: `{"message": "Sua pergunta", "user_id": "id_usuario"}`
  - Response: Detalhes da resposta do agente

## Pipeline RAG (Retrieval Augmented Generation)

### Ingestão de Dados

- **Fonte**: Páginas web do InfinitePay (lista definida em `settings.py`)
- **Extração**: Uso de `requests` e `BeautifulSoup` para scraping de texto
- **Limpeza**: Remoção de scripts/estilos, caracteres não-ASCII, limite de tamanho
- **Processamento**: Função `extract_content_from_url()` em `populate_kb.py`

### Armazenamento

- **Vector Store**: ChromaDB local persistente
- **Embedder**: SentenceTransformer para conversão de texto em vetores
- **Configuração**: Coleção "infinitepay_kb", path configurável via settings

### Recuperação

- **Busca**: Similaridade vetorial baseada na query do usuário
- **Contexto**: Top-k documentos relevantes recuperados
- **Integração**: Agno Knowledge integra automaticamente com agentes

### Geração

- **Modelo**: HuggingFace models via Agno
- **Prompt**: Contexto RAG + instruções do agente
- **Resposta**: Geração fundamentada em dados recuperados


### Testes 

``
pip install -r requirements.txt
``

Os testes incluem:
- `test_agents.py`: Testes dos agentes individuais
- `test_customer_support.py`: Testes específicos do suporte ao cliente

### Cenários de Teste

Exemplos de mensagens para testar:
- "Qual o valor da maquininha Smart?" (Knowledge Agent)
- "Não consigo fazer transferências" (Customer Support Agent)
- "Qual o placar do último jogo do Palmeiras?" (Web Search via Knowledge Agent)

## Como Aproveitamos as Ferramentas de LLM

### Framework Agno

- **Agentes**: Criação simplificada de agentes com roles e instruções
- **Integrações**: Suporte nativo a Google Gemini, ChromaDB, SQLite
- **Ferramentas**: Sistema de tools para agentes (ex: consultas DB)
- **Memória**: Gerenciamento automático de contexto de conversa

### Modelos LLM

- **Google Gemini**: Modelos gratuitos para geração de texto
- **Configuração**: Via settings, com controle de tokens e temperatura
- **Uso**: Tanto para roteamento quanto para geração de respostas

### Técnicas

- **RAG**: Combinação de busca vetorial + geração para respostas precisas
- **Prompt Engineering**: Instruções específicas por agente em português
- **Multi-agent**: Coordenação entre agentes especializados

## Desenvolvimento

### Estrutura do Projeto

```
AgentsSwarm/
├── src/
│   ├── agents/          # Definição dos agentes
│   ├── api/            # API FastAPI
│   ├── config/         # Configurações e setup DB
│   ├── data/           # Base de conhecimento e população
│   └── tools/          # Ferramentas customizadas
├── tests/              # Testes unitários
├── Dockerfile          # Containerização
├── docker-compose.yml  # Orquestração
└── requirements.txt    # Dependências Python
```

### Próximos Passos

- guardrails para segurança
- mais agentes (ex: Slack Agent)
- testes 


