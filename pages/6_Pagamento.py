
import streamlit as st

import os 


import mercadopago
import uuid

# from api_mercadopago import api_pagamento

from auth import verifica_login, verifica_assinante, logout



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




if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None

st.set_page_config(
    page_title="Pagamento",
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
    /* Esconde o link da página de Cadastro (Usando a capitalização 'CADASTRO') */
    [data-testid="stSidebarNav"] a[href*="CADASTRO"] {
        display: none !important;
    }

    /* Esconde o link da página de Recuperação de Senha (Supondo que o href contenha 'rec_senha') */
    [data-testid="stSidebarNav"] a[href*="rec_senha"] {
        display: none !important;
    }

    /* FIX DEFINITIVO: Esconde a página Home (Arquivo principal/raiz). 
       Este seletor mira o PRIMEIRO item da lista de navegação (li:first-child), 
       o que é garantido para funcionar na Home. */
    [data-testid="stSidebarNav"] li:first-child a { 
        display: none !important; 
    }

    /* Esconde o link da página de Pagamento (Usando a capitalização 'Pagamento') */
    [data-testid="stSidebarNav"] a[href*="Pagamento"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)
    
# --- Configuração do Banco de Dados SQLite ---

def criar_preferencia_pagamento():
    """
    Cria uma preferência de pagamento usando o SDK do Mercado Pago.
    Esta função usa o Access Token e deve ser considerada "lógica de backend"
    em um ambiente de Streamlit.
    """
    
    # 1. PEGA O EMAIL DE FORMA SEGURA (JÁ EXISTE NO CÓDIGO)
    id_para_mp = st.session_state.get('user_email') 

    if not id_para_mp:
        # Se nem o email estiver na sessão (o que seria um bug de login)
        raise ValueError("Identificador de usuário ausente na sessão.")
    
    if not MP_ACCESS_TOKEN:
        st.error("Falha na configuração do pagamento: Access Token ausente.")
        return None

    try:
        # 2. CORREÇÃO: PEGA O USER_ID DE FORMA SEGURA, COM FALLBACK PARA O EMAIL
        # Se 'user_id' não existir (dando o erro), ele usa o 'id_para_mp' (email) como fallback na referência.
        user_id_ref = st.session_state.get('user_id', id_para_mp) 
        
        # 3. GERAÇÃO DA REFERÊNCIA AGORA SEGURA
        # Se user_id existe, usa: REF-123-UUID
        # Se user_id não existe, usa: REF-email@exemplo.com-UUID
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
                # 4. CORREÇÃO: AQUI TAMBÉM PODE FALHAR SE O EMAIL SUMIR
                # Usando o id_para_mp, que já foi checado.
                "email": id_para_mp,
            },
            # Metadados para identificar a transação no seu sistema
            "external_reference": ref_id,
            "notification_url": MP_NOTIFICATION_URL,
            
            # URLs de redirecionamento após o pagamento no checkout do Mercado Pago
            "back_urls": {
                # Em um app real, estas URLs apontariam para endpoints públicos do seu Streamlit
                "success": URL_CURSO, # Substitua pela sua URL real
                "pending": URL_CURSO, # Substitua pela sua URL real
                "failure": URL_CURSO # Substitua pela sua URL real
            },
            "auto_return": "approved"
        }

        # Cria a preferência na API do Mercado Pago
        preference_response = sdk.preference().create(preference_data)
        
        if preference_response["status"] == 201:
            # Retorna o link de checkout (sandbox_init_point para testes, init_point para produção)
            return preference_response["response"]["init_point"]
        else:
            # Para debug profissional, inclua a resposta completa para análise
            st.error(f"Erro ao criar preferência: {preference_response['response']['message']}")
            st.code(preference_response) # Opcional: para ver o erro detalhado da API do MP
            return None

    except Exception as e:
        st.error(f"Erro inesperado no Mercado Pago: {e}")
        return None


def tela_pagamento():
    """Tela para gerenciar o status de assinante com fluxo de pagamento profissional."""
    
    # 1. GUARDA DE LOGIN (Usando 'user_nome' ou 'logged_in' é mais seguro)
    if verifica_assinante():
        st.warning("Você já tem a assinatura.")
        st.page_link("Home.py", label="Ir para a página inicial")
        st.stop()        

    if not st.session_state.get('user_nome'):
        st.error("Acesso negado. Por favor, faça login para acessar esta página.")
        st.page_link("Home.py", label="Ir para a página de Login")
        st.stop()
        return

    # 2. DEFINIÇÕES INICIAIS
    is_assinante = st.session_state.get('user_assinante', False)
    
    st.title("💳 Área de Assinatura e Pagamento")
    st.markdown(f"### Olá, {st.session_state['user_nome']}.") 
    st.markdown("---")

    # 3. CONTEÚDO BASEADO NO STATUS DE ASSINANTE (CONSOLIDADO)
    if is_assinante:
        st.success("Você já é um assinante premium e tem acesso total! Obrigado!")
        st.info("Aqui você gerenciaria sua assinatura e datas de renovação.")
        
    else:
        # Lógica para Usuário Não-Assinante
        st.subheader("Assine o Plano Premium e Libere Acesso Ilimitado")
        
        st.warning("Recurso de Simulado Ilimitado apenas para Assinantes.")
        
        st.markdown(f"#### **Valor Único: R$ {VALOR_ASSINATURA:.2f}**")
        st.write("Libere o Módulo 2 e todos os Simulados com pagamento único.")
        
        # --- Botão para iniciar o Checkout ---
        # with st.spinner("Gerando link de pagamento seguro..."):
        #         link_pagamento = criar_preferencia_pagamento()
            
        # if link_pagamento:
        #         # 2. Redireciona o usuário (Usando HTML para abertura segura)
        #         st.session_state['payment_link'] = link_pagamento
                
        #         # Usando um componente Streamlit para ser mais limpo, se possível, 
        #         # ou mantendo o HTML para o link de checkout:
        #         st.markdown(f"""
        #             <a href="{link_pagamento}" target="_blank" style="text-decoration: none;">
        #                 <button style="background-color:#009ee3; color:white; padding: 10px 20px; border:none; border-radius:5px; font-size: 16px; cursor: pointer;">
        #                     Ir para o Checkout de Pagamento Seguro 🔒
        #                 </button>
        #             </a>
        #         """, unsafe_allow_html=True)
                
        #         st.info("Você será redirecionado para o ambiente seguro do Mercado Pago para concluir a transação.")
        # else:
        #         st.error("Não foi possível iniciar o processo de pagamento. Tente novamente mais tarde.")

        # st.markdown("---")
        
        
        if st.button("Pagar com Mercado Pago"):
            
            # 1. Cria a Preferência e Obtém o Link
            with st.spinner("Gerando link de pagamento seguro..."):
                link_pagamento = criar_preferencia_pagamento()
            
            if link_pagamento:
                # 2. Redireciona o usuário (Usando HTML para abertura segura)
                st.session_state['payment_link'] = link_pagamento
                
                # Usando um componente Streamlit para ser mais limpo, se possível, 
                # ou mantendo o HTML para o link de checkout:
                st.markdown(f"""
                    <a href="{link_pagamento}" target="_blank" style="text-decoration: none;">
                        <button style="background-color:#009ee3; color:white; padding: 10px 20px; border:none; border-radius:5px; font-size: 16px; cursor: pointer;">
                            Ir para o Checkout de Pagamento Seguro 🔒
                        </button>
                    </a>
                """, unsafe_allow_html=True)
                
                st.info("Você será redirecionado para o ambiente seguro do Mercado Pago para concluir a transação.")
            else:
                st.error("Não foi possível iniciar o processo de pagamento. Tente novamente mais tarde.")

    st.markdown("---")

    # 5. BOTÃO DE LOGOUT (Consolidado)
    if st.button("Sair da Conta", key="logout_button_pagamento"):
        logout()
        st.success("Você saiu da conta.")
        # Redireciona para Home após logout
        st.switch_page("Home.py") 
        st.stop()

tela_pagamento()