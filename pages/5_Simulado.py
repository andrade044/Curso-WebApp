import streamlit as st
import os 
from dotenv import load_dotenv
import pandas as pd 
import numpy as np

# from api_mercadopago import api_pagamento
from data import SIMULADO_DATA

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
TITULO_ASSINATURA = "Assinatura Premium do Curso de Python"

CHAVE_API_SENDGRID = get_secret('CHAVE_API_SENDGRID')
EMAIL_REMETENTE = get_secret('EMAIL_REMETENTE')
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
    global SIMULADO_DATA # Garante que a variável SIMULADO_DATA está no escopo

    # 1. Se o usuário respondeu, verifica e atualiza o score
    if st.session_state.get('user_answer') is not None:
        
        # Pega a pergunta atual antes de avançar o índice
        pergunta_atual = SIMULADO_DATA[st.session_state['current_question']]
        
        # Verifica se a resposta está correta
        if st.session_state['user_answer'] == pergunta_atual['resposta_correta']:
            st.session_state['score'] += 1
            st.toast("✅ Resposta Correta!", icon='👍')
        else:
            st.toast(f"❌ Resposta Incorreta. A correta era: {pergunta_atual['resposta_correta']}", icon='👎')
    
    # 2. Avança para o próximo índice
    st.session_state['current_question'] += 1
    st.session_state['user_answer'] = None # Limpa a resposta do usuário para a próxima pergunta

    # 3. Verifica se o simulado terminou
    if st.session_state['current_question'] >= len(SIMULADO_DATA):
        st.session_state['quiz_finished'] = True


# --- Lógica para o caminho do arquivo (necessária fora da função cacheada) ---
dir_atual_script = os.path.dirname(os.path.abspath(__file__))
CAMINHO_CSV = os.path.join(dir_atual_script, '..', 'todos_simulados.csv')


@st.cache_data
def load_all_simulados_data(file_mtime):
    """
    Carrega o arquivo CSV, transforma os dados e os agrupa por 'simulado_id'.
    O argumento `file_mtime` força o recarregamento do cache se o arquivo mudar.
    """
    try:
        if not os.path.exists(CAMINHO_CSV):
             st.error(f"Arquivo CSV não encontrado no caminho: {CAMINHO_CSV}")
             return {}
             
        # Tenta ler o arquivo.
        df = pd.read_csv(CAMINHO_CSV, 
                         sep=',', 
                         engine='python', 
                         on_bad_lines='skip')

        # Assegura que o DataFrame tem a estrutura correta (após a correção de CSV)
        colunas_esperadas = ['simulado_id', 'id', 'pergunta', 'opcoes_A', 'opcoes_B', 'opcoes_C', 'opcoes_D', 'resposta_correta', 'pontuacao', 'imagens_locais']
        
        if df.shape[1] > len(colunas_esperadas):
            df = df.iloc[:, :len(colunas_esperadas)]
        
        if df.shape[1] == len(colunas_esperadas):
            df.columns = colunas_esperadas
        else:
            st.error(f"O carregamento resultou em {df.shape[1]} colunas, o que é insuficiente. Esperado: {len(colunas_esperadas)}. Verifique o cabeçalho do CSV.")
            return {}
        
        # Alerta se poucas questões forem carregadas (agora que o CSV foi corrigido)
        if df.empty or df.shape[0] < 5: 
            st.warning(
                f"Atenção: Apenas {df.shape[0]} linhas foram carregadas. Embora o formato CSV pareça correto, "
                f"o número de questões ainda está baixo. Verifique se o seu arquivo 'todos_simulados.csv' "
                f"possui realmente todas as 60 linhas."
            )

        df = df.fillna('')
        
        # 🟢 PASSO CRÍTICO: Agrupar por Simulados
        simulados_agrupados = {}
        
        lista_de_simulados = df['simulado_id'].unique()

        for simulado_nome in lista_de_simulados:
            df_simulado = df[df['simulado_id'] == simulado_nome]
            simulado_data_list = []
            
            for index, row in df_simulado.iterrows():
                
                opcoes_dict = {
                    'A': row['opcoes_A'],
                    'B': row['opcoes_B'],
                    'C': row['opcoes_C'],
                    'D': row['opcoes_D']
                }
                
                imagens = row.get('imagens_locais', '')
                if isinstance(imagens, str) and imagens:
                    imagens_list = [img.strip() for img in imagens.split(';') if img.strip()]
                else:
                    imagens_list = []
                
                question_dict = {
                    'id': row['id'],
                    'pergunta': row['pergunta'],
                    'opcoes': opcoes_dict,
                    'resposta_correta': row['resposta_correta'],
                    'pontuacao': row.get('pontuacao', 1),
                    'imagens_locais': imagens_list
                }
                
                simulado_data_list.append(question_dict)
            
            simulados_agrupados[simulado_nome] = simulado_data_list
            
        return simulados_agrupados

    except Exception as e:
        st.error(f"Erro fatal ao carregar os dados do simulado. Detalhe: {e}")
        return {}

# --- LÓGICA DE CARREGAMENTO PARA FORÇAR O CACHE ---
file_mtime = None
if os.path.exists(CAMINHO_CSV):
    file_mtime = os.path.getmtime(CAMINHO_CSV)

SIMULADOS_DATA_AGRUPADOS = load_all_simulados_data(file_mtime)
# --- FIM DA LÓGICA DE CARREGAMENTO ---


def tela_simulados():
    """Interface principal para a tela de Simulado com acesso restrito a assinantes."""
    

    
    # --- 2. CONTEÚDO DA PÁGINA (Apenas executa se a guarda passar) ---
    st.title("Página de Simulados")

    # A linha que estava dando erro, agora segura:
    st.title("🧠 Simulado de Conhecimento")

    # ------------------ VERIFICAÇÃO DE ACESSO (NOVA LÓGICA) ------------------
    if not verifica_assinante():
        st.warning("🔒 **ACESSO RESTRITO.**")
        st.subheader("Para realizar os simulados, você precisa ser um Assinante Premium.")
        st.info("Acesse a aba 'Pagamento' para liberar este conteúdo.")
        return # Interrompe a função aqui, não exibindo o quiz.
    
    # --------------------------------------------------------------------------
    if not SIMULADOS_DATA_AGRUPADOS:
        st.error("Nenhum simulado carregado. Verifique o arquivo CSV e o erro acima.")
        return

    # 1. PERMITE O USUÁRIO ESCOLHER O SIMULADO
    nomes_dos_simulados = list(SIMULADOS_DATA_AGRUPADOS.keys())
    
    # Inicializa o nome do simulado selecionado no estado da sessão
    if 'selected_simulado' not in st.session_state:
        st.session_state['selected_simulado'] = nomes_dos_simulados[0]
        
    simulado_escolhido = st.selectbox(
        "Selecione o Simulado:",
        options=nomes_dos_simulados,
        key='simulado_selector'
    )
    
    # 2. SE O SIMULADO MUDOU, REINICIA O ESTADO DO QUIZ
    if simulado_escolhido != st.session_state.get('current_simulado_name'):
        # Força o reinício se o simulado mudou
        st.session_state['current_simulado_name'] = simulado_escolhido
        reiniciar_simulado()
        st.stop() # Interrompe e recarrega para aplicar a mudança

    # 3. DEFINE OS DADOS DO SIMULADO ATUAL
    global SIMULADO_DATA
    SIMULADO_DATA = SIMULADOS_DATA_AGRUPADOS.get(simulado_escolhido, [])
    
    if not SIMULADO_DATA:
        st.warning("Simulado selecionado não possui questões.")
        return

    # Verifica o tamanho do simulado
    total_questoes = len(SIMULADO_DATA)
    if total_questoes < 5:
        st.warning(f"Simulado '{simulado_escolhido}' carregou apenas {total_questoes} questão(ões). Certifique-se de que o CSV está salvo corretamente.")

    # O restante do código de inicialização e lógica do quiz (reiniciar_simulado, proxima_pergunta, etc.)
    # deve ser adaptado para usar a variável global SIMULADO_DATA.

    if 'current_question' not in st.session_state or st.session_state.get('current_simulado_name') != simulado_escolhido:
        reiniciar_simulado()

    if 'current_question' not in st.session_state:
        reiniciar_simulado()
        
    # 3.2 Lógica de Finalização
    if st.session_state['quiz_finished']:
        total_questoes = len(SIMULADO_DATA)
        score_final = st.session_state['score']
        aprovado = score_final >= 21 # Critério de aprovação (70% de 30 questões)
        
        if aprovado:
            st.balloons()
            st.success(f"🎉 **APROVADO!** Você acertou {score_final} de {total_questoes}.")
        else:
            st.error(f"😔 **REPROVADO.** Você acertou {score_final} de {total_questoes}.")
        
        st.info("Para ser aprovado, você precisa de 70% de acertos (21/30).")
        
        if st.button("Fazer Novo Simulado"):
            reiniciar_simulado()

    # 3.3 Lógica de Exibição da Pergunta
    else:
        indice_atual = st.session_state['current_question']
        q = SIMULADO_DATA[indice_atual]
        
        # Título da Questão
        st.subheader(f"Questão {indice_atual + 1}/{len(SIMULADO_DATA)} ")
        st.markdown(f"**{q['pergunta']}**")
        
        # Exibe as opções (Radio Button)
        # O valor do radio button é a chave (A, B, C, D)
        resposta_selecionada = st.radio(
            "Sua Resposta:",
            options=q['opcoes'].keys(), 
            format_func=lambda key: f"{key} - {q['opcoes'][key]}", 
            key=f"radio_{q['id']}" # Garante uma chave única para o widget
        )
        
        # Armazena a resposta selecionada no state para uso na função de avanço
        st.session_state['user_answer'] = resposta_selecionada 

        # Botão para Avançar
        proxima_texto = "Finalizar Simulado" if indice_atual == len(SIMULADO_DATA) - 1 else "Próxima Questão"
        
        st.button(
            proxima_texto, 
            on_click=proxima_pergunta, 
            use_container_width=True,
            type="primary"
        )
        
        st.markdown("---")
        st.caption(f"Score atual: {st.session_state['score']}")     
    
    if st.button("Sair"):
        logout()
        
tela_simulados()
