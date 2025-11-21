import streamlit as st
import requests
import os
import mercadopago
import uuid

# URL do backend Flask
def get_secret(key, default=None):
    
    # 1. Tenta ler de st.secrets (para deploy no Streamlit Cloud)
    if 'secrets' in st.session_state and key in st.secrets:
        return st.secrets[key]
    # 2. Tenta ler de os.environ (para Codespace/Local com .env)
    return os.getenv(key, default)

MERCADO_PAGO_ACCESS_TOKEN = get_secret('MERCADO_PAGO_ACCESS_TOKEN')
REFERENCIA_ASSINATURA = get_secret('REFERENCIA_ASSINATURA')

VALOR_ASSINATURA = get_secret('VALOR_ASSINATURA') 
VALOR_ASSINATURA = float(VALOR_ASSINATURA)
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
URL_API_AUTH = get_secret("URL_API_AUTH")
URL_PERFIL = get_secret("URL_PERFIL")

# Inicializa sessão
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'token' not in st.session_state:
    st.session_state['token'] = None
if 'user_nome' not in st.session_state:
    st.session_state['user_nome'] = None
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None

# ---------------------------
# Função: login
# ---------------------------
def login(email, senha):
    
    payload = {"action": "LOGIN", "email": email, "senha": senha}
    try:
        resp = requests.post(URL_API_AUTH, json=payload)
        if resp.status_code == 200:
            data = resp.json()
            st.session_state['logged_in'] = True
            st.session_state['token'] = data.get('token')
            st.session_state['user_nome'] = data.get('nome')
            st.session_state['user_email'] = email
            return True, "Login realizado com sucesso"
        else:
            return False, resp.json().get('message', 'Erro no login')
    except Exception as e:
        return False, f"Erro de conexão: {e}"

# ---------------------------
# Função: cadastro
# ---------------------------
def cadastro(nome, email, senha):
    payload = {"action": "CADASTRO", "nome": nome, "email": email, "senha": senha}
    try:
        resp = requests.post(URL_API_AUTH, json=payload)
        if resp.status_code == 201:
            data = resp.json()
            st.session_state['logged_in'] = True
            st.session_state['token'] = data.get('token')
            st.session_state['user_nome'] = data.get('nome')
            st.session_state['user_email'] = email
            return True, "Cadastro realizado com sucesso"
        else:
            return False, resp.json().get('message', 'Erro no cadastro')
    except Exception as e:
        return False, f"Erro de conexão: {e}"

# ---------------------------
# Função: verifica login
# ---------------------------
def verifica_login():
    if not st.session_state['logged_in'] or not st.session_state['token']:
        st.warning("Você precisa estar logado para acessar esta página.")
        st.page_link("Home.py", label="Voltar para tela de login")
        st.stop()

    headers = {"Authorization": st.session_state['token']}
    try:
        resp = requests.get(URL_PERFIL, headers=headers)
        if resp.status_code == 200:
            user_data = resp.json().get('user', {})
            # ... outras chaves
            st.session_state['user_email'] = user_data.get('email')
            
            # Adicione a chave 'user_id' aqui, se o backend a retornar!
            st.session_state['user_id'] = user_data.get('id')
            return True
        else:
            st.warning("Sessão inválida ou expirada. Faça login novamente.")
            st.session_state['logged_in'] = False
            st.stop()
    except Exception as e:
        st.error(f"Erro ao verificar sessão: {e}")
        st.stop()

    
# ---------------------------
# Função: logout
# ---------------------------
def logout():
    st.session_state['logged_in'] = False
    st.session_state['token'] = None
    st.session_state['user_nome'] = None
    st.session_state['user_email'] = None

def verifica_assinante():

    if not st.session_state['logged_in'] or not st.session_state['token']:
        st.warning("Você precisa estar logado para acessar esta página.")
        st.page_link("Home.py", label="Voltar para tela de login")
        st.stop()

    headers = {"Authorization": st.session_state['token']}
    try:
        resp = requests.get(URL_PERFIL, headers=headers)
        if resp.status_code == 200:
            perfil = resp.json().get('perfil', {})
            if perfil.get("assinante", 0) == 1:
                return True
            else:
                return False
        else:
            st.warning("Sessão inválida ou expirada. Faça login novamente.")
            st.session_state['logged_in'] = False
            st.switch_page("Home.py") 
            st.stop()
    except Exception as e:
        st.error(f"Erro ao verificar assinatura: {e}")
        st.stop()

def criar_preferencia_pagamento():

    # 1. PEGA O EMAIL DE FORMA SEGURA 
    id_para_mp = st.session_state.get('user_email') 

    if not id_para_mp:

        raise ValueError("Identificador de usuário ausente na sessão.")
    
    if not MP_ACCESS_TOKEN:
        st.error("Falha na configuração do pagamento: Access Token ausente.")
        return None

    try:

        user_id_ref = st.session_state.get('user_id', id_para_mp) 
    
        ref_id = f"REF-{user_id_ref}-{uuid.uuid4()}"
        
        # Inicializa o SDK
        sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
        
        preference_data = {
            "items": [
                {
                    "title": TITULO_ASSINATURA,
                    "quantity": 1,
                    "unit_price": VALOR_ASSINATURA
                }
            ],
            "payer": {
                "email": id_para_mp,
            },

            "external_reference": ref_id,
            "notification_url": MP_NOTIFICATION_URL,
            

            "back_urls": {

                "success": URL_CURSO, 
                "pending": URL_CURSO,
                "failure": URL_CURSO 
            },
            "auto_return": "approved"
        }

        preference_response = sdk.preference().create(preference_data)
        
        if preference_response["status"] == 201:
            return preference_response["response"]["init_point"]
        else:
            st.error(f"Erro ao criar preferência: {preference_response['response']['message']}")
            st.code(preference_response)
            return None

    except Exception as e:
        st.error(f"Erro inesperado no Mercado Pago: {e}")
        return None
    
def add_fixed_footer_button(termos_link: str, politicas_link: str):
    """
    Adiciona um rodapé fixo na parte inferior da tela do Streamlit com links para
    Termos de Uso e Políticas de Privacidade.
    
    Args:
        termos_link (str): O URL para a página de Termos de Uso.
        politicas_link (str): O URL para a página de Políticas de Privacidade.
    """
    
    # Injeta o CSS (Estilo e Posicionamento Fixo)
    st.markdown(
        """
        <style>
        /* Contêiner que fica fixo na parte inferior */
        #fixed-footer-container {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #f0f2f6; /* Cor de fundo suave */
            border-top: 1px solid #e6e6e6; 
            padding: 8px 10px;
            text-align: center;
            z-index: 1000;
            box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.05);
        }
        
        /* Estilo dos Links */
        .footer-link {
            color: #0078ff; 
            text-decoration: none;
            margin: 0 10px;
            font-size: 14px;
        }
        
        .footer-link:hover {
            text-decoration: underline;
        }
        
        .separator {
            color: #aaa;
        }

        /* Adiciona preenchimento para evitar que o conteúdo da página fique escondido pelo rodapé */
        .main {
            padding-bottom: 60px; /* Ajuste este valor se o seu rodapé for mais alto */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Injeta o HTML do rodapé com os links dinâmicos
    footer_html = f"""
    <div id="fixed-footer-container">
        <a href="{termos_link}" target="_blank" class="footer-link">Termos de Uso</a>
        <span class="separator">|</span>
        <a href="{politicas_link}" target="_blank" class="footer-link">Políticas de Privacidade</a>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)