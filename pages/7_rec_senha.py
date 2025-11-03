import streamlit as st
# Importa todas as funções de BD, hash e token do seu arquivo principal
# NOTA: Certifique-se que o seu app.py está na raiz e chame-o de 'main_app'
try:
    # Se seu arquivo principal é 'app.py', use 'import app as main_app'
    # Se seu arquivo principal é 'Home.py' (como na sua tela de login), mantenha 'from Home...'
    from app import (
        buscar_usuario, 
        get_reset_token, 
        send_reset_email, 
        verify_reset_token, 
        hash_senha, # Para hash BCrypt
        update_user_password_hash # Onde você inserirá a lógica Supabase
    )
except ImportError:
    st.error("Erro: Não foi possível importar as funções do arquivo principal. Verifique o nome do arquivo.")
    st.stop()
    
# Importação para ler parâmetros da URL
from urllib.parse import urlparse, parse_qs 

st.set_page_config(page_title="Recuperação de Senha")


# -----------------------------------------------------------------
# Função 1: Exibe o formulário inicial para solicitar o e-mail
# -----------------------------------------------------------------

def display_forgot_form():
    """Exibe o formulário 'Esqueci a Senha?' e envia o e-mail de redefinição."""
    st.title("Esqueceu sua Senha? 🧐")
    st.markdown("Insira seu e-mail para receber um link de redefinição.")

    with st.form(key='forgot_form'):
        email = st.text_input("Seu E-mail", key="forgot_email")
        submitted = st.form_submit_button("Receber Link de Redefinição")

        if submitted:
            if not email:
                st.warning("Por favor, preencha o campo de e-mail.")
                return
            
            user_data = buscar_usuario(email)
            
            # Por segurança, sempre retorne a mesma mensagem (evita informar se o e-mail existe)
            if user_data:
                # user_id, nome, senha_hash_salva, assinante, ativo, token_ativacao = user_data
                user_nome = user_data[1] # Nome está na posição 1 do retorno de buscar_usuario
                
                # 1. Gera o token
                token = get_reset_token(email)
                
                # 2. Envia o e-mail
                status_envio = send_reset_email(email, user_nome, token)
                
                if status_envio == 202:
                    st.success("✅ Solicitação Enviada! Se o e-mail estiver cadastrado, verifique sua caixa de entrada (e spam!).")
                else:
                    st.error("❌ Falha no envio do e-mail. Tente novamente ou entre em contato.")

            else:
                st.success("Se o e-mail estiver cadastrado, um link de redefinição será enviado.")
                

# -----------------------------------------------------------------
# Função 2: Exibe o formulário para inserir a nova senha
# -----------------------------------------------------------------

def display_reset_form(token, user_email):
    """Exibe o formulário para o usuário digitar a nova senha."""
    st.title("🔐 Redefinir Sua Senha")
    st.info(f"Redefinindo senha para: **{user_email}**")

    with st.form(key='reset_form'):
        new_password = st.text_input("Nova Senha", type="password")
        confirm_password = st.text_input("Confirme a Nova Senha", type="password")
        reset_submitted = st.form_submit_button("Atualizar Senha")

        if reset_submitted:
            if new_password != confirm_password:
                st.error("As senhas não coincidem.")
            elif len(new_password) < 6:
                st.error("A senha deve ter pelo menos 6 caracteres.")
            else:
                # 1. Hash da nova senha
                new_hash = hash_senha(new_password)
                
                # 2. Atualiza no banco de dados
                if update_user_password_hash(user_email, new_hash):
                    st.success("✅ Senha atualizada com sucesso! Você já pode fazer login.")
                    st.balloons()
                    # Redireciona para o login
                    st.page_link("Home.py", label="Ir para a página de Login", icon="🚪")
                    # st.stop()
                else:
                    st.error("❌ Erro interno ao salvar a nova senha.")


# -----------------------------------------------------------------
# Lógica Principal da Página
# -----------------------------------------------------------------

def main_rec_senha():
    # Pega o token da URL, se existir (ex: http://localhost:8501/7_rec_senha?token=xyz...)
    query_params = st.query_params
    token = query_params.get('token')

    if token:
        # Tenta verificar o token usando a função importada do app.py
        user_email = verify_reset_token(token)
        
        if user_email:
            # Token válido
            display_reset_form(token, user_email)
        else:
            # Token inválido ou expirado
            st.error("🚨 Link de redefinição inválido ou expirado. Por favor, solicite um novo.")
            st.markdown("---")
            display_forgot_form() 
    else:
        # Se não houver token, mostra o formulário inicial de esqueci a senha
        display_forgot_form()

if __name__ == "__main__":
    main_rec_senha()