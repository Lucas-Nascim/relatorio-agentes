import pandas as pd
import streamlit as st
from datetime import datetime

# Configurar página
st.set_page_config(page_title="Relatório de Agentes", layout="wide")

st.title("📊 Relatório de Agentes - TMA")

# Cache com refresh automático a cada 5 minutos
@st.cache_data(ttl=300)
def carregar_dados():
    df = pd.read_excel(r'C:\Users\cliente\OneDrive\Desktop\Excel\02 - Cases\Base_DBM.xlsx', sheet_name='dados')
    return df

# Carregar dados
df = carregar_dados()

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

# Converte TMA para hh:mm:ss
def segundos_para_hms(segundos):
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segs = int(segundos % 60)
    return f'{horas:02d}:{minutos:02d}:{segs:02d}'

totais_por_grupo['TMA'] = totais_por_grupo['TMA'].apply(segundos_para_hms)
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
