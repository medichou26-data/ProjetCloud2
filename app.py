import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Gestion des Stocks",
    page_icon="🚚",
    layout="wide"
)

# Titre principal
st.title("🚚 Dashboard de Gestion Intelligente des Stocks")
st.markdown("**Projet PFE - Supply Chain & Logistique**")
st.markdown("---")

# Fonction pour charger les données (avec données d'exemple si fichier non trouvé)
@st.cache_data
def load_data():
    try:
        # Essayer de charger le fichier CSV
        df = pd.read_csv('stock.csv')
    except FileNotFoundError:
        # Créer des données d'exemple si le fichier n'existe pas
        st.info("⚠️ Fichier 'stock.csv' non trouvé. Chargement de données d'exemple.")
        
        # Créer des produits types pour la supply chain
        categories = ['Électronique', 'Alimentaire', 'Textile', 'Automobile', 'Pharmaceutique']
        produits = []
        
        for i in range(1, 31):
            categorie = categories[i % len(categories)]
            produits.append({
                'produit': f'PROD-{i:03d}',
                'nom': f'Produit {i} ({categorie})',
                'categorie': categorie,
                'quantite': np.random.randint(50, 1000),
                'seuil_minimum': np.random.randint(20, 100),
                'seuil_maximum': np.random.randint(500, 1500),
                'prix_unitaire': round(np.random.uniform(10, 500), 2),
                'fournisseur': np.random.choice(['Fournisseur A', 'Fournisseur B', 'Fournisseur C', 'Fournisseur D']),
                'emplacement': np.random.choice(['Entrepôt A', 'Entrepôt B', 'Entrepôt C']),
                'date_derniere_maj': (datetime.now() - timedelta(days=np.random.randint(0, 30))).strftime('%Y-%m-%d')
            })
        
        df = pd.DataFrame(produits)
        # Ajouter des colonnes calculées
        df['valeur_stock'] = df['quantite'] * df['prix_unitaire']
        df['jours_stock'] = np.random.randint(10, 120, size=len(df))
        df['taux_rotation'] = np.random.uniform(0.5, 8.0, size=len(df))
        
    return df

# Fonction pour calculer les indicateurs
def calculate_kpis(df):
    kpis = {
        'valeur_totale_stock': df['valeur_stock'].sum(),
        'nombre_produits': len(df),
        'produits_en_rupture': len(df[df['quantite'] <= df['seuil_minimum']]),
        'produits_surstock': len(df[df['quantite'] >= df['seuil_maximum']]),
        'taux_rotation_moyen': df['taux_rotation'].mean(),
        'stock_moyen_jours': df['jours_stock'].mean()
    }
    return kpis

# Chargement des données
df = load_data()
kpis = calculate_kpis(df)

# Sidebar pour les filtres
st.sidebar.header("🔧 Filtres et Paramètres")

# Filtre par catégorie
categories = ['Toutes'] + list(df['categorie'].unique())
selected_category = st.sidebar.selectbox("Catégorie", categories)

# Filtre par statut de stock
status_options = ['Tous', 'En alerte rupture', 'Surstock', 'Stock normal']
selected_status = st.sidebar.selectbox("Statut du stock", status_options)

# Filtre par fournisseur
fournisseurs = ['Tous'] + list(df['fournisseur'].unique())
selected_fournisseur = st.sidebar.selectbox("Fournisseur", fournisseurs)

# Application des filtres
filtered_df = df.copy()

if selected_category != 'Toutes':
    filtered_df = filtered_df[filtered_df['categorie'] == selected_category]

if selected_fournisseur != 'Tous':
    filtered_df = filtered_df[filtered_df['fournisseur'] == selected_fournisseur]

if selected_status == 'En alerte rupture':
    filtered_df = filtered_df[filtered_df['quantite'] <= filtered_df['seuil_minimum']]
elif selected_status == 'Surstock':
    filtered_df = filtered_df[filtered_df['quantite'] >= filtered_df['seuil_maximum']]
elif selected_status == 'Stock normal':
    filtered_df = filtered_df[(filtered_df['quantite'] > filtered_df['seuil_minimum']) & 
                              (filtered_df['quantite'] < filtered_df['seuil_maximum'])]

# Section des KPIs
st.header("📊 Tableau de Bord des Indicateurs Clés")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Valeur Totale du Stock",
        value=f"{kpis['valeur_totale_stock']:,.0f} €",
        delta=f"{len(df)} produits"
    )

with col2:
    st.metric(
        label="Produits en Rupture",
        value=kpis['produits_en_rupture'],
        delta=f"{kpis['produits_en_rupture']/kpis['nombre_produits']*100:.1f}%",
        delta_color="inverse"
    )

with col3:
    st.metric(
        label="Produits en Surstock",
        value=kpis['produits_surstock'],
        delta=f"{kpis['produits_surstock']/kpis['nombre_produits']*100:.1f}%",
        delta_color="inverse"
    )

with col4:
    st.metric(
        label="Taux de Rotation Moyen",
        value=f"{kpis['taux_rotation_moyen']:.1f}",
        delta=f"Stock moyen: {kpis['stock_moyen_jours']:.0f} jours"
    )

st.markdown("---")

# Section des graphiques
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Distribution des Stocks par Catégorie")
    
    # Préparation des données pour le graphique
    category_stats = filtered_df.groupby('categorie').agg({
        'valeur_stock': 'sum',
        'produit': 'count',
        'quantite': 'sum'
    }).reset_index()
    
    fig1 = px.bar(
        category_stats,
        x='categorie',
        y='valeur_stock',
        color='categorie',
        title="Valeur du Stock par Catégorie",
        labels={'valeur_stock': 'Valeur (€)', 'categorie': 'Catégorie'},
        text_auto='.2s'
    )
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🔄 Taux de Rotation par Produit")
    
    # Création d'un scatter plot pour le taux de rotation
    fig2 = px.scatter(
        filtered_df.nlargest(20, 'valeur_stock'),
        x='produit',
        y='taux_rotation',
        size='valeur_stock',
        color='categorie',
        hover_data=['nom', 'quantite', 'seuil_minimum'],
        title="Taux de Rotation vs Valeur du Stock (Top 20)",
        labels={'taux_rotation': 'Taux de Rotation', 'produit': 'Produit'}
    )
    fig2.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)

# Section d'alerte de rupture
st.markdown("---")
st.subheader("🚨 Alertes de Rupture Imminente")

# Identification des produits en alerte
alert_df = filtered_df[filtered_df['quantite'] <= filtered_df['seuil_minimum'] * 1.2]  # 20% au-dessus du seuil
alert_df = alert_df.sort_values('quantite')

if not alert_df.empty:
    # Affichage des alertes
    for idx, row in alert_df.iterrows():
        ratio = (row['quantite'] / row['seuil_minimum']) * 100
        
        # Détermination du niveau d'alerte
        if row['quantite'] <= row['seuil_minimum']:
            alert_level = "🔴 Rupture"
            color = "red"
        elif ratio <= 120:
            alert_level = "🟠 Alerte Critique"
            color = "orange"
        else:
            alert_level = "🟡 Attention"
            color = "yellow"
        
        # Création d'une barre de progression
        progress = min(100, (row['quantite'] / row['seuil_minimum']) * 100)
        
        col1, col2, col3 = st.columns([2, 3, 2])
        with col1:
            st.markdown(f"**{row['nom']}**")
            st.caption(f"{row['produit']} | {row['categorie']}")
        with col2:
            st.progress(progress/100)
            st.caption(f"Stock: {row['quantite']} / Seuil: {row['seuil_minimum']} ({progress:.1f}%)")
        with col3:
            st.markdown(f"<h4 style='color:{color};'>{alert_level}</h4>", unsafe_allow_html=True)
            st.caption(f"Fournisseur: {row['fournisseur']}")
        
        st.markdown("---")
else:
    st.success("✅ Aucune alerte de rupture imminente pour les filtres sélectionnés.")

# Section détaillée des stocks
st.markdown("---")
st.subheader("📋 Détail des Produits en Stock")

# Options d'affichage
view_options = st.radio(
    "Mode d'affichage:",
    ["Tableau complet", "Produits en rupture", "Produits en surstock"],
    horizontal=True
)

# Filtrage selon la sélection
if view_options == "Produits en rupture":
    display_df = filtered_df[filtered_df['quantite'] <= filtered_df['seuil_minimum']]
elif view_options == "Produits en surstock":
    display_df = filtered_df[filtered_df['quantite'] >= filtered_df['seuil_maximum']]
else:
    display_df = filtered_df

# Ajout d'une colonne de statut
def get_status(row):
    if row['quantite'] <= row['seuil_minimum']:
        return 'Rupture'
    elif row['quantite'] >= row['seuil_maximum']:
        return 'Surstock'
    else:
        return 'Normal'

display_df = display_df.copy()
display_df['statut'] = display_df.apply(get_status, axis=1)

# Affichage du tableau
st.dataframe(
    display_df[['produit', 'nom', 'categorie', 'quantite', 'seuil_minimum', 
                'seuil_maximum', 'statut', 'valeur_stock', 'taux_rotation', 'fournisseur']].sort_values('quantite'),
    use_container_width=True,
    height=400
)

# Section d'analyse ABC
st.markdown("---")
st.subheader("📊 Analyse ABC des Stocks")

# Calcul de l'analyse ABC
sorted_df = filtered_df.sort_values('valeur_stock', ascending=False)
sorted_df['cumul_valeur'] = sorted_df['valeur_stock'].cumsum()
sorted_df['pourcentage_cumul'] = (sorted_df['cumul_valeur'] / sorted_df['valeur_stock'].sum()) * 100

# Classification ABC
def classify_abc(pct):
    if pct <= 80:
        return 'A'
    elif pct <= 95:
        return 'B'
    else:
        return 'C'

sorted_df['classe_abc'] = sorted_df['pourcentage_cumul'].apply(classify_abc)

# Graphique de l'analyse ABC
fig3 = px.bar(
    sorted_df,
    x='produit',
    y='valeur_stock',
    color='classe_abc',
    title="Analyse ABC des Produits",
    labels={'valeur_stock': 'Valeur (€)', 'produit': 'Produit', 'classe_abc': 'Classe'},
    category_orders={'classe_abc': ['A', 'B', 'C']},
    color_discrete_map={'A': '#FF4B4B', 'B': '#FFA500', 'C': '#2E8B57'}
)
fig3.update_layout(xaxis_tickangle=-45, showlegend=True)
st.plotly_chart(fig3, use_container_width=True)

# Statistiques des classes ABC
abc_stats = sorted_df.groupby('classe_abc').agg({
    'produit': 'count',
    'valeur_stock': 'sum'
}).reset_index()

col1, col2, col3 = st.columns(3)

for idx, classe in enumerate(['A', 'B', 'C']):
    classe_data = abc_stats[abc_stats['classe_abc'] == classe]
    if not classe_data.empty:
        with [col1, col2, col3][idx]:
            count = classe_data['produit'].values[0]
            valeur = classe_data['valeur_stock'].values[0]
            pourcentage = (valeur / sorted_df['valeur_stock'].sum()) * 100
            
            if classe == 'A':
                st.info(f"**Classe {classe}**\n\n{count} produits\n{pourcentage:.1f}% de la valeur")
            elif classe == 'B':
                st.warning(f"**Classe {classe}**\n\n{count} produits\n{pourcentage:.1f}% de la valeur")
            else:
                st.success(f"**Classe {classe}**\n\n{count} produits\n{pourcentage:.1f}% de la valeur")

# Section de recommandations
st.markdown("---")
st.subheader("💡 Recommandations Automatiques")

# Génération de recommandations
recommendations = []

# Recommandations basées sur les ruptures
rupture_products = filtered_df[filtered_df['statut'] == 'Rupture']
if not rupture_products.empty:
    total_rupture_value = rupture_products['valeur_stock'].sum()
    recommendations.append({
        'type': '🔴 Rupture de stock',
        'message': f"{len(rupture_products)} produits en rupture représentant {total_rupture_value:,.0f} € de CA potentiel perdu",
        'action': "Commander immédiatement ces produits"
    })

# Recommandations basées sur le surstock
surstock_products = filtered_df[filtered_df['statut'] == 'Surstock']
if not surstock_products.empty:
    total_surstock_value = surstock_products['valeur_stock'].sum()
    avg_surstock = surstock_products['quantite'].mean()
    recommendations.append({
        'type': '🟡 Surstock',
        'message': f"{len(surstock_products)} produits en surstock (valeur: {total_surstock_value:,.0f} €)",
        'action': "Écouler le stock via promotions ou transferts"
    })

# Recommandations basées sur la rotation
slow_rotation = filtered_df[filtered_df['taux_rotation'] < 1.0]
if not slow_rotation.empty:
    recommendations.append({
        'type': '🔄 Rotation lente',
        'message': f"{len(slow_rotation)} produits avec taux de rotation < 1",
        'action': "Réviser les quantités commandées ou les prix"
    })

# Affichage des recommandations
if recommendations:
    for rec in recommendations:
        with st.expander(rec['type']):
            st.write(rec['message'])
            st.markdown(f"**Action recommandée:** {rec['action']}")
else:
    st.success("✅ Aucune action critique nécessaire. Le stock est bien géré.")

# Pied de page
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    <p>📊 <b>Dashboard de Gestion Intelligente des Stocks</b> - Projet PFE Supply Chain & Logistique</p>
    <p>Technologies: Pandas | Streamlit | Plotly | Python</p>
    <p>© 2024 - Dashboard développé pour les projets de fin d'études</p>
    </div>
    """,
    unsafe_allow_html=True
)