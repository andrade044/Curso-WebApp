from flask import Flask, request, jsonify, redirect, url_for
import os
import mercadopago
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import psycopg2 
from python_http_client.exceptions import HTTPError
import bcrypt

# Carrega variáveis do arquivo .env (se existir)
load_dotenv() 

# --- Configuração do Flask ---
app = Flask(__name__)

# --- Configuração do Banco de Dados e Variáveis de Ambiente ---
DB_NAME = os.getenv('DB_NAME')
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
MP_NOTIFICATION_URL = os.getenv("MP_NOTIFICATION_URL")
CHAVE_API_SENDGRID = os.getenv('CHAVE_API_SENDGRID')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
URL_BASE_ATIVACAO = os.getenv('URL_BASE_ATIVACAO') 
DATABASE_URL = os.getenv("DATABASE_URL")
EMAIL_REMETENTE = os.getenv('EMAIL_REMETENTE')

# CORREÇÃO CRÍTICA: Converte para int e define default para expiração do token
try:
    ACTIVATION_EXPIRATION_DAYS = int(os.getenv('ACTIVATION_EXPIRATION_DAYS', 7))
except ValueError:
    ACTIVATION_EXPIRATION_DAYS = 7
    print("Aviso: ACTIVATION_EXPIRATION_DAYS inválido, usando default de 7 dias.")

# NOVO ENV VAR: URL para onde o usuário será redirecionado após a ativação por e-mail
STREAMLIT_LOGIN_URL = os.getenv('STREAMLIT_LOGIN_URL')


if not MP_ACCESS_TOKEN:
    print("ERRO: MP_ACCESS_TOKEN não configurado no ambiente.")
    sdk = None # Define sdk como None para evitar erro
else:
    sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

def get_db_connection():
    """Conecta ao PostgreSQL usando a URL de ambiente."""
    if not DATABASE_URL:
        raise ConnectionError("DATABASE_URL não está configurada.")
    
    # Adiciona ?sslmode=require para compatibilidade com a maioria dos hosts em nuvem
    return psycopg2.connect(DATABASE_URL + "?sslmode=require")


def update_user_status(user_id, field_name, value):
    """Função genérica para atualizar um campo (ativo/assinante) no DB (PostgreSQL)."""
    conn = None
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        if field_name not in ['assinante', 'ativo']:
            raise ValueError("Nome do campo de atualização inválido.")
            
        sql_query = f"UPDATE usuarios SET {field_name} = %s WHERE id = %s"
        print(f"DEBUG DB: Tentando executar UPDATE no campo {field_name} para ID {user_id} com valor {value}")

        user_id_int = int(user_id) if isinstance(user_id, str) else user_id
        # Nota: Usamos %s para placeholders no psycopg2
        c.execute(sql_query, (value, user_id_int))
        conn.commit()
        
        success = c.rowcount > 0
        print(f"DEBUG DB: Linhas afetadas: {c.rowcount}. Sucesso: {success}")
        if not success:
            print(f"AVISO: 0 linhas afetadas. user_id {user_id} não encontrado ou já atualizado.")
  
        c.close()
        return success

    except Exception as e:
        print(f"ERRO CRÍTICO AO ATUALIZAR DB ({field_name}): {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()


def generate_activation_token(user_id):
    """Gera um token JWT para ativação de conta. Use esta função no seu Streamlit."""
    if not JWT_SECRET_KEY:
        print("ERRO: JWT_SECRET_KEY não configurada.")
        return None
        
    try:
        # Define o payload do token
        payload = {
            'user_id': user_id,
            # Usa a variável convertida para int
            'exp': datetime.now(timezone.utc) + timedelta(days=ACTIVATION_EXPIRATION_DAYS),
            'iat': datetime.now(timezone.utc)
        }
        
        # Codifica o token
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
        return token
    except Exception as e:
        print(f"Erro ao gerar JWT: {e}")
        return None

# @app.route("/api/ativar-conta", methods=["POST"])
# def ativar_conta_post():
#     data = request.get_json()
#     token = data.get('token')
    
#     if not token:
#         print("DEBUG: Token ausente no JSON (POST).")
#         return jsonify({"message": "Token de ativação ausente."}), 400

#     user_id = None
#     try:
#         # 1. VALIDAÇÃO DO TOKEN
#         payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
#         user_id = payload.get('user_id')
        
#         if isinstance(user_id, str):
#             user_id = int(user_id)
            
#         print(f"DEBUG: Token decodificado com sucesso (POST). Tentando ativar User ID: {user_id}")

#     except jwt.ExpiredSignatureError:
#         print(f"ERRO: Token expirado (POST) para user_id: {user_id}")
#         return jsonify({"message": "O link de ativação expirou."}), 401
#     except jwt.InvalidTokenError as e:
#         print(f"ERRO: Token inválido (POST): {e}")
#         return jsonify({"message": "Token de ativação inválido."}), 401
#     except Exception as e:
#         print(f"ERRO INESPERADO NA DECODIFICAÇÃO DO JWT (POST): {e}")
#         return jsonify({"message": "Erro interno do servidor."}), 500

#     # 2. ATUALIZAÇÃO DO BANCO DE DADOS
#     if user_id and update_user_status(user_id, 'ativo', 1):
#         print(f"DEBUG: SUCESSO! Usuário ID {user_id} ativado via POST.")
#         # Retorna sucesso para o Streamlit
#         return jsonify({"message": "Conta ativada com sucesso."}), 200
#     else:
#         print(f"DEBUG: FALHA AO ATUALIZAR DB para User ID: {user_id} (POST)")
#         return jsonify({"message": "Falha ao ativar a conta."}), 500



# @app.route("/api/ativar-conta", methods=["GET"])
# def ativar_conta_get():
#     token = request.args.get('token')
    
#     if not token:
#         print("DEBUG: Token ausente na URL (GET).")
#         return "Erro: Token de ativação ausente.", 400

#     user_id = None
#     try:
#         # 1. VALIDAÇÃO DO TOKEN
#         payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
#         user_id = payload.get('user_id')
        
#         # Garante que user_id é um número (se for o caso)
#         if isinstance(user_id, str):
#             user_id = int(user_id) 

#         print(f"DEBUG: Token decodificado com sucesso (GET). Tentando ativar User ID: {user_id}")
        
#     except jwt.ExpiredSignatureError:
#         print(f"ERRO: Token expirado (GET) para user_id: {user_id}")
#         return "Erro: O link de ativação expirou.", 401
#     except jwt.InvalidTokenError as e:
#         print(f"ERRO: Token inválido (GET): {e}")
#         return "Erro: Token de ativação inválido.", 401
#     except Exception as e:
#         print(f"ERRO INESPERADO NA DECODIFICAÇÃO DO JWT (GET): {e}")
#         return "Erro interno do servidor.", 500

#     # 2. ATUALIZAÇÃO DO BANCO DE DADOS
#     if user_id and update_user_status(user_id, 'ativo', 1):
#         print(f"DEBUG: SUCESSO! Usuário ID {user_id} ativado via GET.")
        
#         if STREAMLIT_LOGIN_URL:
#             return redirect(f"{STREAMLIT_LOGIN_URL}?message=activated&user={user_id}", code=302)
#         else:
#             return "SUCESSO: Conta ativada. Por favor, acesse o seu aplicativo Streamlit e faça login.", 200
       
#     else:
#         print(f"DEBUG: FALHA AO ATUALIZAR DB para User ID: {user_id} (GET)")
#         # Se a ativação falhar (ex: usuário já está ativo), ainda podemos redirecionar para uma mensagem neutra
#         return redirect(f"{STREAMLIT_LOGIN_URL}?message=already_active", code=302)


def hash_senha(senha):
    """Gera o hash BCrypt da senha."""
    senha_bytes = senha.encode('utf-8')
    return bcrypt.hashpw(senha_bytes, bcrypt.gensalt())

def cadastrar_usuario(cpf, email, nome, senha, assinante, ativo=0):
    """
    Cadastra um novo usuário no DB (PostgreSQL/Supabase),
    removendo a necessidade dos campos de token de ativação.
    """
    conn = None
    try:
        conn = get_db_connection() # Usa a função que você já definiu
        c = conn.cursor()
        hashed_password = hash_senha(senha)
        
        # SQL: Removemos token_ativacao e token_expiracao
        sql_query = """
            INSERT INTO usuarios (cpf, email, nome, senha_hash, assinante, ativo)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, nome; -- Assumindo que o ID da tabela é 'id'
        """
        
        c.execute(
            sql_query,
            (cpf, email, nome, hashed_password, assinante, ativo)
        )
        
        user_id, nome_retornado = c.fetchone()
        
        conn.commit()
        c.close()
        
        return user_id, nome_retornado 

    except psycopg2.errors.UniqueViolation as e:
        print(f"ERRO DE CADASTRO - VIOLAÇÃO DE UNICIDADE (Email ou CPF já existe): {e}")
        if conn:
            conn.rollback()
        return False, None
        
    except Exception as e:
        print(f"ERRO DE CADASTRO NO DB: {e}") 
        if conn:
            conn.rollback()
        return False, None
        
    finally:
        if conn:
            conn.close()



@app.route("/cadastro", methods=["POST"])
def cadastro():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')
    cpf = data.get('cpf')
    nome = data.get('nome')
    assinante = 0 # Assume 0 no cadastro inicial
    
    if not all([email, senha, cpf, nome]):
        return jsonify({"message": "Campos obrigatórios ausentes."}), 400

    # user_id e nome são retornados
    user_id, nome_usuario = cadastrar_usuario(cpf, email, nome, senha, assinante)
    
    if user_id:
        
        try:
            # Envia o e-mail de boas-vindas
            enviar_email_ativacao_sendgrid(email, nome_usuario)
            print(f"DEBUG: E-mail de boas-vindas enviado para {email}")
            
        except Exception as e:
            # Loga, mas não impede o sucesso do cadastro
            print(f"ERRO: Falha ao enviar e-mail de boas-vindas: {e}") 
        
        # Retorna sucesso para o Streamlit
        return jsonify({"message": "Cadastro realizado com sucesso! Verifique seu e-mail de boas-vindas."}), 201
    
    else:
        # Erro comum: usuário já existe (IntegrityError capturado em cadastrar_usuario)
        return jsonify({"message": "Este e-mail ou CPF já está cadastrado."}), 40



@app.route("/mercadopago_webhook", methods=["POST"])
def mercadopago_webhook():
    """Endpoint para receber as notificações (Webhooks) do Mercado Pago."""
    
    
    data = request.json
    
    if data is None:
        return jsonify({"message": "Nenhum dado recebido."}), 400

    topic = data.get("topic") or data.get("type")
    
    # Processa apenas notificações de pagamento
    if topic != "payment":
        return jsonify({"message": f"Tópico ignorado: {topic}"}), 200

    # Obtém o ID do pagamento da notificação
    payment_id = data.get("id") or data.get("data", {}).get("id")

    if not payment_id:
        return jsonify({"message": "ID do pagamento ausente."}), 400
    
    print(f"Webhook recebido para Pagamento ID: {payment_id}")

    try:
        # 1. Busca os detalhes completos do pagamento na API do MP
        # Garante que o SDK foi inicializado
        if sdk is None:
             print("ERRO: SDK do Mercado Pago não inicializado.")
             return jsonify({"message": "Serviço MP indisponível"}), 503
             
        payment_response = sdk.payment().get(payment_id)
        payment = payment_response["response"]

        status = payment.get("status")
        external_reference = payment.get("external_reference")

        print(f"Status: {status} | Ref: {external_reference}")

        # 2. Verifica aprovação
        if status == "approved":
            
            # Formato esperado da referência: REF-{user_id}-{uuid}
            if not external_reference or len(external_reference.split("-")) < 2:
                print("ERRO: External reference inválida.")
                return jsonify({"message": "External reference inválida."}), 400

            try:
                # Extrai o ID do usuário
                user_id_str = external_reference.split("-")[1]
                user_id = int(user_id_str)
            except ValueError:
                print("ERRO: ID do usuário na referência não é numérico.")
                return jsonify({"message": "ID do usuário inválido na referência."}), 400

            # 3. Atualiza o status do usuário no DB
            if update_user_status(user_id, 'assinante', 1):
                print(f"SUCESSO: Usuário ID {user_id} atualizado para assinante.")
                return jsonify({"message": "Status de assinante atualizado."}), 200
            else:
                return jsonify({"message": "Erro ao atualizar DB."}), 500
        
        else:
            # Pagamento não aprovado, apenas registra e retorna 200 para o MP
            print(f"Pagamento não aprovado: {status}")
            return jsonify({"message": f"Pagamento com status: {status}"}), 200

    except Exception as e:
        print(f"Erro ao processar pagamento: {e}")
        # Retorna 500 para o Mercado Pago tentar re-enviar
        return jsonify({"message": f"Erro interno no processamento do webhook: {e}"}), 500



def enviar_email_ativacao_sendgrid(destinatario: str, nome_usuario: str, link_ativacao: str) -> int:
    """
    Envia o email de ativação com o link dinâmico usando o SendGrid.
    Retorna o código de status HTTP (200, 202 em sucesso) ou o código de erro.
    """
    api_key = CHAVE_API_SENDGRID
    remetente = EMAIL_REMETENTE

    if not api_key:
        print("ERRO: CHAVE_API_SENDGRID não definida.")
        return 500

    # 1. Conteúdo em Texto Simples (Melhora a entregabilidade)
    email_text = f"""
    Olá, {nome_usuario},
    
    Obrigado por se registrar! Bem-vindo(a) à Plataforma! Seu Cadastro foi Concluído
    
    
    Atenciosamente,
    Equipe do Curso.
    """
    
    # 2. Conteúdo HTML (Copia da Função 1 ou 2, ambos são bons)
    email_html = f"""
    <html>
        <body>
            <p>Olá, **{nome_usuario}**!</p>
            
            <p>Ficamos muito felizes em ter você a bordo. Seu cadastro foi concluído com sucesso e você já pode acessar todo o nosso conteúdo exclusivo na plataforma.</p>
            
            <p>Seus dados de login são:</p>
            <ul>
                <li><strong>E-mail:</strong> {destinatario}</li>
            </ul>
            
            <p>Para começar, basta clicar no link abaixo e usar seu e-mail e senha cadastrados:</p>
            
            <a href="{os.getenv('STREAMLIT_LOGIN_URL')}" style="padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; display: inline-block;">
                Acessar Minha Conta
            </a>
            
            <p style="margin-top: 20px;">Se tiver qualquer dúvida, é só nos responder!</p>
            <p>Atenciosamente,<br>A Equipe de Suporte</p>
        </body>
    </html>
    """
    
    email = Mail(
        from_email=remetente,
        to_emails=destinatario,
        subject='Ativação de Conta - Seu Curso de CNH',
        html_content=email_html,
        plain_text_content=email_text # Adicionando o texto simples
    )

    # 3. Tratamento de Erros Aprimorado
    try:
        conta_sendgrid = SendGridAPIClient(api_key)
        resposta = conta_sendgrid.send(email)
        print(f"Email enviado. Status Code: {resposta.status_code}")
        return resposta.status_code
    except HTTPError as e:
        # Erro específico da API do SendGrid
        print(f"Erro ao enviar email (Status {e.status_code}): {e.body}")
        # Retorna o status code do erro para o chamador
        return e.status_code 
    except Exception as e:
        # Erro inesperado
        print(f"Erro inesperado no envio de email: {e}")
        return 500

@app.route("/auth", methods=["POST"]) # <--- É AQUI QUE VOCÊ COLOCA!
def auth_handler():
    """
    Trata requisições POST para Login ou Cadastro, dependendo do campo 'action'.
    """
    data = request.get_json()
    action = data.get('action') # 'CADASTRO' ou 'LOGIN'
    
    if not action:
        return jsonify({"message": "Ação não especificada."}), 400

    # LÓGICA DE CADASTRO
    if action == "CADASTRO":
        # 1. Extrair dados do payload
        cpf = data.get('cpf')
        email = data.get('email')
        nome = data.get('nome')
        senha = data.get('senha')
        assinante = data.get('assinante', 0)
        
        # 2. Chamar a função de DB e obter ID/Nome
        # Certifique-se que 'cadastrar_usuario' não exige mais os argumentos de token
        user_id, nome_usuario = cadastrar_usuario(cpf, email, nome, senha, assinante, ativo=1) # ATIVO = 1 (Login imediato)
        
        if user_id:
            # 3. Enviar o e-mail de boas-vindas
            enviar_email_ativacao_sendgrid(email, nome_usuario)
            return jsonify({"message": "Cadastro realizado com sucesso! Verifique seu e-mail de boas-vindas."}), 201
        else:
            # Erro de integridade (Email/CPF já existe)
            return jsonify({"message": "Este e-mail ou CPF já está cadastrado."}), 409
    
    # LÓGICA DE LOGIN
    elif action == "LOGIN":
        email = data.get('email')
        senha = data.get('senha')
        
        # 1. Buscar usuário no DB
        user_data = buscar_usuario_com_dados_completos(email) 
        
        if user_data and verificar_senha(senha, user_data['senha_hash']):
            # 2. Retornar dados completos do usuário logado
            return jsonify({
                "message": "Login bem-sucedido",
                "user_data": {
                    "user_id": user_data['id'],
                    "nome": user_data['nome'],
                    "assinante": user_data['assinante']
                }
            }), 200
        else:
            return jsonify({"message": "Email ou senha incorretos."}), 401
        
    else:
        return jsonify({"message": "Ação desconhecida."}), 400

def verificar_senha(senha_digitada, senha_hash_salva):
    """Verifica se a senha digitada corresponde ao hash salvo."""
    senha_digitada_bytes = senha_digitada.encode('utf-8')
    # O hash do banco precisa ser convertido para bytes se estiver em string
    # Nota: No SQLite ele pode ser salvo como BLOB, aqui assumimos que é uma string de texto
    if isinstance(senha_hash_salva, str):
         senha_hash_salva = senha_hash_salva.encode('utf-8')
    
    return bcrypt.checkpw(senha_digitada_bytes, senha_hash_salva)


def get_db_connection():
    """Conecta ao seu banco de dados (ex: PostgreSQL/Supabase)."""
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        # Exemplo com psycopg2:
        # conn = psycopg2.connect(DATABASE_URL) 
        # return conn
        
        # Por enquanto, retorne um erro ou um mock se estiver testando:
        raise Exception("SUBSTITUIR: Implemente sua conexão ao PostgreSQL/Supabase aqui.")
    except Exception as e:
        print(f"Erro de Conexão com o DB: {e}")
        return None

def buscar_usuario_com_dados_completos(email):
    """
    Busca um usuário pelo email no DB (PostgreSQL) e retorna todos os dados necessários.
    """
    conn = get_db_connection()
    if conn is None:
        return None # Falha na conexão

    try:
        with conn.cursor() as c:
            # 1. SQL: Seleciona todos os campos necessários para o login e a sessão
            sql_query = """
                SELECT id, nome, senha_hash, assinante, ativo 
                FROM usuarios 
                WHERE email = %s;
            """
            
            c.execute(sql_query, (email,))
            user_data = c.fetchone()
            
            if user_data:
                # O fetchone retorna uma tupla. Para facilitar, mapeamos para um dicionário.
                
                # Campos na ordem do SELECT:
                fields = ['id', 'nome', 'senha_hash', 'assinante', 'ativo']
                
                return dict(zip(fields, user_data))
            else:
                return None # Usuário não encontrado

    except Exception as e:
        # print(f"ERRO DE BUSCA NO DB: {e}")
        return None
        
    finally:
        if conn:
            conn.close()        
if __name__ == "__main__":
    # Roda o servidor Flask na porta 5000
    app.run(port=5000, debug=True)
