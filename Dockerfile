FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

ENV PYTHONPATH=/app

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (cache build)
COPY requirements.txt .

# Instalar dependências Python (com cache)
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# Copiar código da aplicação
COPY . .

# Executar setup do banco e população da base de conhecimento durante o build
RUN python -c "from src.config.setup_db import setup_mock_data; setup_mock_data()" && \
    python -c "import asyncio; from src.data.populate_kb import populate_knowledge_base; asyncio.run(populate_knowledge_base())"

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "src.api.api:app", "--host", "0.0.0.0", "--port", "8000",  "--reload"]
