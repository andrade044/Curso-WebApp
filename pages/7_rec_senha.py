import streamlit as st
import requests
import os
from dotenv import load_dotenv
import time

# --- Configuração e Variáveis de Ambiente ---
def get_secret(key, default=None):
    """Lê segredos de st.secrets ou de os.environ."""
    # 1. Tenta ler de st.secrets (para deploy no Streamlit Cloud)
    if 'secrets' in st.session_state and key in st.secrets:
        return st.secrets[key]
    # 2. Tenta ler de os.environ (para Codespace/Local com .env)
    return os.getenv(key, default)

load_dotenv()
URL_API_AUTH = get_secret("URL_API_AUTH") 

      
st.set_page_config(
    page_title="Recuperação de senha",
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
    /* Esconde o link da página de Cadastro (Supondo que o href contenha 'cadastro') */
    [data-testid="stSidebarNav"] a[href*="CADASTRO"] {
        display: none !important;
    }

    /* Esconde o link da página de Recuperação de Senha (Supondo que o href contenha 'rec_senha') */
    [data-testid="stSidebarNav"] a[href*="rec_senha"] {
        display: none !important;
    }
    
    /* Esconde o link da página de Pagamento (Supondo que o href contenha 'pagamento') */
    [data-testid="stSidebarNav"] a[href*="Pagamento"] {
        display: none !important;
    }

    /* Esconde o link da página Home (Supondo que o href contenha 'home') */
    [data-testid="stSidebarNav"] li:first-child a { 
    * display: none !important;
    }

</style>
""", unsafe_allow_html=True)
    

def tela_redefinir_senha():
    """
    Controla o fluxo de Esqueceu Senha (solicitação de link) e
    Redefinição de Senha (uso do token).
    """
    st.title("🔒 Redefinir Senha")
    st.markdown("---")

    if st.session_state.get('logged_in'):
            st.info(f"Você já esta logado!, {st.session_state.get('user_nome', 'Usuário')}!")
            time.sleep(1)
            st.switch_page("pages/4_Curso.py")
            st.stop()
    # 1. Tenta extrair o token da URL
    # st.query_params retorna um dict-like com os parâmetros da URL
    query_params = st.query_params
    
    # 🚨 PONTO CRÍTICO: Garantir que a chave usada aqui ("token") é a mesma 
    # que a sua API Flask coloca no link de e-mail.
    reset_token = query_params.get("token") 

    if reset_token:
        # Se houver um token, mostra o formulário para a nova senha
        show_reset_form(reset_token)
    else:
        # Se não houver token, mostra o formulário para solicitação do link
        show_forgot_form()

# --- Formulário de Solicitação de Link (/forgot_password) ---

def show_forgot_form():
    """Pede o e-mail para enviar o link de redefinição."""
    st.subheader("Passo 1: Enviar Link de Redefinição")
    st.info("Insira seu e-mail abaixo. Enviaremos um link para criar uma nova senha.")

    with st.form(key='forgot_form'):
        email = st.text_input("Seu Email", key="forgot_email")
        submitted = st.form_submit_button("Enviar Link")

    if submitted:
        status_message = st.empty()
        status_message.info("Processando solicitação...")

        try:
            # Remove a parte "/auth" da URL para acessar /forgot_password
            base_api_url = URL_API_AUTH.removesuffix('/auth') 
            response = requests.post(f"{base_api_url}/forgot_password", json={"email": email})
            
            if response.status_code == 200:
                status_message.success("Solicitação enviada! Verifique sua caixa de entrada e spam. O link é válido por 1 hora.")
            else:
                error_msg = response.json().get('detail', f"Erro no servidor: Código {response.status_code}")
                status_message.error(error_msg)

        except requests.exceptions.RequestException:
            status_message.error("Erro de conexão. Verifique se a API está online.")

# --- Formulário de Redefinição de Senha (/reset_password) ---

def show_reset_form(token):
    """Pede a nova senha, usa o token e chama a rota /reset_password."""
    st.subheader("Passo 2: Criar Nova Senha")
    st.warning("Você está usando o link de redefinição de senha. O token será enviado na requisição.")

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
            payload = {
                "token": token,
                "new_password": new_password
            }
            
            # Remove a parte "/auth" da URL para acessar /reset_password
            base_api_url = URL_API_AUTH.removesuffix('/auth') 
            response = requests.post(f"{base_api_url}/reset_password", json=payload)

            if response.status_code == 200:
                st.balloons()
                status_message.success("🥳 Senha redefinida com sucesso! Você pode fazer login agora.")
                st.page_link("Home.py", label="Ir para a tela de Login", icon="🚪")
                st.stop()
            else:
                error_msg = response.json().get('message', "Erro ao redefinir a senha.")
                status_message.error(error_msg)
                
        except requests.exceptions.RequestException:
            status_message.error("Erro de conexão. Verifique se a API está online.")


# --- Execução ---
tela_redefinir_senha()
