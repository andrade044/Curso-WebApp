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
from auth import cadastro

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

def tela_cadastro():
    """Mostra o formulário de cadastro e envia dados para a API."""
    
    # if 'user_nome' in st.session_state:
    #     st.warning("Você já está logado, Redirecionando para o curso")     
    #     time.sleep(1)
    #     st.switch_page("pages/4_Curso.py")
    #     st.stop()
    
    
    st.title("📝 Cadastro de Novo Usuário")
    
    with st.form(key='cadastro_form'):
        # Campos de entrada
        cpf_input = st.text_input(label="CPF (apenas números)", max_chars=11, placeholder="12345678900")
        email_input = st.text_input(label="Email", placeholder="seu.email@exemplo.com")
        nome_input = st.text_input(label="Nome Completo", placeholder="Seu nome")
        senha_input = st.text_input(label="Senha", type="password")
        confirma_senha_input = st.text_input(label="Confirma senha", type="password")
        
        submit_button = st.form_submit_button(label='Cadastrar')

    if submit_button:
        erros = False
        
        # 1. Validações Locais (Front-end) - Rápido e evita chamadas desnecessárias
        if not validar_cpf(cpf_input):
            st.error("CPF inválido.")
            erros = True
        elif not validar_email(email_input):
            st.error("Por favor, insira um email válido.")
            erros = True
        elif not nome_input.strip():
            st.error("O nome é obrigatório.")
            erros = True
        elif len(senha_input) < 6:
            st.error("A senha deve ter pelo menos 6 caracteres.")
            erros = True
        elif not senha_input == confirma_senha_input:
            st.error('Senhas diferentes')
            erros = True
            
        # REMOVIDA A VERIFICAÇÃO DE EXISTÊNCIA E A LÓGICA DE TOKEN/E-MAIL

        if not erros:
            
            # 2. Prepara o Payload para a API
            payload = {
                "action": "CADASTRO", # <-- INDICA AO BACK-END QUE É UM CADASTRO
                "cpf": cpf_input,
                "email": email_input,
                "nome": nome_input,
                "senha": senha_input,
                "assinante": 0 
                # O Back-end se encarrega de: hash da senha, salvar no DB, e enviar o e-mail
            }
            
            st.info("Processando cadastro...")
            
            # --- DEBUG TEMPORÁRIO ---
            # EXIBE A URL SENDO USADA. CONFIRME SE ELA ESTÁ CORRETA.
            st.code(f"URL de Requisição: {URL_API_AUTH}", language="text")
            # --- FIM DEBUG TEMPORÁRIO ---

            try:
                # 3. Chama a API de Autenticação/Cadastro Unificada com TIMEOUT
                response = requests.post(
                    URL_API_AUTH, 
                    json=payload, 
                    timeout=10 # Adiciona um timeout de 10 segundos
                )
                
                # 4. Trata a Resposta da API
                if response.status_code == 201: # 201 Created (Sucesso no Cadastro)
                    st.success(response.json().get("message", "Cadastro realizado! Verifique seu e-mail de boas-vindas."))
                    
                    # Loga o usuário diretamente após o cadastro
                    st.session_state['logged_in'] = True
                    st.session_state['user_email'] = email_input
                    st.session_state['user_nome'] = nome_input # Assumindo que o nome de usuário é retornado no 201 ou pode ser o nome_input
                    
                    time.sleep(2)
                    st.switch_page("pages/4_Curso.py")
                    
                elif response.status_code == 409: # 409 Conflict (Email/CPF já existe)
                    st.error(response.json().get("message", "Este e-mail ou CPF já está cadastrado."))
                elif response.status_code >= 400 and response.status_code < 500:
                    # Trata outros erros do cliente (400 Bad Request, 401 Unauthorized, etc.)
                     st.error(response.json().get("message", f"Erro na API (Status {response.status_code}): Requisição inválida."))
                else: # Erros 5xx ou outros desconhecidos
                    st.error(response.json().get("message", f"Erro desconhecido no cadastro (Status {response.status_code}). Tente novamente."))
                        
            except requests.exceptions.Timeout:
                 st.error("Erro de conexão com a API: Tempo limite esgotado (Timeout). O servidor Render pode estar hibernando. Tente novamente em alguns segundos.")
            except requests.exceptions.ConnectionError:
                 st.error(f"Erro de conexão com a API: Não foi possível se conectar a {URL_API_AUTH}. Verifique a URL e o status do servidor.")
            except requests.exceptions.RequestException as e:
                # Catch-all para outros erros de requisição
                st.error(f"Erro inesperado de requisição: {e}")
    if response.status_code == 201:
        st.session_state['logged_in'] = True
        st.session_state['user_email'] = email_input
        st.session_state['user_nome'] = nome_input
        st.session_state['token'] = response.json().get("token")
        st.switch_page("pages/4_Curso.py")


tela_cadastro()
