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

load_dotenv()

MERCADO_PAGO_ACCESS_TOKEN = os.getenv('MERCADO_PAGO_ACCESS_TOKEN')
# VALOR_ASSINATURA = os.getenv('VALOR_ASSINATURA')
REFERENCIA_ASSINATURA = os.getenv('REFERENCIA_ASSINATURA')

VALOR_ASSINATURA = 10
TITULO_ASSINATURA = "Assinatura Premium do Curso de Python"

CHAVE_API_SENDGRID = os.getenv('CHAVE_API_SENDGRID')
EMAIL_REMETENTE =  os.getenv('EMAIL_REMETENTE')
TOKEN_LENGTH_BYTES= os.getenv('TOKEN_LENGTH_BYTES')
TOKEN_EXPIRATION_HOURS= os.getenv('TOKEN_EXPIRATION_HOURS')

URL_BASE_ATIVACAO = "https://seuwebapp.com/ativacao"

from data import SIMULADO_DATA
# --- Configuração de Sessão e Título ---
st.set_page_config(
    page_title="Sistema de Cursos",
    layout="wide",
    
)

# Inicializa o session_state para controlar o estado do login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None


# --- Configuração do Banco de Dados SQLite ---
DB_NAME = 'usuarios.db'

def init_db():
    """Cria a tabela de usuários se ela não existir."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpf TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            senha_hash TEXT NOT NULL, 
            assinante BOOLEAN DEFAULT 0, 
            ativo BOOLEAN DEFAULT 0,    
            token_ativacao TEXT,        
            token_expiracao INTEGER     
        )
    ''')
    conn.commit()
    conn.close()

# Inicializa o banco de dados
init_db()


# --- Funções de Hashing e Verificação ---

def hash_senha(senha):
    """Gera o hash BCrypt da senha."""
    senha_bytes = senha.encode('utf-8')
    return bcrypt.hashpw(senha_bytes, bcrypt.gensalt())

def verificar_senha(senha_digitada, senha_hash_salva):
    """Verifica se a senha digitada corresponde ao hash salvo."""
    senha_digitada_bytes = senha_digitada.encode('utf-8')
    # O hash do banco precisa ser convertido para bytes se estiver em string
    # Nota: No SQLite ele pode ser salvo como BLOB, aqui assumimos que é uma string de texto
    if isinstance(senha_hash_salva, str):
         senha_hash_salva = senha_hash_salva.encode('utf-8')
    
    return bcrypt.checkpw(senha_digitada_bytes, senha_hash_salva)


# --- Funções do Banco de Dados ---

def cadastrar_usuario(cpf, email, nome, senha, assinante, ativo=0, token=None, token_exp=None):
    try:
        hashed_password = hash_senha(senha)
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Inserindo os novos campos 'ativo', 'token_ativacao', 'token_expiracao'
        c.execute(
            "INSERT INTO usuarios (cpf, email, nome, senha_hash, assinante, ativo, token_ativacao, token_expiracao) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (cpf, email, nome, hashed_password, assinante, ativo, token, token_exp)
        )
        conn.commit()
        # Retorna o ID do usuário recém-criado para uso no token update, se necessário.
        user_id = c.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        return False # Indica que CPF ou Email já existe
    except Exception as e:
        st.error(f"Erro no cadastro: {e}")
        return False

def buscar_usuario(email):
    """Busca o usuário pelo email e retorna os dados."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Adicionando 'ativo', 'token_ativacao' e 'token_expiracao'
    c.execute('SELECT id, nome, senha_hash, assinante, ativo, token_ativacao FROM usuarios WHERE email = ?', (email,)) 
    user_data = c.fetchone()
    conn.close()    
    return user_data
# --- Funções de Validação de Input (Reutilizadas) ---

def set_user_active(user_id):
    """Define o status do usuário como ativo e limpa o token."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('UPDATE usuarios SET ativo = 1, token_ativacao = NULL, token_expiracao = NULL WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()


def update_user_token(user_id, token, expiration_timestamp):
    """Atualiza o token de ativação do usuário no banco."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('UPDATE usuarios SET token_ativacao = ?, token_expiracao = ? WHERE id = ?', (token, expiration_timestamp, user_id))
    conn.commit()
    conn.close()





def validar_cpf(cpf):
    cpf = re.sub(r'[^0-9]', '', cpf)
    return len(cpf) == 11

def validar_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def verificar_existencia(email, cpf):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM usuarios WHERE email = ? OR cpf = ?', (email, cpf))
    count = c.fetchone()[0]
    conn.close()
    return count > 0


# try:
#     SENDGRID_API_KEY = st.secrets["SENDGRID_API_KEY"]
#     EMAIL_REMETENTE = st.secrets["EMAIL_REMETENTE"]
# except KeyError:
#     # Se rodando localmente sem secrets.toml
#     st.error("ERRO: Credenciais do SendGrid não encontradas. Verifique seu arquivo secrets.toml.")
#     SENDGRID_API_KEY = None # Define como None para bloquear o envio
#     EMAIL_REMETENTE = "teste@exemplo.com"
# # ---------------------------------------------------

def gerar_codigo_ativacao():
    """Gera e salva um código único para o link de ativação."""
    # Gera um código de 6 dígitos. UUIDs são mais seguros, mas um código simples é mais amigável.
    code = str(random.randint(100000, 999999))
    st.session_state['user_activation_code'] = code
    return code

def gerar_token_ativacao():
    """Gera um token criptograficamente seguro e define a expiração."""
    # Gera um token forte (ex: 64 caracteres hexadecimais)
    token = secrets.token_hex(32)
    # Token expira em 24 horas (em segundos)
    expiracao = int(time.time()) + (24 * 3600)
    return token, expiracao





def enviar_email_ativacao_sendgrid(destinatario: str, nome_usuario: str, link_ativacao: str) -> int:
    """
    Envia o email de ativação com o link dinâmico.
    (Função aprimorada com tratamento de erro e texto simples, conforme combinado)
    """
    # 1. Obter credenciais de forma segura (já usando os.getenv/st.secrets)
    api_key = CHAVE_API_SENDGRID # Assumindo que CHAVE_API_SENDGRID já está populada
    remetente = EMAIL_REMETENTE

    if not api_key:
         print("ERRO: CHAVE_API_SENDGRID não definida.")
         return 500

    from python_http_client.exceptions import HTTPError # Importação local para evitar erros globais
    
    # 2. Conteúdo em Texto Simples (para melhor entregabilidade)
    email_text = f"""
    Olá, {nome_usuario},
    
    Obrigado por se registrar! Para ativar sua conta e liberar o acesso, por favor, visite o link:
    
    {link_ativacao}
    
    Atenciosamente,
    Equipe do Curso.
    """
    
    # 3. Conteúdo HTML
    email_html = f"""
    <html>
      <body>
        <p>Olá, <strong>{nome_usuario}</strong>,</p>
        <p>Obrigado por se registrar! Para ativar sua conta e liberar o acesso, basta clicar no botão abaixo:</p>
        
        <p style="text-align: center;">
            <a href="{link_ativacao}" 
               style="background-color: #4CAF50; 
                      color: white; 
                      padding: 10px 20px; 
                      text-decoration: none; 
                      border-radius: 5px; 
                      display: inline-block;">
                ATIVAR MINHA CONTA
            </a>
        </p>
        
        <p>Se o botão não funcionar, copie e cole o seguinte link no seu navegador:</p>
        <p><small>{link_ativacao}</small></p>
        
        <p>Atenciosamente,<br>Equipe do Curso.</p>
      </body>
    </html>
    """
    
    email = Mail(
        from_email=remetente,
        to_emails=destinatario,
        subject='Ativação de Conta - Seu Curso de CNH',
        html_content=email_html,
        plain_text_content=email_text # Adiciona o conteúdo em texto simples
    )

    # 4. Tratamento de Erros
    try:
        conta_sendgrid = SendGridAPIClient(api_key)
        resposta = conta_sendgrid.send(email)
        print(f"Email enviado. Status Code: {resposta.status_code}")
        return resposta.status_code
    except HTTPError as e:
        st.error(f"Erro ao enviar email (Status {e.status_code}): {e.body}")
        return e.status_code
    except Exception as e:
        st.error(f"Erro inesperado no envio de email: {e}")
        return 500

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


# --- Funções do Simulado ---

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



# --- Telas do Streamlit ---

def tela_login():
    """Mostra o formulário de login."""
    
    st.title("🔑 Login")

    with st.form(key='login_form'):
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        login_button = st.form_submit_button(label='Entrar')

    if login_button:
        user_data = buscar_usuario(email)
        
        if user_data:
            user_id, nome, senha_hash_salva, assinante, ativo, token_ativacao = user_data
            if not ativo:
                    st.warning("⚠️ **Conta Não Ativada.** Por favor, verifique seu e-mail para ativar sua conta.")
            
                
            if verificar_senha(senha, senha_hash_salva):
                st.session_state['logged_in'] = True
                st.session_state['user_email'] = email
                st.session_state['user_nome'] = nome
                st.session_state['user_assinante'] = bool(assinante)
                st.session_state['user_id'] = user_id
                st.success(f"Login bem-sucedido! Bem-vindo(a), {nome}.")
                st.rerun()
            else:
                st.error("Email ou senha incorretos.")
        else:
            st.error("Email ou senha incorretos.")

def tela_cadastro():
    """Mostra o formulário de cadastro."""
    st.title("📝 Cadastro de Novo Usuário")
    
    with st.form(key='cadastro_form'):
        cpf_input = st.text_input(label="CPF (apenas números)", max_chars=11, placeholder="12345678900")
        email_input = st.text_input(label="Email", placeholder="seu.email@exemplo.com")
        nome_input = st.text_input(label="Nome Completo", placeholder="Seu nome")
        senha_input = st.text_input(label="Senha", type="password")
        confirma_senha_input = st.text_input(label="Confirma senha", type="password")
        
        
        assinante_inicial = 0 # Inicia como não-assinante
        
        submit_button = st.form_submit_button(label='Cadastrar')

    if submit_button:
        erros = False
        
        if not validar_cpf(cpf_input):
            st.error("CPF inválido.")
            erros = True
        elif not validar_email(email_input):
            st.error("Por favor, insira um email válido.")
            erros = True
        elif not nome_input.strip():
            st.error("O nome é obrigatório.")
            erros = True
        elif len(senha_input) < 6:
            st.error("A senha deve ter pelo menos 6 caracteres.")
            erros = True
        
        if not erros and verificar_existencia(email_input, cpf_input):
            st.error("Este Email ou CPF já está cadastrado.")
            erros = True
        
        if not senha_input == confirma_senha_input:
            st.error('Senhas diferentes')
            erros = True

        if not erros:
            token_ativacao, expiracao_token = gerar_token_ativacao()
            
            # 2. Monta o link de ativação dinâmico
            # O link de ativação agora inclui o token seguro
            # Se você usar Streamlit, talvez precise de um endpoint de API separado.
            # Aqui, simulamos o link completo que o usuário deve clicar:
            link_ativacao_completo = f"{URL_BASE_ATIVACAO}?token={token_ativacao}"

            # 3. Cadastra o usuário com ativo=0 e o token
            user_id = cadastrar_usuario(
                cpf=cpf_input, 
                email=email_input, 
                nome=nome_input,
                senha=senha_input, 
                assinante=assinante_inicial,
                ativo=0, # Inicia como não-ativo
                token=token_ativacao,
                token_exp=expiracao_token
            )
            if user_id:
                # 4. Envia o email com o link dinâmico
                status_envio = enviar_email_ativacao_sendgrid(
                    destinatario=email_input,
                    nome_usuario=nome_input,
                    link_ativacao=link_ativacao_completo)
                if status_envio == 202:
                    st.success("Cadastro concluído! Enviamos um e-mail de ativação. Por favor, verifique sua caixa de entrada para liberar o acesso.")
                else:
                    st.warning("Cadastro concluído, mas falha no envio do e-mail de ativação. Tente o login para reenviar.")
                
            else:
                st.error("Falha ao salvar usuário no banco de dados.")

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
        # Opcional: Mostra a URL de um vídeo "teaser" ou uma imagem de capa
        # st.image("caminho/para/imagem_capa_modulo_2.png")

########################################################################################################
#Tela do simulado 

# --- Inicialização do Estado do Simulado ---



def tela_verificacao_email():
    """Tela para gerenciar o fluxo de verificação de e-mail."""
    st.title("📧 Verificação de E-mail")

    if st.session_state['user_verificado']:
        st.success("Seu e-mail já está verificado! Você já pode acessar todo o conteúdo.")
        return

    # --- Se o código de ativação ainda não foi gerado, ofereça o envio ---
    if st.session_state['user_activation_code'] is None:
        st.info(f"O seu e-mail **{st.session_state['user_email']}** precisa ser verificado para liberar o acesso.")
        
        if st.button("Enviar E-mail de Ativação"):
            codigo = gerar_codigo_ativacao()
            
            if enviar_email_ativacao_sendgrid(
                destinatario=st.session_state['user_email'],
                nome_usuario=st.session_state['user_nome'],
                codigo=codigo
            ):
                st.session_state['email_sent'] = True 
                st.session_state['tentativas_codigo'] = 0 # Reinicia tentativas
                st.rerun()
            # Se o envio falhar, a mensagem de erro já foi exibida.
                
    # --- Se o e-mail foi enviado, peça o código ---
    if st.session_state.get('email_sent', False) and not st.session_state['user_verificado']:
        st.write(f"Enviamos o código para **{st.session_state['user_email']}**. Verifique sua caixa de entrada e insira-o abaixo.")
        
        with st.form(key="form_verificacao"):
            codigo_digitado = st.text_input("Insira o código de 6 dígitos:", max_chars=6)
            submit_button = st.form_submit_button("Ativar Conta")
            
            if submit_button:
                # Lógica de verificação do código
                if codigo_digitado == st.session_state['user_activation_code']:
                    st.session_state['user_verificado'] = True
                    st.session_state['user_activation_code'] = None # Limpa o código
                    st.success("✅ **Conta ativada com sucesso!** Redirecionando...")
                    st.balloons()
                    st.rerun()
                else:
                    st.session_state['tentativas_codigo'] = st.session_state.get('tentativas_codigo', 0) + 1
                    st.error(f"Código incorreto. Tentativas restantes: {3 - st.session_state['tentativas_codigo']}")
                    
                    if st.session_state['tentativas_codigo'] >= 3:
                         st.warning("Muitas tentativas. Por segurança, por favor, envie um novo código.")
                         st.session_state['email_sent'] = False
                         st.session_state['user_activation_code'] = None
                         st.rerun()

def tela_simulados():
    """Interface principal para a tela de Simulado."""
    """Interface principal para a tela de Simulado com acesso restrito a assinantes."""
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

##########################################################################################
#Pagamento

try:
    MP_ACCESS_TOKEN = st.secrets["MP_ACCESS_TOKEN"]
    # NOTA: Em produção real, você usaria o link do servidor Webhook para MP_NOTIFICATION_URL
    MP_NOTIFICATION_URL = st.secrets.get("MP_NOTIFICATION_URL", "https://exemplo.com/webhook")
except KeyError:
    st.error("ERRO: Credenciais do Mercado Pago não encontradas. Verifique seu secrets.toml.")
    MP_ACCESS_TOKEN = None

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


# --- Lógica Principal (Controle de Página) ---

def main():
    
    # Se o usuário NÃO está logado
    if not st.session_state['logged_in']:
        # Mostra as opções de Login e Cadastro na barra lateral
        pagina = st.sidebar.radio("Navegar", ["Login", "Cadastro"])
        
        if pagina == "Login":
            tela_login()
        elif pagina == "Cadastro":
            tela_cadastro()
            
    # Se o usuário ESTÁ logado
    else:
        st.sidebar.write(f"Bem-vindo(a), {st.session_state['user_nome']}!")
        
        if st.sidebar.button("Sair (Logout)"):
            st.session_state['logged_in'] = False
            st.session_state['user_email'] = None
            st.session_state['user_nome'] = None
            st.session_state['user_assinante'] = None
            st.info("Você foi desconectado.")
            st.rerun() # Recarrega para voltar à tela de Login
            
        # Mostra as telas do sistema logado
        pagina = st.sidebar.radio("Sistema", ["Curso","Simulados", "Pagamento"])
        
        if pagina == "Curso":
            tela_curso()
        elif pagina == "Simulados": 
            tela_simulados()
        elif pagina == "Pagamento":
            tela_pagamento()

if __name__ == '__main__':
    main()