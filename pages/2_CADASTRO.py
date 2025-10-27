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
    
    if 'user_nome' in st.session_state:
        st.warning("Você já está logado, Redirecionando para o curso")    
        time.sleep(1)
        st.switch_page("pages/4_Curso.py")
        st.stop()
    
    
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
            
            try:
                # 3. Chama a API de Autenticação/Cadastro Unificada
                response = requests.post(URL_API_AUTH, json=payload)
                
                # 4. Trata a Resposta da API
                if response.status_code == 201: # 201 Created (Sucesso no Cadastro)
                    st.success(response.json().get("message", "Cadastro realizado! Verifique seu e-mail de boas-vindas."))
                    
                    time.sleep(2)
                    st.session_state['tela_atual'] = 'login'
                    st.rerun()
                    
                elif response.status_code == 409: # 409 Conflict (Email/CPF já existe)
                    st.error(response.json().get("message", "Este e-mail ou CPF já está cadastrado."))
                else:
                    st.error(response.json().get("message", "Erro desconhecido no cadastro. Tente novamente."))
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Erro de conexão com a API: O servidor não respondeu. Verifique URL_API_AUTH.")

tela_cadastro()