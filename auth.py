import streamlit as st
import requests
import os

# URL do backend Flask
def get_secret(key, default=None):
    
    # 1. Tenta ler de st.secrets (para deploy no Streamlit Cloud)
    if 'secrets' in st.session_state and key in st.secrets:
        return st.secrets[key]
    # 2. Tenta ler de os.environ (para Codespace/Local com .env)
    return os.getenv(key, default)

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
    """
    Verifica se o usuário logado é assinante.
    Retorna True se assinante, False caso contrário.
    """
    if not st.session_state['logged_in'] or not st.session_state['token']:
        st.warning("Você precisa estar logado para acessar esta página.")
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
            st.stop()
    except Exception as e:
        st.error(f"Erro ao verificar assinatura: {e}")
        st.stop()
