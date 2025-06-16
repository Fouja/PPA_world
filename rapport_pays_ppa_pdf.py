# rapport_pays_ppa_pdf.py

import requests
import pandas as pd
from functools import reduce

# Indicateurs Banque Mondiale (code: nom lisible)
INDICATEURS = {
    "PIB_par_habitant_PPA_USD": "NY.GDP.PCAP.PP.CD",
    "Croissance_PIB": "NY.GDP.MKTP.KD.ZG",
    "Population": "SP.POP.TOTL",
    "Espérance_de_vie": "SP.DYN.LE00.IN",
    "RNB_par_habitant": "NY.GNI.PCAP.CD",
    "Inflation": "FP.CPI.TOTL.ZG",
    "Indice_Gini": "SI.POV.GINI",
    # L'IDH n'est pas disponible sur la Banque Mondiale, il faudra une autre source si besoin
}

def fetch_indicator(indicator_code, start_year=2000, end_year=2023):
    url = (
        f"https://api.worldbank.org/v2/en/indicator/{indicator_code}"
        f"?downloadformat=csv"
    )
    # Utilisation de l'API JSON pour toutes les années
    url_json = (
        f"https://api.worldbank.org/v2/country/all/indicator/{indicator_code}"
        f"?format=json&per_page=20000&date={start_year}:{end_year}"
    )
    try:
        r = requests.get(url_json)
        r.raise_for_status()
        data = r.json()
        if len(data) < 2 or not isinstance(data[1], list):
            return pd.DataFrame()
        records = []
        for item in data[1]:
            if not item.get("country") or not item.get("countryiso3code"):
                continue
            records.append({
                "Pays": item["country"]["value"],
                "Code_Pays": item["countryiso3code"],
                "Année": int(item["date"]),
                indicator_code: float(item["value"]) if item["value"] is not None else None
            })
        return pd.DataFrame(records)
    except Exception as e:
        print(f"Erreur récupération {indicator_code}: {e}")
        return pd.DataFrame()

def recuperer_donnees_pays(start_year=2000, end_year=2023):
    """
    Télécharge les données des indicateurs économiques pour tous les pays via l'API de la Banque Mondiale.
    Retourne un DataFrame avec les données nettoyées et classées par PIB/hab en PPA.
    """

    print("📞 Récupération des données depuis l'API de la Banque Mondiale...")

    # Récupère tous les indicateurs et fusionne sur Pays, Code_Pays, Année
    dfs = []
    for nom, code in INDICATEURS.items():
        df = fetch_indicator(code, start_year, end_year)
        if not df.empty:
            # Renommer uniquement la colonne de valeur, jamais la colonne Année
            cols_to_rename = {code: nom}
            # Si une colonne Année_X existe, la renommer en Année
            annee_cols = [c for c in df.columns if c.startswith("Année") and c != "Année"]
            if annee_cols:
                cols_to_rename[annee_cols[0]] = "Année"
            df = df.rename(columns=cols_to_rename)
            dfs.append(df)
    # Fusionne tous les DataFrames sur Pays, Code_Pays, Année
    if not dfs:
        return pd.DataFrame()
    df_final = reduce(
        lambda left, right: pd.merge(left, right, on=["Pays", "Code_Pays", "Année"], how="outer"),
        dfs
    )
    # Trie et ajoute le classement par année
    df_final = df_final.sort_values(["Année", "PIB_par_habitant_PPA_USD"], ascending=[False, False])
    df_final["Classement"] = df_final.groupby("Année")["PIB_par_habitant_PPA_USD"].rank(ascending=False, method="min")
    # Nettoie les noms de pays vides
    df_final = df_final[df_final["Pays"].notna()]
    return df_final.reset_index(drop=True)