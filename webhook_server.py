# from flask import Flask, request, jsonify, redirect, url_for
# from flask_cors import CORS # NOVO: Importa a extensão CORS
# import os
# import mercadopago
# import jwt
# from datetime import datetime, timedelta, timezone 
# from dotenv import load_dotenv
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
# import psycopg2 
# from python_http_client.exceptions import HTTPError
# import bcrypt


# # Carrega variáveis do arquivo .env (se existir)
# load_dotenv() 

# # --- Configuração do Flask ---
# app = Flask(__name__)
# CORS(app)

# # --- Configuração do Banco de Dados e Variáveis de Ambiente ---
# DB_NAME = os.getenv('DB_NAME')
# MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
# MP_NOTIFICATION_URL = os.getenv("MP_NOTIFICATION_URL")
# CHAVE_API_SENDGRID = os.getenv('CHAVE_API_SENDGRID')
# JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
# # NOTA: URL_BASE_ATIVACAO e ACTIVATION_EXPIRATION_DAYS não são mais usados no novo fluxo.
# URL_BASE_ATIVACAO = os.getenv('URL_BASE_ATIVACAO') 
# DATABASE_URL = os.getenv("DATABASE_URL")
# EMAIL_REMETENTE = os.getenv('EMAIL_REMETENTE')

# # NOVO ENV VAR: URL para onde o usuário será redirecionado após a ativação por e-mail
# STREAMLIT_LOGIN_URL = os.getenv('STREAMLIT_LOGIN_URL')


# if not MP_ACCESS_TOKEN:
#     print("ERRO: MP_ACCESS_TOKEN não configurado no ambiente.")
#     sdk = None # Define sdk como None para evitar erro
# else:
#     sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

# def get_db_connection():
#     """Conecta ao PostgreSQL usando a URL de ambiente."""
#     if not DATABASE_URL:
#         # Se a variável de ambiente não estiver configurada, lança um erro para avisar
#         raise ConnectionError("DATABASE_URL não está configurada.")
    
#     # Adiciona ?sslmode=require para compatibilidade com a maioria dos hosts em nuvem (ex: Heroku/Railway)
#     return psycopg2.connect(DATABASE_URL + "?sslmode=require")


# def update_user_status(user_id, field_name, value):
#     """Função genérica para atualizar um campo (assinante/ativo) no DB (PostgreSQL)."""
#     conn = None
#     try:
#         conn = get_db_connection()
#         c = conn.cursor()
        
#         if field_name not in ['assinante', 'ativo']:
#             raise ValueError("Nome do campo de atualização inválido.")
            
#         sql_query = f"UPDATE usuarios SET {field_name} = %s WHERE id = %s"
#         print(f"DEBUG DB: Tentando executar UPDATE no campo {field_name} para ID {user_id} com valor {value}")

#         user_id_int = int(user_id) if isinstance(user_id, str) else user_id
#         c.execute(sql_query, (value, user_id_int))
#         conn.commit()
        
#         success = c.rowcount > 0
#         print(f"DEBUG DB: Linhas afetadas: {c.rowcount}. Sucesso: {success}")
 
#         c.close()
#         return success

#     except Exception as e:
#         print(f"ERRO CRÍTICO AO ATUALIZAR DB ({field_name}): {e}")
#         if conn:
#             conn.rollback()
#         return False
        
#     finally:
#         if conn:
#             conn.close()


# def hash_senha(senha):
#     """Gera o hash BCrypt da senha."""
#     senha_bytes = senha.encode('utf-8')
#     return bcrypt.hashpw(senha_bytes, bcrypt.gensalt())


# def verificar_senha(senha_digitada, senha_hash_salva):
#     """Verifica se a senha digitada corresponde ao hash salvo."""
#     senha_digitada_bytes = senha_digitada.encode('utf-8')
#     # Converte o hash salvo para bytes se for uma string (comum em DBs)
#     if isinstance(senha_hash_salva, str):
#         senha_hash_salva = senha_hash_salva.encode('utf-8')
    
#     # Adiciona um try/except para lidar com hashes inválidos/não-bcrypt
#     try:
#         return bcrypt.checkpw(senha_digitada_bytes, senha_hash_salva)
#     except ValueError:
#         print("AVISO: Hash de senha salvo parece ser inválido.")
#         return False


# def buscar_usuario_com_dados_completos(email):
#     """
#     Busca um usuário pelo email no DB (PostgreSQL) e retorna todos os dados necessários.
#     """
#     conn = None
#     try:
#         conn = get_db_connection()
#     except Exception as e:
#         print(f"ERRO DE CONEXÃO: {e}")
#         return None # Falha na conexão

#     try:
#         with conn.cursor() as c:
#             # SQL: Seleciona todos os campos necessários para o login e a sessão
#             sql_query = """
#                 SELECT id, nome, senha_hash, assinante, ativo 
#                 FROM usuarios 
#                 WHERE email = %s;
#             """
            
#             c.execute(sql_query, (email,))
#             user_data = c.fetchone()
            
#             if user_data:
#                 # O fetchone retorna uma tupla. Mapeamos para um dicionário.
#                 fields = ['id', 'nome', 'senha_hash', 'assinante', 'ativo']
#                 return dict(zip(fields, user_data))
#             else:
#                 return None # Usuário não encontrado

#     except Exception as e:
#         print(f"ERRO DE BUSCA NO DB: {e}")
#         return None
        
#     finally:
#         if conn:
#             conn.close() 


# def cadastrar_usuario(cpf, email, nome, senha, assinante, ativo=0):
#     """
#     Cadastra um novo usuário no DB (PostgreSQL/Supabase).
#     """
#     conn = None
#     try:
#         conn = get_db_connection() 
#         c = conn.cursor()
#         hashed_password = hash_senha(senha)
        
#         # SQL: Insere os dados básicos. Assinante e Ativo são opcionais, mas padrão 0.
#         sql_query = """
#             INSERT INTO usuarios (cpf, email, nome, senha_hash, assinante, ativo)
#             VALUES (%s, %s, %s, %s, %s, %s)
#             RETURNING id, nome; 
#         """
        
#         c.execute(
#             sql_query,
#             (cpf, email, nome, hashed_password, assinante, ativo)
#         )
        
#         user_id, nome_retornado = c.fetchone()
        
#         conn.commit()
#         c.close()
        
#         return user_id, nome_retornado 

#     except psycopg2.errors.UniqueViolation as e:
#         print(f"ERRO DE CADASTRO - VIOLAÇÃO DE UNICIDADE (Email ou CPF já existe): {e}")
#         if conn:
#             conn.rollback()
#         return False, None
        
#     except Exception as e:
#         print(f"ERRO DE CADASTRO NO DB: {e}") 
#         if conn:
#             conn.rollback()
#         return False, None
        
#     finally:
#         if conn:
#             conn.close()


# def enviar_email_boas_vindas_sendgrid(destinatario: str, nome_usuario: str) -> int:
#     """
#     Envia um email de boas-vindas (confirmação de cadastro) usando o SendGrid.
#     Retorna o código de status HTTP (200, 202 em sucesso) ou o código de erro.
#     """
#     api_key = CHAVE_API_SENDGRID
#     remetente = EMAIL_REMETENTE

#     if not api_key:
#         print("ERRO: CHAVE_API_SENDGRID não definida.")
#         return 500
#     if not remetente:
#         print("ERRO: EMAIL_REMETENTE não definido.")
#         return 500

#     # O link de login é usado diretamente aqui, pois o usuário já está ativo
#     login_url = os.getenv('STREAMLIT_LOGIN_URL', 'https://seum.app.com/login') 
    
#     # 1. Conteúdo em Texto Simples (Melhora a entregabilidade)
#     email_text = f"""
#     Olá, {nome_usuario},
    
#     Obrigado por se registrar! Bem-vindo(a) à Plataforma! Seu Cadastro foi Concluído.
    
#     Para acessar sua conta: {login_url}
    
#     Atenciosamente,
#     Equipe do Curso.
#     """
    
#     # 2. Conteúdo HTML
#     email_html = f"""
#     <html>
#         <body>
#             <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
#                 <h2 style="color: #007bff;">Olá, **{nome_usuario}**!</h2>
                
#                 <p>Ficamos muito felizes em ter você a bordo. Seu cadastro foi concluído com sucesso e você já pode acessar todo o nosso conteúdo exclusivo na plataforma.</p>
                
#                 <p>Para começar, basta clicar no botão abaixo e usar seu e-mail e senha cadastrados:</p>
                
#                 <a href="{login_url}" style="padding: 12px 25px; background-color: #007bff; color: white; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold; margin: 15px 0;">
#                     Acessar Minha Conta
#                 </a>
                
#                 <p style="margin-top: 20px; color: #555;">Se tiver qualquer dúvida, é só nos responder a este e-mail!</p>
#                 <p style="font-size: 0.9em; color: #888;">Atenciosamente,<br>A Equipe de Suporte</p>
#             </div>
#         </body>
#     </html>
#     """
    
#     email = Mail(
#         from_email=remetente,
#         to_emails=destinatario,
#         subject='Boas-vindas - Seu Curso de CNH',
#         html_content=email_html,
#         plain_text_content=email_text
#     )

#     # 3. Tratamento de Erros
#     try:
#         conta_sendgrid = SendGridAPIClient(api_key)
#         resposta = conta_sendgrid.send(email)
#         print(f"Email enviado. Status Code: {resposta.status_code}")
#         return resposta.status_code
#     except HTTPError as e:
#         print(f"Erro ao enviar email (Status {e.status_code}): {e.body}")
#         return e.status_code 
#     except Exception as e:
#         print(f"Erro inesperado no envio de email: {e}")
#         return 500


# @app.route("/auth", methods=["POST"])
# def auth_handler():
#     """
#     Trata requisições POST para Login ou Cadastro, dependendo do campo 'action'.
#     """
#     data = request.get_json()
#     action = data.get('action') # 'CADASTRO' ou 'LOGIN'
    
#     if not action:
#         return jsonify({"message": "Ação não especificada."}), 400

#     # LÓGICA DE CADASTRO
#     if action == "CADASTRO":
#         # 1. Extrair dados do payload
#         cpf = data.get('cpf')
#         email = data.get('email')
#         nome = data.get('nome')
#         senha = data.get('senha')
#         # Assume 0 para assinante no cadastro inicial
#         assinante = 0 
        
#         if not all([cpf, email, nome, senha]):
#             return jsonify({"message": "Campos obrigatórios ausentes."}), 400

#         # 2. Chamar a função de DB e obter ID/Nome. ATIVO = 1 para login imediato
#         user_id, nome_usuario = cadastrar_usuario(cpf, email, nome, senha, assinante, ativo=1) 
        
#         if user_id:
#             try:
#                 # 3. Enviar o e-mail de boas-vindas
#                 enviar_email_boas_vindas_sendgrid(email, nome_usuario) 
#                 print(f"DEBUG: E-mail de boas-vindas enviado para {email}")
#             except Exception as e:
#                 print(f"ERRO: Falha ao enviar e-mail de boas-vindas: {e}") 
            
#             # Retorna sucesso e os dados básicos para a sessão
#             return jsonify({
#                 "message": "Cadastro realizado com sucesso!",
#                 "user_data": {
#                     "user_id": user_id,
#                     "nome": nome_usuario,
#                     "assinante": assinante 
#                 }
#             }), 201
#         else:
#             # Erro de integridade (Email/CPF já existe)
#             return jsonify({"message": "Este e-mail ou CPF já está cadastrado."}), 409
    
#     # LÓGICA DE LOGIN
#     elif action == "LOGIN":
#         email = data.get('email')
#         senha = data.get('senha')
        
#         if not all([email, senha]):
#             return jsonify({"message": "Email e senha são obrigatórios para login."}), 400
            
#         # 1. Buscar usuário no DB
#         user_data = buscar_usuario_com_dados_completos(email) 
        
#         if user_data and verificar_senha(senha, user_data['senha_hash']):
            
#             # CRÍTICO: Verifica se o usuário está ativo, embora o novo fluxo use ativo=1.
#             # Mantemos a verificação para compatibilidade ou futuros ajustes de fluxo.
#             if user_data['ativo'] != 1:
#                 return jsonify({"message": "Conta inativa. Por favor, verifique seu e-mail para ativar."}), 403

#             # 2. Retornar dados completos do usuário logado
#             return jsonify({
#                 "message": "Login bem-sucedido",
#                 "user_data": {
#                     "user_id": user_data['id'],
#                     "nome": user_data['nome'],
#                     "assinante": user_data['assinante']
#                 }
#             }), 200
#         else:
#             return jsonify({"message": "Email ou senha incorretos."}), 401
        
#     else:
#         return jsonify({"message": "Ação desconhecida."}), 400


# @app.route("/mercadopago_webhook", methods=["POST"])
# def mercadopago_webhook():
#     """Endpoint para receber as notificações (Webhooks) do Mercado Pago."""
    
#     data = request.json
    
#     if data is None:
#         return jsonify({"message": "Nenhum dado recebido."}), 400

#     topic = data.get("topic") or data.get("type")
    
#     # Processa apenas notificações de pagamento
#     if topic != "payment":
#         return jsonify({"message": f"Tópico ignorado: {topic}"}), 200

#     # Obtém o ID do pagamento da notificação
#     payment_id = data.get("id") or data.get("data", {}).get("id")

#     if not payment_id:
#         return jsonify({"message": "ID do pagamento ausente."}), 400
    
#     print(f"Webhook recebido para Pagamento ID: {payment_id}")

#     try:
#         # 1. Busca os detalhes completos do pagamento na API do MP
#         if sdk is None:
#              print("ERRO: SDK do Mercado Pago não inicializado.")
#              return jsonify({"message": "Serviço MP indisponível"}), 503
             
#         payment_response = sdk.payment().get(payment_id)
#         payment = payment_response["response"]

#         status = payment.get("status")
#         external_reference = payment.get("external_reference")

#         print(f"Status: {status} | Ref: {external_reference}")

#         # 2. Verifica aprovação
#         if status == "approved":
            
#             # Formato esperado da referência: REF-{user_id}-{uuid}
#             if not external_reference or len(external_reference.split("-")) < 2:
#                 print("ERRO: External reference inválida.")
#                 return jsonify({"message": "External reference inválida."}), 400

#             try:
#                 # Extrai o ID do usuário
#                 user_id_str = external_reference.split("-")[1]
#                 user_id = int(user_id_str)
#             except ValueError:
#                 print("ERRO: ID do usuário na referência não é numérico.")
#                 return jsonify({"message": "ID do usuário inválido na referência."}), 400

#             # 3. Atualiza o status do usuário no DB
#             if update_user_status(user_id, 'assinante', 1):
#                 print(f"SUCESSO: Usuário ID {user_id} atualizado para assinante.")
#                 return jsonify({"message": "Status de assinante atualizado."}), 200
#             else:
#                 return jsonify({"message": "Erro ao atualizar DB."}), 500
        
#         else:
#             # Pagamento não aprovado, apenas registra e retorna 200 para o MP
#             print(f"Pagamento não aprovado: {status}")
#             return jsonify({"message": f"Pagamento com status: {status}"}), 200

#     except Exception as e:
#         print(f"Erro ao processar pagamento: {e}")
#         # Retorna 500 para o Mercado Pago tentar re-enviar
#         return jsonify({"message": f"Erro interno no processamento do webhook: {e}"}), 500


# if __name__ == "__main__":
#     # Roda o servidor Flask na porta 5000
#     # NOTA: Em produção (ex: Railway), você deve usar o PORT fornecido pelo ambiente
#     app.run(port=5000, debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase_client import supabase
from dotenv import load_dotenv
import os, bcrypt, jwt, datetime

# Carrega variáveis de ambiente
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

app = Flask(__name__)
CORS(app)

# ------------------------------------------------------
# 📌 ROTA /auth → cadastro e login no mesmo endpoint
# ------------------------------------------------------
@app.route("/auth", methods=["POST"])
def login():
    data = request.get_json()
    action = data.get("action")

    if action == "CADASTRO":
        nome = data.get("nome")
        email = data.get("email")
        senha = data.get("senha")

        if not all([nome, email, senha]):
            return jsonify({"message": "Todos os campos são obrigatórios"}), 400

        # Verifica se o e-mail já existe
        existing = supabase.table("usuarios").select("*").eq("email", email).execute()
        if existing.data:
            return jsonify({"message": "E-mail já cadastrado"}), 409

        # Criptografa a senha
        senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Cria usuário
        try:
            supabase.table("usuarios").insert({
                "nome": nome,
                "email": email,
                "senha_hash": senha_hash,
                "ativo": 1,
                "assinante": 0
            }).execute()
        except Exception as e:
            return jsonify({"message": f"Erro ao inserir usuário: {e}"}), 500

        # Gera token JWT
        token = jwt.encode(
            {
                "email": email,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            },
            SECRET_KEY,
            algorithm="HS256"
        )

        return jsonify({
            "message": "Cadastro realizado com sucesso",
            "token": token,
            "email": email,
            "nome": nome
        }), 201

    elif action == "LOGIN":
        email = data.get("email")
        senha = data.get("senha")

        if not email or not senha:
            return jsonify({"message": "E-mail e senha são obrigatórios"}), 400

        # Busca usuário no Supabase
        user = supabase.table("usuarios").select("*").eq("email", email).execute()
        if not user.data:
            return jsonify({"message": "Usuário não encontrado"}), 404

        user_data = user.data[0]

        # Verifica se está ativo
        if user_data["ativo"] != 1:
            return jsonify({"message": "Conta inativa. Entre em contato com o suporte."}), 403

        # Confere a senha
        senha_hash = user_data["senha_hash"].encode("utf-8")
        if not bcrypt.checkpw(senha.encode("utf-8"), senha_hash):
            return jsonify({"message": "Senha incorreta"}), 401

        # Cria token JWT
        token = jwt.encode(
            {
                "email": email,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            },
            SECRET_KEY,
            algorithm="HS256"
        )

        return jsonify({
            "message": "Login realizado com sucesso",
            "token": token,
            "email": user_data["email"],
            "nome": user_data["nome"],
            "assinante": user_data["assinante"]
        }), 200

    else:
        return jsonify({"message": "Ação inválida"}), 400




# ------------------------------------------------------
# 🔒 ROTA TESTE - EXIGE TOKEN (opcional)
# ------------------------------------------------------
@app.route("/perfil", methods=["GET"])
def perfil():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"message": "Token não fornecido"}), 401

    try:
        dados = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = dados["email"]
        user = supabase.table("usuarios").select("id,nome,email,assinante").eq("email", email).execute()

        if not user.data:
            return jsonify({"message": "Usuário não encontrado"}), 404

        return jsonify({"perfil": user.data[0]})
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Token inválido"}), 401

def send_welcome_email_sendgrid(recipient_email, recipient_name):
    """
    Envia um email HTML de boas-vindas usando o SDK do SendGrid.
    """
    if not SENDGRID_API_KEY or not SENDER_EMAIL:
        print("Erro: A chave de API ou o e-mail remetente do SendGrid estão ausentes.")
        return False
        
    try:
        # Conteúdo HTML da mensagem
        html_content = f"""
        <html>
            <body>
                <h2 style="color: #007bff;">🎉 Olá, {recipient_name}!</h2>
                <p>Obrigado por se juntar à nossa comunidade.</p>
                <p>Seu cadastro foi concluído com sucesso. Você já pode acessar:</p>
                <ul>
                    <li><strong>Email:</strong> {recipient_email}</li>
                    <li><strong>Link para login:</strong> <a href="https://seu-app-streamlit.com/Home">Clique aqui para começar!</a></li>
                </ul>
                <p>Em caso de dúvidas, não hesite em nos contatar.</p>
                <p>Atenciosamente,<br>A Equipe do Curso</p>
            </body>
        </html>
        """
        
        # Cria o objeto Mail
        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=recipient_email,
            subject='🎉 Bem-vindo(a) à Plataforma do Curso!',
            html_content=html_content
        )
        
        # Inicializa o cliente SendGrid e envia o email
        sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.client.mail.send.post(request_body=message.get())
        
        # Verifica se a API do SendGrid aceitou o envio (status 200 ou 202)
        if response.status_code in [200, 202]:
            print(f"E-mail de boas-vindas enviado com sucesso para {recipient_email}.")
            # Se você quiser mais debug: print(response.body, response.headers)
            return True
        else:
            print(f"Falha na API do SendGrid (Status {response.status_code}): {response.body}")
            return False

    except Exception as e:
        print(f"Erro inesperado durante o envio com SendGrid: {e}")
        return False

if __name__ == "__main__":
    app.run(debug=True)