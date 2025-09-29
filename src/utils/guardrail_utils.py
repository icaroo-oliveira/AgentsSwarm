from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


def validate_guardrail_response(guardrail_check):
    """
    Valida a estrutura da resposta do guardrail agent.
    Levanta HTTPException se houver conflito, atividade suspeita ou estrutura inválida.
    """
    try:
        content = getattr(guardrail_check, "content", None)
        #  content for None, isso já indica problema
        if content is None:
            raise ValueError("guardrail returned empty content")

        there = getattr(content, "there_is_id_conflict", None)
        susp = getattr(content, "suspicious_activity", None)
        reason = getattr(content, "reason", "")

        # campos obrigatórios devem existir (não None)
        if there is None or susp is None:
            raise ValueError("guardrail response missing required fields")

        if bool(there) or bool(susp):
            logger.warning(f"Mensagem bloqueada: {reason or 'razão não informada'}")
            raise HTTPException(status_code=403, detail=f"Mensagem bloqueada pelo Guardrail Agent: {reason or 'razão não informada'}")

    except HTTPException:
        raise
    except Exception as e:
        # falha de estrutura: bloquear por segurança
        raw = getattr(guardrail_check, 'content', str(guardrail_check))
        logger.error(f"Estrutura inválida na resposta do Guardrail: {e}; raw: {raw}")
        raise HTTPException(status_code=403, detail="Mensagem bloqueada pelo Guardrail: saída inválida")
