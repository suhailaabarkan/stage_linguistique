# pip install xlrd pandas openpyxl requests (si ce n'est pas fait)
import pandas as pd
import re
import os
import requests


def extract_info(file):
    """Extraction du numéro INSEE et de l'identifiant du locuteur dans le nom des fichiers Excel."""
    match = re.match(r'PaRL_(\d{5})_(e\d{2})_Questionnaire_Conte', file)
    if match:
        return match.groups()
    return None, None  # dans le cas où les infos sont pas/mal renseignées


def filter_excel(file):
    """Filtrage des fichiers Excel pour récupérer les informations du conte et du locuteur."""
    df = pd.read_excel(file, sheet_name=0)
    # lignes du conte commençant par des numéros (1, 2, ..., 44)
    conte_df = df[df.iloc[:, 0].astype(str).str.match(r'^\d+.*')]
    # lignes contenant les infos du locuteur
    locuteur_df = df.iloc[-8:, 2].tolist()
    return conte_df, locuteur_df


def get_geo_info(code_insee):
    """Récupération des informations géographiques selon le code INSEE, via une api."""
    url = f'https://geo.api.gouv.fr/communes/{code_insee}?fields=nom,code,codesPostaux,surface,population,centre,contour,departement'
    response = requests.get(url)
    data = response.json()
    return {
        'ville': data['nom'],
        'departement': data['departement']['nom'],
        'x': data['centre']['coordinates'][0],
        'y': data['centre']['coordinates'][1]
    }


# def split_phrase(phrase):
#   """Séparation mot à mot d'une phrase."""
#   séparer par rapport aux apostrophes et supprimer ces dernières ainsi que les virgules
#   mots = re.split(r"[^\w']+", phrase.replace(',', '').replace("'", ' '))
#   return {f'mot_{i+1}': mot for i, mot in enumerate(mots)}


def create_csv(files, output_csv='bdd_conte_v2.csv'):
    """Création de fichier .csv sous 'bdd_conte_v1.csv' en remplissant avec les informations des fichier Excel."""
    columns = ['code_INSEE', 'ville', 'departement', 'x', 'y', 'identifiant', 'age', 'lieu_de_naissance',
               'sexe', 'lieu_de_residence', 'parler_local', 'commune_apprentissage', 'profession',
               'adresse_courriel', 'num_phrase', 'phrase', 'commentaire']
    df_output = pd.DataFrame(columns=columns)

    for file in files:
        df, locuteur_info = filter_excel(file)
        code_insee, identifiant = extract_info(file.split('/')[-1])
        geo_info = get_geo_info(code_insee)
        new_rows = []
        for _, row in df.iterrows():
            num_phrase = row.iloc[0]
            phrase = row.iloc[2]
            # mots = split_phrase(phrase)
            new_row = {
                'code_INSEE': code_insee,
                'ville': geo_info['ville'],
                'departement': geo_info['departement'],
                'x': geo_info['x'],
                'y': geo_info['y'],
                'identifiant': identifiant,
                'age': locuteur_info[0],
                'lieu_de_naissance': locuteur_info[1],
                'sexe': locuteur_info[2],
                'lieu_de_residence': locuteur_info[3],
                'parler_local': locuteur_info[4],
                'commune_apprentissage': locuteur_info[5],
                'profession': locuteur_info[6],
                'adresse_courriel': locuteur_info[7],
                'num_phrase': num_phrase,
                'phrase': phrase,
                'commentaire': row.iloc[3],
                # **mots
            }
            new_rows.append(new_row)
        df_output = pd.concat(
            [df_output, pd.DataFrame(new_rows)], ignore_index=True)

    df_output.to_csv(output_csv, index=False)
    print(f"Base de données créée et enregistrée sous {output_csv}")


def list_files(directory):
    """Récupération de tous les fichiers excel (.xls et .xlsx) dans le dossier "directory"."""
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('.xls', '.xlsx'))]


directory = 'reponses'  # le dossier contenant tous les fichiers excel
files = list_files(directory)
create_csv(files)
