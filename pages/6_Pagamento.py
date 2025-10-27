
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

def criar_preferencia_pagamento():
    """
    Cria uma preferência de pagamento usando o SDK do Mercado Pago.
    Esta função usa o Access Token e deve ser considerada "lógica de backend"
    em um ambiente de Streamlit.
    """
    if not MP_ACCESS_TOKEN:
        st.error("Falha na configuração do pagamento: Access Token ausente.")
        return None

    try:
        # Inicializa o SDK
        sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
        
        # Gera uma referência única para rastreamento
        ref_id = f"REF-{st.session_state['user_id']}-{uuid.uuid4()}"
        
        streamlit_base_url = MP_NOTIFICATION_URL.replace("/mercadopago_webhook", "")
        meu_link_ngrok = "https://quizzically-ungymnastic-lamar.ngrok-free.dev"
        preference_data = {
            "items": [
                {
                    "title": TITULO_ASSINATURA,
                    "quantity": 1,
                    "unit_price": VALOR_ASSINATURA
                }
            ],
            "payer": {
                "email": st.session_state['user_email'],
            },
            # Metadados para identificar a transação no seu sistema
            "external_reference": ref_id,
            "notification_url": MP_NOTIFICATION_URL,
            
            # URLs de redirecionamento após o pagamento no checkout do Mercado Pago
            "back_urls": {
                # Em um app real, estas URLs apontariam para endpoints públicos do seu Streamlit
                # Ex: "https://seu-app-streamlit.com/?status=success"
                "success": meu_link_ngrok, # Substitua pela sua URL real
                "pending": meu_link_ngrok, # Substitua pela sua URL real
                "failure": meu_link_ngrok # Substitua pela sua URL real
            },
            "auto_return": "approved"
        }

        # Cria a preferência na API do Mercado Pago
        preference_response = sdk.preference().create(preference_data)
        
        if preference_response["status"] == 201:
            # Retorna o link de checkout (sandbox_init_point para testes, init_point para produção)
            # Usando init_point que funciona tanto em teste quanto em produção
            return preference_response["response"]["init_point"]
        else:
            st.error(f"Erro ao criar preferência: {preference_response['response']['message']}")
            return None

    except Exception as e:
        st.error(f"Erro inesperado no Mercado Pago: {e}")
        return None


def tela_pagamento():
    """Tela para trocar o status de assinante com fluxo de pagamento profissional."""
    
    if 'user_assinante' not in st.session_state:
        st.error("Acesso negado. Por favor, faça login para acessar os Simulados.")
        # Redireciona o usuário para a página de login/home

        st.switch_page("pages/1_Login.py")
        st.stop()

    # --- 2. CONTEÚDO DA PÁGINA (Apenas executa se a guarda passar) ---
    st.title("Página de Simulados")
    
    # A linha que estava dando erro, agora segura:
    if not st.session_state['user_assinante']:
        # Lógica para usuário Free
        st.warning("Recurso de Simulado Ilimitado apenas para Assinantes.")
        st.markdown("Clique  para assinar e liberar acesso total.")
    else:
        # Lógica para usuário Assinante
        st.success("Acesso ilimitado liberado!")
        st.info("Parabéns! Você pode iniciar todos os simulados disponíveis abaixo.")
    
    st.title("💳 Área de Pagamento")
    st.markdown(f"Olá, **{st.session_state['user_nome']}**.") 
    
    if st.session_state['user_assinante']:
        st.success("Você já é um assinante premium e tem acesso total! Obrigado!")
        
    else:
        st.subheader("Assine o Plano Premium")
        st.markdown(f"#### **Valor: R$ {VALOR_ASSINATURA:.2f}**")
        st.write("Libere o Módulo 2 e todos os Simulados com pagamento único.")
        
        # --- Botão para iniciar o Checkout ---
        if st.button("Pagar com Mercado Pago", key="mp_checkout_button"):
            
            # 1. Cria a Preferência e Obtém o Link
            with st.spinner("Gerando link de pagamento seguro..."):
                link_pagamento = criar_preferencia_pagamento()
            
            if link_pagamento:
                # 2. Redireciona o usuário (Usando HTML para abertura segura)
                st.session_state['payment_link'] = link_pagamento
                
                st.markdown(f"""
                    <a href="{link_pagamento}" target="_blank">
                        <button style="background-color:#009ee3; color:white; padding: 10px 20px; border:none; border-radius:5px; font-size: 16px; cursor: pointer;">
                            Ir para o Checkout de Pagamento Seguro 🔒
                        </button>
                    </a>
                """, unsafe_allow_html=True)
                
                st.info("Você será redirecionado para o ambiente seguro do Mercado Pago para concluir a transação. Não manipulamos seus dados de cartão.")
                
                # Opcional: Mostrar o link de teste para depuração
                # st.caption(f"Link Gerado: {link_pagamento}")
            else:
                st.error("Não foi possível iniciar o processo de pagamento. Tente novamente mais tarde.")

        st.markdown("---")
        st.warning("""
        **NOTA IMPORTANTE (Profissionalismo):**
        O *status de assinante* (liberação do acesso) só pode ser atualizado após o Mercado Pago confirmar o pagamento, o que é feito por meio de um **Webhook**.
        Em uma aplicação real, este Streamlit precisaria de um **Servidor Backend (Ex: Flask/FastAPI)** para receber o Webhook e atualizar o status do usuário no banco de dados.
        O simples redirecionamento de volta (`back_urls`) não garante a confirmação.
        """)

tela_pagamento()