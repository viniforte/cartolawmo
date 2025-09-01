import streamlit as st
import pandas as pd
# libs do plotly
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 Ranking Progressivo - Cartola FC")

# Carregar planilha
file_path = "Linha do tempo cartola 1.xlsx"
df = pd.read_excel(file_path)
df.rename(columns={df.columns[0]: "Time"}, inplace=True)

# Converter para formato long
df_long = df.melt(id_vars="Time", var_name="Rodada", value_name="Pontuação")
df_long = df_long.dropna(subset=["Pontuação"])
df_long = df_long[df_long["Pontuação"] > 0]
df_long["Rodada"] = df_long["Rodada"].str.replace("Rodada ", "").astype(int)
df_long = df_long.sort_values(by=["Time", "Rodada"])

# Pontuação acumulada
df_long["Pontuação_Acumulada"] = df_long.groupby("Time")["Pontuação"].cumsum()

# Ranking progressivo
df_long["Posição"] = df_long.groupby("Rodada")["Pontuação_Acumulada"]\
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
    min_value=int(df_long["Rodada"].min()),
    max_value=int(df_long["Rodada"].max()),
    value=int(df_long["Rodada"].max())
)

# Filtrar dados (usar .copy() pra evitar warnings)
df_filtrado = df_long[
    (df_long["Time_Label"].isin(times_selecionados)) &
    (df_long["Rodada"] <= rodadas)
].copy()

if df_filtrado.empty:
    st.warning("Nenhum dado para o filtro selecionado.")
else:
    # plot base (sem text no trace)
    fig = px.line(
        df_filtrado,
        x="Rodada",
        y="Posição",
        color="Time_Label",
        markers=True,
        line_group="Time_Label",
        hover_data=["Pontuação", "Pontuação_Acumulada"],
        title="Ranking Progressivo do Cartolas"
    )

    fig2 = px.line(
    df_filtrado,
    x="Rodada",
    y="Posição",
    facet_col="Time",
    facet_col_wrap=3,
    markers=True,
    line_group="Time",
    hover_data=["Pontuação", "Pontuação_Acumulada"],
    title="Posição por Rodada - Small Multiples",
    text="Posição"  # mostra a posição no ponto
    )


    # permitir que elementos não sejam cortados
    for trace in fig.data:
        # garante que marcador/linha não sejam cortados pelo eixo
        trace.update(cliponaxis=False)

    # Ajuste dos eixos (forçar todos os ticks e inverter Y)
    fig.update_yaxes(tickmode="linear", dtick=1, autorange="reversed", title="Posição durante o Campeonato")
    fig.update_xaxes(tickmode="linear", dtick=1)

    # expandir o range do eixo X para deixar espaço à direita (não cortar labels)
    xmin = int(df_filtrado["Rodada"].min())
    xmax = int(df_filtrado["Rodada"].max())
    # coloca um pequeno padding à direita (ex.: +1.2 rodadas)
    fig.update_xaxes(range=[xmin - 0.5, xmax + 1.2])

    # Preparar anotações: pegar o último ponto de cada time (depois do filtro)
    df_last = df_filtrado.sort_values(["Time", "Rodada"]).groupby("Time").tail(1).copy()

    # Evitar sobreposição vertical quando várias equipes tiverem a mesma posição:
    dup_counts = df_last["Posição"].value_counts().to_dict()
    seen_per_pos = {}
    annotations = []
    for _, row in df_last.iterrows():
        pos = row["Posição"]
        # quantos já posicionados nessa mesma posição
        idx = seen_per_pos.get(pos, 0)
        seen_per_pos[pos] = idx + 1
        num_same = dup_counts.get(pos, 1)
        # calcula offset centrado (se houver 3 iguais: -0.12, 0, +0.12)
        offset = (idx - (num_same - 1) / 2) * 0.12

        # texto mais curto para evitar corte; pode usar row['Time'] ou row['Time_Label']
        texto = f"{row['Time']} — {int(row['Pontuação_Acumulada'])}"

        annotations.append(dict(
            x=row["Rodada"] + 0.15, #desloca um pouco à direita do último ponto
            y=row["Posição"] + offset,
            xref='x',
            yref='y',
            text=texto,
            showarrow=False,
            xanchor='left',
            yanchor='middle',
            font=dict(size=11, color='white'),
            align='left',
            bgcolor='rgba(0,0,0,0)',  # fundo transparente
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=0.5
        ))

    # adicionar anotações e margem direita maior (para garantir espaço)
    # adicionar anotações e margem direita maior (para garantir espaço)
    fig.update_layout(
        annotations=annotations,
        margin=dict(l=100, r=220, t=80, b=120),
        width=1200,
        height=700,
        showlegend=False  # <<< remove a legenda
    )

    st.plotly_chart(fig, use_container_width=True)

    
    # Inverter eixo Y (posição 1 no topo)
    fig2.update_yaxes(autorange="reversed", dtick=2)  # menos linhas, intervalo maior

    # Mostrar os valores sobre os pontos
    fig2.update_traces(textposition="top center", textfont=dict(size=10, color='white'))

    # Remover legenda e ajustar layout
    fig2.update_layout(
    showlegend=False,
    margin=dict(l=50, r=50, t=80, b=50),
    height=300 + 250 * (len(times_selecionados) // 3)
    )
    st.plotly_chart(fig2, use_container_width=True)
