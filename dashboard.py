import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from rapport_pays_ppa_pdf import recuperer_donnees_pays

# --- Définitions des indicateurs ---
INDICATEUR_DEFS = {
    "PIB_par_habitant_PPA_USD": "Produit Intérieur Brut par habitant en Parité de Pouvoir d'Achat (USD)",
    "Croissance_PIB": "Taux de croissance annuel du PIB (%)",
    "Population": "Nombre total d'habitants",
    "Espérance_de_vie": "Espérance de vie à la naissance (années)",
    "RNB_par_habitant": "Revenu National Brut par habitant (USD)",
    "Inflation": "Taux d'inflation annuel (%)",
    "Indice_Gini": "Indice de Gini (inégalité des revenus, 0=égalité parfaite, 100=inégalité totale)",
    "Production_agricole_brute_USD": "Valeur ajoutée brute du secteur agricole (USD courants)",
    "Exportations_biens_services_PIB": "Exportations de biens et services (% du PIB)",
    "Importations_biens_services_PIB": "Importations de biens et services (% du PIB)",
    "Dette_extérieure_totale_RNB": "Dette extérieure totale (% du RNB)",
    "Balance_commerciale_USD": "Balance commerciale (USD courants)",
    "IDE_entrées_net_PIB": "Investissements directs étrangers, entrées nettes (% du PIB)",
    "Taux_chomage": "Taux de chômage (% de la population active)",
    "Depenses_sante_PIB": "Dépenses de santé (% du PIB)",
    "Depenses_education_PIB": "Dépenses d'éducation (% du PIB)",
    "Conso_energie_hab": "Consommation d'énergie par habitant (kg équivalent pétrole)"
}

ARABIC_TRANSLATIONS = {
    "PIB_par_habitant_PPA_USD": "الناتج المحلي الإجمالي للفرد (تعادل القوة الشرائية بالدولار الأمريكي)",
    "Croissance_PIB": "معدل نمو الناتج المحلي الإجمالي (%)",
    "Population": "عدد السكان",
    "Espérance_de_vie": "متوسط العمر المتوقع عند الولادة (بالسنوات)",
    "RNB_par_habitant": "الدخل القومي الإجمالي للفرد (دولار أمريكي)",
    "Inflation": "معدل التضخم السنوي (%)",
    "Indice_Gini": "مؤشر جيني (عدم المساواة في الدخل، 0 = مساواة تامة، 100 = عدم مساواة تامة)",
    "Production_agricole_brute_USD": "القيمة المضافة الإجمالية للقطاع الزراعي (دولار أمريكي)",
    "Exportations_biens_services_PIB": "صادرات السلع والخدمات (% من الناتج المحلي الإجمالي)",
    "Importations_biens_services_PIB": "واردات السلع والخدمات (% من الناتج المحلي الإجمالي)",
    "Dette_extérieure_totale_RNB": "إجمالي الدين الخارجي (% من الدخل القومي الإجمالي)",
    "Balance_commerciale_USD": "الميزان التجاري (دولار أمريكي)",
    "IDE_entrées_net_PIB": "الاستثمار الأجنبي المباشر، صافي التدفقات الداخلة (% من الناتج المحلي الإجمالي)",
    "Taux_chomage": "معدل البطالة (% من القوى العاملة)",
    "Depenses_sante_PIB": "الإنفاق على الصحة (% من الناتج المحلي الإجمالي)",
    "Depenses_education_PIB": "الإنفاق على التعليم (% من الناتج المحلي الإجمالي)",
    "Conso_energie_hab": "استهلاك الطاقة للفرد (كجم مكافئ نفط)"
}

# --- Fonction utilitaire pour convertir une image en base64 ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- ESPACE LOGO ET TITRE EN HAUT DE PAGE ---
logo_path = "foujelab.png"
logo_base64 = get_base64_of_bin_file(logo_path)
st.markdown(
    f"""
    <div style='display: flex; align-items: center; justify-content: center; margin-bottom: 10px;'>
        <img src="data:image/png;base64,{logo_base64}" alt="Logo" width="180" style="margin-right: 25px; border-radius: 15px; box-shadow: 0 4px 12px #0002;">
        <span style='font-size: 2.5em; color: #1f77b4; font-weight: bold; letter-spacing:1px; text-shadow: 1px 1px 2px #eee;'>Dashboard Économique Mondial</span>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("<hr style='border:1px solid #1f77b4; margin-top:0;'>", unsafe_allow_html=True)

# --- Traduction arabe ---
if "langue_arabe" not in st.session_state:
    st.session_state["langue_arabe"] = False

col1, col2 = st.columns([1, 8])
with col1:
    if st.button("dz Traduire en arabe"):
        st.session_state["langue_arabe"] = not st.session_state["langue_arabe"]

langue_arabe = st.session_state["langue_arabe"]

st.markdown("")

# --- Chargement des données ---
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
    # Sidebar stylée
    st.sidebar.markdown(
        "<div style='text-align:center;'><img src='https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/World_Bank_logo.svg/1200px-World_Bank_logo.svg.png' width='120'></div>",
        unsafe_allow_html=True
    )
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
        list(INDICATEUR_DEFS.keys())
    )

    df_filtre = df_annee[df_annee["Pays"].isin(pays_selectionnes)]

    tab1, tab2, tab3 = st.tabs([
        "📊 Vue générale", 
        "📈 Graphiques", 
        "🗺️ Carte mondiale"
    ])

    # --- Surbrillance verte si pays sélectionné sur la carte ---
    selected_country = st.session_state.get("selected_country", None)
    def highlight_selected(row):
        if selected_country and row["Pays"] == selected_country:
            return ['background-color: #4CAF50; color: white'] * len(row)
        return [''] * len(row)

    with tab1:
        st.markdown(
            "<div style='background-color:#f8fbff; border-radius:10px; padding:18px 10px 10px 10px; border:1px solid #e0eafc;'>",
            unsafe_allow_html=True
        )
        st.subheader(f"📋 Données détaillées des pays sélectionnés ({annee_selection})")
        format_dict = {
            "PIB_par_habitant_PPA_USD": "{:.0f}",
            "Croissance_PIB": "{:.2f}%",
            "RNB_par_habitant": "{:.0f}",
            "Population": "{:,}",
            "Espérance_de_vie": "{:.1f}",
            "Inflation": "{:.2f}%",
            "Indice_Gini": "{:.2f}",
            "Production_agricole_brute_USD": "{:.0f}",
            "Exportations_biens_services_PIB": "{:.2f}%",
            "Importations_biens_services_PIB": "{:.2f}%",
            "Dette_extérieure_totale_RNB": "{:.2f}%",
            "Balance_commerciale_USD": "{:.0f}",
            "IDE_entrées_net_PIB": "{:.2f}%",
            "Taux_chomage": "{:.2f}%",
            "Depenses_sante_PIB": "{:.2f}%",
            "Depenses_education_PIB": "{:.2f}%",
            "Conso_energie_hab": "{:.0f}"
        }
        st.dataframe(
            df_filtre.style.format(format_dict, na_rep="-").apply(highlight_selected, axis=1)
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown(
            "<div style='background-color:#f8fbff; border-radius:10px; padding:18px 10px 10px 10px; border:1px solid #e0eafc;'>",
            unsafe_allow_html=True
        )
        st.subheader("📉 Comparaison des indicateurs")
        choix_indicateur = st.selectbox("Choisissez un indicateur à comparer :", list(INDICATEUR_DEFS.keys()))
        fig_compare = px.bar(
            df_filtre,
            x='Pays',
            y=choix_indicateur,
            title=f"Comparaison par pays : {choix_indicateur.replace('_', ' ')} ({annee_selection})",
            color='Pays'
        )
        st.plotly_chart(fig_compare, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown(
            "<div style='background-color:#f8fbff; border-radius:10px; padding:18px 10px 10px 10px; border:1px solid #e0eafc;'>",
            unsafe_allow_html=True
        )
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
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("📄 Voir toutes les données brutes"):
        st.dataframe(df_annee)

else:
    st.warning("⚠️ Aucune donnée disponible. Réessaye plus tard ou vérifie ta connexion Internet.")

st.markdown("---")

# --- Bloc définitions stylé en bas ---
st.markdown(
    """
    <div style='background-color:#f4f8fa; border-radius:10px; padding:18px 25px 10px 25px; border:1px solid #e0eafc; margin-top:25px;'>
        <h4 style='color:#1f77b4; margin-bottom: 10px;'>Définitions des indicateurs</h4>
    """,
    unsafe_allow_html=True
)

# Bouton traduction juste au-dessus des définitions
col1, col2 = st.columns([1, 8])
with col1:
    if st.button("🇸🇦 Traduire en arabe", key="traduction_bas"):
        st.session_state["langue_arabe"] = not st.session_state["langue_arabe"]

langue_arabe = st.session_state.get("langue_arabe", False)

if not langue_arabe:
    for k, v in INDICATEUR_DEFS.items():
        st.markdown(f"<b>{k}</b> : {v}", unsafe_allow_html=True)
else:
    for k, v in ARABIC_TRANSLATIONS.items():
        st.markdown(f"<b>{k}</b> : {v}", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    "<p style='text-align: center; color: #888; margin-top:20px;'>Dashboard interactif basé sur les données de la Banque Mondiale et Our World in Data</p>",
    unsafe_allow_html=True
)

# --- Logo et titre en haut, version plus petite ---
logo_path = "foujelab.png"
logo_base64 = get_base64_of_bin_file(logo_path)
st.markdown(
    f"""
    <div style='display: flex; align-items: center; justify-content: center; margin-bottom: 6px;'>
        <img src="data:image/png;base64,{logo_base64}" alt="Logo" width="70" style="margin-right: 12px; border-radius: 8px; box-shadow: 0 2px 6px #0001;">
        <span style='font-size: 1.1em; color: #1f77b4; font-weight: bold; letter-spacing:1px; text-shadow: 1px 1px 2px #eee;'>Dashboard Économique Mondial</span>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("<hr style='border:1px solid #1f77b4; margin-top:0;'>", unsafe_allow_html=True)