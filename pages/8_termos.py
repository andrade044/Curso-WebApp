import streamlit as st
import os 
import requests
from auth import logout, verifica_assinante

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
    /* Esconde o link da página de Politica (Usando a capitalização 'politica') */
    [data-testid="stSidebarNav"] a[href*="politica"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Variáveis para substituição ---
NOME_EMPRESA = "[Nome da Sua Empresa/Plataforma]"
EMAIL_CONTATO = "[Seu Email de Contato]"
JURISDICAO = "[Jurisdição - Ex: República Federativa do Brasil]"

# --- Conteúdo da Política de Privacidade (em formato Markdown) ---
politica_privacidade_markdown = f"""
## 📄 Política de Privacidade (Rascunho Genérico)

---

### 1. Introdução

Esta Política de Privacidade descreve como **{NOME_EMPRESA}** ("nós", "nosso" ou "a Empresa") coleta, usa, armazena e protege as informações pessoais de seus usuários ("você"). Ao utilizar nossos serviços, você concorda com a coleta e uso de informações de acordo com esta política.

### 2. Informações que Coletamos

Podemos coletar diferentes tipos de informações para diversas finalidades, incluindo:

* **Dados Pessoais:** Nome, endereço de e-mail, número de telefone, endereço físico e outros dados de identificação.
* **Dados de Uso:** Informações sobre como o serviço é acessado e usado (endereço IP, tipo de navegador, páginas visitadas, tempo de permanência, etc.).
* **Dados de Rastreamento & Cookies:** Usamos cookies e tecnologias de rastreamento semelhantes para rastrear a atividade em nosso Serviço e manter certas informações.

### 3. Uso dos Dados

Os dados coletados podem ser utilizados para:

* Fornecer e manter o Serviço.
* Gerenciar sua conta e fornecer suporte.
* Melhorar, personalizar e expandir nosso Serviço.
* Comunicar sobre alterações no Serviço.
* Realizar análises ou fornecer informações de marketing/publicidade.
* Monitorar o uso do Serviço e prevenir problemas técnicos.

### 4. Compartilhamento e Divulgação de Dados

Não vendemos, trocamos ou transferimos seus Dados Pessoais para terceiros, exceto nas seguintes situações:

* **Com Provedores de Serviço:** Podemos empregar empresas e indivíduos terceirizados para facilitar nosso Serviço.
* **Para Cumprimento da Lei:** Podemos divulgar seus Dados Pessoais se exigido por lei ou em resposta a solicitações válidas de autoridades públicas.
* **Transferência de Negócios:** Em caso de fusão, aquisição ou venda de ativos.

### 5. Segurança dos Dados

A segurança dos seus dados é importante para nós, mas lembre-se que nenhum método de transmissão pela Internet ou método de armazenamento eletrônico é 100% seguro. Para exercer seus direitos, entre em contato conosco em **{EMAIL_CONTATO}**.

---
"""

# --- Conteúdo dos Termos de Uso (em formato Markdown) ---
termos_uso_markdown = f"""
## 📜 Termos de Uso (Rascunho Genérico)

---

### 1. Aceitação dos Termos

Ao acessar ou usar o serviço operado por **{NOME_EMPRESA}** ("o Serviço"), você concorda em cumprir e estar sujeito a estes Termos de Uso.

### 2. Uso do Serviço

O Serviço e seus conteúdos são destinados apenas para seu uso pessoal e não comercial. Você concorda em não reproduzir, duplicar, copiar, vender, revender ou explorar qualquer parte do Serviço sem nossa permissão expressa por escrito.

### 3. Contas de Usuário

* Você é responsável por manter a confidencialidade de sua conta e senha.
* Reservamo-nos o direito de suspender ou encerrar sua conta a nosso exclusivo critério.

### 4. Propriedade Intelectual

O Serviço e seu conteúdo original, recursos e funcionalidade são e continuarão sendo propriedade exclusiva de **{NOME_EMPRESA}**.

### 5. Conteúdo do Usuário

Ao enviar conteúdo para o Serviço (comentários, postagens, etc.), você nos concede uma licença para usar, reproduzir e distribuir esse conteúdo em conexão com o Serviço.

### 6. Limitação de Responsabilidade

Em nenhuma circunstância **{NOME_EMPRESA}** será responsável por quaisquer danos indiretos, incidentais, especiais, consequenciais ou punitivos resultantes do seu uso ou incapacidade de usar o Serviço.

### 7. Lei Aplicável e Jurisdição

Estes Termos serão regidos e interpretados de acordo com as leis de **{JURISDICAO}**.

---
"""

# -----------------------------------------------------
# --- Estrutura do Streamlit ---
# -----------------------------------------------------

st.title("Documentos Legais da Plataforma")

st.info("**ATENÇÃO:** Lembre-se de **substituir** os placeholders `[Nome da Sua Empresa/Plataforma]`, `[Seu Email de Contato]` e `[Jurisdição]` no código-fonte por suas informações reais e consultar um **advogado**.")

# Adiciona um seletor para que o usuário escolha qual documento quer ver
opcao = st.selectbox(
    "Selecione o documento que deseja visualizar:",
    ("Termos de Uso", "Política de Privacidade")
)

st.write("---")

if opcao == "Política de Privacidade":
    # Exibe o conteúdo da Política de Privacidade usando Markdown
    st.markdown(politica_privacidade_markdown, unsafe_allow_html=False)
elif opcao == "Termos de Uso":
    # Exibe o conteúdo dos Termos de Uso usando Markdown
    st.markdown(termos_uso_markdown, unsafe_allow_html=False)

st.button("Ir para cursos", key="hidden_button_termos", on_click=lambda: st.page_link("pages/4_Curso.py"))
st.button("Ir para simulados", key="hidden_button_politicas", on_click=lambda: st.switch_page("pages/5_Simulado.py"))