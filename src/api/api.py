from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from typing import Dict, Any, Optional
import logging
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.agents.router_team import router_team
from src.config.logging_config import setup_logging, get_logger
from src.config.settings import settings


setup_logging()
logger = get_logger("api")




app = FastAPI(
    title="Agent Swarm API",
    description="Multi-agent system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_id: str


class ChatResponse(BaseModel):
    success: bool
    response: str
    agent_used: str
    metadata: Dict[str, Any]
    user_id: str

router_agent = None


@app.on_event("startup")
async def startup_event():
    """Initialize agents on startup."""
    global router_agent
    try:
        logger.info("Inicializando Agent Swarm com Agno...")
        logger.info(f"Servidor: http://{settings.api_host}:{settings.api_port}")
        
        # Verificar e configurar banco de dados se necessário
        db_path = "memory.db"
        if not os.path.exists(db_path):
            logger.info("Banco de dados não encontrado, configurando dados mock...")
            import src.config.setup_db as mock_data
            mock_data.setup_mock_data()
            logger.info("Banco de dados configurado com sucesso!")
        else:
            logger.info("Banco de dados já existe, pulando configuração.")
        
        # Verificar e popular base de conhecimento se necessário
        if len(os.listdir(settings.vector_store_path)) <= 1:
            logger.info("Base de conhecimento não encontrada ou vazia, populando...")
            import src.data.populate_kb as populate
            await populate.populate_knowledge_base()
            logger.info("Base de conhecimento populada com sucesso!")
        else:
            logger.info("Base de conhecimento já existe, pulando população.")
        
        #inicialzia router agent
        router_agent = router_team
        logger.info("Router Agent inicializado com sucesso!")
        
    except Exception as e:
        logger.error(f"Falha ao inicializar Agent Swarm: {e}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "router_initialized": router_agent is not None
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Aceita POST requests com JSON payload:
    {
        "message": "Your query or statement here",
        "user_id": "some_user_identifier"  
    }
    
    Processa através do agent swarm e retorna resposta significativa.
    """
    try:
        if not router_team:
            raise HTTPException(status_code=500, detail="Router team não inicializado")

        # Processa mensagem pelo router team
        team_response = await router_team.arun(input=f"User ID: {request.user_id}. Message: {request.message}", user_id=request.user_id)
        response = ChatResponse(
            success=True,
            response=team_response.content,
            agent_used="router_team",
            metadata={"team_response": team_response.content, "original_message": request.message},
            user_id=request.user_id
        )
        logger.info(f"Resposta do Team: {team_response.content}...")
        return response
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno do servidor: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )