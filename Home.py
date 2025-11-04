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
    page_title="Auto Escola",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Adiciona um CSS para esconder os botões de menu e footer, se necessário
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

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


if 'current_question' not in st.session_state:
    st.session_state['current_question'] = 0
if 'score' not in st.session_state:
    st.session_state['score'] = 0
if 'quiz_finished' not in st.session_state:
    st.session_state['quiz_finished'] = False
if 'user_answer' not in st.session_state:
    st.session_state['user_answer'] = None



def tela_login():
    """Mostra o formulário de login e autentica o usuário via API."""
    


    # Adicionando verificação para redirecionar se o usuário já estiver logado
    if st.session_state.get('logged_in'):
        st.info(f"Bem-vindo de volta, {st.session_state.get('user_nome', 'Usuário')}!")
        st.switch_page("pages/4_Curso.py")
        st.stop()
        return

    st.title("🚪 Login")

    # --- REMOVIDOS OS CAMPOS DUPLICADOS AQUI ---
    # email = st.text_input("Email")
    # senha = st.text_input("Senha", type="password")

    # APENAS UM FORMULÁRIO DE LOGIN DEVE EXISTIR
    with st.form(key='login_form'):
        email = st.text_input("Email", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_senha")
        submitted = st.form_submit_button("Entrar")
        
        col1, col2,col3, col4 = st.columns([1, 6, 1, 1])


        with col1:
            st.page_link("pages/2_CADASTRO.py", label="Novo por aqui? [Cadastre-se aqui]")
        
        with col4:
            st.page_link("pages/7_rec_senha.py", label="Esqueceu a senha?")


    if submitted:
        # Placeholder para mensagens de status
        status_message = st.empty()
        status_message.info("Autenticando...")

        # Prepara o Payload para a API
        payload = {
            "action": "LOGIN",
            "email": email,
            "senha": senha
        }

        try:
            # 1. Chama a API
            response = requests.post(URL_API_AUTH, json=payload)
            
            # 2. Trata a Resposta
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('user', {})
                token = data.get('token') # Captura o token

                # 3. DEFINE AS CHAVE1S DE SESSÃO (CRÍTICO)
                st.session_state['logged_in'] = True
                st.session_state['user_nome'] = data.get('nome', 'Usuário')
                st.session_state['user_assinante'] = data.get('assinante', False)
                st.session_state['user_email'] = data.get('email', email)
                st.session_state['token'] = token   
                
                status_message.success(f"Login bem-sucedido! Olá, {st.session_state['user_nome']}.")
                
                # 🚨 4. REDIRECIONAMENTO CORRETO
                st.switch_page("pages/4_Curso.py")
                # st.stop() é opcional após switch_page, mas garante a parada imediata.
                st.stop()
            
            elif response.status_code == 401:
                status_message.error("Credenciais inválidas. Verifique seu email e senha.")
            
            else:
                # Trata outros erros HTTP
                error_msg = response.json().get('detail', f"Erro no servidor: Código {response.status_code}")
                status_message.error(error_msg)

        except requests.exceptions.RequestException:
            status_message.error("Erro de conexão com o servidor. Verifique se a API está online.")

    
    return
# ----------------------------------------------------------------------
# FUNÇÃO PRINCIPAL DA PÁGINA (CONTROLADOR DE TELAS)
# ----------------------------------------------------------------------

tela_login()
