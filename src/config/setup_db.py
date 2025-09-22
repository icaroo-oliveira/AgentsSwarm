from agno.db.sqlite import SqliteDb
import sqlite3

# Configurar banco SQLite para Memory e dados mockados
db = SqliteDb(db_file="memory.db")

# Criar tabelas para dados mockados dos usuários
def setup_mock_data():
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    
    # Tabela para perfil do usuário
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            account_status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela para histórico de transações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            date TEXT,
            amount REAL,
            status TEXT,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
        )
    ''')
    
    # Inserir dados mockados
    cursor.execute('''
        INSERT OR IGNORE INTO user_profiles (user_id, name, email, account_status) VALUES
        ('client789', 'João Silva', 'joao.silva@email.com', 'ativo'),
        ('client123', 'Maria Santos', 'maria.santos@email.com', 'ativo'),
        ('client456', 'Pedro Oliveira', 'pedro.oliveira@email.com', 'bloqueado')
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO user_transactions (user_id, date, amount, status, description) VALUES
        ('client789', '2024-09-20', 150.00, 'aprovada', 'Compra no cartão'),
        ('client789', '2024-09-19', -50.00, 'aprovada', 'Transferência PIX'),
        ('client123', '2024-09-18', 200.00, 'pendente', 'Pagamento boleto'),
        ('client456', '2024-09-17', 100.00, 'rejeitada', 'Tentativa de compra')
    ''')
    
    conn.commit()
    conn.close()

# Executar setup das tabelas mockadas
setup_mock_data()