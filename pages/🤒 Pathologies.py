# %%
import pandas as pd
import matplotlib .pyplot as plt
import seaborn as sns
import streamlit as st
import re

data = pd.read_csv('data/pathologie_clean.csv',sep=",")
# Création des onglets
tab1, tab2, tab3 = st.tabs([
    " Profil épidémiologique de la Haute-Garonne (2023)",
    "Dynamique pluriannuelle des 5 pathologies majeures",
    "Zoom sur les maladies respiratoire chroniques"
])

#st.title("Dashboard sur l'état de Santé dans le Département 31")
###################vsiualisation des pathologies existantes et leur  prevalence dans le dept 31###########################

hors_patho = ["Affections de longue durée (dont 31 et 32) pour d'autres causes",
                'Hospitalisations hors pathologies repérées (avec ou sans pathologies, traitements ou maternité)',
                'Traitements antalgiques ou anti-inflammatoires (hors pathologies, traitements, maternité ou hospitalisations)',
                'Traitements psychotropes (hors pathologies)','Traitements du risque vasculaire (hors pathologies)',
                'Hospitalisation pour Covid-19','Maternité (avec ou sans pathologies)']

data_soins=["Affections de longue durée (dont 31 et 32) pour d'autres causes",
                'Hospitalisations hors pathologies repérées (avec ou sans pathologies, traitements ou maternité)',
                'Traitements antalgiques ou anti-inflammatoires (hors pathologies, traitements, maternité ou hospitalisations)',
                'Traitements psychotropes (hors pathologies)','Traitements du risque vasculaire (hors pathologies)',
                'Hospitalisation pour Covid-19','Maternité (avec ou sans pathologies)']
# Filtrage de base pour le 31 et hors_patho
data_patho = data[~data['patho_niv1'].str.contains('|'.join(re.escape(x) for x in hors_patho), case=False, na=False, regex=True)]

# Filtrer pour le département 31, l'année 2023 et la population globale
df_31= data_patho[(data_patho['dept'] == 31)]
df_66= data_patho[(data_patho['dept'] == 66)]
df_31_2023 = df_31[
                (df_31['annee'] == 2023)]
# 2. Exclure 'tous âges' pour ne pas fausser la comparaison entre les tranches spécifiques
df_respi_ages = df_31_2023[df_31_2023['libelle_classe_age'] != 'tous âges'].copy()

# Trier par prévalence pour un meilleur rendu visuel
df_31_2023 = df_respi_ages.sort_values(by='prev_calculee',ascending=False)



with tab1:
    st.subheader("Fréquence des pathologies en Haute-Garonne (2023) ")

    fig, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(
        data=df_31_2023,
        x='prev_calculee',
        y='patho_niv1',
        hue='patho_niv1',
        palette='viridis',
        ax=ax
    )

    #ax.set_title('Prévalence des pathologies dans le département 31 (2023)')
    ax.set_xlabel('Prévalence (en %)')
    ax.set_ylabel('Pathologies')
    ax.grid(axis='x', linestyle='--', alpha=0.7)

    plt.tight_layout()

    st.pyplot(fig)

    st.write("""

- Le diabète et les maladies respiratoires -> Un enjeu majeur de santé publique dans le département Haute-Garonne 
- Les maladies cardioneurovasculaires, les cancers, les maladies neurologiques et les maladies psychiatriques -> position intermédiaire,              

""")

###################visualiser les tranches d'ages des personnes plus vulnerables face aux maladies respiratoires ###########
# 1. Filtrer pour l'année 2023, le département 31 et la pathologie spécifique
# Note : Vérifiez bien que le nom correspond exactement à celui de votre colonne 'patho_niv1'
patho_cible = "Maladies respiratoires chroniques (hors mucoviscidose)"

df_respi_2023 = df_31[
    (df_31['annee'] == 2023) &  
    (df_31['patho_niv1'].str.contains('respiratoires chroniques', case=False, na=False))

]

# 2. Exclure 'tous âges' pour ne pas fausser la comparaison entre les tranches spécifiques
df_respi_ages = df_respi_2023[df_respi_2023['libelle_classe_age'] != 'tous âges'].copy()

# 3. Trier les données par prévalence décroissante
df_respi_ages = df_respi_ages.sort_values(by='prev_calculee', ascending=False)

# 4. Visualisation

################################################################

with tab3:
    st.subheader("Sensibilité aux pathologies respiratoires : les tranches d'âge les plus exposées")

    sns.set_style("whitegrid")

    fig, ax = plt.subplots(figsize=(12, 8))

    sns.barplot(
        data=df_respi_ages,
        x='prev_calculee',
        y='libelle_classe_age',
        palette='Blues_r',
        ax=ax
    )
    

    # Ajout des étiquettes de données
    for i, val in enumerate(df_respi_ages['prev_calculee']):
        ax.text(val, i, f' {val:.2f}%', va='center', fontsize=10)

    ax.set_title(f'Prévalence par âge : {patho_cible}\n(Haute-Garonne - 2023)', fontsize=14)
    ax.set_xlabel('Prévalence (%)')
    ax.set_ylabel("Tranche d'âge")

    plt.tight_layout()

    st.pyplot(fig)
    st.write("""

    Protection de la population sensible:                                                               
    
    -Renforcer la surveillance et la prévention chez les 0-4 ans (crèches, pédiatrie, qualité de l'air intérieur).

    -Adapter les stratégies de prise en charge pour les 80 ans et plus, population la plus vulnérable.

    """)
    
    

######################################Etude de l'evolution des 5 patologies frequentes dans le dept31##################
# Liste des mots-clés à exclure 
hors_patho = ["Affections de longue durée (dont 31 et 32) pour d'autres causes",
                'Hospitalisations hors pathologies repérées (avec ou sans pathologies, traitements ou maternité)',
                'Traitements antalgiques ou anti-inflammatoires (hors pathologies, traitements, maternité ou hospitalisations)',
                'Traitements psychotropes (hors pathologies)','Traitements du risque vasculaire (hors pathologies)',
                'Hospitalisation pour Covid-19','Maternité (avec ou sans pathologies)']

# Filtrage de base pour le 31 et hors_patho
#data_patho = data[~data['patho_niv1'].str.contains('|'.join(re.escape(x) for x in hors_patho), case=False, na=False, regex=True)]

# Top 5 pour 2023 (en prenant la moyenne sur les âges pour classer)
top_5_names = (data_patho[data_patho['annee'] == 2023]
               .groupby('patho_niv1')['prev_calculee']
               .mean()
               .sort_values(ascending=False)
               .head(5).index)

# On ne garde que ces 5 pathologies pour la suite
df_top5_occitanie = data_patho[data_patho['patho_niv1'].isin(top_5_names)]

df_top5_31 = df_31[df_31['patho_niv1'].isin(top_5_names)]
df_top5_66 = df_66[df_66['patho_niv1'].isin(top_5_names)]

###visualisation d'evolution sur le dept31

with tab2:
    st.subheader("Évolution des 5 affections prépondérantes : 2015-2023")
    fig, ax = plt.subplots(figsize=(14, 8))
    sns.lineplot(
        data=df_top5_31,
        x="annee",
        y="prev_calculee",
        hue="patho_niv1",
        errorbar=None,
        marker="o",
        ax=ax
    )
    ax.set_title("Évolution des 5 affections prépondérantes dans le departement (Haut Garonne)")
    ax.set_xlabel("Année")
    ax.set_ylabel("Prévalence calculée")
    ax.set_ylim(0, 10)
    ax.legend(title='Pathologies', bbox_to_anchor=(1.05, 1), loc='lower center')
    ax.grid(True, alpha=0.9)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

##fig1 occitanie

    st.set_page_config(layout="wide")
    #st.subheader("Évolution des 5 affections prépondérantes dans la region occitanie : 2015-2023")
    fig, ax = plt.subplots(figsize=(14, 8))
    sns.lineplot(
        data=df_top5_occitanie,
        x="annee",
        y="prev_calculee",
        hue="patho_niv1",
        errorbar=None,
        marker="o",
        ax=ax
    )
    ax.set_title("Évolution de la prévalence des 5 pathologies les plus fréquentes (occitanie)")
    ax.set_xlabel("Année")
    ax.set_ylabel("Prévalence calculée")
    ax.set_ylim(0, 10)
    #ax.legend(title="Pathologie")
    ax.legend(title='Pathologies', bbox_to_anchor=(1.05, 1), loc='lower center')
    ax.grid(True, alpha=0.9)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    
    st.write("""

    - une prédominance constante du diabète et des maladies respiratoires chroniques entre les deux territoires

    **Conclusion :**
    --> nécessité de renforcer les actions de prévention, de dépistage et de prise en charge ciblées sur ces pathologies prioritaires au niveau regional et départemental.
    """)
    
    
