# app.py

from flask import Flask, render_template, request
# import os # Não é mais necessário para o CSV
import pyodbc # Importar o módulo pyodbc para conectar ao SQL Server

app = Flask(__name__)
app.secret_key = 'uma_chave_secreta_muito_segura' # Mantenha sua chave secreta

# --- Configurações do Banco de Dados SQL Server ---
# ATENÇÃO: SUBSTITUA ESTES VALORES PELOS SEUS DADOS REAIS DO SQL SERVER!
# String de conexão ODBC para SQL Server
# Para Autenticação do SQL Server:
# Se você está usando autenticação do Windows, pode ser um pouco diferente: 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=SEU_NOME_DO_SERVIDOR;DATABASE=RestauranteDB;Integrated Security=SSPI;'
DB_SERVER = 'DESKTOP-5CI11MT' # <--- APENAS O NOME DO SEU PC!
DB_DATABASE = 'RestauranteDB'
DB_USERNAME = 'magno' # ATENÇÃO: Veremos isso abaixo!
DB_PASSWORD = 'Titan150'   # ATENÇÃO: Veremos isso abaixo!

# String de conexão ODBC para SQL Server
DB_CONNECTION_STRING = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'  # Esta linha está correta
    f'SERVER={DB_SERVER};'                       # <-- CORRIGIDO: palavra-chave SERVER, valor da variável DB_SERVER
    f'DATABASE={DB_DATABASE};'                   # <-- CORRIGIDO: palavra-chave DATABASE, valor da variável DB_DATABASE
    f'Integrated Security=SSPI;'
     f'TrustServerCertificate=yes;' # ESSA LINHA É PARA AUTENTICAÇÃO DO WINDOWS
    #f'Authentication=ActiveDirectoryIntegrated;' # Esta linha precisa ser removida ou comentada
    #f'Authentication=ActiveDirectoryInteractive;' # Esta linha precisa ser removida ou comentada
)


# --- Função para conectar ao banco de dados ---
# --- Função para conectar ao banco de dados ---
def get_db_connection():
    conn = None
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        print("Conexão ao banco de dados SQL Server estabelecida com sucesso!")
        return conn
    except pyodbc.Error as ex:
        # Esta linha abaixo é a que precisamos AGORA para ver o erro detalhado!
        print(f"Erro detalhado ao conectar ao SQL Server: {ex}")
        sqlstate = ex.args[0]
        if sqlstate == '28000':
            print("Erro de autenticação ao conectar ao SQL Server. Verifique usuário e senha.")
        else:
            print(f"Erro genérico de conexão ao SQL Server: {ex}") # Mudei a mensagem para 'genérico'
        return None


# --- Backend: Função para salvar no SQL Server (Substitui a de CSV) ---
def salvar_reserva_sql(reserva_data):
    """
    Função para salvar os dados da reserva na tabela 'Reservas' do SQL Server.
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # O ReservationID é IDENTITY (auto-incrementável), então não o incluímos no INSERT
            sql = """
            INSERT INTO Reservas (NomeCliente, EmailCliente, TelefoneCliente, DataReserva, HoraReserva, NumeroPessoas)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql,
                            reserva_data.get('nome'),
                            reserva_data.get('email'),
                            reserva_data.get('telefone'),
                            reserva_data.get('data'),
                            reserva_data.get('hora'),
                            int(reserva_data.get('pessoas')) # Converte para int, pois é um número
                            )
            conn.commit() # Confirma a transação
            print(f"Reserva de {reserva_data.get('nome')} salva no SQL Server com sucesso!")
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Erro ao inserir reserva no SQL Server: {ex}")
            conn.rollback() # Desfaz a transação em caso de erro
        finally:
            cursor.close()
            conn.close()
    else:
        print("Não foi possível salvar a reserva, conexão com o banco de dados falhou.")


@app.route('/')
def index():
    """
    Renderiza a página inicial (o formulário de reserva).
    """
    return render_template('index.html')

@app.route('/reservar', methods=['POST'])
def reservar():
    """
    Recebe os dados do formulário de reserva quando ele é enviado (método POST).
    Aqui é onde você, como backend, processa e salva os dados.
    """
    if request.method == 'POST':
        # Coleta os dados do formulário
        nome = request.form['name']
        email = request.form['email']
        telefone = request.form['phone']
        data = request.form['date']
        hora = request.form['time']
        pessoas = request.form['guests']

        reserva_atual = {
            'nome': nome,
            'email': email,
            'telefone': telefone,
            'data': data,
            'hora': hora,
            'pessoas': pessoas
        }

        try:
            # Agora chamamos a função que salva no SQL Server
            salvar_reserva_sql(reserva_atual)
            print(f"--- Nova Reserva Recebida e Processada (SQL Server) ---")
            print(f"Dados: {reserva_atual}")
            print(f"--------------------------------------------------")
            return "Reserva recebida com sucesso e salva no banco de dados!", 200
        except Exception as e:
            print(f"--- ERRO ao processar e salvar reserva no SQL Server ---")
            print(f"Erro geral: {e}")
            print(f"Dados da reserva que falhou: {reserva_atual}")
            print(f"----------------------------------------------------")
            return f"Erro ao processar reserva: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)