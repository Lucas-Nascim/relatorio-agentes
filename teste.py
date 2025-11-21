import pandas as pd
import streamlit as st
from datetime import datetime
from pathlib import Path
from auth import login, logout, obter_usuario_atual

# Configurar página (será reconfigurado após login)
st.set_page_config(page_title="Relatório de Agentes", layout="wide")

# Verificar autenticação
if not login():
    st.stop()

# Reconfigura página após login bem-sucedido
st.set_page_config(page_title="Relatório de Agentes", layout="wide")

# Obter usuário atual
usuario_atual = obter_usuario_atual()

st.title("📊 Relatório de Agentes - TMA")

# Exibir informações do usuário logado na barra lateral
with st.sidebar:
    st.markdown(f"**👤 Usuário:** {usuario_atual['name']}")
    st.markdown(f"**📧 Email:** {usuario_atual['email']}")
    st.markdown(f"**💼 Cargo:** {usuario_atual['role']}")
    st.markdown("---")
    if st.button("🚪 Logout"):
        logout()

# Local esperado do arquivo dentro do repositório (relativo ao arquivo Python)
DATA_PATH = Path(__file__).parent / "data" / "Base_DBM.xlsx"
CSV_PATH = Path(__file__).parent / "data" / "Base_DBM.csv"


# função pura para ler o excel (cacheável)
@st.cache_data(ttl=300)
def carregar_dados_de_buffer(buffer):
    # buffer pode ser um caminho (str/Path) ou um file-like (uploaded)
    return pd.read_excel(buffer, sheet_name='dados')


def obter_dados():
    # 1) se existir arquivo em data/, usa ele
    if DATA_PATH.exists():
        try:
            return carregar_dados_de_buffer(DATA_PATH)
        except Exception as e:
            st.error(f"Erro ao ler '{DATA_PATH}': {e}")

    # 1b) se existir CSV de exemplo, usa ele (útil para deploy/ambientes sem Excel)
    if CSV_PATH.exists():
        try:
            return pd.read_csv(CSV_PATH)
        except Exception as e:
            st.error(f"Erro ao ler '{CSV_PATH}': {e}")

    # 2) senão, solicitar upload do arquivo pelo usuário
    st.warning("Arquivo de dados não encontrado em 'data/Base_DBM.xlsx'. Faça upload do arquivo Excel (.xlsx) usado pelo app.")
    uploaded = st.file_uploader("Faça upload do Base_DBM.xlsx (sheet: 'dados')", type=["xlsx"])
    if uploaded is None:
        st.info("Aguardando upload do arquivo para continuar.")
        st.stop()

    try:
        # se o usuário enviou um xlsx, o buffer será lido pela função cacheada
        if uploaded.name.lower().endswith('.csv'):
            return pd.read_csv(uploaded)
        return carregar_dados_de_buffer(uploaded)
    except Exception as e:
        st.error(f"Erro ao ler arquivo enviado: {e}")
        st.stop()


# Carregar dados
df = obter_dados()

colunas_tempo = [
    'Tempo_em_Servico', 'Tempo_DAC', 'Tempo_POS_AT', 'Tempo_tocando', 
    'Tempo_Ramal_Entrada', 'Tempo_Ramal_Saida', 'Tempo_Disponivel', 
    'Tempo_em_PAUSA'
]

colunas_chams = [
    'Chams_DAC', 'Chams_Ramal_Entrada', 'Chams_Ramal_Saida'
]

# Agrupa e soma
totais_por_grupo = df.groupby('Nome_do_Agente')[colunas_tempo + colunas_chams].sum()

# Calcula TMA
totais_por_grupo['TMA'] = (totais_por_grupo['Tempo_DAC'] + totais_por_grupo['Tempo_POS_AT'] + totais_por_grupo['Tempo_Ramal_Saida']) / totais_por_grupo['Chams_DAC']

# Filtra agentes válidos
totais_por_grupo = totais_por_grupo[(totais_por_grupo['Chams_DAC'] > 0) & 
                                    (totais_por_grupo['Tempo_DAC'] > 0) & 
                                    (totais_por_grupo['Tempo_POS_AT'] > 0) & 
                                    (totais_por_grupo['Tempo_Ramal_Saida'] > 0)]

totais_por_grupo['TMA'] = totais_por_grupo['TMA'].fillna(0)

# Calcula TMA médio ANTES de converter para hh:mm:ss
tma_medio_segundos = totais_por_grupo['TMA'].mean()


# Converte TMA para hh:mm:ss com proteção para valores inválidos/NaN
def segundos_para_hms(segundos):
    try:
        segundos = float(segundos)
    except Exception:
        segundos = 0
    if pd.isna(segundos):
        segundos = 0
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segs = int(segundos % 60)
    return f'{horas:02d}:{minutos:02d}:{segs:02d}'

totais_por_grupo['TMA'] = totais_por_grupo['TMA'].apply(segundos_para_hms)

# proteger caso média seja NaN
if pd.isna(tma_medio_segundos):
    tma_medio_segundos = 0

tma_medio_formatado = segundos_para_hms(tma_medio_segundos)

# Seleciona apenas as colunas desejadas
resultado = totais_por_grupo[['Chams_DAC', 'TMA']]

# Exibe métricas
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total de Agentes", len(resultado))
with col2:
    st.metric("Total de Chamadas", resultado['Chams_DAC'].sum())
with col3:
    st.metric("Chamadas Médias", int(resultado['Chams_DAC'].mean()))
with col4:
    st.metric("TMA Médio", tma_medio_formatado)

# Botão de refresh manual
if st.button("🔄 Atualizar Dados Agora"):
    st.cache_data.clear()
    st.rerun()

# Exibe tabela
st.dataframe(resultado, use_container_width=True)

# Rodapé com data/hora
st.caption(f"⏱️ Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
