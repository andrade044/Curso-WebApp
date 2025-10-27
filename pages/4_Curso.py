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


def tela_curso():
    """Conteúdo do Curso (Acesso Condicional)."""
    st.title(f"Bem-vindo(a) ao Curso, {st.session_state['user_nome']}!")
    
    status = "Assinante" if st.session_state['user_assinante'] else "Usuário Básico (Não-Assinante)"
    st.subheader(f"Seu Status: {status}")

    # Conteúdo Gratuito
    st.markdown("---")
    
    # Expander para o Módulo 1 (Sempre aberto ou facilmente acessível)
    with st.expander("📚 Módulo 1: Introdução e Primeiros Passos (Grátis)", expanded=True):
        st.info("Este conteúdo está liberado para todos os usuários.")

        # VÍDEO 1.1 (GRÁTIS)
        with st.expander("▶️ Aula 1.1: Configurando o Ambiente"):
            st.video('https://www.youtube.com/watch?v=ZZ4B0QUHuNc&list=PLtqF5YXg7GLmCvTswG32NqQypOuYkPRUE') 
            st.write("Descrição: Introdução ao tema e instalação das ferramentas necessárias.")
        
        # VÍDEO 1.2 (GRÁTIS)
        with st.expander("▶️ Aula 1.2: Visão Geral e Estrutura Básica"):
            st.video('https://www.youtube.com/watch?v=VIDEO_GRATUITO_2') 
            st.write("Descrição: Conceitos fundamentais e a primeira linha de código.")

    # Conteúdo Pago
    st.markdown("---")
    st.header("Módulo 2: Conteúdo Avançado")
    
        
    
        # ACESSO LIBERADO
    st.markdown("---")
    
    # Verifica o status de assinante para liberar o Módulo 2
    if st.session_state['user_assinante']:
        
        # Expander para o Módulo 2 (Liberado para Assinantes)
        with st.expander("👑 Módulo 2: Conteúdo Avançado e Práticas Profissionais", expanded=False):
            st.success("🎉 ACESSO LIBERADO! Conteúdo exclusivo para Assinantes.")
            
            # VÍDEO 2.1 (PAGO)
            with st.expander("🔒 Aula 2.1: Hashing e Segurança (BCrypt na Prática)"):
                st.video('https://www.youtube.com/watch?v=8M20LyCZDOY&list=PLtqF5YXg7GLmCvTswG32NqQypOuYkPRUE&index=2') 
                st.write("Descrição: Detalhamento sobre hasheamento de senhas e proteção contra SQL Injection.")

            # VÍDEO 2.2 (PAGO)
            with st.expander("🔒 Aula 2.2: Integração com Bancos NoSQL e Desempenho"):
                video_file = open('video.mp4','rb')
                video_byts = video_file.read()
                st.video(video_byts) 
                st.write("Descrição: Estratégias para armazenar dados não estruturados de forma eficiente.")
                
            st.markdown("---")
            st.write("Material complementar e exercícios práticos do Módulo 2.")
            
    else:
        # CONTEÚDO BLOQUEADO
        # Exibe um expender com aviso de bloqueio
        with st.expander("🔒 Módulo 2: Conteúdo Avançado e Práticas Profissionais"):
            st.warning("🔒 **CONTEÚDO EXCLUSIVO PARA ASSINANTES.**")
            st.write("Adquira sua assinatura na aba 'Pagamento' para liberar este e outros módulos avançados.")

tela_curso()