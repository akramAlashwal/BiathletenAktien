import json
import pandas as pd
from datetime import datetime


def load_json_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

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

dividend_data = load_json_file("data/stock_dividend.json")
price_data    = load_json_file("data/historical_price_full.json")
income_data   = load_json_file("data/income_statement_annual.json")
symbol_change = load_json_file("data/symbol_change.json")
sp500_index   = load_json_file("data/sp500_index.json")

holding_years = 5


def analyze_dividend_yield(target_year, dividend_yield_min=0.5, dividend_yield_max=6):
    companies_df = load_sp500_data(target_year)
    total_companies = len(companies_df)

    count_dividend_not_found = 0
    count_no_dividend_payment = 0
    count_price_not_found = 0
    count_price_missing_target_year = 0
    count_successful_computation = 0
    count_yield_criteria = 0
    count_successful_non_filtered = 0

    filtered_companies = []
    successful_companies = []

    for idx, row in companies_df.iterrows():
        ticker = row["Ticker"]
        if ticker not in dividend_data or "historical" not in dividend_data[ticker]:
            count_dividend_not_found += 1
            continue

        total_dividends = 0.0
        dividends_list = []
        dividend_dates = []
        for record in dividend_data[ticker]["historical"]:
            try:
                rec_year = extract_year(record["date"])
            except Exception:
                continue
            if rec_year == target_year:
                try:
                    d = float(record["adjDividend"])
                except Exception:
                    continue
                total_dividends += d
                dividends_list.append(d)
                dividend_dates.append(record["date"])
        if total_dividends == 0:
            count_no_dividend_payment += 1
            continue

        if ticker not in price_data or "historical" not in price_data[ticker]:
            count_price_not_found += 1
            continue

        target_records = [record for record in price_data[ticker]["historical"]
                          if record["date"].startswith(str(target_year))]
        if not target_records:
            count_price_missing_target_year += 1
            continue

        last_record_target = max(target_records,
                                 key=lambda r: parse_date(r["date"]))
        try:
            target_date_price = float(last_record_target["adjClose"])
        except Exception:
            count_price_missing_target_year += 1
            continue
        price_date = last_record_target["date"]
        trailing_yield = (total_dividends / target_date_price) * 100
        count_successful_computation += 1

        company_data = {
            "Ticker": ticker,
            "Total Dividends": f"{total_dividends:.3f}",
        #    "Dividends List": dividends_list,
            "Dividend Dates": dividend_dates,
        #    "Target Date Price": target_date_price,
            "Price Date": price_date,
            "Trailing Yield": trailing_yield
        }
        successful_companies.append(company_data)

        if dividend_yield_min <= trailing_yield <= dividend_yield_max:
            count_yield_criteria += 1
            company_data["Trailing Yield"] = float(f"{trailing_yield:.3f}")
            filtered_companies.append(company_data)
        else:
            count_successful_non_filtered += 1

    sum_categories = (count_dividend_not_found + count_no_dividend_payment +
                      count_price_not_found + count_price_missing_target_year +
                      count_successful_computation)
    # Zusammenfassung ausgeben (kann in der Konsole erscheinen)
    print(f"\n--- Dividend yield Zusammenfassung (basierend auf Zieljahr {target_year}) ---")
    print(f"Gesamtzahl der Unternehmen in der CSV: {total_companies}")
    print(f"Ticker ohne Dividendendaten: {count_dividend_not_found}")
    print(f"Ticker mit Dividendendaten, aber keine Zahlung: {count_no_dividend_payment}")
    print(f"Ticker ohne Preisdaten: {count_price_not_found}")
    print(f"Ticker ohne Daten für {target_year}: {count_price_missing_target_year}")
    print(f"Erfolgreich berechnete Unternehmen: {count_successful_computation}")
    print(f"Erfüllen Yield-Kriterium ({dividend_yield_min}% - {dividend_yield_max}%): {count_yield_criteria}")
    print(f"Erfolgreich berechnete außerhalb des Kriteriums: {count_successful_non_filtered}")
    print(f"Summe der Kategorien (muss {total_companies} ergeben): {sum_categories}")
    print("\n--- Unternehmen, die das Yield-Kriterium erfüllen ---")

    df_dividend = pd.DataFrame(filtered_companies)
    return df_dividend

def analyze_dividend_cagr(target_year):
    start_year = target_year - 10
    companies_df = load_sp500_data(target_year)
    successful_count = 0
    filtered_companies = []

    for idx, row in companies_df.iterrows():
        ticker = row["Ticker"]
        if ticker not in dividend_data or "historical" not in dividend_data[ticker]:
            continue

        dividends_target = 0.0
        dividends_start = 0.0
        target_dates = []
        start_dates = []
        dividends_target_values = []
        dividends_start_values = []

        for record in dividend_data[ticker]["historical"]:
            try:
                rec_date = datetime.strptime(record["date"], "%Y-%m-%d")
            except Exception:
                continue
            rec_year = rec_date.year
            try:
                computed_adj_dividend = float(record["adjDividend"])
            except Exception:
                continue

            if rec_year == target_year:
                dividends_target += computed_adj_dividend
                dividends_target_values.append(computed_adj_dividend)
                target_dates.append(record["date"])
            elif rec_year == start_year:
                dividends_start += computed_adj_dividend
                dividends_start_values.append(computed_adj_dividend)
                start_dates.append(record["date"])

        if dividends_target == 0 or dividends_start == 0:
            continue

        successful_count += 1
        cagr = (dividends_target / dividends_start) ** (1 / 10) - 1
        cagr_percentage = cagr * 100

        if cagr_percentage >= 5:  # mindestens 5%
            filtered_companies.append({
                "Ticker": ticker,
                f"Gesamte Dividenden im Startjahr ({start_year})": f"{dividends_start:.3f}",
            #    f"Einzelne Dividenden im Startjahr ({start_year})": ", ".join(f"{x:.3f}" for x in dividends_start_values),
                f"Gesamte Dividenden im Zieljahr ({target_year})": f"{dividends_target:.3f}",
            #    f"Einzelne Dividenden im Zieljahr ({target_year})": ", ".join(f"{x:.3f}" for x in dividends_target_values),
                "Dividend CAGR (%)": f"{cagr_percentage:.3f}",
                "Start Datum": min(start_dates) if start_dates else None,
                "End Datum": max(target_dates) if target_dates else None
            })

    df_cagr = pd.DataFrame(filtered_companies)
    print(f"\n--- Dividend CAGR Analyse (Zieljahr {target_year}) ---")
    print(f"Erfolgreich berechnete Unternehmen: {successful_count}")
    print(f"Erfüllen das Kriterium (CAGR >= 5%): {len(filtered_companies)}")
    return df_cagr

def analyze_eps_growth(target_year, progression_years=5):
    start_year = target_year - progression_years + 1
    companies_df = load_sp500_data(target_year)

    def valid_growth(eps_list, threshold=25.0):
        allowed_down = False
        growth_rates = []
        max_eps = eps_list[0]
        i = 0
        while i < len(eps_list) - 1:
            prev = eps_list[i]
            curr = eps_list[i+1]
            if prev <= 0:
                return False, []
            growth = ((curr - prev) / prev) * 100
            if growth >= threshold:
                growth_rates.append(round(growth, 2))
                max_eps = max(max_eps, curr)
                i += 1
            elif growth < 0 and not allowed_down and (i+2 < len(eps_list)):
                next_val = eps_list[i+2]
                if next_val > max_eps:
                    growth_rates.append(round(growth, 2))
                    recovery_growth = ((next_val - curr) / curr) * 100
                    growth_rates.append(round(recovery_growth, 2))
                    max_eps = next_val
                    allowed_down = True
                    i += 2
                else:
                    return False, []
            else:
                return False, []
        if len(growth_rates) < (len(eps_list) - 1):
            return False, []
        return True, growth_rates

    filtered_companies = []
    missing_tickers = []
    insufficient_data = []

    for idx, row in companies_df.iterrows():
        ticker = row["Ticker"]
        if ticker not in income_data:
            missing_tickers.append(ticker)
            continue

        eps_dict = {}
        for record in income_data[ticker]:
            try:
                year = int(record.get("calendarYear", 0))
            except Exception:
                continue
            if start_year <= year <= target_year and record.get("eps") is not None:
                eps_dict[year] = record["eps"]
        if len(eps_dict) < progression_years:
            insufficient_data.append((ticker, list(eps_dict.keys())))
            continue

        sorted_years = sorted(eps_dict.keys())
        if len(sorted_years) > progression_years:
            sorted_years = sorted_years[-progression_years:]
        eps_values = [eps_dict[yr] for yr in sorted_years]
        valid, rates = valid_growth(eps_values, threshold=01.0)##5
        if valid:
            filtered_companies.append({
                "Ticker": ticker,
                "Jahre": sorted_years,
            #    "Alle EPS": [round(e, 2) for e in eps_values],
                "Wachstumsraten (%)": rates
            })
    df_eps = pd.DataFrame(filtered_companies)
    print(f"\n--- EPS-Wachstumsanalyse (Zieljahr {target_year}) ---")
    print(f"Gesamtzahl der Unternehmen in der CSV: {len(companies_df)}")
    print(f"Unternehmen ohne EPS-Daten: {len(missing_tickers)}")
    print(f"Unternehmen mit unzureichenden Daten (< {progression_years} Jahre): {len(insufficient_data)}")
    print(f"\nAnzahl der Unternehmen, die das EPS-Wachstumskriterium erfüllen: {len(df_eps)}")
    print("Beispiele für fehlende Ticker (max. 5):", missing_tickers[:5])
    print("Beispiele für unzureichende Daten (max. 5):", insufficient_data[:5])
    print("\nGefilterte Unternehmen:")
    ##pd.set_option('display.max_rows', None)  # Set to None to display all rows
    ##pd.set_option('display.max_columns', None)  # Set to None to display all columns
    ##display(df_eps)

    return df_eps


def analyze_revenue_cagr(target_year):
    start_year = target_year - 10
    companies_df = load_sp500_data(target_year)
    total_companies = len(companies_df)

    successful_count = 0
    filtered_companies = []

    for idx, row in companies_df.iterrows():
        ticker = row["Ticker"]
        if ticker not in income_data:
            continue

        revenue_target = None
        revenue_start = None
        date_target = None
        date_start = None

        for record in income_data[ticker]:
            try:
                rec_date = datetime.strptime(record["date"], "%Y-%m-%d")
            except Exception:
                continue
            rec_year = rec_date.year
            try:
                revenue_val = float(record["revenue"])
            except Exception:
                continue

            if rec_year == target_year:
                revenue_target = revenue_val
                date_target = record["date"]
            elif rec_year == start_year:
                revenue_start = revenue_val
                date_start = record["date"]

        if revenue_target is None or revenue_start is None or revenue_target <= 0 or revenue_start <= 0:
            continue

        successful_count += 1
        cagr = (revenue_target / revenue_start) ** (1/10) - 1
        cagr_percentage = cagr * 100

        if 5 <= cagr_percentage <= 25:
            filtered_companies.append({
                "Ticker": ticker,
                "Revenue CAGR (%)": f"{cagr_percentage:.3f}",
                "Start Datum": date_start,
                "End Datum": date_target
            })

    df_cagr = pd.DataFrame(filtered_companies)
    print(f"\n--- Revenue CAGR Analyse (Zieljahr {target_year}) ---")
    print(f"Erfolgreich berechnete Unternehmen: {successful_count}")
    print(f"Erfüllen das Kriterium (CAGR zwischen 5% und 25%): {len(filtered_companies)}")
    return df_cagr

def merge_results(target):
    dividend_df = analyze_dividend_yield(target)
    dividend_cagr_df = analyze_dividend_cagr(target)
    eps_growth_df = analyze_eps_growth(target)
    revenue_growth_df = analyze_revenue_cagr(target)

    try:
        merged_df = (
            revenue_growth_df
            .merge(eps_growth_df, on="Ticker", how="inner")
            .merge(dividend_df, on="Ticker", how="inner")
            .merge(dividend_cagr_df, on="Ticker", how="inner")
        )
    except Exception as e:
        print(f"Merge-Fehler für {target}: {e}")
        return pd.DataFrame()
    return merged_df

def collect_top_tickers_per_year(start_year=2011, end_year=2024):
    results_top_filtering = {}
    for target_year in range(start_year, end_year + 1):
        print(f"\n********** Analyse für das Jahr {target_year} **********")
        merged_df = merge_results(target_year)
        if not merged_df.empty:
            tickers_ = merged_df["Ticker"].tolist()
            results_top_filtering[target_year] = tickers_
            print(f"Top Ticker ({target_year}): {tickers_}")
            print(f"Anzahl der Unternehmen: {len(tickers_)}")
        else:
            results_top_filtering[target_year] = []
            print(f"Top Ticker ({target_year}): []")
            print("Anzahl der Unternehmen: 0")
    return results_top_filtering

results_top_filtering = collect_top_tickers_per_year()


def simulate_returns(price_data, dividend_data, portfolios_by_start_year, symbol_changes, max_tickers=20, holding_years=5):
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
                start_price = float(max(start_prices, key=lambda r: parse_date(r["date"]))["adjClose"])
                end_price = float(max(end_prices, key=lambda r: parse_date(r["date"]))["adjClose"])
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

def simulate_index_returns(index_data, holding_years=5):
    from datetime import datetime
    import pandas as pd

    def parse_date_local(s):
        return datetime.strptime(s, "%Y-%m-%d")
    historical = index_data.get("historical", [])
    records_by_year = {}
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

def compare_simulations(price_data, dividend_data, portfolios_by_start_year, symbol_changes, sp500_index, max_tickers=20, holding_years=5):
    import pandas as pd
    strategy_df = simulate_returns(price_data, dividend_data, portfolios_by_start_year, symbol_changes, max_tickers, holding_years)
    index_df = simulate_index_returns(sp500_index, holding_years)
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


def main():
    years = range(2011, 2025)
    filtering_results = {}
    for y in years:
        df_div_yield = analyze_dividend_yield(y)
        df_div_cagr = analyze_dividend_cagr(y)
        df_eps = analyze_eps_growth(y, progression_years=5)
        df_rev = analyze_revenue_cagr(y)
        df_merge = merge_results(y)
        filtering_results[y] = {
            "dividend_yield": df_div_yield.to_dict(orient="records"),
            "dividend_cagr": df_div_cagr.to_dict(orient="records"),
            "eps_growth": df_eps.to_dict(orient="records"),
            "revenue_cagr": df_rev.to_dict(orient="records"),
            "merged_filtering": df_merge.to_dict(orient="records")
        }
    with open("filtering_analysis/results/filtering_results.json", "w", encoding="utf-8") as f:
        json.dump(filtering_results, f, indent=2)
    print("Filter-Ergebnisse in 'filtering_results.json' gespeichert.")

    # Simulationsergebnisse
    simulation_results = {}
    for hold in range(1, 11):
        df_sim = simulate_returns(price_data, dividend_data, results_top_filtering, symbol_change, max_tickers=20, holding_years=hold)
        simulation_results[hold] = df_sim.to_dict(orient="records")
    with open("filtering_analysis/results/filtering_simulation.json", "w", encoding="utf-8") as f:
        json.dump(simulation_results, f, indent=2)
    print("Filtering-Simulation in 'filtering_simulation.json' gespeichert.")

    # Vergleichsergebnisse
    comparison_results = {}
    for hold in range(1, 11):
        df_comp = compare_simulations(price_data, dividend_data, results_top_filtering, symbol_change, sp500_index, max_tickers=20, holding_years=hold)
        comparison_results[hold] = df_comp.to_dict(orient="records")
    with open("filtering_analysis/results/filtering_comparison.json", "w", encoding="utf-8") as f:
        json.dump(comparison_results, f, indent=2)
    print("Filtering-Vergleich in 'filtering_comparison.json' gespeichert.")

if __name__ == "__main__":
    main()