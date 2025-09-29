"""Configuration settings for the Agent Swarm application."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Hugging Face Configuration (gratuito!)
    huggingfacehub_api_token: str = Field(..., env="HF_TOKEN")
    
    # Google Gemini Configuration (gratuito!)
    google_api_key: str = Field(default="", env="GOOGLE_API_KEY")
    
    # Model Configuration - Modelos gratuitos Google Gemini
    router_model: str = Field(default="gemini-2.5-flash", env="MODEL_ROUTER")
    knowledge_model: str = Field(default="gemini-2.5-pro", env="MODEL_KNOWLEDGE")
    support_model: str = Field(default="gemini-2.5-flash", env="MODEL_SUPPORT")
    custom_model: str = Field(default="gemini-2.0-flash", env="MODEL_CUSTOM")
    guardrail_model: str = Field(default="gemini-2.0-flash-lite", env="MODEL_GUARDRAIL")

    # Embedder Configuration
    embedder_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDER_MODEL")

    # Vector Store Configuration
    vector_store_path: str = Field(default="./src/data/vector_store", env="VECTOR_STORE_PATH")
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_workers: int = Field(default=1, env="API_WORKERS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # InfinitePay Configuration
    infinitepay_base_url: str = Field(default="https://www.infinitepay.io", env="INFINITEPAY_BASE_URL")
    infinitepay_urls: list[str] = [
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
        "https://www.infinitepay.io/rendimento"
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


#global
settings = Settings()
