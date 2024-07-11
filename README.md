# STAGE LINGUISTIQUE

## Installation : 

Pour obtenir toutes les extensions utilisées dans ce projet, veuillez exécuter cette commande dans le terminal : 

```bash 
pip install -r requirements.txt
```

## 1 - Transcription

Biblio-prospective sur la transcription automatique :

- version Transkribus (application), voir `transkribus.pdf`

- version Python, voir `script.ipynb` 

## 2 - Conte de l'âne triste

Création de bases de données sous 2 versions :

- `Version 1 :` Dans ce cas, une réponse à l'enquête (fichier excel contenant le texte entier) est égale à une ligne dans le fichier csv. Il contient, de plus, les coordonnées géographiques ainsi que les informations du locuteur. Enfin, pour chaque phrase (du français actuel) du conte, il y a la phrase traduite dans la commune, ainsi qu'un potentiel commentaire sur cette dernière, avec un découpage par mots.

- `Version 2 :` Contrairement à la première version, chaque phrase de l'enquête (fichier excel) correspond à une ligne dans le fichier csv, accompagnée d'un numéro par phrase. Au total, il y a 44 phrases par locuteur. Comme dans la version précédente, il contient les coordonnées géographiques ainsi que les informations du locuteur. Enfin, il est aussi possible d'avoir un découpage par mots pour chaque phrase, il faudra cependant dé-commenter le code correspondant.

Une fois la base de données créée pour la `première version`, des tables de contingences, sur les types d'opérations (selon Levenshtein) entre chaque paires de mots sont faites. De plus, des calculs de fréquences selon le type d'opérations effectués, ainsi que des calculs de fréquences sur les opérations classées par type, sont effectués. 

## 3 - Base de données (3e) sur l'enquête Bourciez

Ici, la base de données est déjà créé (bd3_Bourciez.csv), donc on travaille directement là dessus pour la suite du fichier `bd3_bourciez.ipynb`. Ce fichier notebook prend une durée d'environ 6/7 minutes pour l'exécution totale.
Plusieurs analyses statistiques, clustering, matrices, etc sont créées et sont les suivantes :

- `Analyse des types d'opérations` : À la méthode de **Levenshtein**, quelques mots choisis (*malheureux* et *être*) sont analysés selon le type d'opérations possibles et leur fréquence : **insertion**, **suppression** et **substitution**.

- `Calcul des plus proches voisins` : Deux méthodes sont testées pour calculer les plus proches voisins selon la distance géographique entre chaque traduction : **diagramme de Voronoï** et **triangulation de Delaunay**. Dans la suite, ce sera la triangulation qui sera utilisée pour les analyses.

- `Analyse des types d'opérations des plus proches voisins` : Pour les mêmes mots choisis précédemment, une analyse des types d'opérations est à nouveau effectuée, mais sur les plus proches voisins qu'aura trouvé la triangulation de Delaunay. Il y a deux façons de visualiser ces résultats : le retour que propose vscode ('View as a scrollable element' ou 'open in a text editor') ou un **fichier .csv**. Le fichier .csv est créé **par mot** et est enregistré dans un **dossier nommé "voisins"**. En effet, un **processus automatisé** permet cette analyse sur TOUS les mots de la base de données, et pas seulement sur les 2 mots choisis précédemment.

- `Matrices, corrélations, nuages de points, courbes d'ajustement` : Dans un dossier nommé "matrices", des matrices de **distances géographiques** (dist_geo.npy) et de **distances linguistiques** (selon Levenshtein) (dist_lv.npy) sur tous les mots sont créées et enregistrées (afin d'éviter de les recalculer, ce qui prendrait quelques minutes). Des matrices de distances linguistiques (selon Levenshtein) pour le mot "malheureux" et le mot "être" sont aussi créées (mais pas enregistrées, car elles sont très rapides à calculer). Par suite, des corrélations sont faites entre ces différentes matrices, ainsi qu'une étude entre le nombre de mots pris en compte dans la corrélation entre les matrices linguistiques et géographiques, afin de capter une possible évolution. Enfin, des courbes d'ajustement ainsi que des nuages de points selon une fonction logarithmique sont créés.

- `Clustering des distances géographiques` : Selon la **méthode du coude**, un choix du nombre de clusters est donné pour la réalisation du **dendrogramme de la CAH avec la méthode de Ward**, puis de la **projection de ces clusters sur une carte**, selon la matrice des distances géographiques.

- `Clustering des distances linguistiques selon Levenshtein` : De la même façon, des **dendrogrammes de la CAH avec la méthode de Ward**, puis des **projections de clusters sur des cartes** sont effectués pour les matrices des distances linguistiques selon Levenshtein, sur tous les mots, puis pour le mot "malheureux" et pour le mot "être".

- `INSEE Population 1896` : Afin de **compléter la base de données**, le **nombre de population par communes** qui ont répondu à l'enquête va être récupéré grâce à des fichiers excel que dispose l'INSEE en 1896 (base-pop-historiques-1876-2021.xlsx). *Un fichier pour avoir la population par département est aussi récupéré (REC_T68.xls) et sont tous deux enregistrés dans le dossier nommé "datas".* Des valeurs manquantes seront enregistrées dans quelques communes (516 sur 3392) et quelques procédés seront faits pour y remédier : 
    1) associer le même nombre de population d'une commune se terminant par "bis", qu'une commune ayant le même nom sans "bis";
    2) associer le même nombre de population d'une commune que le nombre dans la commune la plus proche géographiquement, grâce au triangle de Delaunay.

- `Clustering sur la population` : Une fois que toutes les données du nombre de population par communes sont renseignées, un nouveau fichier de base de données est créé pour inclure cette information (bd3_Bourciez_new.csv). Du côté du clustering, on retrouve : des **matrices sur la population** (par exemple, (P_i * P) avec i une commune différente et P l'information de la population), des **corrélations** entre ces matrices de population créées et les matrices de distances linguistiques (selon Levenshtein) et distances géographiques, des **modèles de régression** avec un calcul du $R^2$ pour notamment voir si l'inclusion de la population augmente ce score, et enfin des **dendrogrammes de la CAH de Ward**.

## Mini-rapport

Rapport de deux pages résumant mon travail au cours de ces six semaines de stage encadrées par M. Genadot, les difficultés que j'ai pu rencontrer, les questions que je me suis posées ainsi que ce que j'en ai pensé globalement (voir `Mini-rapport.pdf`).