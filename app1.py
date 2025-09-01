import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")  # Layout mais amplo

st.title("📊 Ranking Progressivo - Cartola FC")

# Carregar planilha
file_path = "Linha do tempo cartola 1.xlsx"
df = pd.read_excel(file_path)
df.rename(columns={df.columns[0]: "Time"}, inplace=True)

# Converter para formato long
df_long = df.melt(id_vars="Time", var_name="Rodada", value_name="Pontuação")
df_long = df_long.dropna(subset=["Pontuação"])
df_long = df_long[df_long["Pontuação"] > 0]
df_long["Rodada_Num"] = df_long["Rodada"].str.replace("Rodada ", "").astype(int)
df_long = df_long.sort_values(by=["Time", "Rodada_Num"])

# Pontuação acumulada
df_long["Pontuação_Acumulada"] = df_long.groupby("Time")["Pontuação"].cumsum()

# Ranking progressivo
df_long["Posição"] = df_long.groupby("Rodada_Num")["Pontuação_Acumulada"]\
    .rank(method="min", ascending=False).astype(int)

# Somatório total para legenda
somas = df_long.groupby("Time")["Pontuação"].sum().to_dict()
df_long["Time_Label"] = df_long["Time"].apply(lambda t: f"{t} (Total: {somas[t]})")

# Sidebar para filtros
times_selecionados = st.sidebar.multiselect(
    "Selecione os times",
    options=df_long["Time_Label"].unique(),
    default=df_long["Time_Label"].unique()
)

rodadas = st.sidebar.slider(
    "Escolha o número de rodadas",
    min_value=int(df_long["Rodada_Num"].min()),
    max_value=int(df_long["Rodada_Num"].max()),
    value=int(df_long["Rodada_Num"].max())
)

# Filtrar dados
df_filtrado = df_long[
    (df_long["Time_Label"].isin(times_selecionados)) &
    (df_long["Rodada_Num"] <= rodadas)
]

# Criar coluna com rótulo apenas no último ponto da linha
df_filtrado["Rotulo_Time"] = df_filtrado.groupby("Time")["Rodada_Num"].transform(
    lambda x: x.eq(x.max())
)
df_filtrado["Rotulo_Time"] = df_filtrado.apply(
    lambda row: row["Time"] if row["Rotulo_Time"] else "", axis=1
)

# Gráfico
fig = px.line(
    df_filtrado,
    x="Rodada_Num",
    y="Posição",
    color="Time_Label",
    markers=True,
    line_group="Time_Label",
    text="Rotulo_Time",
    hover_data=["Pontuação", "Pontuação_Acumulada"],
    title="Ranking Progressivo do Cartolas"
)

# Ajustes de rótulo e eixo
fig.update_traces(mode="lines+markers+text", textposition="middle right")
fig.update_yaxes(autorange="reversed", title="Posição a cada rodada")

# Layout maior
fig.update_layout(
    width=1200,
    height=700,
    xaxis=dict(title="Rodadas"),
    margin=dict(l=100, r=50, t=80, b=120)
)

st.plotly_chart(fig, use_container_width=True)