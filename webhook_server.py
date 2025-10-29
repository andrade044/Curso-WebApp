
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase_client import supabase
from dotenv import load_dotenv
import os, bcrypt, jwt, datetime

import streamlit as st
import sqlite3
import re
import bcrypt
import os 
from dotenv import load_dotenv
import random
import mercadopago
import uuid
import secrets
import time
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
# from api_mercadopago import api_pagamento
from data import SIMULADO_DATA
import requests
import sendgrid
from auth import verifica_login, verifica_assinante, logout
from python_http_client.exceptions import BadRequestsError



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
TOKEN_LENGTH_BYTES= get_secret('TOKEN_LENGTH_BYTES')
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
        cpf = data.get("cpf") # OK: Coletando o novo campo

        # CORREÇÃO 1: Incluir 'cpf' na verificação de campos obrigatórios
        if not all([nome, email, senha, cpf]):
            return jsonify({"message": "Todos os campos (nome, email, senha, cpf) são obrigatórios"}), 400

        # Verifica se o e-mail já existe
        existing_email = supabase.table("usuarios").select("*").eq("email", email).execute()
        if existing_email.data:
            return jsonify({"message": "E-mail já cadastrado"}), 409

        # RECOMENDAÇÃO: Verifica se o CPF já existe
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
                "assinante": 0, # CORREÇÃO 2: Adicionada a vírgula aqui
                "cpf": cpf # OK: Inserindo o novo campo
            }).execute()
        except Exception as e:
            # Em um ambiente real, você deve logar 'e' e retornar uma mensagem mais genérica
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

    # O resto da função de LOGIN está OK, pois o login não usa o campo 'cpf'
    elif action == "LOGIN":
        # ... (código do LOGIN continua aqui) ...
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
    """
    Envia um e-mail de ativação usando o SendGrid e retorna o status code.
    """
    
    # 1. Definição do Email (Como estava, presumindo que URL_CURSO está resolvida)
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
       
        # 2. Inicializa o cliente SendGrid e envia o email
        conta_sendgrid = sendgrid.SendGridAPIClient(CHAVE_API_SENDGRID)
       
        response = conta_sendgrid.send(email)
        # 3. Imprime o status de sucesso para o log
        print(f"E-mail enviado com sucesso. Status: {response.status_code}")
        
        # Retorna o status code
        return response.status_code

    except BadRequestsError as e:
        # 4. TRATAMENTO DO ERRO 4XX (BadRequestsError)
        print("--- ERRO FATAL DO SENDGRID (BadRequestsError) ---")
        
        # O status code está diretamente no objeto e
        print(f"Status Code: {e.status_code}")
        
        # Acesso correto ao corpo da resposta de erro da API
        try:
            # e.response é o objeto de resposta completo
            error_details = e.response.text 
            print(f"Detalhes do Erro da API: {error_details}")
        except Exception as body_e:
            print(f"Erro ao obter o corpo da resposta: {body_e}")
            
        print("--------------------------------------------------")
        
        # Retorna o status code do erro (geralmente 400, 401, 403)
        return e.status_code


from supabase_client import create_client, Client

def atualizar_assinante_supabase(user_id_or_email) -> bool:
    """Atualiza o campo 'assinante' para True no Supabase pelo email."""
    try:
        # Inicializa o cliente Supabase com as chaves de backend
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # 1. Faz a atualização
        response = supabase.table('usuarios') \
            .update({'assinante': True}) \
            .eq('email', user_id_or_email) \
            .execute()
        
        # O Supabase retorna uma resposta complexa. Verifica se houve linhas afetadas.
        if response.data and len(response.data) > 0:
            print(f"SUCESSO: Usuário {user_id_or_email} atualizado no Supabase.")
            return True
        else:
            print(f"AVISO: Usuário {user_id_or_email} não encontrado no Supabase para atualização.")
            # Logue o erro ou o fato de não ter achado o usuário
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

        # O Mercado Pago geralmente envia a URL completa (ex: /v1/payments/{id})
        if topic == 'payment':
            payment_id = resource_url.split('/')[-1]
        elif topic == 'merchant_order':
            # Se você estiver usando Merchant Orders (menos comum)
            # Você precisará de uma lógica diferente para o ID
            return jsonify({"status": "ignored", "message": "Tipo merchant_order ignorado"}), 200
        else:
            return jsonify({"status": "ignored", "message": f"Tipo {topic} não processado"}), 200

        # 1. BUSCA OS DETALHES DO PAGAMENTO NA API DO MP
        sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
        payment_info = sdk.payment().get(payment_id)
        
        if payment_info["status"] != 200:
            print(f"ERRO MP: Falha ao buscar pagamento {payment_id}. Status: {payment_info['status']}")
            return jsonify({"status": "error", "message": "Falha ao consultar MP"}), 500

        payment = payment_info["response"]
        status = payment.get("status")
        external_reference = payment.get("external_reference") 

        # 2. VERIFICAÇÃO DE APROVAÇÃO E ATUALIZAÇÃO
        if status == 'approved':
            # Extrai o ID do usuário/email (baseado na sua estrutura: REF-{user_id_ref}-{uuid.uuid4()})
            try:
                # Pega a segunda parte, que é o email (ou ID)
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