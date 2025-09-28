from agno.tools import tool
import contextvars

# Customer Support Tools

# contextVar para armazenar o user_id para a requisição atual
CURRENT_API_USER_ID: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "CURRENT_API_USER_ID", default=None
)


def _resolve_user_id(passed_user_id: str | None) -> str | None:
    """Retorna o user_id autoritativo para a requisição atual.

    Prefere o valor da ContextVar quando definido, caso contrário, usa o id passado.
    """
    ctx_id = CURRENT_API_USER_ID.get()
    if ctx_id:
        return ctx_id
    return passed_user_id


@tool
def get_user_account_info(user_id: str | None) -> str:
    """Recupera informações básicas da conta do usuário.

    Segurança: evita exposição de dados pessoais, preferindo o user_id da requisição atual.
    """
    import sqlite3

    uid = _resolve_user_id(user_id)
    if not uid or uid != user_id:
        return "Erro: conflito ou user_id inválido."

    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, account_status FROM user_profiles WHERE user_id = ?", (uid,))
    result = cursor.fetchone()
    conn.close()
    if result:
        name, email, status = result
        return f"Informações da conta para {name} ({uid}): Email: {email}, Status: {status}."
    else:
        return f"Usuário {uid} não encontrado."


@tool
def get_user_transactions(user_id: str | None, limit: int = 5) -> str:
    """Recupera últimas transações do usuário.

    Segurança: evita exposição de dados pessoais, preferindo o user_id da requisição atual.
    """
    import sqlite3

    uid = _resolve_user_id(user_id)
    if not uid or uid != user_id:
        return "Erro: conflito ou user_id inválido."

    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT date, amount, status, description FROM user_transactions WHERE user_id = ? ORDER BY date DESC LIMIT ?", (uid, limit))
    results = cursor.fetchall()
    conn.close()
    if results:
        transactions = "\n".join([f"- {date}: R$ {amount:.2f} ({status}) - {description}" for date, amount, status, description in results])
        return f"Últimas transações para {uid}:\n{transactions}"
    else:
        return f"Nenhuma transação encontrada para {uid}."