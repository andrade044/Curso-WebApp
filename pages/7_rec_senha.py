import streamlit as st
import requests
import os
from dotenv import load_dotenv

# --- Configuração e Variáveis de Ambiente ---
# Replicar a função get_secret de app.py para garantir que a página funcione isoladamente
def get_secret(key, default=None):
    """Lê segredos de st.secrets ou de os.environ."""
    # 1. Tenta ler de st.secrets (para deploy no Streamlit Cloud)
    if 'secrets' in st.session_state and key in st.secrets:
        return st.secrets[key]
    # 2. Tenta ler de os.environ (para Codespace/Local com .env)
    return os.getenv(key, default)

load_dotenv()
URL_API_AUTH = get_secret("URL_API_AUTH") # A rota /forgot_password é gerenciada pelo mesmo servidor

# --- Funções de UI ---

def tela_redefinir_senha():
    """
    Controla o fluxo de Esqueceu Senha (solicitação de link) e
    Redefinição de Senha (uso do token).
    """
    st.title("🔒 Redefinir Senha")
    st.markdown("---")

    # 1. Tenta extrair o token da URL
    query_params = st.query_params
    reset_token = query_params.get("token")

    if reset_token:
        # Se houver um token na URL, mostra o formulário para a nova senha
        show_reset_form(reset_token)
    else:
        # Se não houver token, mostra o formulário para solicitação do link
        show_forgot_form()

# --- Formulário de Solicitação de Link (/forgot_password) ---

def show_forgot_form():
    """
    Pede o e-mail para enviar o link de redefinição.
    Chama a rota /forgot_password.
    """
    st.subheader("Passo 1: Enviar Link de Redefinição")
    st.info("Insira seu e-mail abaixo. Se encontrarmos sua conta, enviaremos um link para criar uma nova senha.")

    with st.form(key='forgot_form'):
        email = st.text_input("Seu Email", key="forgot_email")
        submitted = st.form_submit_button("Enviar Link")

    if submitted:
        status_message = st.empty()
        status_message.info("Processando solicitação...")

        try:
            # Chama o endpoint /forgot_password da API Flask
            payload = {"email": email}
            # OBS: Usamos a mesma URL base da API de autenticação
            response = requests.post(f"{URL_API_AUTH.replace('/auth', '')}/forgot_password", json=payload)
            
            # Como a rota /forgot_password sempre retorna 200 (ou 500 em caso de erro fatal),
            # usamos a resposta de sucesso genérica para segurança.
            if response.status_code == 200:
                status_message.success("Solicitação enviada! Verifique sua caixa de entrada e spam. O link é válido por 1 hora.")
            else:
                # Se for um erro interno (500), informamos o usuário
                status_message.error("Erro interno do servidor ao processar a solicitação.")
                print(f"Erro na API /forgot_password: {response.status_code}, {response.text}")

        except requests.exceptions.RequestException:
            status_message.error("Erro de conexão. Verifique se a API está online.")

# --- Formulário de Redefinição de Senha (/reset_password) ---

def show_reset_form(token):
    """
    Pede a nova senha, usa o token e chama a rota /reset_password.
    """
    st.subheader("Passo 2: Criar Nova Senha")
    st.warning("Você está usando o link de redefinição de senha. O token expira em breve.")

    with st.form(key='reset_form'):
        new_password = st.text_input("Nova Senha", type="password", key="new_pass")
        confirm_password = st.text_input("Confirme a Nova Senha", type="password", key="confirm_pass")
        submitted = st.form_submit_button("Redefinir Senha")

    if submitted:
        status_message = st.empty()
        status_message.info("Tentando redefinir sua senha...")
        
        if new_password != confirm_password:
            status_message.error("As senhas não coincidem.")
            return

        if len(new_password) < 6:
            status_message.error("A senha deve ter pelo menos 6 caracteres.")
            return
            
        try:
            # Chama o endpoint /reset_password da API Flask
            payload = {
                "token": token,
                "new_password": new_password
            }
            # OBS: Usamos a mesma URL base da API de autenticação
            response = requests.post(f"{URL_API_AUTH.replace('/auth', '')}/reset_password", json=payload)

            if response.status_code == 200:
                status_message.success("🥳 Senha redefinida com sucesso! Você pode fazer login agora.")
                # Redireciona para a tela de login
                st.balloons()
                st.page_link("app.py", label="Ir para a tela de Login", icon="🚪")
                st.stop()
            else:
                # O token pode estar inválido (400) ou expirado (400)
                error_msg = response.json().get('message', "Erro ao redefinir a senha.")
                status_message.error(error_msg)
                
        except requests.exceptions.RequestException:
            status_message.error("Erro de conexão. Verifique se a API está online.")


# --- Execução ---
tela_redefinir_senha()
