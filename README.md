# 📈 Biathleten-Aktien

Dieses Projekt wurde im Rahmen meiner Bachelorarbeit im Studiengang Informatik an der TH Köln entwickelt. Es bildet den praktischen Teil einer wissenschaftlichen Untersuchung zur Kombination von Dividenden- und Wachstumsstrategien im Aktienmarkt. Es basiert auf einer wissenschaftlichen Untersuchung, die auf der Auswertung und Kombination mehrerer anerkannter wissenschaftlicher Studien zur Aktienbewertung, Dividenden- und Wachstumsstrategien fußt.

---

## 🧠 Hintergrund & Ziel

Die sogenannte **Biathleten-Strategie** ist ein datengetriebener Ansatz zur Aktienbewertung, der die Vorzüge von Dividenden- und Wachstumsinvestments kombiniert. Ziel ist es, ausgewogene Portfolios mit einem vorteilhaften Verhältnis von Rendite, Stabilität und Risiko zu konstruieren.

Die Analyse basiert auf allen Unternehmen des S&P 500 von 2011 bis 2024. Dabei werden vier zentrale Kennzahlen berücksichtigt:

- **Dividendenrendite**
- **10-jährige Dividendenwachstumsrate (CAGR)**
- **5-jähriges EPS-Wachstum**
- **10-jährige Umsatz-CAGR**

---

## 🧪 Zwei Varianten der Strategie

- **Filtering-Strategie**  
  Nur Aktien, die alle festgelegten Mindestschwellen gleichzeitig erfüllen, gelangen in das Portfolio eines Jahres.

- **Ranking-Strategie**  
  Alle Unternehmen werden relativ zueinander anhand der vier Kennzahlen bewertet. Die besten 20 Titel werden jährlich ausgewählt.

---

## 🧮 Methodik

- Verwendung historischer Finanzdaten der **Financial Modeling Prep API (FMP)**.
- Auswertung erfolgt vollständig automatisiert in **Python**.
- Interaktive Darstellung der Ergebnisse in **Streamlit**.
- Rückwirkende Simulation der gebildeten Portfolios über Haltedauern von **1 bis 10 Jahren**.
- Vergleich der Ergebnisse (Total Return, CAGR, kumulierte Dividenden) mit dem **S&P 500 Index**.

---

## 📊 Ergebnisse

- Die **Filtering-Strategie** übertrifft den S&P 500 bei Haltedauern von 3–5 Jahren mit **hundertprozentiger Konstanz** und erzielt im Schnitt höhere Kurszuwächse.
- Die **Ranking-Strategie** liefert zwar niedrigere Kursrenditen, aber **deutlich höhere Dividendenerträge** und eine leicht reduzierte Volatilität.
- Insgesamt zeigen beide Varianten, dass die gezielte Kombination von Dividenden- und Wachstumskennzahlen **einen signifikanten Mehrwert gegenüber passivem Index-Investieren** bieten kann.

---

## 📌 Hinweise

- Die **JSON-Rohdaten** sind aus Lizenzgründen nicht enthalten.
- Der **API-Key** für die FMP API ist nicht im Code enthalten.
- Die Berechnungen und Simulationen basieren auf lokal gespeicherten Daten.

---

## ⚖️ Lizenz

Dieses Projekt steht unter der **[GNU General Public License v3.0](LICENSE)**.

> Du darfst:
> - den Code verwenden, verändern und weitergeben,  
> - solange du deine Änderungen ebenfalls unter GPL v3 veröffentlichst,  
> - und **den ursprünglichen Autor nennst**.

© 2025 Akram  
[Informatik Bachelorarbeit – TH Köln]
