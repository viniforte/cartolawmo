import streamlit as st
import pandas as pd
import plotly.express as px

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

st.title("📊 Ranking Progressivo - Nome do time na linha")

# Criar coluna com rótulo apenas no último ponto da linha
df_long["Rotulo_Time"] = df_long.groupby("Time")["Rodada_Num"].transform(
    lambda x: x.eq(x.max())
)  # True no último ponto
df_long["Rotulo_Time"] = df_long.apply(
    lambda row: row["Time"] if row["Rotulo_Time"] else "", axis=1
)

# Somatório total para legenda
somas = df_long.groupby("Time")["Pontuação"].sum().to_dict()
df_long["Time_Label"] = df_long["Time"].apply(lambda t: f"{t} (Total: {somas[t]})")

# Seleção de times
times = st.multiselect(
    "Selecione os times",
    options=df_long["Time_Label"].unique(),
    default=df_long["Time_Label"].unique()
)
df_filtrado = df_long[df_long["Time_Label"].isin(times)]

# Gráfico
fig = px.line(
    df_filtrado,
    x="Rodada_Num",
    y="Posição",
    color="Time_Label",
    markers=True,
    line_group="Time_Label",
    text="Rotulo_Time",  # mostra nome apenas no último ponto
    hover_data=["Pontuação", "Pontuação_Acumulada"],
    title="Ranking Progressivo do Cartolas"
)

# Ajustes de rótulo e eixo
fig.update_traces(mode="lines+markers+text", textposition="middle right")
fig.update_yaxes(autorange="reversed", title="Posição a cada rodada")

# Layout
fig.update_layout(
    xaxis=dict(title="Rodadas"),
    legend=dict(
        title="Times",
        orientation="h",
        yanchor="bottom",
        y=-0.4,
        xanchor="center",
        x=0.5
    ),
    margin=dict(l=100, r=50, t=80, b=120)
)

st.plotly_chart(fig, use_container_width=True)
