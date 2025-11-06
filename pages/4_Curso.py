import streamlit as st
import os 
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

st.set_page_config(
    page_title="Curso",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Adiciona um CSS para esconder os botões de menu e footer, se necessário
# st.markdown("""
# <style>
#     #MainMenu {visibility: hidden;}
#     footer {visibility: hidden;}
#     header {visibility: hidden;}
# </style>
# """, unsafe_allow_html=True)

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


if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.page_link("Home.py", label="Voltar para tela de login")
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

nome_usuario = st.session_state['user_nome']

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
    
    # Mensagem de status consolidada
    if verifica_assinante():
        st.success("🎉 Conteúdo premium desbloqueado!")
    else:
        st.warning("🔒 Conteúdo premium bloqueado. Faça upgrade para acessar.")
        if st.button("💰 Desbloquear Conteúdo Premium Agora", use_container_width=True):
            st.switch_page("pages/6_Pagamento.py")
    # 2.2. Botão de Logout (Consolidado)

    st.markdown("---")

    # 3. MÓDULO 1: CONTEÚDO GRATUITO
    with st.expander("📚 Módulo 1: Introdução e Primeiros Passos (Grátis)", expanded=True):
        st.info("Este conteúdo está liberado para todos os usuários.")

        # VÍDEO 1.1 (GRÁTIS)
        with st.expander("▶️ Aula 1.1: Boas Vindas"):
            # Nota: Este link parece ser de uma playlist. Streamlit pode não tocar a playlist.
            st.video('https://www.youtube.com/watch?v=LIbALvdxXqM') 
            st.write("Descrição: Introdução ao tema e instalação das ferramentas necessárias.")
        
        # VÍDEO 1.2 (GRÁTIS)
        with st.expander("▶️ Aula 1.2: Explicando como funciona"):
            # Substitua 'VIDEO_GRATUITO_2' pela URL real do vídeo
            st.video('https://www.youtube.com/watch?v=VIDEO_GRATUITO_2_URL_AQUI') 
            st.write("Descrição: Conceitos fundamentais e a primeira linha de código.")

    st.markdown("---")
    st.header("Módulo 2: Conteúdo Avançado")

    # 4. MÓDULO 2: CONTEÚDO PAGO (Acesso Condicional)
    if verifica_assinante():
        # CONTEÚDO LIBERADO
        with st.expander("📝 Módulo 2: Direção Defensiva", expanded=False):
            st.success("🎉 ACESSO LIBERADO! Desfrute do conteúdo exclusivo.")
            
            # VÍDEO 2.1 (PAGO)
            with st.expander("▶️ Aula 2.1: Introdução a direção defensiva"):
                st.video('https://www.youtube.com/watch?v=f5R-6Pp2w5E') 
                st.write("Descrição: Detalhamento sobre hasheamento de senhas e proteção contra ameaças.")

            # VÍDEO 2.2 (PAGO)
            with st.expander("▶️ Aula 2.2: Integração com Bancos NoSQL e Desempenho"):
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


        with st.expander("📝 Módulo 3: Legislação de trânsito ", expanded=False):
            # st.success("🎉 ACESSO LIBERADO! Desfrute do conteúdo exclusivo.")
            
            with st.expander("▶️ Aula 3.1: Introdução a direção defensiva"):
                st.video('https://www.youtube.com/watch?v=f5R-6Pp2w5E') 
                st.write("Descrição: Tudo sobre Legislação de Transito.")

            # VÍDEO 2.2 (PAGO)
            with st.expander("▶️ Aula 3.2: Legislação Generico!"):
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
            st.write("Material complementar e exercícios práticos do Módulo 3.")


        with st.expander("📝 Módulo 4: Primeiros socorros ", expanded=False):
            # st.success("🎉 ACESSO LIBERADO! Desfrute do conteúdo exclusivo.")
            
            with st.expander("▶️ Aula 4.1: Introdução a Primeiros socorros!"):
                st.video('https://www.youtube.com/watch?v=f5R-6Pp2w5E') 
                st.write("Descrição: Tudo sobre Legislação de Transito.")

            # VÍDEO 2.2 (PAGO)
            with st.expander("▶️ Aula 4.2: Legislação Generico!"):
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
            st.write("Material complementar e exercícios práticos do Módulo 4.")


        with st.expander("📝 Módulo 5: Mecânica ", expanded=False):
            # st.success("🎉 ACESSO LIBERADO! Desfrute do conteúdo exclusivo.")
            
            with st.expander("▶️ Aula 5.1: Introdução a Mecânica Básica !"):
                st.video('https://www.youtube.com/watch?v=f5R-6Pp2w5E') 
                st.write("Descrição: Tudo sobre Legislação de Transito.")

            # VÍDEO 2.2 (PAGO)
            with st.expander("▶️ Aula 5.2: Mecânica Generica !"):
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
            st.write("Material complementar e exercícios práticos do Módulo 5.")


        with st.expander("📝 Módulo 6: Meio ambiente e cidadania ", expanded=False):
            # st.success("🎉 ACESSO LIBERADO! Desfrute do conteúdo exclusivo.")
            
            with st.expander("▶️ Aula 6.1: Introdução a Meio ambiente !"):
                st.video('https://www.youtube.com/watch?v=f5R-6Pp2w5E') 
                st.write("Descrição: Tudo sobre Legislação de Transito.")

            # VÍDEO 2.2 (PAGO)
            with st.expander("▶️ Aula 6.2: Meio Ambiente Generica !"):
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
            st.write("Material complementar e exercícios práticos do Módulo 6.")
         


    else:
        # CONTEÚDO BLOQUEADO
        with st.expander("🔒 Módulo 2, 3, 4, 5, 6: Conteúdo Avançado e Práticas Profissionais (Bloqueado)"):
            st.warning("🔒 **CONTEÚDO EXCLUSIVO PARA ASSINANTES.**")
            st.write("Adquira sua assinatura para liberar este e outros módulos avançados.")

    if st.button("Sair da Conta",
                 type="primary"):
        logout()
        st.success("Você saiu da conta. Redirecionando...")
        # Usa switch_page para redirecionar para o login/home
        st.switch_page("Home.py") 
        st.stop()

    
tela_curso()