import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np


@st.cache_data
def load_prepared_filtering_data():
    with open("filtering_analysis/results/filtering_results.json", "r", encoding="utf-8") as f:
        filtering_data = json.load(f)
    with open("filtering_analysis/results/filtering_simulation.json", "r", encoding="utf-8") as f:
        simulation_data = json.load(f)
    with open("filtering_analysis/results/filtering_comparison.json", "r", encoding="utf-8") as f:
        comparison_data = json.load(f)
    return filtering_data, simulation_data, comparison_data

st.set_page_config(page_title="S&P500 Filtering Analyse", layout="wide")
st.title("S&P500 Filtering Analyse")

filtering_data, simulation_data, comparison_data = load_prepared_filtering_data()


years = list(range(2011, 2025))
selected_year = st.sidebar.selectbox("Wähle ein Zieljahr", years, index=len(years)-1)

Filtering_option = st.sidebar.selectbox(
    "Wähle die Filtering-Analyse",
    ["Dividend Yield Filtering", "Dividend CAGR Filtering", "Revenue CAGR Filtering", "EPS Growth Filtering", "Gemergtes Filtering", "Simulation", "S&P500 VS Biathletes Strategy"],
    index=5
)


if Filtering_option == "Dividend Yield Filtering":
    st.header(f"Dividend Yield Analyse für {selected_year}")
    df = pd.DataFrame(filtering_data[str(selected_year)]["dividend_yield"])
    st.dataframe(df)
    if not df.empty:
        fig = px.bar(
            df,
            x="Ticker",
            y="Trailing Yield",
            title=f"Trailing Dividend Yield ({selected_year})"
        )
        st.plotly_chart(fig)

elif Filtering_option == "Dividend CAGR Filtering":
    st.header(f"Dividend CAGR Analyse für {selected_year}")
    df = pd.DataFrame(filtering_data[str(selected_year)]["dividend_cagr"])
    st.dataframe(df)
    if not df.empty:
        st.subheader("Balkendiagramm: Dividend CAGR")
        # Umwandlung in float für die Darstellung
        df["Dividend CAGR (%)"] = df["Dividend CAGR (%)"].astype(float)
        fig = px.bar(
            df.sort_values("Dividend CAGR (%)", ascending=False),
            x="Ticker",
            y="Dividend CAGR (%)",
            title=f"Dividend CAGR ({selected_year})"
        )
        st.plotly_chart(fig)

elif Filtering_option == "Revenue CAGR Filtering":
    st.header(f"Revenue CAGR Analyse für {selected_year}")
    df = pd.DataFrame(filtering_data[str(selected_year)]["revenue_cagr"])
    st.dataframe(df)
    if not df.empty:
        st.subheader("Balkendiagramm: Revenue CAGR")
        df["Revenue CAGR (%)"] = df["Revenue CAGR (%)"].astype(float)
        fig = px.bar(
            df.sort_values("Revenue CAGR (%)", ascending=False),
            x="Ticker",
            y="Revenue CAGR (%)",
            title=f"Revenue CAGR ({selected_year})"
        )
        st.plotly_chart(fig)

elif Filtering_option == "EPS Growth Filtering":
    st.header(f"EPS Growth Analyse für {selected_year}")
    df = pd.DataFrame(filtering_data[str(selected_year)]["eps_growth"])
    st.dataframe(df)
    if not df.empty:
        st.subheader("Balkendiagramm: EPS-Wachstumsraten")
        # Berechne den Durchschnitt der Wachstumsraten (sofern vorhanden)
        df["Durchschnittliche EPS-Wachstumsrate (%)"] = df["Wachstumsraten (%)"].apply(lambda rates: round(np.mean(rates), 2) if rates else 0)
        fig = px.bar(
            df.sort_values("Durchschnittliche EPS-Wachstumsrate (%)", ascending=False),
            x="Ticker",
            y="Durchschnittliche EPS-Wachstumsrate (%)",
            title=f"EPS Growth (Ø) ({selected_year})"
        )
        st.plotly_chart(fig)

elif Filtering_option == "Gemergtes Filtering":
    st.header(f"Gemergte Filtering-Ergebnisse für {selected_year}")
    df_merge = pd.DataFrame(filtering_data[str(selected_year)]["merged_filtering"])
    st.dataframe(df_merge)
    if not df_merge.empty:
        st.subheader("Anzahl Unternehmen nach allen Kriterien:")
        st.write(f"{len(df_merge)} Unternehmen")
        fig = px.bar(
            df_merge,
            x="Ticker",
            y="Revenue CAGR (%)",
            title=f"Revenue CAGR der gemergten Unternehmen ({selected_year})"
        )
        st.plotly_chart(fig)

elif Filtering_option == "Simulation":
    holding_years = st.number_input("Gib eine Haltedauer (in Jahren) ein", min_value=1, max_value=10, value=5, step=1)
    st.header(f"Simulation der Ergebnisse für {holding_years}-jährige Haltedauer")
    df_sim = pd.DataFrame(simulation_data[str(holding_years)])
    st.dataframe(df_sim)

    fig_return = px.line(
        df_sim,
        x="StartYear",
        y="TotalReturn (%)",
        markers=True,
        title="Entwicklung von TotalReturn (%)"
    )
    st.plotly_chart(fig_return)

    fig_cagr = px.line(
        df_sim,
        x="StartYear",
        y="TotalCAGR (%)",
        markers=True,
        title="Entwicklung von TotalCAGR (%)",
        color_discrete_sequence=["#AB63FA"]
    )
    st.plotly_chart(fig_cagr)

    fig_dividend = px.line(
        df_sim,
        x="StartYear",
        y="TotalDividend",
        markers=True,
        title="Entwicklung von TotalDividend",
        color_discrete_sequence=["#19D3F3"]
    )
    st.plotly_chart(fig_dividend)

    fig_total_return = px.box(
        df_sim,
        y="TotalReturn (%)",
        title="Boxplot: Total Return (%)",
        points="all"
    )
    fig_total_return.update_layout(height=600)
    fig_total_cagr = px.box(
        df_sim,
        y="TotalCAGR (%)",
        title="Boxplot: Total CAGR (%)",
        points="all"
    )
    fig_total_cagr.update_layout(height=600)
    fig_total_dividend = px.box(
        df_sim,
        y="TotalDividend",
        title="Boxplot: Total Dividend",
        points="all"
    )
    fig_total_dividend.update_layout(height=600)
    st.plotly_chart(fig_total_return)
    st.plotly_chart(fig_total_cagr)
    st.plotly_chart(fig_total_dividend)

    # Heatmap: Ticker-Präsenz
    st.subheader("Heatmap: Ticker-Präsenz in der Simulation")
    # Erstelle eine Ticker-Jahres-Matrix
    ticker_years = {}
    for _, row in df_sim.iterrows():
        year = row["StartYear"]
        for ticker in row["IncludedTickers"]:
            ticker_years.setdefault(ticker, []).append(year)
    all_years = sorted(df_sim["StartYear"].unique())
    presence_matrix = pd.DataFrame(0, index=sorted(ticker_years), columns=all_years)
    for ticker, years_list in ticker_years.items():
        presence_matrix.loc[ticker, years_list] = 1

    top_n = 30
    top_tickers = presence_matrix.sum(axis=1).sort_values(ascending=False).head(top_n).index
    presence_matrix = presence_matrix.loc[top_tickers]

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=presence_matrix.values,
        x=presence_matrix.columns,
        y=presence_matrix.index,
        colorscale='Blues',
        showscale=False,
        hovertemplate='Jahr: %{x}<br>Ticker: %{y}<br>Präsenz: %{z}<extra></extra>',
        xgap=1,
        ygap=1
    ))
    fig_heatmap.update_layout(
        title=f"Ticker-Präsenz in der Simulation (Top {top_n})",
        xaxis=dict(title='Jahr', showgrid=False),
        yaxis=dict(title='Ticker', showgrid=False, autorange='reversed')
    )
    st.plotly_chart(fig_heatmap)

elif Filtering_option == "S&P500 VS Biathletes Strategy":
    holding_years = st.number_input("Gib eine Haltedauer (in Jahren) ein", min_value=1, max_value=10, value=5, step=1)
    st.header(f"Vergleich der Ergebnisse mit S&P500 für {holding_years}-jährige Haltedauer")
    df_compare = pd.DataFrame(comparison_data[str(holding_years)])
    st.dataframe(df_compare)
    fig_return_compare = px.line(
        df_compare,
        x="StartYear",
        y=["Strategy_TotalReturn (%)", "Index_Return (%)"],
        markers=True,
        title="Liniendiagramm Vergleich: Total Return (%) – S&P500 vs. Biathletes Strategy"
    )
    fig_bar = px.bar(
        df_compare,
        x="StartYear",
        y=["Strategy_TotalReturn (%)", "Index_Return (%)"],
        barmode="group",
        title="Balkendiagramm Vergleich: Total Return (%) – S&P500 vs. Biathletes Strategy",
        labels={"value": "Total Return (%)", "variable": "Legende"}
    )
    st.plotly_chart(fig_bar)
    st.plotly_chart(fig_return_compare)