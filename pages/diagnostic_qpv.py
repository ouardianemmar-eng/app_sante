
import streamlit as st
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from etablissement.utils import load_data, build_carte


def main():

    # -------------------------------------------------------------------------
    # ⚙️ CONFIGURATION GÉNÉRALE
    # -------------------------------------------------------------------------
    st.set_page_config(
        page_title="Diagnostic QPV – Toulouse",
        layout="wide",
        page_icon="🏙️"
    )

    # -------------------------------------------------------------------------
    # 🧭 SIDEBAR
    # -------------------------------------------------------------------------
    with st.sidebar:
        st.header("ℹ️ À propos")
        st.write("Diagnostic des Quartiers Prioritaires de Toulouse.")
        st.write("Sources : INSEE, IGN, Toulouse Métropole")
        st.markdown("---")
        st.write("Application réalisée avec Streamlit.")

    # -------------------------------------------------------------------------
    # 📌 FONCTIONS INTERNES
    # -------------------------------------------------------------------------
    @st.cache_data
    def compute_indicators(_df):  # underscore = évite erreur hash GeoDataFrame
        df = _df.copy()

        qpv = df[df["is_qpv"] == 1]
        hors = df[df["is_qpv"] == 0]

        revenu_qpv = qpv["revenu_median"].median()
        revenu_hors = hors["revenu_median"].median()

        return {
            "nb_qpv": qpv.shape[0],
            "nb_iris": df.shape[0],
            "revenu_qpv": revenu_qpv,
            "revenu_hors": revenu_hors,
            "ecart": revenu_hors - revenu_qpv if revenu_qpv and revenu_hors else None,
            "ratio": round(revenu_qpv / revenu_hors, 2) if revenu_hors and revenu_hors > 0 else None
        }

    # -------------------------------------------------------------------------
    # 🏙️ TITRE PRINCIPAL
    # -------------------------------------------------------------------------
    st.title("🏙️ Diagnostic QPV – Toulouse")

    st.markdown("""
    Cette application présente un diagnostic complet des Quartiers Prioritaires de Toulouse :

    - Carte interactive  
    - Indicateurs clés  
    - Graphiques  
    - Tableau des IRIS  
    """)

    # -------------------------------------------------------------------------
    # 📥 CHARGEMENT DES DONNÉES
    # -------------------------------------------------------------------------
    iris_tlse = load_data()
    iris_tlse = iris_tlse.dropna(subset=["revenu_median"])

    # -------------------------------------------------------------------------
    # 🧩 ONGLET
    # -------------------------------------------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗺️ Carte QPV",
        "📊 Indicateurs",
        "📈 Graphiques",
        "📋 Tableau IRIS"
    ])

    # -------------------------------------------------------------------------
    # 🗺️ TAB 1 — CARTE
    # -------------------------------------------------------------------------
    with tab1:
        st.subheader("🗺️ Carte interactive des QPV")
        m = build_carte(iris_tlse)
        st_folium(m, width=1000, height=650)

    # -------------------------------------------------------------------------
    # 📊 TAB 2 — INDICATEURS
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("📊 Indicateurs clés")

        ind = compute_indicators(iris_tlse)

        col1, col2, col3 = st.columns(3)
        col1.metric("Nombre de QPV", ind["nb_qpv"])
        col2.metric("Revenu médian QPV",
                    f"{ind['revenu_qpv']:.0f} €" if ind["revenu_qpv"] else "N/A")
        col3.metric("Revenu médian hors QPV",
                    f"{ind['revenu_hors']:.0f} €" if ind["revenu_hors"] else "N/A")

        col4, col5 = st.columns(2)
        col4.metric("Écart de revenu",
                    f"{ind['ecart']:.0f} €" if ind["ecart"] else "N/A")
        col5.metric("Ratio QPV / hors QPV",
                    ind["ratio"] if ind["ratio"] else "N/A")

        st.caption("Le revenu médian est calculé uniquement sur les IRIS disposant d’une donnée valide.")

    # -------------------------------------------------------------------------
    # 📈 TAB 3 — GRAPHIQUES
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("📈 Graphiques")

        colA, colB = st.columns(2)

        # Histogramme
        with colA:
            st.write("Distribution du revenu médian")
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.histplot(iris_tlse["revenu_median"], kde=True, ax=ax)
            ax.set_xlabel("Revenu médian (€)")
            st.pyplot(fig)

        # Boxplot
        with colB:
            st.write("Revenu médian : QPV vs hors QPV")
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.boxplot(
                data=iris_tlse,
                x="is_qpv",
                y="revenu_median",
                ax=ax
            )
            ax.set_xticks([0, 1])
            ax.set_xticklabels(["Hors QPV", "QPV"])
            st.pyplot(fig)

        # Bar chart QPV
        st.write("Revenu médian par quartier QPV")
        qpv = iris_tlse[iris_tlse["is_qpv"] == 1][["NOM_IRIS", "revenu_median"]]
        qpv = qpv.sort_values("revenu_median")

        fig, ax = plt.subplots(figsize=(10, 7))
        sns.barplot(data=qpv, x="revenu_median", y="NOM_IRIS", ax=ax)
        ax.set_xlabel("Revenu médian (€)")
        st.pyplot(fig)

    # -------------------------------------------------------------------------
    # 📋 TAB 4 — TABLEAU
    # -------------------------------------------------------------------------
    with tab4:
        st.subheader("📋 Tableau complet des IRIS")

        filtre = st.selectbox(
            "Filtrer par type de zone",
            ["Tous", "QPV", "Hors QPV"]
        )

        df = iris_tlse.copy()

        if filtre == "QPV":
            df = df[df["is_qpv"] == 1]
        elif filtre == "Hors QPV":
            df = df[df["is_qpv"] == 0]

        st.dataframe(
            df[["NOM_IRIS", "is_qpv", "revenu_median"]],
            hide_index=True
        )

        st.download_button(
            "📥 Télécharger les données",
            data=df.to_csv(index=False),
            file_name="iris_toulouse.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main()