import streamlit as st
import os
from supabase_client import create_client, Client # Importe o SDK

# Para este arquivo, usaremos a variável do ambiente que define a URL base
# Lembre-se de definir esta variável (URL_BASE_ATIVACAO) nas suas secrets.
def get_secret(key, default=None):
    
    # 1. Tenta ler de st.secrets (para deploy no Streamlit Cloud)
    if 'secrets' in st.session_state and key in st.secrets:
        return st.secrets[key]
    # 2. Tenta ler de os.environ (para Codespace/Local com .env)
    return os.getenv(key, default)
try:
    # Tente importar o cliente anon de onde ele foi definido (melhor prática)
    from supabase_client import supabase_anon 
except ImportError:
    # Fallback ou aviso se o cliente não for encontrado
    st.error("Erro: Não foi possível importar 'supabase_anon'. Verifique seu arquivo 'supabase_client.py'.")
    st.stop()
    
URL_BASE_ATIVACAO = get_secret("URL_BASE_ATIVACAO") 

def handle_password_recovery(email: str):
    """
    Chama a função de recuperação de senha do Supabase Auth.
    O Supabase enviará um link de "Redefinir Senha" para o email fornecido.
    """
    if not email:
        st.error("Por favor, insira seu endereço de e-mail.")
        return

    try:
        # A URL 'redirectTo' garante que o usuário volte para sua página Streamlit 
        # (Home.py) após clicar no link de redefinição no e-mail.
        redirect_url = f"{URL_BASE_ATIVACAO}/Home.py"
        
        response = supabase_anon.auth.reset_password_for_email(
            email=email,
            # Redireciona o usuário de volta para o seu app após a confirmação do link
            redirectTo=redirect_url 
        )
        
        # A API pode retornar um erro no objeto de resposta
        if response.error:
             st.error(f"Erro ao solicitar recuperação: {response.error.message}. Tente novamente.")
        else:
            # Mensagem de sucesso, independentemente de o email existir, por segurança.
            st.success("Se o e-mail estiver registrado, você receberá um link de recuperação em breve. Verifique sua caixa de spam e as configurações de e-mail do seu projeto Supabase.")
            
    except Exception as e:
        # Erro de conexão ou inesperado
        st.error(f"Ocorreu um erro inesperado na comunicação: {e}")


def password_recovery_page():
    """Renderiza a página de recuperação de senha no Streamlit."""
    
    st.set_page_config(page_title="Recuperação de Senha", layout="centered")
    
    st.markdown(
        """
        <style>
        .stButton>button {
            background-color: #009ee3; 
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 16px;
        }
        .stTextInput>div>div>input {
            border-radius: 8px;
        }
        </style>
        """, unsafe_allow_html=True
    )
    
    st.title("🔒 Recuperação de Senha")
    st.markdown("Insira seu e-mail para que possamos enviar um link **seguro** para você redefinir sua senha.")

    with st.form(key='recovery_form'):
        email = st.text_input(
            "Seu E-mail", 
            placeholder="exemplo@dominio.com", 
            key="recovery_email_input"
        )
        submit_button = st.form_submit_button("Enviar Link de Redefinição")

        if submit_button:
            handle_password_recovery(email)

    st.markdown("---")
    
    # Adiciona um link para voltar à página de login
    st.page_link("Home.py", label="Voltar ao Login", icon="🔙")

