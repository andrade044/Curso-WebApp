
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
from auth import verifica_login, verifica_assinante, logout


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
    if not CHAVE_API_SENDGRID or not EMAIL_REMETENTE:
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
            from_email=EMAIL_REMETENTE,
            to_emails=recipient_email,
            subject='🎉 Bem-vindo(a) à Plataforma do Curso!',
            html_content=html_content
        )
        
        # Inicializa o cliente SendGrid e envia o email
        sg = sendgrid.SendGridAPIClient(CHAVE_API_SENDGRID)
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