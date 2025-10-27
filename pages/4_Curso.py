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
from auth import verifica_login, logout, verifica_assinante

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
URL_PERFIL = get_secret("URL_PERFIL")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None


# --- Configuração do Banco de Dados SQLite ---
DB_NAME = 'usuarios.db'

if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.stop()

# Se quiser, podemos validar o token direto na API
token = st.session_state.get('token')

headers = {"Authorization": token}
try:
    resp = requests.get(URL_PERFIL, headers=headers)
    if resp.status_code != 200:
        st.warning("Sessão inválida ou expirada. Faça login novamente.")
        st.session_state['logged_in'] = False
        st.stop()
except Exception as e:
    st.error(f"Erro ao verificar sessão: {e}")
    st.stop()

# Usuário está logado e token válido, mostra o conteúdo do curso
st.title(f"Bem-vindo(a), {st.session_state['user_nome']}!")
st.write("Aqui está o conteúdo do seu curso...")


def tela_curso():
    """Conteúdo do Curso (Acesso Condicional e Protegido)."""

    # 1. GUARDA DE LOGIN (CRÍTICO)
    # Se não estiver logado, exibe erro, oferece link de login e para a execução.
    if not st.session_state.get('user_nome'):
        st.error("Acesso negado. Por favor, faça login para acessar o Curso.")
        
        # Redireciona para a página principal ou login
        st.page_link("Home.py", label="Ir para a página de Login")
        
        st.stop() # Interrompe a execução do restante do código da página
        return
        
    # --- 2. INÍCIO DO CONTEÚDO (Executa SOMENTE se a guarda passar) ---
    
    # 2.1. Cabeçalho e Status
    nome_usuario = st.session_state['user_nome']
    is_assinante = st.session_state.get('user_assinante', False)
    
    st.title(f"🎓 Bem-vindo(a) ao Curso, {nome_usuario}!")
    
    status_label = "Assinante Premium 👑" if is_assinante else "Usuário Básico"
    st.subheader(f"Seu Status: {status_label}")

    # Mensagem de status consolidada
    if is_assinante:
        st.success("🎉 Conteúdo premium desbloqueado!")
    else:
        st.warning("🔒 Conteúdo premium bloqueado. Faça upgrade para acessar.")

    st.markdown("---")
    
    # 2.2. Botão de Logout (Consolidado)
    if st.button("Sair da Conta"):
        logout()
        st.success("Você saiu da conta. Redirecionando...")
        # Usa switch_page para redirecionar para o login/home
        st.switch_page("Home.py") 
        st.stop()

    st.markdown("---")

    # 3. MÓDULO 1: CONTEÚDO GRATUITO
    with st.expander("📚 Módulo 1: Introdução e Primeiros Passos (Grátis)", expanded=True):
        st.info("Este conteúdo está liberado para todos os usuários.")

        # VÍDEO 1.1 (GRÁTIS)
        with st.expander("▶️ Aula 1.1: Configurando o Ambiente"):
            # Nota: Este link parece ser de uma playlist. Streamlit pode não tocar a playlist.
            st.video('https://www.youtube.com/watch?v=ZZ4B0QUHuNc') 
            st.write("Descrição: Introdução ao tema e instalação das ferramentas necessárias.")
        
        # VÍDEO 1.2 (GRÁTIS)
        with st.expander("▶️ Aula 1.2: Visão Geral e Estrutura Básica"):
            # Substitua 'VIDEO_GRATUITO_2' pela URL real do vídeo
            st.video('https://www.youtube.com/watch?v=VIDEO_GRATUITO_2_URL_AQUI') 
            st.write("Descrição: Conceitos fundamentais e a primeira linha de código.")

    st.markdown("---")
    st.header("Módulo 2: Conteúdo Avançado")

    # 4. MÓDULO 2: CONTEÚDO PAGO (Acesso Condicional)
    if is_assinante:
        # CONTEÚDO LIBERADO
        with st.expander("👑 Módulo 2: Conteúdo Avançado e Práticas Profissionais (Assinantes)", expanded=True):
            st.success("🎉 ACESSO LIBERADO! Desfrute do conteúdo exclusivo.")
            
            # VÍDEO 2.1 (PAGO)
            with st.expander("🔒 Aula 2.1: Hashing e Segurança (BCrypt na Prática)"):
                st.video('https://www.youtube.com/watch?v=8M20LyCZDOY') 
                st.write("Descrição: Detalhamento sobre hasheamento de senhas e proteção contra ameaças.")

            # VÍDEO 2.2 (PAGO)
            with st.expander("🔒 Aula 2.2: Integração com Bancos NoSQL e Desempenho"):
                # Aviso: Lembre-se que 'video.mp4' deve estar no mesmo diretório ou caminho correto 
                # e que arquivos grandes podem ser lentos em deploys como o Render.
                try:
                    video_file = open('video.mp4', 'rb')
                    video_byts = video_file.read()
                    st.video(video_byts) 
                    st.write("Descrição: Estratégias para armazenar dados não estruturados de forma eficiente.")
                except FileNotFoundError:
                    st.error("Arquivo de vídeo 'video.mp4' não encontrado.")
                
            st.markdown("---")
            st.write("Material complementar e exercícios práticos do Módulo 2.")
            
    else:
        # CONTEÚDO BLOQUEADO
        with st.expander("🔒 Módulo 2: Conteúdo Avançado e Práticas Profissionais (Bloqueado)"):
            st.warning("🔒 **CONTEÚDO EXCLUSIVO PARA ASSINANTES.**")
            st.write("Adquira sua assinatura para liberar este e outros módulos avançados.")


    
tela_curso()