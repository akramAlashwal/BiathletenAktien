

import requests
import json
import os

# API Key einfügen
API_KEY = ""

BASE_URL = "https://financialmodelingprep.com/api/v3/"
SYMBOL_CHANGE_URL = "https://financialmodelingprep.com/api/v4/symbol_change"

# Liste der S&P500 Ticker von 2011 bis 2025 verarbeitet (819 symbols)
sp500_11to25_unique = ['A', 'AA', 'AAL', 'AAP', 'AAPL', 'ABBV', 'ABC', 'ABMD', 'ABNB', 'ABT', 'ACE', 'ACGL', 'ACN', 'ACT', 'ADBE', 'ADI', 'ADM', 'ADP', 'ADS', 'ADSK', 'ADT', 'AEE', 'AEP', 'AES', 'AET', 'AFL', 'AGN', 'AIG', 'AIV', 'AIZ', 'AJG', 'AKAM', 'AKS', 'ALB', 'ALGN', 'ALK', 'ALL', 'ALLE', 'ALTR', 'ALXN', 'AMAT', 'AMCR', 'AMD', 'AME', 'AMG', 'AMGN', 'AMP', 'AMT', 'AMTM', 'AMZN', 'AN', 'ANDV', 'ANET', 'ANF', 'ANR', 'ANSS', 'ANTM', 'AON', 'AOS', 'APA', 'APC', 'APD', 'APH', 'APO', 'APOL', 'APTV', 'ARE', 'ARG', 'ARNC', 'ATI', 'ATO', 'ATVI', 'AVB', 'AVGO', 'AVP', 'AVY', 'AWK', 'AXON', 'AXP', 'AYI', 'AZO', 'BA', 'BAC', 'BALL', 'BAX', 'BBBY', 'BBT', 'BBWI', 'BBY', 'BCR', 'BDX', 'BEAM', 'BEN', 'BF-B', 'BF.B', 'BFB', 'BG', 'BHF', 'BHGE', 'BHI', 'BIG', 'BIIB', 'BIO', 'BK', 'BKNG', 'BKR', 'BLDR', 'BLK', 'BLL', 'BMC', 'BMS', 'BMY', 'BR', 'BRCM', 'BRK-B', 'BRK.B', 'BRO', 'BSX', 'BTU', 'BWA', 'BX', 'BXLT', 'BXP', 'C', 'CA', 'CAG', 'CAH', 'CAM', 'CARR', 'CAT', 'CB', 'CBE', 'CBG', 'CBOE', 'CBRE', 'CBS', 'CCE', 'CCI', 'CCL', 'CDAY', 'CDNS', 'CDW', 'CE', 'CEG', 'CELG', 'CEPH', 'CERN', 'CF', 'CFG', 'CFN', 'CHD', 'CHK', 'CHRW', 'CHTR', 'CI', 'CINF', 'CL', 'CLF', 'CLX', 'CMA', 'CMCSA', 'CME', 'CMG', 'CMI', 'CMS', 'CNC', 'CNP', 'CNX', 'COF', 'COG', 'COH', 'COL', 'COO', 'COP', 'COR', 'COST', 'COTY', 'COV', 'CPAY', 'CPB', 'CPGX', 'CPRI', 'CPRT', 'CPT', 'CPWR', 'CRL', 'CRM', 'CRWD', 'CSC', 'CSCO', 'CSGP', 'CSRA', 'CSX', 'CTAS', 'CTL', 'CTLT', 'CTRA', 'CTSH', 'CTVA', 'CTXS', 'CVC', 'CVH', 'CVS', 'CVX', 'CXO', 'CZR', 'D', 'DAL', 'DAY', 'DD', 'DE', 'DECK', 'DELL', 'DF', 'DFS', 'DG', 'DGX', 'DHI', 'DHR', 'DIS', 'DISCA', 'DISCK', 'DISH', 'DLPH', 'DLR', 'DLTR', 'DNB', 'DNR', 'DO', 'DOC', 'DOV', 'DOW', 'DPS', 'DPZ', 'DRE', 'DRI', 'DTE', 'DTV', 'DUK', 'DV', 'DVA', 'DVN', 'DWDP', 'DXC', 'DXCM', 'EA', 'EBAY', 'ECL', 'ED', 'EFX', 'EG', 'EIX', 'EL', 'ELV', 'EMC', 'EMN', 'EMR', 'ENDP', 'ENPH', 'EOG', 'EP', 'EPAM', 'EQIX', 'EQR', 'EQT', 'ERIE', 'ERTS', 'ES', 'ESRX', 'ESS', 'ESV', 'ETFC', 'ETN', 'ETR', 'ETSY', 'EVHC', 'EVRG', 'EW', 'EXC', 'EXPD', 'EXPE', 'EXR', 'F', 'FANG', 'FAST', 'FB', 'FBHS', 'FCX', 'FDO', 'FDS', 'FDX', 'FE', 'FFIV', 'FHN', 'FI', 'FICO', 'FII', 'FIS', 'FISV', 'FITB', 'FL', 'FLIR', 'FLR', 'FLS', 'FLT', 'FMC', 'FO', 'FOSL', 'FOX', 'FOXA', 'FRC', 'FRT', 'FRX', 'FSLR', 'FTI', 'FTNT', 'FTR', 'FTV', 'GAS', 'GCI', 'GD', 'GDDY', 'GE', 'GEHC', 'GEN', 'GEV', 'GGP', 'GILD', 'GIS', 'GL', 'GLW', 'GM', 'GMCR', 'GME', 'GNRC', 'GNW', 'GOOG', 'GOOGL', 'GPC', 'GPN', 'GPS', 'GR', 'GRMN', 'GS', 'GT', 'GWW', 'HAL', 'HAR', 'HAS', 'HBAN', 'HBI', 'HCA', 'HCBK', 'HCN', 'HCP', 'HD', 'HES', 'HFC', 'HIG', 'HII', 'HLT', 'HNZ', 'HOG', 'HOLX', 'HON', 'HOT', 'HP', 'HPE', 'HPQ', 'HRB', 'HRL', 'HRS', 'HSIC', 'HSP', 'HST', 'HSY', 'HUBB', 'HUM', 'HWM', 'IBM', 'ICE', 'IDXX', 'IEX', 'IFF', 'IGT', 'ILMN', 'INCY', 'INFO', 'INTC', 'INTU', 'INVH', 'IP', 'IPG', 'IPGP', 'IQV', 'IR', 'IRM', 'ISRG', 'IT', 'ITT', 'ITW', 'IVZ', 'J', 'JBHT', 'JBL', 'JCI', 'JCP', 'JDSU', 'JEC', 'JEF', 'JKHY', 'JNJ', 'JNPR', 'JNS', 'JOY', 'JOYG', 'JPM', 'JWN', 'K', 'KDP', 'KEY', 'KEYS', 'KFT', 'KHC', 'KIM', 'KKR', 'KLAC', 'KMB', 'KMI', 'KMX', 'KO', 'KORS', 'KR', 'KRFT', 'KSS', 'KSU', 'KVUE', 'L', 'LB', 'LDOS', 'LEG', 'LEN', 'LH', 'LHX', 'LIFE', 'LII', 'LIN', 'LKQ', 'LLL', 'LLTC', 'LLY', 'LM', 'LMT', 'LNC', 'LNT', 'LO', 'LOW', 'LRCX', 'LSI', 'LTD', 'LUK', 'LULU', 'LUMN', 'LUV', 'LVLT', 'LVS', 'LW', 'LXK', 'LYB', 'LYV', 'M', 'MA', 'MAA', 'MAC', 'MAR', 'MAS', 'MAT', 'MCD', 'MCHP', 'MCK', 'MCO', 'MDLZ', 'MDT', 'MET', 'META', 'MGM', 'MHFI', 'MHK', 'MHP', 'MHS', 'MI', 'MJN', 'MKC', 'MKTX', 'MLM', 'MMC', 'MMI', 'MMM', 'MNK', 'MNST', 'MO', 'MOH', 'MOLX', 'MON', 'MOS', 'MPC', 'MPWR', 'MRK', 'MRNA', 'MRO', 'MS', 'MSCI', 'MSFT', 'MSI', 'MTB', 'MTCH', 'MTD', 'MU', 'MUR', 'MWV', 'MWW', 'MXIM', 'MYL', 'NAVI', 'NBL', 'NBR', 'NCLH', 'NDAQ', 'NDSN', 'NE', 'NEE', 'NEM', 'NFLX', 'NFX', 'NI', 'NKE', 'NKTR', 'NLOK', 'NLSN', 'NOC', 'NOV', 'NOW', 'NRG', 'NSC', 'NSM', 'NTAP', 'NTRS', 'NU', 'NUE', 'NVDA', 'NVLS', 'NVR', 'NWL', 'NWS', 'NWSA', 'NXPI', 'NYX', 'O', 'ODFL', 'OGN', 'OI', 'OKE', 'OMC', 'ON', 'ORCL', 'ORLY', 'OTIS', 'OXY', 'PANW', 'PARA', 'PAYC', 'PAYX', 'PBCT', 'PBI', 'PCAR', 'PCG', 'PCL', 'PCLN', 'PCP', 'PCS', 'PDCO', 'PEAK', 'PEG', 'PENN', 'PEP', 'PETM', 'PFE', 'PFG', 'PG', 'PGN', 'PGR', 'PH', 'PHM', 'PKG', 'PKI', 'PLD', 'PLL', 'PLTR', 'PM', 'PNC', 'PNR', 'PNW', 'PODD', 'POM', 'POOL', 'PPG', 'PPL', 'PRGO', 'PRU', 'PSA', 'PSX', 'PTC', 'PVH', 'PWR', 'PX', 'PXD', 'PYPL', 'QCOM', 'QEP', 'QRVO', 'R', 'RAI', 'RCL', 'RDC', 'RE', 'REG', 'REGN', 'RF', 'RHI', 'RHT', 'RIG', 'RJF', 'RL', 'RMD', 'ROK', 'ROL', 'ROP', 'ROST', 'RRC', 'RRD', 'RSG', 'RSH', 'RTN', 'RTX', 'RVTY', 'S', 'SAI', 'SBAC', 'SBNY', 'SBUX', 'SCG', 'SCHW', 'SE', 'SEDG', 'SEE', 'SHLD', 'SHW', 'SIAL', 'SIG', 'SIVB', 'SJM', 'SLB', 'SLE', 'SLG', 'SLM', 'SMCI', 'SNA', 'SNDK', 'SNI', 'SNPS', 'SO', 'SOLV', 'SPG', 'SPGI', 'SPLS', 'SRCL', 'SRE', 'STE', 'STI', 'STJ', 'STLD', 'STT', 'STX', 'STZ', 'SUN', 'SVU', 'SW', 'SWK', 'SWKS', 'SWN', 'SWY', 'SYF', 'SYK', 'SYMC', 'SYY', 'T', 'TAP', 'TDC', 'TDG', 'TDY', 'TE', 'TECH', 'TEG', 'TEL', 'TER', 'TFC', 'TFX', 'TGNA', 'TGT', 'THC', 'TIE', 'TIF', 'TJX', 'TLAB', 'TMK', 'TMO', 'TMUS', 'TPL', 'TPR', 'TRGP', 'TRIP', 'TRMB', 'TROW', 'TRV', 'TSCO', 'TSLA', 'TSN', 'TSO', 'TSS', 'TT', 'TTWO', 'TWC', 'TWTR', 'TWX', 'TXN', 'TXT', 'TYC', 'TYL', 'UA', 'UA.C', 'UAA', 'UAL', 'UBER', 'UDR', 'UHS', 'ULTA', 'UNH', 'UNM', 'UNP', 'UPS', 'URBN', 'URI', 'USB', 'UTX', 'V', 'VAR', 'VFC', 'VIAB', 'VIAC', 'VICI', 'VLO', 'VLTO', 'VMC', 'VNO', 'VNT', 'VRSK', 'VRSN', 'VRTX', 'VST', 'VTR', 'VTRS', 'VZ', 'WAB', 'WAG', 'WAT', 'WBA', 'WBD', 'WCG', 'WDAY', 'WDC', 'WEC', 'WELL', 'WFC', 'WFM', 'WFR', 'WHR', 'WIN', 'WLP', 'WLTW', 'WM', 'WMB', 'WMT', 'WPI', 'WPO', 'WPX', 'WRB', 'WRK', 'WST', 'WTW', 'WU', 'WY', 'WYN', 'WYNN', 'X', 'XEC', 'XEL', 'XL', 'XLNX', 'XOM', 'XRAY', 'XRX', 'XYL', 'YHOO', 'YUM', 'ZBH', 'ZBRA', 'ZION', 'ZMH', 'ZTS']


DATA_DIR = "data/s&p500"
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Fehler {response.status_code} beim Abrufen von {url}")
            return None
    except Exception as e:
        print(f"Exception {e} beim Abrufen von {url}")
        return None

def fetch_all_financial_data():
    stock_dividend_data = {}
    stock_split_data = {}
    income_statement_annual_data = {}
    income_statement_quarter_data = {}
    historical_price_full_data = {}

    for ticker in sp500_11to25_unique:
        print(f"Lade Daten für {ticker}...")

        stock_dividend_data[ticker] = fetch_url(f"{BASE_URL}historical-price-full/stock_dividend/{ticker}?apikey={API_KEY}")
        stock_split_data[ticker] = fetch_url(f"{BASE_URL}historical-price-full/stock_split/{ticker}?apikey={API_KEY}")
        income_statement_annual_data[ticker] = fetch_url(f"{BASE_URL}income-statement/{ticker}?period=annual&apikey={API_KEY}")
        income_statement_quarter_data[ticker] = fetch_url(f"{BASE_URL}income-statement/{ticker}?period=quarter&apikey={API_KEY}")
        historical_price_full_data[ticker] = fetch_url(f"{BASE_URL}historical-price-full/{ticker}?from=2010-12-31&to=2025-02-28&apikey={API_KEY}")

    with open(os.path.join(DATA_DIR, "stock_dividend.json"), "w") as f:
        json.dump(stock_dividend_data, f, indent=4)

    with open(os.path.join(DATA_DIR, "stock_split.json"), "w") as f:
        json.dump(stock_split_data, f, indent=4)

    with open(os.path.join(DATA_DIR, "income_statement_annual.json"), "w") as f:
        json.dump(income_statement_annual_data, f, indent=4)

    with open(os.path.join(DATA_DIR, "income_statement_quarter.json"), "w") as f:
        json.dump(income_statement_quarter_data, f, indent=4)

    with open(os.path.join(DATA_DIR, "historical_price_full.json"), "w") as f:
        json.dump(historical_price_full_data, f, indent=4)

    print("Alle Unternehmensdaten wurden gespeichert.")

def fetch_sp500_index_and_dividends():
    index_data = fetch_url(f"{BASE_URL}historical-price-full/index/^GSPC?from=2010-01-01&to=2024-12-31&apikey={API_KEY}")
    if index_data:
        with open(os.path.join(DATA_DIR, "sp500_index.json"), "w") as f:
            json.dump(index_data, f, indent=4)
        print("sp500_index.json gespeichert.")

    dividend_data = fetch_url(f"{BASE_URL}historical-price-full/stock_dividend/^GSPC?apikey={API_KEY}")
    if dividend_data:
        with open(os.path.join(DATA_DIR, "sp500_dividends.json"), "w") as f:
            json.dump(dividend_data, f, indent=4)
        print("sp500_dividends.json gespeichert.")

    constituent_data = fetch_url(f"{BASE_URL}historical/sp500_constituent?apikey={API_KEY}")
    if constituent_data:
        with open(os.path.join(DATA_DIR, "sp500_constituent.json"), "w") as f:
            json.dump(constituent_data, f, indent=4)
        print("sp500_constituent.json gespeichert.")

def fetch_symbol_changes():
    symbol_changes = fetch_url(SYMBOL_CHANGE_URL)
    if symbol_changes:
        with open(os.path.join(DATA_DIR, "symbol_change.json"), "w") as f:
            json.dump(symbol_changes, f, indent=4)
        print("symbol_change.json gespeichert.")

def main():
    fetch_all_financial_data()
    fetch_sp500_index_and_dividends()
    fetch_symbol_changes()
    print("Datenabruf abgeschlossen.")

if __name__ == "__main__":
    main()