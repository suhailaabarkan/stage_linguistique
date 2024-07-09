# STAGE LINGUISTIQUE

## Installation : 

Pour obtenir toutes les extensions utilisées dans ce projet, veuillez exécuter cette commande dans le terminal : 

```bash 
pip install -r requirements.txt
```

## 1 - Transcription

Biblio-prospective sur la transcription automatique :

- version Python, voir `script.ipynb` 

- version Transkribus (application), voir `transkribus.pdf`

## 2 - Conte de l'âne triste

Création de bases de données sous 2 versions :

- Version 1 : Dans ce cas, une réponse à l'enquête (fichier excel contenant le texte entier) est égale à une ligne dans le fichier csv. Il y contient, de plus, les coordonnées géographiques ainsi que les informations du locuteur. Enfin, pour chaque phrase (du français actuel) du conte, il y a la phrase traduite dans la commune, ainsi qu'un potentiel commentaire sur cette dernière, avec un découpage par mots.

- Version 2 : Contrairement à la première version, chaque phrase de l'enquête (fichier excel) correspond à une ligne dans le fichier csv, accompagnée d'un numéro par phrase. Au total, il y a 44 phrases par locuteur. Comme dans la version précédente, il y contient les coordonnées géographiques ainsi que les informations du locuteur. Enfin, il est aussi possible d'avoir un découpage par mots pour chaque phrase, il faudra cependant dé-commenter le code correspondant.

Une fois la base de données créée pour la première version, des tables de contingences, sur les types d'opération (selon Levenshtein) entre chaque paires de mots sont faites. De plus, des calculs de fréquences selon le type d'opérations effectués, ainsi que des calculs de fréquences sur les opérations classées par type, sont effectués. 