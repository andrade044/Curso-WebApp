import streamlit as st

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
from auth import login

load_dotenv()

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

# --- Configuração de Sessão e Título ---
st.set_page_config(
    page_title="Sistema de Cursos",
    layout="wide",
    
)

# Inicializa o session_state para controlar o estado do login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None


# --- Configuração do Banco de Dados SQLite ---
DB_NAME = 'usuarios.db'




def validar_cpf(cpf):
    cpf = re.sub(r'[^0-9]', '', cpf)
    return len(cpf) == 11

def validar_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))


# # ---------------------------------------------------

def gerar_codigo_ativacao():
    """Gera e salva um código único para o link de ativação."""
    # Gera um código de 6 dígitos. UUIDs são mais seguros, mas um código simples é mais amigável.
    code = str(random.randint(100000, 999999))
    st.session_state['user_activation_code'] = code
    return code


def reiniciar_simulado():
    """Reseta todas as variáveis do quiz."""
    st.session_state['current_question'] = 0
    st.session_state['score'] = 0
    st.session_state['quiz_finished'] = False
    st.session_state['user_answer'] = None
    st.rerun()

if 'current_question' not in st.session_state:
    st.session_state['current_question'] = 0
if 'score' not in st.session_state:
    st.session_state['score'] = 0
if 'quiz_finished' not in st.session_state:
    st.session_state['quiz_finished'] = False
if 'user_answer' not in st.session_state:
    st.session_state['user_answer'] = None


# --- Funções do Simulado ---






def tela_login():
    """Mostra o formulário de login e autentica o usuário via API."""
    
    st.title("🚪 Login")

    # Adiciona um link para a página de Cadastro
    
    

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    with st.form(key='login_form'):
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")
        st.page_link("pages/2_CADASTRO.py", label="Novo por aqui? Cadastre-se aqui")


    if submitted:
        # Prepara o Payload para a API
        payload = {
            "action": "LOGIN",
            "email": email,
            "senha": senha
        }

        try:
            st.info("Autenticando...")
            # 1. Chama a API
            response = requests.post("URL_API_AUTH_AQUI", json=payload)
            
            # 2. Trata a Resposta
            if response.status_code == 200:
                user_data = response.json().get('user', {})
                
                # 3. DEFINE AS CHAVES DE SESSÃO (CRÍTICO)
                st.session_state['user_nome'] = user_data.get('nome', 'Usuário')
                st.session_state['user_assinante'] = user_data.get('assinante', False)
                st.session_state['user_email'] = user_data.get('email')
                
                st.success(f"Login bem-sucedido! Olá, {st.session_state['user_nome']}.")
                
                # 🚨 4. REDIRECIONAMENTO PARA O CURSO
                # st.switch_page("pages/4_Curso.py")
                st.stop() # 🛑 Garante que o redirecionamento ocorra imediatamente.
            
            elif response.status_code == 401:
                st.error("Credenciais inválidas. Verifique seu email e senha.")
            else:
                st.error("Erro no servidor de autenticação.")

        except requests.exceptions.RequestException:
            st.error("Erro de conexão com o servidor. Verifique se a API está online.")
    if response.status_code == 200:
        st.session_state['logged_in'] = True
        st.session_state['user_email'] = email
        st.session_state['user_nome'] = response.json().get("nome")
        st.session_state['token'] = response.json().get("token")
        st.page_link("pages/4_Curso.py")
        st.session_state['logged_in'] = True
    if response.status_code == 200:
                data = response.json()
                user_data = data.get('user', {})
                token = data.get('token')

    st.session_state['token'] = token
    

# ----------------------------------------------------------------------
# FUNÇÃO PRINCIPAL DA PÁGINA (CONTROLADOR DE TELAS)
# ----------------------------------------------------------------------

def main_auth():
    # --- 🚨 1. GUARDA DE REDIRECIONAMENTO (Executa antes de tudo) ---
    # if 'user_nome' in st.session_state:
    #     st.success(f"Você já está logado como {st.session_state['user_nome']}. Redirecionando para o Curso...")
    #     # Redirecionamento imediato para a página do curso
    #     st.switch_page("pages/4_Curso.py")
    #     st.stop() # CRÍTICO: Não executa o restante do código.

    # --- 2. MOSTRA A TELA DE LOGIN ---
    tela_login()

if __name__ == '__main__':
    main_auth()