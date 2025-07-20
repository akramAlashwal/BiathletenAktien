import streamlit as st
import json
import pandas as pd
import numpy as np
from datetime import datetime

@st.cache_data
def load_json_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_sp500_data(target_year):
    sp500_csv_path = f"data/s&p500/sp500_{target_year}.csv"
    return pd.read_csv(sp500_csv_path)


def extract_year(date_str):
    try:
        return int(date_str.split("-")[0])
    except Exception:
        return None

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        return None

def calculate_dividend_yield_rank(ticker, target_year):
    if ticker not in dividend_data or "historical" not in dividend_data[ticker]:
        return None

    total_dividends = 0.0
    for record in dividend_data[ticker]["historical"]:
        try:
            rec_year = extract_year(record["date"])
            if rec_year == target_year:
                d = float(record["adjDividend"])
                total_dividends += d
        except:
            pass

    if total_dividends == 0:
        return None

    if ticker not in price_data or "historical" not in price_data[ticker]:
        return None

    target_records = [r for r in price_data[ticker]["historical"] if r["date"].startswith(str(target_year))]
    if not target_records:
        return None

    last_record_target = max(target_records, key=lambda r: parse_date(r["date"]))
    try:
        target_date_price = float(last_record_target["adjClose"])
        if target_date_price > 0:
            return (total_dividends / target_date_price) * 100.0
    except:
        pass
    return None

def analyze_dividend_yield_rank(target_year):
    companies_df = load_sp500_data(target_year)
    results = []
    for idx, row in companies_df.iterrows():
        ticker = row["Ticker"]
        dy = calculate_dividend_yield_rank(ticker, target_year)
        results.append({
            "Ticker": ticker,
            "DividendYield": dy if dy is not None else np.nan
        })
    return pd.DataFrame(results)

def analyze_dividend_cagr_rank(target_year):
    start_year = target_year - 10
    companies_df = load_sp500_data(target_year)
    results = []

    for idx, row in companies_df.iterrows():
        ticker = row["Ticker"]
        div_cagr = np.nan

        if ticker in dividend_data and "historical" in dividend_data[ticker]:
            dividends_target = 0.0
            dividends_start  = 0.0

            for record in dividend_data[ticker]["historical"]:
                try:
                    rec_date = datetime.strptime(record["date"], "%Y-%m-%d")
                    rec_year = rec_date.year
                    adj_div = float(record["adjDividend"])
                except:
                    continue

                if rec_year == target_year:
                    dividends_target += adj_div
                elif rec_year == start_year:
                    dividends_start += adj_div

            if dividends_target > 0 and dividends_start > 0:
                try:
                    cagr = (dividends_target / dividends_start) ** (1/10) - 1
                    div_cagr = cagr * 100.0
                except:
                    pass

        results.append({
            "Ticker": ticker,
            "DividendCAGR": div_cagr
        })

    return pd.DataFrame(results)

def analyze_eps_growth_rank(target_year, progression_years=5):
    start_year = target_year - progression_years + 1
    companies_df = load_sp500_data(target_year)
    results = []
    for idx, row in companies_df.iterrows():
        ticker = row["Ticker"]
        eps_growth_value = np.nan
        if ticker in income_data:
            eps_dict = {}
            for record in income_data[ticker]:
                try:
                    year = int(record.get("calendarYear", 0))
                    eps_val = float(record["eps"])
                except:
                    continue
                if start_year <= year <= target_year:
                    eps_dict[year] = eps_val
            if start_year in eps_dict and target_year in eps_dict:
                eps_start = eps_dict[start_year]
                eps_end   = eps_dict[target_year]
                if eps_start > 0 and eps_end > 0:
                    n = target_year - start_year
                    try:
                        growth = (eps_end / eps_start) ** (1/n) - 1
                        eps_growth_value = growth * 100.0
                    except:
                        pass
        results.append({
            "Ticker": ticker,
            "EPSGrowth": eps_growth_value
        })
    return pd.DataFrame(results)

def analyze_revenue_cagr_rank(target_year):
    start_year = target_year - 10
    companies_df = load_sp500_data(target_year)
    results = []
    for idx, row in companies_df.iterrows():
        ticker = row["Ticker"]
        rev_cagr = np.nan
        if ticker in income_data:
            revenue_target = None
            revenue_start  = None
            for record in income_data[ticker]:
                try:
                    rec_date = datetime.strptime(record["date"], "%Y-%m-%d")
                    rec_year = rec_date.year
                    revenue_val = float(record["revenue"])
                except:
                    continue
                if rec_year == target_year:
                    revenue_target = revenue_val
                elif rec_year == start_year:
                    revenue_start = revenue_val
            if revenue_target and revenue_start and revenue_target > 0 and revenue_start > 0:
                try:
                    cagr = (revenue_target / revenue_start) ** (1/10) - 1
                    rev_cagr = cagr * 100.0
                except:
                    pass
        results.append({
            "Ticker": ticker,
            "RevenueCAGR": rev_cagr
        })
    return pd.DataFrame(results)

def simulate_index_returns(index_data, holding_years=5):

    def parse_date_local(s):
        return datetime.strptime(s, "%Y-%m-%d")

    historical = index_data.get("historical", [])
    records_by_year = {}

    # Gruppiere nach Jahr
    for record in historical:
        try:
            year = record["date"][:4]
            records_by_year.setdefault(year, []).append(record)
        except:
            continue

    simulation_results = []

    for start_year in sorted(records_by_year.keys()):
        start_year_int = int(start_year)
        if start_year_int < 2011:
            continue

        end_year_int = start_year_int + holding_years
        end_year_str = str(end_year_int)

        if end_year_str not in records_by_year:
            continue

        try:
            start_record = max(records_by_year[start_year], key=lambda r: parse_date_local(r["date"]))
            end_record = max(records_by_year[end_year_str], key=lambda r: parse_date_local(r["date"]))
        except:
            continue

        try:
            start_price = float(start_record["adjClose"])
            end_price = float(end_record["adjClose"])
        except:
            continue

        if start_price <= 0:
            continue

        total_return = ((end_price - start_price) / start_price) * 100.0
        total_return = round(total_return, 2)

        try:
            cagr = ((end_price / start_price) ** (1 / holding_years) - 1) * 100
            cagr = round(cagr, 2)
        except:
            cagr = None

        simulation_results.append({
            "StartYear": start_year_int,
            "EndYear": end_year_int,
            "BuyPrice": round(start_price, 2),
            "SellPrice": round(end_price, 2),
            "Return (%)": total_return,
            "CAGR (%)": cagr
        })

    return pd.DataFrame(simulation_results)

def simulate_returns(price_data, dividend_data, portfolios_by_start_year, symbol_changes, max_tickers=20, holding_years=5):
    # Symbolwechsel-Mapping vorbereiten
    symbol_mapping = {}
    for record in symbol_changes:
        old_symbol = record["oldSymbol"].strip()
        symbol_mapping[old_symbol] = {
            "newSymbol": record["newSymbol"].strip(),
            "change_date": record["date"]
        }

    simulation_results = []

    def get_historical(sym):
        return price_data.get(sym, {}).get("historical", [])

    def sum_dividends(ticker, year_start, year_end):
        total = 0.0
        if ticker not in dividend_data or "historical" not in dividend_data[ticker]:
            return total
        for record in dividend_data[ticker]["historical"]:
            try:
                rec_year = int(record["date"][:4])
                if year_start <= rec_year <= year_end:
                    total += float(record["adjDividend"])
            except:
                continue
        return total

    def get_total_dividends_for_ticker(ticker, start_year, end_year):
        total = 0.0
        if ticker in symbol_mapping:
            change_info = symbol_mapping[ticker]
            change_year = int(change_info["change_date"][:4])
            if change_year <= start_year:
                total += sum_dividends(symbol_mapping[ticker]["newSymbol"], start_year, end_year)
            elif start_year < change_year <= end_year:
                total += sum_dividends(ticker, start_year, change_year - 1)
                total += sum_dividends(symbol_mapping[ticker]["newSymbol"], change_year, end_year)
            else:
                total += sum_dividends(ticker, start_year, end_year)
        else:
            total += sum_dividends(ticker, start_year, end_year)
        return total

    for start_year, tickers in portfolios_by_start_year.items():
        end_year = start_year + holding_years
        valid_tickers_info = []
        portfolio_total_dividends = 0.0

        for ticker in tickers:
            if ticker in symbol_mapping:
                change_info = symbol_mapping[ticker]
                change_year = int(change_info["change_date"][:4])
                if change_year <= start_year:
                    symbol_start = change_info["newSymbol"]
                    symbol_end = change_info["newSymbol"]
                elif start_year < change_year <= end_year:
                    symbol_start = ticker
                    symbol_end = change_info["newSymbol"]
                else:
                    symbol_start = ticker
                    symbol_end = ticker
            else:
                symbol_start = ticker
                symbol_end = ticker

            hist_start = get_historical(symbol_start)
            hist_end = get_historical(symbol_end)

            start_prices = [r for r in hist_start if r["date"].startswith(str(start_year))]
            end_prices = [r for r in hist_end if r["date"].startswith(str(end_year))]

            if not start_prices or not end_prices:
                continue

            try:
                start_price = max(start_prices, key=lambda r: parse_date(r["date"]))["adjClose"]
                end_price = max(end_prices, key=lambda r: parse_date(r["date"]))["adjClose"]
                start_price = float(start_price)
                end_price = float(end_price)
            except:
                continue

            if start_price > 0:
                ret = ((end_price - start_price) / start_price) * 100.0
                valid_tickers_info.append((ticker, ret))
                ticker_dividend = get_total_dividends_for_ticker(ticker, start_year, end_year)
                portfolio_total_dividends += ticker_dividend

            if len(valid_tickers_info) == max_tickers:
                break

        n = len(valid_tickers_info)
        if n > 0:
            start_value = n
            end_value = sum(1 + (tup[1] / 100.0) for tup in valid_tickers_info)
            total_return = ((end_value - start_value) / start_value) * 100
            total_return = round(total_return, 2)
            try:
                cagr = ((1 + total_return / 100.0) ** (1 / holding_years) - 1) * 100
                cagr = round(cagr, 2)
            except:
                cagr = None
        else:
            total_return = None
            cagr = None

        included_tickers = [tup[0] for tup in valid_tickers_info]
        if end_year >= 2025:
            break

        simulation_results.append({
            "StartYear": start_year,
            "EndYear": end_year,
            "TotalReturn (%)": total_return,
            "TotalCAGR (%)": cagr,
            "TotalDividend": round(portfolio_total_dividends, 2),
            "IncludedTickersCount": n,
            "IncludedTickers": included_tickers
        })

    return pd.DataFrame(simulation_results)

def compare_simulations(price_data, dividend_data, portfolios_by_start_year, symbol_changes, sp500_index, max_tickers=20, holding_years=5):
    # Strategie-Simulation (inkl. Dividenden etc.)
    strategy_df = simulate_returns(price_data, dividend_data, portfolios_by_start_year, symbol_changes, max_tickers, holding_years)
    # Index-Simulation (nur für Jahre ab 2011)
    index_df = simulate_index_returns(sp500_index, holding_years)
    # Zusammenführen der Ergebnisse anhand von StartYear und EndYear
    merged_df = pd.merge(strategy_df, index_df, on=["StartYear", "EndYear"], how="inner", suffixes=("_strategy", "_index"))
    merged_df = merged_df.rename(columns={
        "TotalReturn (%)": "Strategy_TotalReturn (%)",
        "TotalCAGR (%)": "Strategy_TotalCAGR (%)",
        "Return (%)": "Index_Return (%)",
        "CAGR (%)": "Index_CAGR (%)"
    })
    merged_df["Strategy_Beats_Index"] = (
        (merged_df["Strategy_TotalReturn (%)"] > merged_df["Index_Return (%)"]) &
        (merged_df["Strategy_TotalCAGR (%)"] > merged_df["Index_CAGR (%)"])
    )
    final_df = merged_df[[
        "StartYear",
        "EndYear",
        "Strategy_TotalReturn (%)",
        "Strategy_TotalCAGR (%)",
        "Index_Return (%)",
        "Index_CAGR (%)",
        "Strategy_Beats_Index"
    ]]
    return final_df

def merge_and_rank(target_year):
    df_yield    = analyze_dividend_yield_rank(target_year)
    df_div_cagr = analyze_dividend_cagr_rank(target_year)
    df_eps      = analyze_eps_growth_rank(target_year, progression_years=5)
    df_rev      = analyze_revenue_cagr_rank(target_year)

    sp500_df = load_sp500_data(target_year)[["Ticker"]]
    merged = sp500_df.merge(df_yield, on="Ticker", how="inner")
    merged = merged.merge(df_div_cagr, on="Ticker", how="inner")
    merged = merged.merge(df_eps, on="Ticker", how="inner")
    merged = merged.merge(df_rev, on="Ticker", how="inner")
    merged.dropna(subset=["DividendYield", "DividendCAGR", "EPSGrowth", "RevenueCAGR"], inplace=True)
    merged["Rank_DividendYield"] = merged["DividendYield"].rank(method="dense", ascending=False)
    merged["Rank_DividendCAGR"]  = merged["DividendCAGR"].rank(method="dense", ascending=False)
    merged["Rank_EPSGrowth"]     = merged["EPSGrowth"].rank(method="dense", ascending=False)
    merged["Rank_RevenueCAGR"]   = merged["RevenueCAGR"].rank(method="dense", ascending=False)
    merged["Rank_Sum"] = (
        merged["Rank_DividendYield"] +
        merged["Rank_DividendCAGR"]  +
        merged["Rank_EPSGrowth"]     +
        merged["Rank_RevenueCAGR"]
    )
    merged.sort_values("Rank_Sum", inplace=True)
    merged.reset_index(drop=True, inplace=True)
    return merged

def extract_top():
    top30_ticker_dict_ranking = {}
    for target_year in range(2011, 2025):
        final_df = merge_and_rank(target_year)
        top30_ticker_dict_ranking[target_year] = final_df["Ticker"].head(30).tolist()
    return top30_ticker_dict_ranking



dividend_data = load_json_file("data/stock_dividend.json")
price_data    = load_json_file("data/historical_price_full.json")
income_data   = load_json_file("data/income_statement_annual.json")
symbol_change = load_json_file("data/symbol_change.json")
sp500_index   = load_json_file("data/sp500_index.json")


def main():
    years = range(2011, 2025)

    ranking_results = {}
    for y in years:
        df_div_yield = analyze_dividend_yield_rank(y)
        df_div_cagr  = analyze_dividend_cagr_rank(y)
        df_eps       = analyze_eps_growth_rank(y, progression_years=5)
        df_rev       = analyze_revenue_cagr_rank(y)
        df_merged    = merge_and_rank(y)
        ranking_results[y] = {
            "dividend_yield": df_div_yield.to_dict(orient="records"),
            "dividend_cagr":  df_div_cagr.to_dict(orient="records"),
            "eps_growth":     df_eps.to_dict(orient="records"),
            "revenue_cagr":   df_rev.to_dict(orient="records"),
            "merged_rank":    df_merged.to_dict(orient="records")
        }

    with open("ranking_analysis/results/ranking_results.json", "w", encoding="utf-8") as f:
        json.dump(ranking_results, f, indent=2)
    print("Ranking-Daten wurden in 'ranking_results.json' gespeichert.")


    top_portfolios = extract_top()
    simulation_results = {}
    for holding_years in range(1, 11):
        df_sim = simulate_returns(
            price_data=price_data,
            dividend_data=dividend_data,
            portfolios_by_start_year=top_portfolios,
            symbol_changes=symbol_change,
            max_tickers=20,
            holding_years=holding_years
        )
        simulation_results[holding_years] = df_sim.to_dict(orient="records")

    with open("ranking_analysis/results/simulation_results.json", "w", encoding="utf-8") as f:
        json.dump(simulation_results, f, indent=2)
    print("Simulationsdaten wurden in 'simulation_results.json' gespeichert.")


    comparison_results = {}
    for holding_years in range(1, 11):
        df_compare = compare_simulations(
            price_data=price_data,
            dividend_data=dividend_data,
            portfolios_by_start_year=top_portfolios,
            symbol_changes=symbol_change,
            sp500_index=sp500_index,
            max_tickers=20,
            holding_years=holding_years
        )
        comparison_results[holding_years] = df_compare.to_dict(orient="records")

    with open("ranking_analysis/results/comparison_results.json", "w", encoding="utf-8") as f:
        json.dump(comparison_results, f, indent=2)
    print("Vergleichsdaten wurden in 'comparison_results.json' gespeichert.")

if __name__ == "__main__":
    main()