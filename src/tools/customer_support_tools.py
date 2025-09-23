from agno.tools import tool

# Customer Support Tools
@tool
def get_user_account_info(user_id: str) -> str:
    """Recupera informações básicas da conta do usuário."""
    import sqlite3
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, account_status FROM user_profiles WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        name, email, status = result
        return f"Informações da conta para {name} ({user_id}): Email: {email}, Status: {status}."
    else:
        return f"Usuário {user_id} não encontrado."

@tool
def get_user_transactions(user_id: str, limit: int = 5) -> str:
    """Recupera últimas transações do usuário."""
    import sqlite3
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT date, amount, status, description FROM user_transactions WHERE user_id = ? ORDER BY date DESC LIMIT ?", (user_id, limit))
    results = cursor.fetchall()
    conn.close()
    if results:
        transactions = "\n".join([f"- {date}: R$ {amount:.2f} ({status}) - {description}" for date, amount, status, description in results])
        return f"Últimas transações para {user_id}:\n{transactions}"
    else:
        return f"Nenhuma transação encontrada para {user_id}."