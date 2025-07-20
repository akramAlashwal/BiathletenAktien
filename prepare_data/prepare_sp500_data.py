import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def get_sp500_companies(url):
    """ archivierte Wayback-Seite: die S&P 500 Unternehmen extrahieren"""
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Fehler beim Abrufen der Seite: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"class": "wikitable"})

    if not table:
        print("Fehler: Tabelle nicht gefunden.")
        return None

    data = []
    rows = table.find_all("tr")
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) < 5:
            continue
        ticker = cols[0].text.strip()
        company = cols[1].text.strip()
        sector = cols[3].text.strip()
        sub_industry = cols[4].text.strip()
        data.append([ticker, company, sector, sub_industry])

    return data

def save_to_csv(data, filename):
    df = pd.DataFrame(data, columns=["Ticker", "Company", "Sector", "Sub-Industry"])
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"Gespeichert: {filename}")

def download_all_years(year_url_mapping, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for year, url in year_url_mapping.items():
        print(f"Verarbeite Jahr {year}...")
        data = get_sp500_companies(url)
        if data:
            save_path = os.path.join(save_dir, f"sp500_{year}.csv")
            save_to_csv(data, save_path)
        else:
            print(f"Warnung: Keine Daten für {year} gespeichert.")

def list_all_unique_tickers(save_dir):

    all_tickers = set()

    for year in range(2011, 2025):
        filepath = os.path.join(save_dir, f"sp500_{year}.csv")
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            all_tickers.update(df["Ticker"].dropna().unique())
        else:
            print(f"Achtung: Datei fehlt für {year}")

    sorted_tickers = sorted(all_tickers)
    print(f"\nAlle einzigartigen Ticker ({len(sorted_tickers)}):")
    print(sorted_tickers)

if __name__ == "__main__":
    # Mapping manuell gepflegt
    year_url_mapping = {
        2011: "https://web.archive.org/web/20110926203521/http://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        2012: "https://web.archive.org/web/20120718014943/http://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        2013: "https://web.archive.org/web/20130826044028/http://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        2014: "https://web.archive.org/web/20141124110032/http://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        2015: "https://web.archive.org/web/20151230161044/https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        2016: "https://web.archive.org/web/20161020172115/https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        2017: "https://web.archive.org/web/20170820205408/https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        2018: "https://web.archive.org/web/20181025141733/https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        2019: "https://web.archive.org/web/20190912150512/https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        2020: "https://web.archive.org/web/20201203052621/https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        2021: "https://web.archive.org/web/20211224231343/https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        2022: "https://web.archive.org/web/20221227092115/https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        2023: "https://web.archive.org/web/20231230133757/http://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        2024: "https://web.archive.org/web/20241225212401/https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        2025: "https://web.archive.org/web/20250217151549/https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    }

    save_directory = "data/s&p500"
    download_all_years(year_url_mapping, save_directory)
    list_all_unique_tickers(save_directory)