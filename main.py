import sqlite3
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import requests
import os

# Lien vers la base de données sur GitHub
url_db = "https://github.com/loulou867/database_world_collapse/raw/refs/heads/main/evenements_actu.db"
local_db_path = 'evenements_actu.db'

# Télécharger la base de données si elle est plus récente
def telecharger_db():
    try:
        response = requests.get(url_db)
        response.raise_for_status()  # Vérifie les erreurs de téléchargement
        
        remote_size = len(response.content)  # Taille du contenu téléchargé
        if os.path.exists(local_db_path):
            local_size = os.path.getsize(local_db_path)
        else:
            local_size = 0

        if remote_size > local_size:
            print("Téléchargement de la base de données -->")
            with open(local_db_path, 'wb') as f:
                f.write(response.content)
            print("Base de données téléchargée avec succès.")
        else:
            print("La base de données est à jour.")
            print("Taille DB Github :", remote_size)
            print("Taille DB local :", local_size)
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement : {e}")

# Appeler la fonction de téléchargement pour mettre à jour la db
telecharger_db()



# Connexion à la base de données
print("Chargement de la base de données 'evenements_actu.db'...")
conn = sqlite3.connect(local_db_path)  # Connexion à la base locale (après téléchargement si nécessaire)
cursor = conn.cursor()  # Création du curseur pour interagir avec les données

# Fonction pour compter le nombre total d'événements
def compter_evenements():
    cursor.execute('SELECT COUNT(*) FROM evenements')
    return cursor.fetchone()[0]  # Retourne le nombre d'événements

# Calcul des moyennes de gravité mensuelles et du nombre d'événements pour chaque catégorie
def calculer_moyennes_mensuelles():
    mois = range(1, 13)  # De janvier à septembre
    parametres = {
        'crise_economique': [],
        'terrorisme': [],
        'tensions_internationales': [],
        'menace_nucleaire': [],
        'manifestations': [],
        'guerres': [],
        'catastrophes_environmentales': [],
        'instabilite_politique': []
    }
    nombres_evenements = {key: [] for key in parametres}

    for mois_data in mois:
        for parametre in parametres.keys():
            cursor.execute('''
            SELECT AVG(gravite)
            FROM evenements
            WHERE parametre = ? AND strftime('%m', date_publication) = ?
            ''', (parametre, f'{mois_data:02d}'))
            
            result = cursor.fetchone()[0]
            parametres[parametre].append(result if result is not None else 0)

            cursor.execute('''
            SELECT COUNT(*)
            FROM evenements
            WHERE parametre = ? AND strftime('%m', date_publication) = ?
            ''', (parametre, f'{mois_data:02d}'))
            
            nombres_evenements[parametre].append(cursor.fetchone()[0])

    return parametres, nombres_evenements  # Retourne les résultats calculés

# Générer le graphique des moyennes mensuelles avec le nombre d'événements
def generer_graphique():
    mois = range(1, 13)  # Mois de janvier à septembre
    parametres, nombres_evenements = calculer_moyennes_mensuelles()

    # Abréviations pour les mois
    mois_abreviations = ['Jan', 'Fev', 'Ma', 'Avr', 'Mai', 'Jui', 'Juil', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec']


    # Créer une grille de sous-graphiques (4x2)
    fig, axs = plt.subplots(4, 2, figsize=(16, 14), sharex=True)

    # Couleurs et titres pour chaque paramètre
    parametre_infos = {
        'crise_economique': ('#1f77b4', 'Crise Économique 💸'),
        'terrorisme': ('#ff7f0e', 'Terrorisme 💥'),
        'tensions_internationales': ('#2ca02c', 'Tensions Internationales 🌍'),
        'menace_nucleaire': ('#d62728', 'Menace Nucléaire ☢️'),
        'manifestations': ('#9467bd', 'Manifestations 🗣️'),
        'guerres': ('#8c564b', 'Guerres ⚔️'),
        'catastrophes_environmentales': ('#e377c2', 'Catastrophes Environnementales 🌪️'),
        'instabilite_politique': ('#7f7f7f', 'Instabilité Politique 🏛️')
    }

    # Remplir chaque sous-graphe avec les données
    for i, (parametre, (couleur, titre)) in enumerate(parametre_infos.items()):
        ax = axs[i // 2, i % 2]
        ax.plot(mois, parametres[parametre], label=titre, color=couleur, marker='o')
        ax.set_title(titre)
        ax.set_ylabel('Gravité Moyenne')
        ax.set_xticks(mois)
        ax.set_xticklabels(mois_abreviations, rotation=45, ha='right', fontsize=10)
        ax.legend()
        
        # Annoter les points avec le nombre d'événements
        for j, nombre in enumerate(nombres_evenements[parametre]):
            ax.annotate(f'{nombre}', (mois[j], parametres[parametre][j]), textcoords="offset points", xytext=(0,5), ha='center', fontsize=8, color=couleur)

    # Ajustement des marges et de l'espacement entre les sous-graphiques
    plt.tight_layout()
    fig.subplots_adjust(top=0.9, bottom=0.2, hspace=0.35, wspace=0.3)

    plt.show()  # Afficher le graphique

# Afficher le nombre d'événements dans la base
nombre_evenements = compter_evenements()
print(f"Nombre d'événements stockés dans la base de données : {nombre_evenements}")

# Générer et afficher le graphique
generer_graphique()

# Fermer la connexion à la base de données
conn.close()
