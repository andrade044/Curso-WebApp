import streamlit as st
import os 
import requests
from auth import logout, verifica_assinante, add_fixed_footer_button

def get_secret(key, default=None):
    
    if 'secrets' in st.session_state and key in st.secrets:
        return st.secrets[key]

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
BACKEND = get_secret("BACKEND")



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
    
    /* Esconde o link da página de termos (Usando a capitalização 'Termos') */
    [data-testid="stSidebarNav"] a[href*="termos"] {
        display: none !important;
    }

</style>
""", unsafe_allow_html=True)


if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.page_link("Home.py", label="Voltar para tela de login")
    st.stop()

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

nome_usuario = st.session_state['user_nome']

def tela_curso():
  
    """Conteúdo do Curso (Acesso Condicional e Protegido)."""

    if not st.session_state.get('user_nome'):
        st.error("Acesso negado. Por favor, faça login para acessar o Curso.")
        st.page_link("Home.py", label="Ir para a página de Login")
        st.stop()
        return
    

    nome_usuario = st.session_state['user_nome']
    
    st.title(f"🎓 Bem-vindo(a) ao Curso, {nome_usuario}!")
    
    # Mensagem de status consolidada
    if verifica_assinante():
        st.success("🎉 Conteúdo premium desbloqueado!")
    else:
        st.warning("🔒 Conteúdo premium bloqueado. Faça upgrade para acessar.")
        if st.button("💰 Desbloquear Conteúdo Premium Agora", use_container_width=True):
            st.switch_page("pages/6_Pagamento.py")

    st.markdown("---")

    # MÓDULO 1: CONTEÚDO GRATUITO
    with st.expander("📚 Módulo 1: Introdução e Primeiros Passos (Grátis)", expanded=True):
        st.info("Este conteúdo está liberado para todos os usuários.")

        # VÍDEO 1.1 (GRÁTIS)
        with st.expander("▶️ Aula 1.1: Boas Vindas"):
            st.video('https://www.youtube.com/watch?v=LIbALvdxXqM') 
            st.write("Descrição: Introdução ao tema e instalação das ferramentas necessárias.")
        
        # VÍDEO 1.2 (GRÁTIS)
        with st.expander("▶️ Aula 1.2: Explicando como funciona"):
            st.video('https://www.youtube.com/watch?v=VIDEO_GRATUITO_2_URL_AQUI') 
            st.write("Descrição: Conceitos fundamentais e a primeira linha de código.")

    st.markdown("---")
    st.header("Módulo 2: Conteúdo Avançado")

    # MÓDULO 2: CONTEÚDO PAGO
    if verifica_assinante():
        # CONTEÚDO LIBERADO
        with st.expander("📝 Módulo 2: Direção Defensiva", expanded=False):
            st.success("🎉 ACESSO LIBERADO! Desfrute do conteúdo exclusivo.")

            # VÍDEO 2.1 (PAGO)
            with st.expander("▶️ Aula 2.1: Introdução e conceito de direção defensiva"):
                st.write("Descrição: ")
                
                video_id = "e34640a9-b5e6-473c-b90e-cdbe143eb4f4"
        
                req = requests.get(f"{BACKEND}/video/{video_id}")
                data = req.json()

                iframe = f"""
                <iframe
                    src="{data['iframe']}"
                    width="100%"
                    height="450"
                    allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
                    allowfullscreen="true">
                </iframe>
                """

                st.components.v1.html(iframe, height=480)
            # VÍDEO 2.2 (PAGO)
            with st.expander("▶️ Aula 2.2: Condições adversas"):
                st.write("Descrição: .")
                
                video_id = "bbe1c1c7-7a49-4d87-8e1a-d7fa39b1307a"
        
                req = requests.get(f"{BACKEND}/video/{video_id}")
                data = req.json()

                iframe = f"""
                <iframe
                    src="{data['iframe']}"
                    width="100%"
                    height="450"
                    allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
                    allowfullscreen="true">
                </iframe>
                """

                st.components.v1.html(iframe, height=480)
                
            st.markdown("---")


            with st.expander("▶️ Aula 2.3: Derrapagens"):
                    st.write("Descrição: .")
                    
                    video_id = "69352220-2277-4fd1-815a-a253818398d7"
            
                    req = requests.get(f"{BACKEND}/video/{video_id}")
                    data = req.json()

                    iframe = f"""
                    <iframe
                        src="{data['iframe']}"
                        width="100%"
                        height="450"
                        allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
                        allowfullscreen="true">
                    </iframe>
                    """

                    st.components.v1.html(iframe, height=480)
                    
            st.markdown("---")
            
            
            with st.expander("▶️ Aula 2.4: Importância do cinto de segurança"):
                    st.write("Descrição: .")
                    
                    video_id = "9ea57e15-43b6-468a-bb2d-0732ff336ebe"
            
                    req = requests.get(f"{BACKEND}/video/{video_id}")
                    data = req.json()

                    iframe = f"""
                    <iframe
                        src="{data['iframe']}"
                        width="100%"
                        height="450"
                        allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
                        allowfullscreen="true">
                    </iframe>
                    """

                    st.components.v1.html(iframe, height=480)
                    
            st.markdown("---")

            with st.expander("▶️ Aula 2.5: Comportamentos seguros"):
                    st.write("Descrição: .")
                    
                    video_id = "91d9841c-a3e3-460b-8f17-771f386049bc"
            
                    req = requests.get(f"{BACKEND}/video/{video_id}")
                    data = req.json()

                    iframe = f"""
                    <iframe
                        src="{data['iframe']}"
                        width="100%"
                        height="450"
                        allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
                        allowfullscreen="true">
                    </iframe>
                    """

                    st.components.v1.html(iframe, height=480)
                    
            st.markdown("---")

            with st.expander("▶️ Aula 2.6: Importância do cinto de segurança"):
                    st.write("Descrição: .")
                    
                    video_id = "9ea57e15-43b6-468a-bb2d-0732ff336ebe"
            
                    req = requests.get(f"{BACKEND}/video/{video_id}")
                    data = req.json()

                    iframe = f"""
                    <iframe
                        src="{data['iframe']}"
                        width="100%"
                        height="450"
                        allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
                        allowfullscreen="true">
                    </iframe>
                    """

                    st.components.v1.html(iframe, height=480)
                    
            st.markdown("---")




            # st.write("Material complementar e exercícios práticos do Módulo 2.")

        with st.expander("📝 Módulo 3: Legislação de trânsito ", expanded=False):
            
            with st.expander("▶️ Aula 3.1: Introdução a direção defensiva"):
                st.video('https://www.youtube.com/watch?v=f5R-6Pp2w5E') 
                st.write("Descrição: Tudo sobre Legislação de Transito.")

            with st.expander("▶️ Aula 3.2: Legislação Generico!"):

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
           
            with st.expander("▶️ Aula 4.1: Introdução a Primeiros socorros!"):
                st.video('https://www.youtube.com/watch?v=f5R-6Pp2w5E') 
                st.write("Descrição: Tudo sobre Legislação de Transito.")

            with st.expander("▶️ Aula 4.2: Legislação Generico!"):

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
        
            with st.expander("▶️ Aula 5.1: Introdução a Mecânica Básica !"):
                st.video('https://www.youtube.com/watch?v=f5R-6Pp2w5E') 
                st.write("Descrição: Tudo sobre Legislação de Transito.")

            with st.expander("▶️ Aula 5.2: Mecânica Generica !"):

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

            with st.expander("▶️ Aula 6.1: Introdução a Meio ambiente !"):
                st.video('https://www.youtube.com/watch?v=f5R-6Pp2w5E') 
                st.write("Descrição: Tudo sobre Legislação de Transito.")

            with st.expander("▶️ Aula 6.2: Meio Ambiente Generica !"):

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

    if st.button("Ir aos Simulados"):
        st.switch_page("pages/5_Simulado.py")

    if st.button("Sair da Conta",
                 type="primary"): 
        logout()
        st.success("Você saiu da conta. Redirecionando...")
        st.switch_page("Home.py") 
        st.stop()

add_fixed_footer_button(
    termos_link="https://autoescolaemvideo.streamlit.app/termos",
    politicas_link="https://autoescolaemvideo.streamlit.app/termos"
)
    
tela_curso()