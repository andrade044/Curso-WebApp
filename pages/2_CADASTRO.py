import streamlit as st
import re
import os 
import time

# from api_mercadopago import api_pagamento
import requests
from auth import cadastro
from webhook_server import enviar_email_ativacao_sendgrid


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

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None


st.set_page_config(
    page_title="Cadastro",
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

st.markdown("""
<style>
    /* Esconde o link da página de Cadastro (Página 2) */
    [data-testid="stSidebarNav"] a[href*="CADASTRO"] {
        display: none !important;
    }

    /* Esconde o link da página de Recuperação de Senha (Página 7) */
    [data-testid="stSidebarNav"] a[href*="rec_senha"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)
    

# --- Configuração do Banco de Dados SQLite ---

def validar_cpf(cpf):
    cpf = re.sub(r'[^0-9]', '', cpf)
    return len(cpf) == 11

def validar_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def tela_cadastro():
    """Mostra o formulário de cadastro e envia dados para a API."""
    
    # Verifica se já está logado e redireciona (boa prática)
    if st.session_state.get('logged_in'):
        st.warning("Você já está logado. Redirecionando para o curso.")
        time.sleep(1)
        st.switch_page("pages/4_Curso.py")
        st.stop()
        return
    
    st.title("📝 Cadastro de Novo Usuário")
    
    with st.form(key='cadastro_form'):
        # Campos de entrada
        # Adicione chaves (key) nos inputs se precisar reter o valor após submissão falha
        cpf_input = st.text_input(label="CPF (apenas números)", max_chars=11, placeholder="12345678900")
        email_input = st.text_input(label="Email", placeholder="seu.email@exemplo.com")
        nome_input = st.text_input(label="Nome Completo", placeholder="Seu nome")
        senha_input = st.text_input(label="Senha", type="password")
        confirma_senha_input = st.text_input(label="Confirma senha", type="password")
        
        col1, col3 ,col4 = st.columns([2, 6, 1])

        with col1:
            submit_button = st.form_submit_button(label='Cadastrar')    
        
        with col4:
            st.markdown(
                '<div style="text-align: right;">'
                '   <a href="/" target="_self">Já tem conta? Fazer Login</a>'
                '</div>', 
                unsafe_allow_html=True
            )
            
            
    if submit_button:
        erros = False
        
        # 1. Validações Locais (Front-end)
        # Usando 'erros' para controlar o fluxo
        if not validar_cpf(cpf_input):
            st.error("CPF inválido. Deve conter 11 números.")
            erros = True
        if not validar_email(email_input):
            st.error("Por favor, insira um email válido.")
            erros = True
        if not nome_input.strip():
            st.error("O nome é obrigatório.")
            erros = True
        if len(senha_input) < 6:
            st.error("A senha deve ter pelo menos 6 caracteres.")
            erros = True
        if senha_input != confirma_senha_input: # Corrigida a verificação da senha (simplificada)
            st.error('As senhas digitadas não são iguais.')
            erros = True
            
        
        if not erros:
            # 2. Prepara o Payload para a API
            payload = {
                "action": "CADASTRO",
                "cpf": cpf_input,
                "email": email_input,
                "nome": nome_input,
                "senha": senha_input,
                "assinante": 0 
            }
            
            # Placeholder para mostrar o status do processamento
            status_message = st.empty()
            status_message.info("Processando cadastro...")
            
            # --- REMOVIDO DEBUG DE CÓDIGO (st.code()) ---

            try:
                # 3. Chama a API
                response = requests.post(
                    URL_API_AUTH, 
                    json=payload, 
                    timeout=20 # Adiciona um timeout de 10 segundos
                )
                
                # 4. Trata a Resposta da API
                if response.status_code == 201: # Sucesso no Cadastro
                    token = response.json().get("token") # Pega o token se o backend retornar
                    
                    status_message.success(response.json().get("message", "Cadastro realizado com sucesso!"))
                    
                    # LOGA O USUÁRIO E REDIRECIONA
                    st.session_state['logged_in'] = True
                    st.session_state['user_email'] = email_input
                    st.session_state['user_nome'] = nome_input 
                    st.session_state['token'] = token

                    enviar_email_ativacao_sendgrid(
                    email_input, nome_input)


                    time.sleep(1) # Dá tempo para o usuário ver a mensagem de sucesso
                    st.switch_page("pages/4_Curso.py")
                
                elif response.status_code == 409: # Conflito (Email/CPF já existe)
                    status_message.error(response.json().get("message", "Este e-mail ou CPF já está cadastrado."))
                
                elif response.status_code >= 400 and response.status_code < 500:
                    # Erros do cliente (400, 401, 403, etc.)
                    status_message.error(response.json().get("message", f"Erro na API (Status {response.status_code}): Requisição inválida."))
                
                else: # Erros 5xx ou outros desconhecidos
                    status_message.error(response.json().get("message", f"Erro desconhecido no cadastro (Status {response.status_code}). Tente novamente."))
                        
            except requests.exceptions.Timeout:
                status_message.error("Erro de conexão Tempo limite esgotado (Timeout).")
            except requests.exceptions.ConnectionError:
                status_message.error(f"Erro de conexão Não foi possível se conectar .")
            except requests.exceptions.RequestException as e:
                # Catch-all para outros erros de requisição
                status_message.error(f"Erro inesperado de requisição: {e}")


tela_cadastro()
