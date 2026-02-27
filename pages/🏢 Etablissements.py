import streamlit as st
import plotly.express as px
import pandas as pd


st.set_page_config(layout="wide", page_title="Dashboard Santé Occitanie")

# ─── CHARGEMENT DONNÉES ───────────────────────────────────────────
df = pd.read_csv("../data/finess_occitanie2.csv", dtype={"departement": str})
df_distances = pd.read_csv("data/distances_communes_urgence_occitanie.csv")
df_communes = pd.read_csv("data/communes-france-2025.csv", sep=",", encoding="utf-8")
df_communes_occitanie = df_communes[df_communes['reg_nom'] == 'Occitanie']
df_urgences = df[df['libelle activite'].str.contains("urgence", case=False, na=False)]
df_join = pd.read_csv("data/finess_occitanie_join.csv")
df['longitude'] = df['longitude'].astype(float)
df['latitude'] = df['latitude'].astype(float)
#Sélectionne uniquement les données de la métropole de Toulouse
df_toulouse = df_join[df_join['epci_nom'] == 'Toulouse Métropole']
df_cc = df_join[df_join['epci_nom'] == 'CC Pyrénées Audoises']


# ─── ONGLET PRINCIPAL ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏥 Vue d’ensemble", "📍 Établissements", "🩺 Soins",  "🚑 Distances aux urgences", "🌇 Métropôle de Toulouse", "🐄 CC Pyrénées Audoises"
])

# =================================================================
# 🟦 ONGLET 1 — KPI + TYPOLOGIES
# =================================================================
with tab1:
    st.header("Vue d’ensemble des établissements de santé en Occitanie")

    # --- KPI ---
    total_etabs = df['numero finess etablissement'].nunique()
    nb_types = df['type d etablissements'].nunique()
    nb_deps = df['departement'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Établissements recensés", f"{total_etabs}")
    col2.metric("Types d’établissements", f"{nb_types}")
    col3.metric("Départements couverts", f"{nb_deps}")
    col4.metric("Nb de personnes par établissement", f"{df_communes_occitanie['population'].sum()/df['numero finess etablissement'].nunique(): .0f}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Établissements recensés en France", f"102553")
    col2.metric("Types d’établissements", f"{nb_types}")
    col3.metric("Départements couverts en France", f"106")
    col4.metric("Nb de personnes par établissement en France", f"673")

    st.markdown(f"""
                ### 📍 Informations clés
    L'occitanie représente {round(total_etabs/102553*100, 2)} % des établissements de santé en France.
    Avec une population d'environ {df_communes_occitanie['population'].sum():,} habitants, soit 11,47% de la population française.Cela correspond à environ {round(df_communes_occitanie['population'].sum()/total_etabs):,} personnes par établissement.""")
    st.subheader("Typologie des établissements")

    table_typo = (
        df.groupby('type d etablissements')
          .agg(nb_etablissements=('numero finess etablissement', 'count'))
          .reset_index()
    )
    table_typo['pourcentage'] = (table_typo['nb_etablissements'] / total_etabs * 100).round(2)
    table_typo = table_typo.sort_values('nb_etablissements', ascending=False)

    st.dataframe(table_typo, use_container_width=True, hide_index=True)

    fig_typo = px.bar(
        table_typo,
        x='type d etablissements',
        y='nb_etablissements',
        title="Nombre d'établissements par typologie",
        labels={'type d etablissements': 'Typologie', 'nb_etablissements': 'Nombre'},
    )
    st.plotly_chart(fig_typo, use_container_width=True)

# =================================================================
# 🟩 ONGLET 2 — CARTE PAR TYPE D'ÉTABLISSEMENT
# =================================================================
with tab2:
    st.header("Carte interactive des établissements de santé")

    groupes = sorted(df['type d etablissements'].dropna().unique())
    departements = sorted(df['departement'].dropna().unique())

    option_tous_groupes = "Tous les types"
    option_tous_deps = "Tous les départements"

    selection_groupes = st.multiselect(
        "Sélectionner un ou plusieurs types d'établissements :",
        [option_tous_groupes] + groupes,
        default=[option_tous_groupes],
        key="filtre_groupes"
    )

    selection_deps = st.multiselect(
        "Sélectionner un ou plusieurs départements :",
        [option_tous_deps] + departements,
        default=[option_tous_deps],
        key="filtre_departements"
    )

    df_filtre = df.copy()

    if option_tous_groupes not in selection_groupes:
        df_filtre = df_filtre[df_filtre['type d etablissements'].isin(selection_groupes)]

    if option_tous_deps not in selection_deps:
        df_filtre = df_filtre[df_filtre['departement'].isin(selection_deps)]

    if not df_filtre.empty:
        center_lat = df_filtre['latitude'].mean()
        center_lon = df_filtre['longitude'].mean()
    else:
        center_lat, center_lon = 46.5, 2.5

    fig = px.scatter_map(
        df_filtre,
        lat="latitude",
        lon="longitude",
        hover_name="raison_sociale",
        hover_data={"type d etablissements": True},
        color="type d etablissements",
        zoom=6,
        height=650
    )

    fig.update_layout(
        map_style="open-street-map",
        map_center={"lat": center_lat, "lon": center_lon},
        margin={"r":0, "t":0, "l":0, "b":0}
    )

    st.plotly_chart(fig, use_container_width=True)

# =================================================================
# 🟧 ONGLET 3 — CARTE PAR TYPE DE SOIN
# =================================================================
with tab3:
    st.header("Carte interactive des soins de santé")

    # --- KPI ---
    total_soins = df['libelle activite'].notna().sum()
    

    col1, col2, col3 = st.columns(3)
    col1.metric("Nombre d'Établissements de soins recensés", f"{total_soins}")
    
   

    soins = sorted(df['libelle activite'].dropna().unique())
    departements2 = sorted(df['departement'].dropna().unique())

    option_tous_soins = "Tous les soins"
    option_tous_deps2 = "Tous les départements"

    selection_soins = st.multiselect(
        "Sélectionner un ou plusieurs soins :",
        [option_tous_soins] + soins,
        default=[option_tous_soins],
        key="filtre_soins"
    )

    selection_deps2 = st.multiselect(
        "Sélectionner un ou plusieurs départements :",
        [option_tous_deps2] + departements2,
        default=[option_tous_deps2],
        key="filtre_departements_soins"
    )

    df_filtre2 = df.copy()

    if option_tous_soins not in selection_soins:
        df_filtre2 = df_filtre2[df_filtre2['libelle activite'].isin(selection_soins)]

    if option_tous_deps2 not in selection_deps2:
        df_filtre2 = df_filtre2[df_filtre2['departement'].isin(selection_deps2)]

    if not df_filtre2.empty:
        center_lat = df_filtre2['latitude'].mean()
        center_lon = df_filtre2['longitude'].mean()
    else:
        center_lat, center_lon = 46.5, 2.5

    fig2 = px.scatter_map(
        df_filtre2,
        lat="latitude",
        lon="longitude",
        hover_name="raison_sociale",
        hover_data={"type d etablissements": True},
        color="libelle activite",
        zoom=6,
        height=650
    )

    fig2.update_layout(
        map_style="open-street-map",
        map_center={"lat": center_lat, "lon": center_lon},
        margin={"r":0, "t":0, "l":0, "b":0}
    )

    st.plotly_chart(fig2, use_container_width=True)

# =================================================================
# 🟧 ONGLET 4 — SERVICES D URGENCE
# =================================================================

with tab4:
    st.header("Distance aux services d’urgence")

    # Charger les distances calculées dans le notebook
    df_dist = df_distances.copy()

    # KPI distance moyenne
    distance_moyenne = df_dist["distance_urgence_km"].mean()

    st.metric(
        "Distance moyenne au service d’urgence le plus proche",
        f"{distance_moyenne:.1f} km"
    )

    # Tableau complet
    st.subheader("Distances par commune")

    colonnes_a_garder = [
        "code_insee",
        "nom_standard",
        "dep_nom",
        "canton_nom",
        "epci_nom",
        "distance_urgence_km"
    ]

    df_final = df_dist[colonnes_a_garder].sort_values("distance_urgence_km", ascending=False)

    st.dataframe(df_final, use_container_width=True)




    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distance moyenne par département")
    # Distance moyenne par département
        
        distance_par_dep = (
            df_dist
            .groupby('dep_nom')['distance_urgence_km']
            .mean()
            .reset_index()
            .sort_values('distance_urgence_km')
        )

        st.dataframe(distance_par_dep, use_container_width=True, hide_index=True)
    

    with col2:
        col2.subheader("Distance moyenne par densité de population")
        # Distance moyenne par densité de population

        distance_par_dep = (
           df_dist 
            .groupby('grille_densite_texte')['distance_urgence_km']
            .mean()
            .reset_index()
            .sort_values('distance_urgence_km')
        )

  
        st.dataframe(distance_par_dep, use_container_width=True, hide_index=True)

    # Mettre un graphique de distribution des distances
    


    # ───────────────────────────────────────────────
    #  Histogramme lissé (density) — sans SciPy
    # ───────────────────────────────────────────────
    st.subheader("Distribution lissée (density)")

    fig_density = px.histogram(
        df_dist,
        x="distance_urgence_km",
        nbins=40,
        histnorm="density",
        opacity=0.6,
        title="Distribution lissée des distances aux urgences",
        labels={"distance_urgence_km": "Distance (km)"},
        marginal="box"  # ajoute un boxplot au-dessus
    )

    st.plotly_chart(fig_density, use_container_width=True)

    st.header("Carte des communes et des centres d’urgence")

    # --- Carte Plotly ---
    fig = px.scatter_map(
        df_distances,
        lat="latitude_centre",
        lon="longitude_centre",
        hover_name="nom_standard",
        hover_data={"dep_nom": True, "distance_urgence_km": True},
        color="distance_urgence_km",   # 🔥 coloration selon la distance
        color_continuous_scale="Viridis",  # ou "Turbo", "Plasma", "Inferno"

        zoom=6,
        height=700
    )

    # Ajouter les centres d’urgence en rouge
    fig.add_scattermap(
        lat=df_urgences["latitude"],
        lon=df_urgences["longitude"],
        mode="markers",
        marker=dict(size=10, color="red"),
        name="Centres d'urgence",
        hovertext=df_urgences["raison_sociale"]
    )

    fig.update_layout(
        map_style="open-street-map",
        margin={"r":0, "t":0, "l":0, "b":0}
    )

    st.plotly_chart(fig, use_container_width=True)



# =================================================================
# 🟧 ONGLET 5 — TOULOUSE
# =================================================================

with tab5:
    st.header("Métropôle de Toulouse")
    df_communes_met_toulouse = df_communes_occitanie[df_communes_occitanie['epci_nom'] == 'Toulouse Métropole']
    print('Population de la métropole de Toulouse :', df_communes_met_toulouse['population'].sum())



    # --- KPI ---
    total_etabs = df_toulouse['numero finess etablissement'].nunique()
    nb_types = df_toulouse['type d etablissements'].nunique()
    nb_communes = df_communes_met_toulouse['nom_standard'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Établissements recensés", f"{total_etabs}")
    col2.metric("Types d’établissements", f"{nb_types}")
    col3.metric("Communes couvertes", f"{nb_communes}")
    col4.metric("Nb de personnes par établissement", f"{df_communes_met_toulouse['population'].sum()/df_toulouse['numero finess etablissement'].nunique(): .0f}")

    st.subheader("Typologie des établissements de Toulouse")

    table_typo = (
        df_toulouse.groupby('type d etablissements')
          .agg(nb_etablissements=('numero finess etablissement', 'count'))
          .reset_index()
    )
    table_typo['pourcentage'] = (table_typo['nb_etablissements'] / total_etabs * 100).round(2)
    table_typo = table_typo.sort_values('nb_etablissements', ascending=False)

    st.dataframe(table_typo, use_container_width=True, hide_index=True)

    fig_typo = px.bar(
        table_typo,
        x='type d etablissements',
        y='nb_etablissements',
        title="Nombre d'établissements par typologie",
        labels={'type d etablissements': 'Typologie', 'nb_etablissements': 'Nombre'},
    )
    st.plotly_chart(fig_typo, use_container_width=True)
    # --- Carte interactive des établissements de Toulouse ---
    
    groupes_toulouse = sorted(df_toulouse['type d etablissements'].dropna().unique())
    communes = sorted(df_toulouse['nom_standard'].dropna().unique())

    option_tous_groupes_toulouse = "Tous les types"
    option_toutes_communes = "Toutes les communes"

    selection_groupes = st.multiselect(
        "Sélectionner un ou plusieurs types d'établissements :",
        [option_tous_groupes_toulouse] + groupes_toulouse,
        default=[option_tous_groupes_toulouse],
        key="filtre_groupes_toulouse"
    )

    selection_communes = st.multiselect(
        "Sélectionner une ou plusieurs communes :",
        [option_toutes_communes] + communes,
        default=[option_toutes_communes],
        key="filtre_communes"
    )

    df_filtre_toulouse = df_toulouse.copy()

    if option_tous_groupes_toulouse not in selection_groupes:
        df_filtre_toulouse = df_filtre_toulouse[df_filtre_toulouse['type d etablissements'].isin(selection_groupes)]

    if option_toutes_communes not in selection_communes:
        df_filtre_toulouse = df_filtre_toulouse[df_filtre_toulouse['nom_standard'].isin(selection_communes)]

    # Centre de la carte je veux le
    center_lat = 43.6045
    center_lon = 1.4440
    zoom_level = 13


    fig = px.scatter_map(
        df_filtre_toulouse,
        lat="latitude",
        lon="longitude",
        hover_name="raison_sociale",
        hover_data={"type d etablissements": True},
        color="type d etablissements",
        zoom=6,
        height=650
    )

    fig.update_layout(
        map_style="open-street-map",
        map_center={"lat": center_lat, "lon": center_lon},
        margin={"r":0, "t":0, "l":0, "b":0}
    )

    st.plotly_chart(fig, use_container_width=True)

# =================================================================
# 🟧 ONGLET 6 — CC PYRENEES AUDOISES
# =================================================================

with tab6:
    st.header("🐄 CC Pyrénées Audoises")
    df_communes_met_cc = df_communes_occitanie[df_communes_occitanie['epci_nom'] == 'CC Pyrénées Audoises']
    print('Population de la CC Pyrénées Audoises :', df_communes_met_cc['population'].sum())



    # --- KPI ---
    total_etabs = df_cc['numero finess etablissement'].nunique()
    nb_types = df_cc['type d etablissements'].nunique()
    nb_communes = df_communes_met_cc['nom_standard'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Établissements recensés", f"{total_etabs}")
    col2.metric("Types d’établissements", f"{nb_types}")
    col3.metric("Communes couvertes", f"{nb_communes}")
    col4.metric("Nb de personnes par établissement", f"{df_communes_met_cc['population'].sum()/df_cc['numero finess etablissement'].nunique(): .0f}")

    st.subheader("Typologie des établissements de la CC Pyrénées Audoises")

    table_typo_cc = (
        df_cc.groupby('type d etablissements')
          .agg(nb_etablissements=('numero finess etablissement', 'count'))
          .reset_index()
    )
    table_typo_cc['pourcentage'] = (table_typo_cc['nb_etablissements'] / total_etabs * 100).round(2)
    table_typo_cc = table_typo_cc.sort_values('nb_etablissements', ascending=False)

    st.dataframe(table_typo_cc, use_container_width=True, hide_index=True)

    fig_typo = px.bar(
        table_typo_cc,
        x='type d etablissements',
        y='nb_etablissements',
        title="Nombre d'établissements par typologie",
        labels={'type d etablissements': 'Typologie', 'nb_etablissements': 'Nombre'},
    )
    st.plotly_chart(fig_typo, use_container_width=True)
    # --- Carte interactive des établissements de CC Pyrénees  ---

    groupes_cc = sorted(df_cc['type d etablissements'].dropna().unique())
    communes_cc = sorted(df_cc['nom_standard'].dropna().unique())

    option_tous_groupes_cc = "Tous les types"
    option_toutes_communes_cc = "Toutes les communes"

    selection_groupes = st.multiselect(
        "Sélectionner un ou plusieurs types d'établissements :",
        [option_tous_groupes_cc] + groupes_cc,
        default=[option_tous_groupes_cc],
        key="filtre_groupes_cc"
    )

    selection_communes = st.multiselect(
        "Sélectionner une ou plusieurs communes :",
        [option_toutes_communes_cc] + communes_cc,
        default=[option_toutes_communes_cc],
        key="filtre_communes_cc"
    )

    df_filtre_cc = df_cc.copy()

    if option_tous_groupes_cc not in selection_groupes:
        df_filtre_cc = df_filtre_cc[df_filtre_cc['type d etablissements'].isin(selection_groupes)]

    if option_toutes_communes_cc not in selection_communes:
        df_filtre_cc = df_filtre_cc[df_filtre_cc['nom_standard'].isin(selection_communes)]

    # Centre de la carte je veux le
    center_lat = df_communes_met_cc["latitude_centre"].mean()
    center_lon = df_communes_met_cc["longitude_centre"].mean()

    zoom_level = 13


    fig = px.scatter_map(
        df_filtre_cc,
        lat="latitude",
        lon="longitude",
        hover_name="raison_sociale",
        hover_data={"type d etablissements": True},
        color="type d etablissements",
        zoom=6,
        height=650
    )

    fig.update_layout(
        map_style="open-street-map",
        map_center={"lat": center_lat, "lon": center_lon},
        margin={"r":0, "t":0, "l":0, "b":0}
    )

    st.plotly_chart(fig, use_container_width=True)

