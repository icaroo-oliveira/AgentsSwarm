# Agent Swarm - Multi-Agent System with Agno

## Description

This project implements an intelligent agent system (Agent Swarm) using the Agno framework. The system processes user messages through three specialized agent types: Router Agent, Knowledge Agent, and Customer Support Agent. The application is containerized with Docker and exposes a REST API for interaction.

## Agent Swarm Architecture

### Implemented Agents

1. **Router Agent**
   - **Function**: Main entry point for all messages.
   - **Responsibilities**: Analyzes message content and decides which specialized agent should handle it.
   - **Decisions**: Based on intent and context analysis.

2. **Knowledge Agent**
   - **Function**: Answers questions about InfinitePay products and services.
   - **Technology**: Uses Structured RAG (Retrieval Augmented Generation) with structural chunking for responses based on official website data.
   - **Tools**: Web search for general questions, RAG for specific knowledge.

3. **Customer Support Agent**
   - **Function**: Provides customer support by retrieving specific user data.
   - **Tools**: Two implemented tools to query user profile and transactions.
   - **Database**: SQLite with mocked data for simulation.
   - **Security**: Tools include defenses to prevent access to other users' data via prompt injection, using ContextVar for request isolation.

4. **Guardrail Agent**
   - **Function**: Security layer that validates messages before processing.
   - **Responsibilities**: Checks for user ID conflicts (e.g., attempts to access other users' data) and suspicious activities (e.g., prohibited requests or jailbreaks).
   - **Technology**: Uses LLM to analyze message content and return structured validation (JSON with conflict flags, severity, and reason).
   - **Integration**: Runs before routing, blocking invalid requests with HTTP 403.

### Message Processing Flow

1. **Reception**: API receives POST to `/chat` with JSON containing `message` and `user_id`.
2. **Guardrail Check**: Guardrail Agent validates the message for security (ID conflicts, suspicious activities).
3. **Routing**: Router Agent analyzes the message and selects the appropriate agent.
4. **Processing**: Selected agent executes its logic (RAG, DB queries, etc.).
5. **Response**: System returns JSON with response, used agent, confidence, and metadata.
6. **Memory**: Conversation data is stored for future context.

### Design Choices

- **Agno Framework**: Chosen for simplicity in creating agents and LLM integrations.
- **FastAPI**: For fast, automatically documented REST API.
- **ChromaDB**: Vector store for RAG, running as a Docker service.
- **Docker**: Containerization for portability and isolation.
- **SQLite**: Simple database for mocked user data.

## How to Build, Configure, and Run

### Prerequisites

- Docker and Docker Compose installed
- Google Gemini API key (free, for LLM models) (aistudio.google.com/app/apikey)

### Configuration

1. **Clone the repository**:
   ```bash
   git clone https://github.com/icaro-oliveira/MultiAgent.git
   cd MultiAgent
   ```

2. **Configure environment variables**:
   Create a `.env` file in the project root:
   ```
   GOOGLE_API_KEY=your_key_here
   MODEL=gemini-2.5-flash
   EMBEDDER_MODEL=gemini-embedding-001
   CHROMA_HOST=localhost
   CHROMA_PORT=8001
   LOG_LEVEL=INFO
   ```

3. **Populate the knowledge base** (for Knowledge Agent):
   ```bash
   python src/data/populate_kb.py
   ```

4. **Configure the user database** (for Customer Support Agent):
   The `src/config/setup_db.py` script creates tables and inserts mocked data automatically when starting the application. If you want to run manually:
   ```bash
   python -c "from src.config.setup_db import setup_mock_data; setup_mock_data()"
   ```

### Execution with Docker Compose (Recommended)

```bash
docker-compose up --build
```

The application will be available at `http://localhost:8000`.

### Manual Execution with Docker

```bash
# Build the image
docker build -t agent-swarm .

# Execution
docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=your_key \
  agent-swarm
```

### Health Check

Access `http://localhost:8000/health` to verify the application is running.

### Local Execution (Without Docker)

If you prefer to run without Docker, follow these steps:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure the `.env` file** as described in the configuration section.

3. **Run the application**:
   ```bash
   python src/api/api.py
   ```

The application will be available at `http://localhost:8000`.

### API Endpoints

- `GET /health`: Health check
- `POST /chat`: Message processing
  - Body: `{"message": "Your question", "user_id": "user_id"}`
  - Response: Agent response details

## RAG Pipeline (Retrieval Augmented Generation)

We use **Structured RAG** — a chunking strategy that preserves the semantic structure of the source pages instead of splitting text into fixed-size fragments.

### Why Structured RAG?

The InfinitePay pages are marketing landing pages with clear HTML hierarchy (H1, H2, H3, FAQs). Fixed-size chunking would break sections in the middle, mixing unrelated topics in the same chunk and losing context. Structural chunking keeps each section as a self-contained unit, preserving its meaning and hierarchy. This results in more relevant retrieval and better-grounded responses.

### Data Ingestion

- **Source**: 18 InfinitePay web pages (URLs defined in `settings.py`)
- **Extraction**: `requests` + `BeautifulSoup` for HTML scraping
- **Structural Chunking**: Content is split into three chunk types:
  - **Hero**: H1 + introductory paragraph (page overview)
  - **Section**: H2 + associated body content (product features, benefits)
  - **FAQ**: H3 ending in `?` + answer text (common questions)
- **Metadata**: Each chunk carries `url`, `product`, `section_type`, and `heading`
- **Processing**: `extract_structural_chunks()` in `populate_kb.py`

### Storage

- **Vector Store**: ChromaDB running as a Docker service (port 8001)
- **Embedder**: GeminiEmbedder (`gemini-embedding-001`, 768 dimensions)
- **Collection**: `infinitepay_kb`

### Retrieval

- **Search**: Vector similarity based on user query
- **Context**: Top-k relevant documents retrieved with metadata
- **Integration**: Agno Knowledge integrates automatically with agents

### Generation

- **Model**: Google Gemini via Agno
- **Prompt**: RAG context + agent instructions
- **Response**: Generation grounded in retrieved data

### Tests

```
pip install -r requirements.txt
```

The tests include:
- `test_agents.py`: Individual agent tests
- `test_customer_support.py`: Specific customer support tests

### Test Scenarios

Example messages to test:
- "What is the value of the Smart machine?" (Knowledge Agent)
- "I can't make transfers" (Customer Support Agent)
- "What was the last Palmeiras game score?" (Web Search via Knowledge Agent)

## How We Leveraged LLM Tools

### Agno Framework

- **Agents**: Simplified creation of agents with roles and instructions
- **Integrations**: Native support for Google Gemini, ChromaDB, SQLite
- **Tools**: Tool system for agents (e.g., DB queries)
- **Memory**: Automatic conversation context management

### LLM Models

- **Google Gemini**: Free models for text generation
- **Configuration**: Via settings, with token and temperature control
- **Usage**: For both routing and response generation

### Techniques

- **RAG**: Combination of vector search + generation for accurate responses
- **Prompt Engineering**: Specific instructions per agent in Portuguese
- **Multi-agent**: Coordination between specialized agents

## Development

### Project Structure

```
AgentsSwarm/
├── src/
│   ├── agents/          # Agent definitions
│   ├── api/            # FastAPI
│   ├── config/         # Configurations and DB setup
│   ├── data/           # Knowledge base and population
│   └── tools/          # Custom tools
├── tests/              # Unit tests
├── Dockerfile          # Containerization
├── docker-compose.yml  # Orchestration
└── requirements.txt    # Python dependencies
```

### Next Steps

- more agents (e.g., Slack Agent)
- tests 


