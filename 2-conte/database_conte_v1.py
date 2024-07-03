# pip install xlrd pandas re os requests openpyxl Levenshtein (si ce n'est pas fait)
import pandas as pd
import re
import os
import requests
import Levenshtein as lv
from collections import Counter


def list_files(directory):
    """Récupération de tous les fichiers excel (.xls et .xlsx) dans le dossier "directory"."""
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('.xls', '.xlsx'))]


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


def split_text(text):
    """Séparation mot à mot d'une phrase."""
    # convertit tout le texte en minuscules, supprime les virgules et les apostrophes, et sépare les mots
    words = re.split(
        r"[^\w']+", text.lower().replace(',', '').replace("'", ' '))
    # supprime les mots vides et les espaces
    words = [word.strip() for word in words if word.strip()]
    return words


def create_csv(files, output_csv='bdd_conte_v1.csv'):
    """Création de fichier .csv sous 'bdd_conte_v1.csv' en remplissant avec les informations des fichier Excel."""
    # création des tableaux (vides pour l'instant)
    phrases = []
    traductions = []
    commentaires = []
    locuteur_infos = []

    for file in files:  # récupération des données correspondantes
        conte_df, locuteur_df = filter_excel(file)
        if not phrases:
            phrases = conte_df.iloc[:, 1].tolist()
        traductions.append(conte_df.iloc[:, 2].tolist())
        commentaires.append(conte_df.iloc[:, 3].tolist())
        locuteur_infos.append(locuteur_df)

    columns = ['code_INSEE', 'ville', 'departement', 'x', 'y', 'identifiant', 'age', 'lieu_de_naissance',
               'sexe', 'lieu_de_residence', 'parler_local', 'commune_apprentissage', 'profession', 'adresse_courriel']

    # on gère le cas où il y a le même mot dans une même phrase
    word_counts = {}
    for i, phrase in enumerate(phrases):
        words = split_text(phrase)
        columns.append(phrase)
        columns.append(f'commentaire_phrase_{i+1}')
        for word in words:
            col_name = f'{word}_MOT_phrase_{i+1}'
            if col_name in word_counts:  # si le mot apparait déjà
                col_name = f'{word}_MOT_phrase_{i+1}_bis'
            else:
                word_counts[col_name] = 1
            columns.append(col_name)

    df_output = pd.DataFrame(columns=columns)

    for x, file in enumerate(files):
        # remplissage des lignes de données
        code_insee, identifiant = extract_info(file.split('/')[-1])
        geo_info = get_geo_info(code_insee)
        locuteur_info = locuteur_infos[x]
        row = [code_insee, geo_info['ville'], geo_info['departement'], geo_info['x'], geo_info['y'],
               identifiant, locuteur_info[0], locuteur_info[1], locuteur_info[2], locuteur_info[3],
               locuteur_info[4], locuteur_info[5], locuteur_info[6], locuteur_info[7]]

        for i in range(len(phrases)):
            row.append(traductions[x][i])
            row.append(commentaires[x][i])
            phrase_words = split_text(phrases[i])
            traduction_words = split_text(traductions[x][i])

            for word_index, word in enumerate(phrase_words):
                # trouver les mots les plus proches en termes de position
                # 1er cas : len(traduction_words) = len(phrase_words)
                start = word_index
                end = word_index + 1
                # 2e cas :
                if len(traduction_words) < len(phrase_words):
                    start = max(0, word_index - 1 -
                                (len(phrase_words) - len(traduction_words)))
                    end = min(len(traduction_words), word_index + 2 +
                              (len(phrase_words) - len(traduction_words)))
                # 3e cas :
                elif len(traduction_words) > len(phrase_words):
                    start = max(0, word_index - 1 -
                                (len(traduction_words) - len(phrase_words)))
                    end = min(len(traduction_words), word_index + 2 +
                              (len(traduction_words) - len(phrase_words)))

                context_words = traduction_words[start:end]

                min_distance = float('inf')
                best_match = ''
                for trad_word in context_words:
                    distance = lv.distance(word, trad_word)
                    if distance < min_distance:
                        min_distance = distance
                        best_match = trad_word

                # ajoute le mot traduit trouvé ou laisse vide si aucun mot n'est trouvé
                row.append(f'{best_match}' if best_match else '')

                # idée : si une même traduction est trouvée pour 2 mots dans la phrase,
                # alors on choisit la traduction qui a la plus petite distance de Levenshtein ?

        df_output.loc[x] = row

    df_output.to_csv(output_csv, index=False)
    # print(f"Base de données créée et enregistrée sous {output_csv}")
    return df_output


# création du fichier .csv
directory = 'reponses'  # le dossier contenant tous les fichiers excel
files = list_files(directory)
df = create_csv(files)


########### Affichage sur le terminal ###########

def get_operations(word1, word2):  # valable que pour deux traductions à la fois
    """Extraction des opérations entre deux mots en utilisant Levenshtein."""
    operations = lv.editops(word1, word2)
    details = []
    details.append(f"{word1} -> {word2}")
    contingency_table = {"insertions": 0,
                         "suppressions": 0, "substitutions": 0}
    if word1 == word2:
        details.append("Les mots sont identiques.")
    else:
        for op in operations:
            if op[0] == 'insert':
                contingency_table["insertions"] += 1
                details.append(
                    f"Insertion de '{word2[op[2]]}' à la position {op[1]}")
            elif op[0] == 'delete':
                contingency_table["suppressions"] += 1
                details.append(
                    f"Suppression de '{word1[op[1]]}' à la position {op[1]}")
            elif op[0] == 'replace':
                contingency_table["substitutions"] += 1
                details.append(
                    f"Substitution de '{word1[op[1]]}' par '{word2[op[2]]}' à la position {op[1]}")
    return contingency_table, details, operations


def create_contingency_table(df, word_col):
    """Création d'une table de contingence montrant les opérations entre paires de mots."""
    translations = df[word_col].dropna().values
    word1, word2 = translations[:2]
    contingency_table, details, operations = get_operations(word1, word2)
    contingency_df = pd.DataFrame([contingency_table])
    details_df = pd.DataFrame(details, columns=["Détails"])
    return contingency_df, details_df, operations, word1, word2


def print_most_common_operations(operation_counter, operation_type, N=3):
    """Affichage des N opérations les plus fréquentes pour un type donné."""
    most_common = operation_counter.most_common(N)
    if most_common:
        print(f"\n{operation_type.capitalize()}s les plus fréquentes :")
        for i, (operation, count) in enumerate(most_common):
            print(f"{i+1}. {operation}: {count}")
    else:
        print(f"\nAucune {operation_type} trouvée.")


insertion_operations = Counter()
suppression_operations = Counter()
substitution_operations = Counter()

# affichage des tables de contigences, avec le détail des opérations effectuées par Levenshtein
for i in range(1, 45):  # on parcourt tous les mots de toutes les phrases
    word_columns = [
        col for col in df.columns if col.endswith(f'_MOT_phrase_{i}')]
    for word_col in word_columns:
        contingency_table, details_tables, operations, word1, word2 = create_contingency_table(
            df, word_col)
        if contingency_table is not None:
            for op in operations:
                if op[0] == 'insert':
                    insertion_operations[word2[op[2]]
                                         ] += contingency_table['insertions'][0]
                elif op[0] == 'delete':
                    suppression_operations[word1[op[1]]
                                           ] += contingency_table['suppressions'][0]
                elif op[0] == 'replace':
                    substitution_operations[(
                        word1[op[1]], word2[op[2]])] += contingency_table['substitutions'][0]

            print(f"\nTable de contingence pour le mot '{word_col}':")
            print(contingency_table)
            print(details_tables)


# affichage des fréquences par opérations
total_operations = len(insertion_operations) + \
    len(suppression_operations) + len(substitution_operations)

insertions_frequency = len(insertion_operations) / total_operations
suppressions_frequency = len(suppression_operations) / total_operations
substitutions_frequency = len(substitution_operations) / total_operations

print(f"\nFréquence des opérations :")
print(f"Insertions : {insertions_frequency:.2%}")
print(f"Suppressions : {suppressions_frequency:.2%}")
print(f"Substitutions : {substitutions_frequency:.2%}")


# affichage des opérations les plus fréquentes
print_most_common_operations(insertion_operations, "insertion")
print_most_common_operations(suppression_operations, "suppression")
print_most_common_operations(substitution_operations, "substitution")
