from flask import Flask, request, jsonify, redirect, url_for
import os
import mercadopago
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import psycopg2 
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
        

        user_id_int = int(user_id) if isinstance(user_id, str) else user_id
        # Nota: Usamos %s para placeholders no psycopg2
        c.execute(sql_query, (value, user_id_int))
        conn.commit()
        
        success = c.rowcount > 0
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

@app.route("/ativar_conta", methods=["GET"])
def ativar_conta():
    """
    Recebe o token de ativação do e-mail, valida, atualiza o DB (ativo=1)
    e redireciona o usuário para o Streamlit.
    """
    token = request.args.get('token')
    
    # 1. Checa se o token existe
    if not token:
        return "Erro: Token de ativação ausente.", 400

    user_id = None
    try:
        # 2. Decodifica e valida o token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        
        if isinstance(user_id,str):
            user_id = int(user_id)

        if not user_id:
            return "Erro: Token inválido (ID de usuário ausente).", 400

    except jwt.ExpiredSignatureError:
        print(f"Erro: Token expirado para user_id: {user_id}")
        return "Erro: O link de ativação expirou. Por favor, registre-se novamente.", 401
    except jwt.InvalidTokenError as e:
        print(f"Erro: Token inválido: {e}")
        return "Erro: Token de ativação inválido.", 401
    except Exception as e:
        print(f"Erro inesperado na decodificação do JWT: {e}")
        return "Erro interno do servidor.", 500

    # 3. Atualiza o status de ativação no DB (ativo = 1)
    if update_user_status(user_id, 'ativo', 1):
        print(f"SUCESSO: Usuário ID {user_id} ativado via e-mail.")
        
        # 4. Redireciona para a tela de login do Streamlit (USANDO ENV VAR)
        if STREAMLIT_LOGIN_URL:
            # Redireciona para o Streamlit com o parâmetro 'activated'
            return redirect(f"{STREAMLIT_LOGIN_URL}?message=activated&user={user_id}", code=302)
        else:
            return "SUCESSO: Conta ativada. Por favor, acesse o seu aplicativo Streamlit e faça login.", 200
    else:
        # Se a atualização falhar (usuário não encontrado ou erro de DB)
        return "Erro: Falha ao ativar a conta no banco de dados.", 500


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



def enviar_email_ativacao_sendgrid(destinatario, nome_usuario, link_ativacao):
    """
    Função auxiliar para envio de e-mail. 
    Chame esta função no Streamlit após o registro.
    """
    if not CHAVE_API_SENDGRID:
        print("ERRO: CHAVE_API_SENDGRID não configurada para envio.")
        return False

    try:
        conta_sendgrid = SendGridAPIClient(CHAVE_API_SENDGRID)
        
        html_content = f"""
        <html>
          <body>
            <p>Olá, <strong>{nome_usuario}</strong>,</p>
            <p>Obrigado por se registrar! Para ativar sua conta e liberar o acesso, basta clicar no botão abaixo:</p>
            
            <p style="text-align: center;">
                <a href="{link_ativacao}" 
                    style="background-color: #4CAF50; 
                           color: white; 
                           padding: 10px 20px; 
                           text-decoration: none; 
                           border-radius: 5px; 
                           display: inline-block;">
                    ATIVAR MINHA CONTA
                </a>
            </p>
            
            <p>Se o botão não funcionar, copie e cole o seguinte link no seu navegador:</p>
            <p><small>{link_ativacao}</small></p>
            
            <p>Atenciosamente,<br>Equipe do Curso.</p>
          </body>
        </html>
        """

        email = Mail(from_email=EMAIL_REMETENTE, 
                     to_emails=destinatario,
                     subject='Ativação de Conta - Seu Curso de CNH',
                     html_content=html_content)

        resposta = conta_sendgrid.send(email)
        print(f"E-mail enviado. Status Code: {resposta.status_code}")
        return resposta.status_code in [200, 202]
        
    except Exception as e:
        print(f"ERRO ao enviar e-mail com SendGrid: {e}")
        return False


if __name__ == "__main__":
    # Roda o servidor Flask na porta 5000
    app.run(port=5000, debug=True)
