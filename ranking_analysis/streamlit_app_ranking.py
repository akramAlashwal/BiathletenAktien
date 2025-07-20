import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


st.set_page_config(page_title="S&P500 Ranking Analyse", layout="wide")



def load_prepared_data():
    with open("ranking_analysis/results/ranking_results.json", "r", encoding="utf-8") as f:
        ranking_data = json.load(f)
    with open("ranking_analysis/results/simulation_results.json", "r", encoding="utf-8") as f:
        simulation_data = json.load(f)
    with open("ranking_analysis/results/comparison_results.json", "r", encoding="utf-8") as f:
        comparison_data = json.load(f)
    return ranking_data, simulation_data, comparison_data

ranking_data, simulation_data, comparison_data = load_prepared_data()


st.title("S&P500 Ranking Analyse")

years = list(range(2011, 2025))
selected_year = st.sidebar.selectbox("Wähle ein Zieljahr", years, index=len(years)-1)

ranking_option = st.sidebar.selectbox(
    "Wähle die Ranking-Analyse",
    [
        "Dividend Yield Ranking",
        "Dividend CAGR Ranking",
        "Revenue CAGR Ranking",
        "EPS Growth Ranking",
        "Gemergtes Ranking",
        "Simulation",
        "S&P500 VS Biathletes Strategy"
    ],
    index=5
)


if ranking_option == "Dividend Yield Ranking":
    st.header(f"Dividend Yield Ranking für {selected_year}")
    df = pd.DataFrame(ranking_data[str(selected_year)]["dividend_yield"])
    st.dataframe(df)
    if not df.empty:
        fig = px.bar(
            df,
            x="Ticker",
            y="DividendYield",
            title=f"Dividend Yield ({selected_year})"
        )
        st.plotly_chart(fig)

elif ranking_option == "Dividend CAGR Ranking":
    st.header(f"Dividend CAGR Ranking für {selected_year}")
    df = pd.DataFrame(ranking_data[str(selected_year)]["dividend_cagr"])
    st.dataframe(df)
    if not df.empty:
        st.subheader("Balkendiagramm: Dividend CAGR")
        chart_data = df.set_index("Ticker")["DividendCAGR"]
        st.bar_chart(chart_data)

elif ranking_option == "Revenue CAGR Ranking":
    st.header(f"Revenue CAGR Ranking für {selected_year}")
    df = pd.DataFrame(ranking_data[str(selected_year)]["revenue_cagr"])
    st.dataframe(df)
    if not df.empty:
        st.subheader("Balkendiagramm: Revenue CAGR")
        chart_data = df.set_index("Ticker")["RevenueCAGR"]
        st.bar_chart(chart_data)

elif ranking_option == "EPS Growth Ranking":
    st.header(f"EPS Growth Ranking für {selected_year}")
    df = pd.DataFrame(ranking_data[str(selected_year)]["eps_growth"])
    st.dataframe(df)
    if not df.empty:
        fig = px.bar(
            df.sort_values("EPSGrowth"),
            x="Ticker",
            y="EPSGrowth",
            title=f"EPS Growth ({selected_year})"
        )
        st.plotly_chart(fig)

elif ranking_option == "Gemergtes Ranking":
    st.header(f"Gesamtranking für {selected_year}")
    df_merge = pd.DataFrame(ranking_data[str(selected_year)]["merged_rank"])
    st.write(f"Anzahl Ticker nach Merge & DropNA: {len(df_merge)}")
    round_columns = ["DividendYield", "DividendCAGR", "EPSGrowth", "RevenueCAGR", "Rank_Sum"]
    df_merge[round_columns] = df_merge[round_columns].round(3)
    st.subheader("Top-Ranking Unternehmen nach Gesamtpunktzahl (Rank Sum)")
    st.dataframe(df_merge)
    top_df = df_merge.head(20)
    fig = px.bar(
        df_merge,
        x="Ticker",
        y="Rank_Sum",
        title=f"Gesamtranking (Rank Sum) ({selected_year})",
        labels={"Rank_Sum": "Gesamtrang"},
        text="Rank_Sum"
    )
    fig_top = px.bar(
        top_df,
        x="Ticker",
        y="Rank_Sum",
        title=f"Gesamtranking (Rank Sum) ({selected_year})",
        color="Ticker"
    )
    st.plotly_chart(fig)
    st.plotly_chart(fig_top)


elif ranking_option == "Simulation":
    holding_years = st.number_input("Gib eine Haltedauer (in Jahren) ein", min_value=1, max_value=10, value=5, step=1)
    st.header(f"Simulation der Ergebnisse für {holding_years}-jährige Haltedauer")
    df_sim = pd.DataFrame(simulation_data[str(holding_years)])
    st.dataframe(df_sim)

    # Linien-Diagramme
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

    # Boxplots
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


elif ranking_option == "S&P500 VS Biathletes Strategy":
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