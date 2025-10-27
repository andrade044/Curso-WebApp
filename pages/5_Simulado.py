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

def reiniciar_simulado():
    """Reseta todas as variáveis do quiz."""
    st.session_state['current_question'] = 0
    st.session_state['score'] = 0
    st.session_state['quiz_finished'] = False
    st.session_state['user_answer'] = None
    st.rerun()

if 'current_question' not in st.session_state:
    st.session_state['current_question'] = 0
if 'score' not in st.session_state:
    st.session_state['score'] = 0
if 'quiz_finished' not in st.session_state:
    st.session_state['quiz_finished'] = False
if 'user_answer' not in st.session_state:
    st.session_state['user_answer'] = None

def proxima_pergunta():
    """Lógica para avançar para a próxima pergunta e verificar a resposta."""
    
    
    
    # Se o usuário respondeu, verifica
    if st.session_state['user_answer'] is not None:
        pergunta_atual = SIMULADO_DATA[st.session_state['current_question']]
        
        # Verifica se a resposta está correta
        if st.session_state['user_answer'] == pergunta_atual['resposta_correta']:
            st.session_state['score'] += 1
            st.toast("✅ Resposta Correta!", icon='👍')
        else:
            st.toast(f"❌ Resposta Incorreta. A correta era: {pergunta_atual['resposta_correta']}", icon='👎')
    
    # Avança para o próximo índice
    st.session_state['current_question'] += 1
    st.session_state['user_answer'] = None # Limpa a resposta para a próxima pergunta

def tela_simulados():
    """Interface principal para a tela de Simulado."""
    """Interface principal para a tela de Simulado com acesso restrito a assinantes."""
    
    # --- 1. GUARDA DE SEGURANÇA (Adicione este bloco no início) ---
    
    # Verifica se o usuário está logado e se a chave de assinatura foi carregada
    if 'user_assinante' not in st.session_state:
        st.error("Acesso negado. Por favor, faça login para acessar os Simulados.")
        # Redireciona o usuário para a página de login/home
        time.sleep(1)
        st.switch_page("pages/1_Login.py")
    # --- 2. CONTEÚDO DA PÁGINA (Apenas executa se a guarda passar) ---
    st.title("Página de Simulados")
    
    # A linha que estava dando erro, agora segura:
    if not st.session_state['user_assinante']:
        # Lógica para usuário Free
        st.warning("Recurso de Simulado Ilimitado apenas para Assinantes.")
        # ...
    else:
        # Lógica para usuário Assinante
        st.success("Acesso ilimitado liberado!")
    
    st.title("🧠 Simulado de Conhecimento")

    # ------------------ VERIFICAÇÃO DE ACESSO (NOVA LÓGICA) ------------------
    if not st.session_state['user_assinante']:
        st.warning("🔒 **ACESSO RESTRITO.**")
        st.subheader("Para realizar os simulados, você precisa ser um Assinante Premium.")
        st.info("Acesse a aba 'Pagamento' para liberar este conteúdo.")
        return # Interrompe a função aqui, não exibindo o quiz.
    # --------------------------------------------------------------------------
    
    # Se for assinante, o código continua:
    total_perguntas = len(SIMULADO_DATA)
    
    # ------------------ SE O QUIZ TERMINOU ------------------
    if st.session_state['current_question'] >= total_perguntas:
        st.session_state['quiz_finished'] = True
        
        st.balloons()
        st.subheader("Simulado Finalizado!")
        
        porcentagem = (st.session_state['score'] / total_perguntas) * 100
        
        if porcentagem >= 70:
            st.success(f"Parabéns, você passou! 🎉 Sua pontuação final é: **{st.session_state['score']}/{total_perguntas}** ({porcentagem:.1f}%)")
        else:
            st.warning(f"Você pode melhorar. Sua pontuação final é: **{st.session_state['score']}/{total_perguntas}** ({porcentagem:.1f}%)")
            
        # Botão para recomeçar
        st.button("Tentar Novamente", on_click=reiniciar_simulado)
        
    # ------------------ SE O QUIZ ESTÁ EM ANDAMENTO ------------------
    else:
        pergunta_idx = st.session_state['current_question']
        pergunta_data = SIMULADO_DATA[pergunta_idx]
        
        # Exibe o progresso
        st.markdown(f"**Questão {pergunta_idx + 1} de {total_perguntas}**")
        st.progress((pergunta_idx) / total_perguntas)

        # Exibe a pergunta
        st.subheader(pergunta_data["pergunta"])

        # Formulário para o Radio Button
        with st.form(key=f"quiz_form_{pergunta_idx}"):
            
            # Opções (Radio Button)
            escolha = st.radio(
                "Escolha a opção correta:",
                pergunta_data["opcoes"],
                index=None, 
                key=f"radio_{pergunta_idx}"
            )
            
            # Submissão
            submit_button = st.form_submit_button(label="Próxima Questão")
            
            if submit_button:
                if escolha is None:
                    st.error("Por favor, selecione uma resposta antes de continuar.")
                else:
                    st.session_state['user_answer'] = escolha
                    proxima_pergunta()
                    st.rerun()

tela_simulados()