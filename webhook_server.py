from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase_client import supabase
from dotenv import load_dotenv
import os, bcrypt, jwt, datetime
import streamlit as st
import bcrypt
import os 
from dotenv import load_dotenv
import mercadopago
import secrets
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import sendgrid
from python_http_client.exceptions import BadRequestsError
from typing import Optional, Tuple




def get_secret(key, default=None):
    
    # 1. Tenta ler de st.secrets (para deploy no Streamlit Cloud)
    if 'secrets' in st.session_state and key in st.secrets:
        return st.secrets[key]
    # 2. Tenta ler de os.environ (para Codespace/Local com .env)
    return os.getenv(key, default)


MERCADO_PAGO_ACCESS_TOKEN = get_secret('MERCADO_PAGO_ACCESS_TOKEN')
REFERENCIA_ASSINATURA = get_secret('REFERENCIA_ASSINATURA')

VALOR_ASSINATURA = get_secret('VALOR_ASSINATURA') 
TITULO_ASSINATURA = "Assinatura Premium do Curso de Python"

CHAVE_API_SENDGRID = get_secret('CHAVE_API_SENDGRID')
EMAIL_REMETENTE =  get_secret('EMAIL_REMETENTE')
TOKEN_LENGTH_BYTES= int(get_secret('TOKEN_LENGTH_BYTES'))
TOKEN_EXPIRATION_HOURS= get_secret('TOKEN_EXPIRATION_HOURS')

URL_BASE_ATIVACAO = get_secret("URL_BASE_ATIVACAO") 
MP_ACCESS_TOKEN = get_secret('MP_ACCESS_TOKEN')
MP_NOTIFICATION_URL = get_secret('MP_NOTIFICATION_URL')
URL_API_ATIVACAO =get_secret('URL_API_ATIVACAO')
URL_API_AUTH = get_secret("URL_API_AUTH")
URL_CURSO = get_secret("URL_CURSO")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


# Carrega variáveis de ambiente
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
DB_TABLE_NAME = 'usuarios' 
app = Flask(__name__)
CORS(app)

def hash_senha(senha: str) -> str:
    """Gera o hash da senha usando bcrypt."""
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def buscar_usuario(email: str) -> Optional[Tuple[int, str, str, int, int, Optional[str]]]:

    try:
        response = supabase.table('usuarios').select(
            'id, nome, senha_hash, assinante, ativo, token_ativacao'
        ).eq('email', email).limit(1).execute()
        
        data = response.data
        
        if data:
            user_dict = data[0]
            user_data_tuple = (
                user_dict['id'],
                user_dict['nome'],
                user_dict['senha_hash'],
                user_dict['assinante'],
                user_dict['ativo'],
                user_dict.get('token_ativacao')
            )
            return user_data_tuple
        else:
            return None
            
    except Exception as e:
        print(f"ERRO SUPABASE em buscar_usuario: {e}") 
        return None


# ------------------------------------------------------
# 📌 ROTA /auth → cadastro e login no mesmo endpoint
# ------------------------------------------------------

def get_reset_token(email: str) -> str:
    """
    Gera um token de redefinição único, armazena no Supabase e retorna.
    O Supabase deve ter os campos 'token_reset' e 'token_expiracao'.
    """
    token = secrets.token_urlsafe(TOKEN_LENGTH_BYTES)
    
    # Calcula a expiração como timestamp UTC
    exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=int(TOKEN_EXPIRATION_HOURS))
    # Formato ISO string para o Supabase
    exp_iso = exp_time.isoformat().replace('+00:00', 'Z')
    
    try:
        # Atualiza o usuário no Supabase
        response = supabase_service.table(DB_TABLE_NAME) \
            .update({'token_reset': token, 'token_expiracao': exp_iso}) \
            .eq('email', email) \
            .execute()
            
        if response.data:
            print(f"Token de reset gerado e salvo para: {email}")
            return token
        
    except Exception as e:
        print(f"ERRO SUPABASE ao salvar token de reset: {e}")
    
    return ""

def verify_reset_token(token: str) -> Optional[str]:

    try:
        response = supabase.table(DB_TABLE_NAME).select(
            'email, token_expiracao'
        ).eq('token_reset', token).limit(1).execute()
        
        user_data = response.data
        
        if not user_data:
            return None 
        
        user = user_data[0]
        
        # Verifica a expiração
        exp_iso_str = user['token_expiracao']
        if not exp_iso_str:
            return None 
            
        # Converte a string ISO para objeto datetime (UTC)
        exp_time = datetime.datetime.fromisoformat(exp_iso_str.replace('Z', '+00:00'))
        
        if exp_time < datetime.datetime.now(datetime.timezone.utc):
            print(f"AVISO: Token expirado para o usuário {user['email']}")
            return None
            
        return user['email']
        
    except Exception as e:
        print(f"ERRO SUPABASE ao verificar token: {e}")
        return None
    
def update_user_password_hash(email: str, new_hash: str) -> bool:

    try:
        # Usa o cliente de serviço para garantir que a atualização funcione
        response = supabase_service.table(DB_TABLE_NAME) \
            .update({'senha_hash': new_hash, 'token_reset': None, 'token_expiracao': None}) \
            .eq('email', email) \
            .execute()
        
        if response.data:
            print(f"Senha de {email} atualizada com sucesso.")
            return True
        return False
        
    except Exception as e:
        print(f"ERRO SUPABASE ao atualizar senha: {e}")
        return False
    
def send_reset_email(destinatario: str, nome_usuario: str, token: str) -> int:

    link_redefinicao = f"{URL_BASE_ATIVACAO}/rec_senha?token={token}"
    
    email_html = f"""
    <html>
    <body>
        <h1 style="color: #ffc107; text-align: center;">🔒 Redefinição de Senha</h1>

        <p>Olá, <strong>{nome_usuario}</strong>,</p>

        <p>
            Recebemos uma solicitação para redefinir a senha da sua conta.
            Se você não solicitou essa alteração, pode ignorar este e-mail com segurança.
        </p>
        
        <p>Para criar uma nova senha, clique no botão abaixo. Este link é válido por {TOKEN_EXPIRATION_HOURS} horas:</p>
        
        <p style="text-align: center;">
            <a href="{link_redefinicao}" 
                style="background-color: #ffc107; 
                        color: #333; 
                        padding: 12px 25px; 
                        text-decoration: none; 
                        border-radius: 5px; 
                        display: inline-block;
                        font-weight: bold;">
                REDEFINIR MINHA SENHA AGORA
            </a>
        </p>
        
        <p style="margin-top: 20px;">Se o botão não funcionar, copie e cole o seguinte link no seu navegador:</p>
        <p><small><a href="{link_redefinicao}">{link_redefinicao}</a></small></p>
        
        <p>
            Em caso de dúvidas, entre em contato com o suporte.
        </p>
        
        <p>Atenciosamente,<br>A Equipe do Curso.</p>
    </body>
    </html> 
    """
    
    email = Mail(
        from_email=EMAIL_REMETENTE,
        to_emails=destinatario,
        subject='[Seu Curso] Link para Redefinir sua Senha',
        html_content=email_html
    )

    try:
        conta_sendgrid = SendGridAPIClient(CHAVE_API_SENDGRID)
        response = conta_sendgrid.send(email)
        
        print(f"DEBUG: Email de reset enviado. Status Code: {response.status_code}")
        # Se for 202, significa que o SendGrid aceitou.
        return response.status_code

    except BadRequestsError as e:
        # Tratamento de erro específico do SendGrid 400 ou 403
        print("--- ERRO FATAL DO SENDGRID (BadRequestsError) ---")
        print(f"Status Code: {e.status_code}")
        try:
            error_details = e.response.text 
            print(f"Detalhes do Erro da API: {error_details}")
            st.error(f"Falha no envio do e-mail de redefinição. Status: {e.status_code}. Detalhes no console.")
        except Exception as body_e:
            print(f"Erro ao obter o corpo da resposta: {body_e}")
            st.error(f"Falha no envio do e-mail de redefinição. Status: {e.status_code}.")
            
        print("--------------------------------------------------")
        return e.status_code
        
    except Exception as e:
        print(f"🚨 ERRO INESPERADO NO ENVIO: {e}")
        st.error(f"Erro inesperado no envio de email: {e}")
        return 500

@app.route("/forgot_password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"message": "O e-mail é obrigatório."}), 400

    # Busca o usuário usando o cliente normal
    user_response = supabase.table("usuarios").select("nome").eq("email", email).execute()
    
    response_success = jsonify({"message": "Se o e-mail estiver em nosso sistema, enviaremos um link de redefinição."}), 200
    
    if not user_response.data:
        print(f"AVISO: Tentativa de redefinição de senha para e-mail não encontrado: {email}")
        return response_success 

    nome_usuario = user_response.data[0]["nome"]
    
    # 1. Gera o token e armazena no DB
    reset_token = get_reset_token(email)
    
    if not reset_token:
        print(f"ERRO: Falha ao gerar e salvar o token de reset para {email}.")
        return jsonify({"message": "Erro interno ao gerar token."}), 500
        
    # Envia o e-mail
    send_status = send_reset_email(email, nome_usuario, reset_token)
    
    if send_status >= 400:
        print(f"ERRO: Falha ao enviar e-mail de reset para {email}. Status: {send_status}")
        return response_success

    return response_success

@app.route("/reset_password", methods=["POST"])
def reset_password():
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("new_password")

    if not token or not new_password:
        return jsonify({"message": "O token e a nova senha são obrigatórios."}), 400

    # Verifica a validade do token
    email_do_usuario = verify_reset_token(token)
    
    if not email_do_usuario:
        return jsonify({"message": "Token inválido ou expirado."}), 400
        
    # Gera o novo hash da senha
    new_hash = hash_senha(new_password)
    
    # 3. Atualiza o hash e limpa o token
    if update_user_password_hash(email_do_usuario, new_hash):
        return jsonify({"message": "Senha atualizada com sucesso!"}), 200
    else:
        return jsonify({"message": "Erro ao atualizar a senha no banco de dados."}), 500

@app.route("/auth", methods=["POST"])
def login():
    data = request.get_json()
    action = data.get("action")

    if action == "CADASTRO":
        nome = data.get("nome")
        email = data.get("email")
        senha = data.get("senha")
        cpf = data.get("cpf") 

        # CORREÇÃO 1: Incluir 'cpf' na verificação de campos obrigatórios
        if not all([nome, email, senha, cpf]):
            return jsonify({"message": "Todos os campos (nome, email, senha, cpf) são obrigatórios"}), 400

        # Verifica se o e-mail já existe
        existing_email = supabase.table("usuarios").select("*").eq("email", email).execute()
        if existing_email.data:
            return jsonify({"message": "E-mail já cadastrado"}), 409

        # Verifica se o CPF já existe
        existing_cpf = supabase.table("usuarios").select("*").eq("cpf", cpf).execute()
        if existing_cpf.data:
            return jsonify({"message": "CPF já cadastrado"}), 409

        # Criptografa a senha
        senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Cria usuário
        try:
            supabase.table("usuarios").insert({
                "nome": nome,
                "email": email,
                "senha_hash": senha_hash,
                "ativo": 1,
                "assinante": 0,
                "cpf": cpf 
            }).execute()
        except Exception as e:
            return jsonify({"message": f"Erro ao inserir usuário no banco de dados."}), 500
        
        enviar_email_ativacao_sendgrid(email, nome)


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


def enviar_email_ativacao_sendgrid(destinatario: str, nome_usuario: str) -> int:

    email = Mail(
        from_email=EMAIL_REMETENTE,
        to_emails=destinatario,
        subject='Felicitações de boas vindas - Seu Curso de CNH',
        html_content=f"""
        <html>
    <body>
        <h1 style="color: #007bff; text-align: center;">🎉 Bem-vindo(a) à Família do Curso!</h1>

        <p>Olá, <strong>{nome_usuario}</strong>,</p>

        <p>
            Sua jornada para a aprovação no exame teórico acaba de começar! Estamos muito animados por ter você conosco.
            Seu cadastro foi realizado com sucesso.
        </p>
        
        <p>Para ativar sua conta e liberar imediatamente seu acesso à plataforma de estudos, basta clicar no botão abaixo:</p>
        
        <p style="text-align: center;">
            <a href="{URL_CURSO}" 
               style="background-color: #4CAF50; 
                      color: white; 
                      padding: 10px 20px; 
                      text-decoration: none; 
                      border-radius: 5px; 
                      display: inline-block;
                      font-weight: bold;">
                ACESSAR AGORA E ATIVAR MINHA CONTA
            </a>
        </p>
        
        <p style="margin-top: 20px;">Se o botão não funcionar (alguns clientes de e-mail bloqueiam botões), copie e cole o seguinte link no seu navegador:</p>
        <p><small><a href="{URL_CURSO}">{URL_CURSO}</a></small></p>
        
        <p>
            Em caso de dúvidas ou problemas com o acesso, nossa equipe de suporte está à disposição.
        </p>
        
        <p>Bons estudos!<br>Atenciosamente,<br>A Equipe do Curso.</p>
    </body>
</html>   """
 )
    
    
    try:
       
        # Inicializa o cliente SendGrid e envia o email
        conta_sendgrid = sendgrid.SendGridAPIClient(CHAVE_API_SENDGRID)
       
        response = conta_sendgrid.send(email)
        # Imprime o status de sucesso para o log
        print(f"E-mail enviado com sucesso. Status: {response.status_code}")
        
        # Retorna o status code
        return response.status_code

    except BadRequestsError as e:
        print("--- ERRO FATAL DO SENDGRID (BadRequestsError) ---")
        
        print(f"Status Code: {e.status_code}")
        
        try:

            error_details = e.response.text 
            print(f"Detalhes do Erro da API: {error_details}")
        except Exception as body_e:
            print(f"Erro ao obter o corpo da resposta: {body_e}")
            
        print("--------------------------------------------------")
        return e.status_code


from supabase_client import create_client, Client
supabase_service = create_client(SUPABASE_URL, SUPABASE_KEY)
def atualizar_assinante_supabase(user_id_or_email) -> bool:
    """
    Atualiza o campo 'assinante' para True no Supabase pelo email, 
    usando o cliente de serviço (Service Role Key) para ignorar as RLS.
    """
    
    TABELA_USUARIOS = 'usuarios' 
    
    # LOG DE DEBUG ADICIONADO
    print(f"DEBUG: Tentando atualizar o usuário com email: {user_id_or_email}")
    
    try:
        # CORREÇÃO APLICADA: 'assinante' agora recebe o inteiro 1 
        response = supabase_service.table(TABELA_USUARIOS) \
            .update({'assinante': 1}) \
            .eq('email', user_id_or_email) \
            .execute()
        
        # O Supabase retorna uma resposta complexa. Verifica se houve linhas afetadas.
        if response.data and len(response.data) > 0:
            print(f"SUCESSO: Usuário {user_id_or_email} atualizado no Supabase (Service Key).")
            return True
        else:
            print(f"AVISO: Usuário {user_id_or_email} não encontrado na tabela '{TABELA_USUARIOS}'. Resposta Supabase: {response.data}")
            return False

    except Exception as e:
        print(f"ERRO SUPABASE: Falha ao atualizar assinante {user_id_or_email}. Erro: {e}")
        return False


@app.route('/mercadopago_webhook', methods=['POST'])
def mercadopago_webhook():
    try:
        data_payload = request.get_json()
        
        # Validação básica
        topic = data_payload.get('topic')
        resource_url = data_payload.get('resource') 

        if not topic or not resource_url:
            return jsonify({"status": "error", "message": "Payload inválido"}), 400

        # O Mercado Pago geralmente envia a URL completa
        if topic == 'payment':
            payment_id = resource_url.split('/')[-1]
        elif topic == 'merchant_order':
            return jsonify({"status": "ignored", "message": "Tipo merchant_order ignorado"}), 200
        else:
            return jsonify({"status": "ignored", "message": f"Tipo {topic} não processado"}), 200

        # BUSCA OS DETALHES DO PAGAMENTO NA API DO MP
        sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
        payment_info = sdk.payment().get(payment_id)
        
        if payment_info["status"] != 200:
            print(f"ERRO MP: Falha ao buscar pagamento {payment_id}. Status: {payment_info['status']}")
            return jsonify({"status": "error", "message": "Falha ao consultar MP"}), 500

        payment = payment_info["response"]
        status = payment.get("status")
        external_reference = payment.get("external_reference") 

        # VERIFICAÇÃO DE APROVAÇÃO E ATUALIZAÇÃO
        if status == 'approved':
            # Extrai o ID do usuário/email (baseado na sua estrutura: REF-{user_id_ref}-{uuid.uuid4()})
            try:
                # Pega a segunda parte, que é o email
                user_id_or_email = external_reference.split('-')[1] 
            except IndexError:
                print(f"ERRO MP: external_reference mal formatado: {external_reference}")
                return jsonify({"status": "error", "message": "Referência externa inválida"}), 400
            
            # Chama a função que altera o Supabase
            if atualizar_assinante_supabase(user_id_or_email):
                return jsonify({"status": "success", "message": "Assinante atualizado"}), 200
            else:
                # Logou o erro no Supabase, mas retorna 200 para o MP não tentar de novo
                return jsonify({"status": "warning", "message": "Falha ao atualizar Supabase"}), 200
        
        # Retorna 200 para o MP em caso de status não-aprovado (pendente, rejeitado)
        return jsonify({"status": "ignored", "message": f"Pagamento não aprovado. Status: {status}"}), 200

    except Exception as e:
        # Erro geral (importante para evitar loop de retentativa do MP)
        print(f"ERRO FATAL no Webhook: {e}")
        return jsonify({"status": "error", "message": "Erro interno do servidor"}), 500

if __name__ == "__main__":
    app.run(debug=True)