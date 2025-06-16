# dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
from rapport_pays_ppa_pdf import recuperer_donnees_pays
import base64

# --- Fonction utilitaire pour convertir une image en base64 ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- ESPACE LOGO EN HAUT DE PAGE ---
logo_path = "C:/Users/asus/Desktop/test/foujelab.png"
logo_base64 = get_base64_of_bin_file(logo_path)


# ...ou plus simplement, juste avant le titre :
st.image("C:/Users/asus/Desktop/test/foujelab.png", width=80)
st.markdown("<h1 style='text-align: center; color: #1f77b4;'>🌍 Dashboard Économique Mondial</h1>", unsafe_allow_html=True)

@st.cache_data
def charger_donnees():
    try:
        df = recuperer_donnees_pays()
        st.success("✅ Données chargées avec succès !")
        return df
    except Exception as e:
        st.error(f"❌ Échec du chargement des données : {e}")
        return pd.DataFrame()

df = charger_donnees()

if not df.empty:
    # Vérification des colonnes
    if "Année" not in df.columns:
        st.error(f"❌ La colonne 'Année' est absente des données. Colonnes disponibles : {list(df.columns)}")
        st.stop()
    # Sidebar
    st.sidebar.header("🔍 Filtres")

    annees_dispo = sorted(df["Année"].dropna().unique(), reverse=True)
    annee_selection = st.sidebar.selectbox("Année", annees_dispo, index=0)

    df_annee = df[df["Année"] == annee_selection]

    default_countries = df_annee["Pays"].head(3).tolist()
    pays_selectionnes = st.sidebar.multiselect(
        "Sélectionnez des pays",
        options=df_annee["Pays"].unique(),
        default=default_countries,
        key="pays_multiselect"
    )

    indicateur_principal = st.sidebar.selectbox(
        "Indicateur à afficher sur la carte",
        [
            "PIB_par_habitant_PPA_USD", "Croissance_PIB", "Inflation",
            "Indice_Gini", "RNB_par_habitant", "Espérance_de_vie", "Population"
        ]
    )

    df_filtre = df_annee[df_annee["Pays"].isin(pays_selectionnes)]

    tab1, tab2, tab3 = st.tabs(["📊 Vue générale", "📈 Graphiques", "🗺️ Carte mondiale"])

    # --- GESTION DE LA SÉLECTION SUR LA CARTE ---
    selected_country = st.session_state.get("selected_country", None)

    with tab3:
        st.subheader(f"🗺️ Carte mondiale - {indicateur_principal.replace('_', ' ')} ({annee_selection})")
        fig_map = px.choropleth(
            df_annee,
            locations='Code_Pays',
            locationmode='ISO-3',
            color=indicateur_principal,
            hover_name='Pays',
            color_continuous_scale='Blues',
            title=f"{indicateur_principal.replace('_', ' ')} par pays ({annee_selection})"
        )
        selected = st.plotly_chart(fig_map, use_container_width=True)
        # Pour la sélection, il faut utiliser st.session_state ou un composant externe si besoin

    # --- SURBRILLANCE DANS LE TABLEAU ---
    def highlight_selected(row):
        if selected_country and row["Pays"] == selected_country:
            return ['background-color: #4CAF50; color: white'] * len(row)
        return [''] * len(row)

    with tab1:
        st.subheader(f"📋 Données détaillées des pays sélectionnés ({annee_selection})")
        st.dataframe(
            df_filtre.style.format({
                "PIB_par_habitant_PPA_USD": "{:.0f}",
                "Croissance_PIB": "{:.2f}%",
                "RNB_par_habitant": "{:.0f}",
                "Population": "{:,}",
                "Espérance_de_vie": "{:.1f}",
                "Inflation": "{:.2f}%",
                "Indice_Gini": "{:.2f}"
            }, na_rep="-").apply(highlight_selected, axis=1)
        )

    with tab2:
        st.subheader("📉 Comparaison des indicateurs")
        choix_indicateur = st.selectbox("Choisissez un indicateur à comparer :", [
            "PIB_par_habitant_PPA_USD", "Croissance_PIB", "RNB_par_habitant", "Inflation", "Indice_Gini", "Population"
        ])
        fig_compare = px.bar(
            df_filtre,
            x='Pays',
            y=choix_indicateur,
            title=f"Comparaison par pays : {choix_indicateur.replace('_', ' ')} ({annee_selection})",
            color='Pays'
        )
        st.plotly_chart(fig_compare, use_container_width=True)

else:
    st.warning("⚠️ Aucune donnée disponible. Réessaye plus tard ou vérifie ta connexion Internet.")

st.markdown("---")
st.markdown("<p style='text-align: center;'>Dashboard interactif basé sur les données de la Banque Mondiale</p>", unsafe_allow_html=True)