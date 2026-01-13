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

video_id_1 = get_secret("video_id_1")
video_id_2 = get_secret("video_id_2")
video_id_3 = get_secret("video_id_3")
video_id_4 = get_secret("video_id_4")
video_id_5 = get_secret("video_id_5")
video_id_6 = get_secret("video_id_6")

video_id_7 =  get_secret("video_id_7")
video_id_8 = get_secret("video_id_8")
video_id_9 = get_secret("video_id_9")
video_id_10 = get_secret("video_id_10")
video_id_11 = get_secret("video_id_11")
video_id_12 = get_secret("video_id_12")
video_id_13 = get_secret("video_id_13")
video_id_14 = get_secret("video_id_14")






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
        
                req = requests.get(f"{BACKEND}/video/{video_id_1}")
                data = req.json()

                iframe = f"""
                            <iframe
                                src="{data['iframe']}"
                                width="100%"
                                height="450"
                                allow="accelerometer; gyroscope; encrypted-media; picture-in-picture"
                                allowfullscreen="true">
                            </iframe>
                        """

                st.components.v1.html(iframe, height=480)
            # VÍDEO 2.2 (PAGO)
            with st.expander("▶️ Aula 2.2: Condições adversas"):
                st.write("Descrição: .")

                req = requests.get(f"{BACKEND}/video/{video_id_2}")
                data = req.json()

                iframe = f"""
                            <iframe
                                src="{data['iframe']}"
                                width="100%"
                                height="450"
                                allow="accelerometer; gyroscope; encrypted-media; picture-in-picture"
                                allowfullscreen="true">
                            </iframe>
                        """

                st.components.v1.html(iframe, height=480)
                
            st.markdown("---")


            with st.expander("▶️ Aula 2.3: Derrapagens"):
                    st.write("Descrição: .")
            
                    req = requests.get(f"{BACKEND}/video/{video_id_3}")
                    data = req.json()

                    iframe = f"""
                            <iframe
                                src="{data['iframe']}"
                                width="100%"
                                height="450"
                                allow="accelerometer; gyroscope; encrypted-media; picture-in-picture"
                                allowfullscreen="true">
                            </iframe>
                        """

                    st.components.v1.html(iframe, height=480)
                    
            st.markdown("---")
            
            
            with st.expander("▶️ Aula 2.4: Importância do cinto de segurança"):
                    st.write("Descrição: .")
            
                    req = requests.get(f"{BACKEND}/video/{video_id_4}")
                    data = req.json()

                    iframe = f"""
                            <iframe
                                src="{data['iframe']}"
                                width="100%"
                                height="450"
                                allow="accelerometer; gyroscope; encrypted-media; picture-in-picture"
                                allowfullscreen="true">
                            </iframe>
                        """

                    st.components.v1.html(iframe, height=480)
                    
            st.markdown("---")

            with st.expander("▶️ Aula 2.5: Comportamentos seguros"):
                    st.write("Descrição: .")
                    
                    req = requests.get(f"{BACKEND}/video/{video_id_5}")
                    data = req.json()

                    iframe = f"""
                            <iframe
                                src="{data['iframe']}"
                                width="100%"
                                height="450"
                                allow="accelerometer; gyroscope; encrypted-media; picture-in-picture"
                                allowfullscreen="true">
                            </iframe>
                        """

                    st.components.v1.html(iframe, height=480)
                    
            st.markdown("---")

            with st.expander("▶️ Aula 2.6: Importância do cinto de segurança"):
                    st.write("Descrição: .")
            
                    req = requests.get(f"{BACKEND}/video/{video_id_6}")
                    data = req.json()

                    iframe = f"""
                            <iframe
                                src="{data['iframe']}"
                                width="100%"
                                height="450"
                                allow="accelerometer; gyroscope; encrypted-media; picture-in-picture"
                                allowfullscreen="true">
                            </iframe>
                        """

                    st.components.v1.html(iframe, height=480)
                    
            st.markdown("---")

            # st.write("Material complementar e exercícios práticos do Módulo 2.")

        with st.expander("📝 Módulo 3: Legislação de trânsito ", expanded=False):
            
            with st.expander("▶️ Aula 3.1: Legislação de trânsito - Parte 1"):
                st.write("Descrição: .")
            
                req = requests.get(f"{BACKEND}/video/{video_id_7}")
                data = req.json()

                iframe = f"""
                            <iframe
                                src="{data['iframe']}"
                                width="100%"
                                height="450"
                                allow="accelerometer; gyroscope; encrypted-media; picture-in-picture"
                                allowfullscreen="true">
                            </iframe>
                        """

                st.components.v1.html(iframe, height=480)
                    
            st.markdown("---")

            with st.expander("▶️ Aula 3.2: Legislação de trânsito - Parte 2"):
                st.write("Descrição: Categorias  A e B")
            
                req = requests.get(f"{BACKEND}/video/{video_id_8}")
                data = req.json()

                iframe = f"""
                            <iframe
                                src="{data['iframe']}"
                                width="100%"
                                height="450"
                                allow="accelerometer; gyroscope; encrypted-media; picture-in-picture"
                                allowfullscreen="true">
                            </iframe>
                        """

                st.components.v1.html(iframe, height=480)
                    
            st.markdown("---")
            
            with st.expander("▶️ Aula 3.3: Legislação de trânsito - Parte 3"):
                st.write("Descrição: Categorias  C,D e E")
            
                req = requests.get(f"{BACKEND}/video/{video_id_9}")
                data = req.json()

                iframe = f"""
                            <iframe
                                src="{data['iframe']}"
                                width="100%"
                                height="450"
                                allow="accelerometer; gyroscope; encrypted-media; picture-in-picture"
                                allowfullscreen="true">
                            </iframe>
                        """

                st.components.v1.html(iframe, height=480)
                    
            st.markdown("---")

            with st.expander("▶️ Aula 3.4: Legislação de trânsito - Parte 4"):
                st.write("Descrição: Maneiras de estacionar corretamente.")
            
                req = requests.get(f"{BACKEND}/video/{video_id_10}")
                data = req.json()

                iframe = f"""
                            <iframe
                                src="{data['iframe']}"
                                width="100%"
                                height="450"
                                allow="accelerometer; gyroscope; encrypted-media; picture-in-picture"
                                allowfullscreen="true">
                            </iframe>
                        """

                st.components.v1.html(iframe, height=480)
                    
            st.markdown("---")

            with st.expander("▶️ Aula 3.5: Legislação de trânsito - Parte 5"):
                st.write("Descrição: IPVA e acc.")
            
                req = requests.get(f"{BACKEND}/video/{video_id_11}")
                data = req.json()

                iframe = f"""
                            <iframe
                                src="{data['iframe']}"
                                width="100%"
                                height="450"
                                allow="accelerometer; gyroscope; encrypted-media; picture-in-picture"
                                allowfullscreen="true">
                            </iframe>
                        """

                st.components.v1.html(iframe, height=480)
                    
            st.markdown("---")

            with st.expander("▶️ Aula 3.6: Legislação de trânsito - Parte 6"):
                st.write("Descrição: Maneiras corretas de circulação.")
            
                req = requests.get(f"{BACKEND}/video/{video_id_12}")
                data = req.json()

                iframe = f"""
                            <iframe
                                src="{data['iframe']}"
                                width="100%"
                                height="450"
                                allow="accelerometer; gyroscope; encrypted-media; picture-in-picture"
                                allowfullscreen="true">
                            </iframe>
                        """

                st.components.v1.html(iframe, height=480)
                    
            st.markdown("---")

            with st.expander("▶️ Aula 3.7: Legislação de trânsito - Parte 7"):
                st.write("Descrição: Manobras de mudança de direção.")
            
                req = requests.get(f"{BACKEND}/video/{video_id_13}")
                data = req.json()

                iframe = f"""
                            <iframe
                                src="{data['iframe']}"
                                width="100%"
                                height="450"
                                allow="accelerometer; gyroscope; encrypted-media; picture-in-picture"
                                allowfullscreen="true">
                            </iframe>
                        """

                st.components.v1.html(iframe, height=480)
                    
            st.markdown("---")

            with st.expander("▶️ Aula 3.8: Legislação de trânsito - Parte 8"):
                st.write("Descrição: Classificação das Vias.")
            
                req = requests.get(f"{BACKEND}/video/{video_id_14}")
                data = req.json()

                iframe = f"""
                            <iframe
                                src="{data['iframe']}"
                                width="100%"
                                height="450"
                                allow="accelerometer; gyroscope; encrypted-media; picture-in-picture"
                                allowfullscreen="true">
                            </iframe>
                        """

                st.components.v1.html(iframe, height=480)
                    
            st.markdown("---")

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
    termos_link="https://autoescolaemvideo.onrender.com/termos"
)

link_whatsapp = "https://wa.me/5599999999999?text=Ol%C3%A1%2C%20preciso%20de%20suporte%20sobre%20o%20curso%20online."

# Código HTML e CSS corrigido para posicionamento fixo (fixed)
html_code_fixed = f"""
<div style="
    /* Posicionamento Fixo */
    position: fixed;
    bottom: 20px; /* Distância do fundo da página */
    right: 20px; /* Distância da direita da página */
    z-index: 1000; /* Garante que fique acima de outros elementos */
">
    <a href="{link_whatsapp}" target="_blank" style="
        /* Estilo do Botão */
        display: inline-flex; /* Usar flex para centralizar o conteúdo se adicionar um ícone */
        align-items: center;
        padding: 10px 20px;
        background-color: #25D366; /* Cor do WhatsApp */
        color: white;
        text-decoration: none;
        border-radius: 30px; /* Deixa o botão mais arredondado */
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Sombra para destacar */
        transition: background-color 0.3s;
    ">
        💬 Fale com o Suporte
    </a>
</div>
"""

# Injeta o código HTML/CSS na página
st.html(html_code_fixed)

tela_curso()