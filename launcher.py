import os
import sys
import subprocess


def main():
    print("Bitte wähle die Strategie:")
    print("1 - Ranking-Strategie")
    print("2 - Filtering-Strategie")
    choice = input("Deine Wahl (1 oder 2): ").strip()

    if choice == "1":
        print("Starte Ranking-Strategie (ranking_analysis/streamlit_app_ranking.py)...")
        subprocess.run(["streamlit", "run", "ranking_analysis/streamlit_app_ranking.py"])
    elif choice == "2":
        print("Starte Filtering-Strategie (streamlit_app_filtering.py)...")

        subprocess.run(["streamlit", "run", "filtering_analysis/streamlit_app_filtering.py"])
    else:
        print("Ungültige Eingabe. Bitte 1 oder 2 wählen.")
        sys.exit(1)


if __name__ == '__main__':
    main()

