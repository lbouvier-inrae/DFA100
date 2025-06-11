
# Bubble Video Analyzer

## Description du projet

Ce logiciel lit image par image une vidéo issue du DFA100 et détecte automatiquement les bulles présentes dans chaque frame. Il calcule ensuite leur surface, le nombre de bulles, et l’écart type, puis exporte les résultats dans un fichier Excel, avec possibilité d’associer les vidéos à des fichiers de référence.

## Fonctionnalités

- Ajout et gestion de vidéos à analyser
- Détection automatique des bulles sur chaque image (avec gestion du scale en px/mm)
- Configuration des paramètres d’analyse (step, agitation, etc.)
- Association automatique ou manuelle avec un fichier Excel de référence
- Extraction des statistiques (nombre de bulles, surface moyenne, écart type)
- Export des résultats dans un fichier `.xlsx` structuré

## Télécharger et utiliser uniquement l'application (sans coder)

Si vous ne souhaitez **pas modifier le code**, il suffit de télécharger l'application prête à l'emploi :

1. Allez ici : [Dernière version de l'application](https://github.com/lbouvier-inrae/DFA100/releases)
2. Cliquez sur **"Assets"** sous la dernière release.
3. Téléchargez le fichier `BubbleVideoAnalyzer.zip`.
4. Faites un clic droit → "Extraire tout..." (sous Windows).
5. Double-cliquez sur `BubbleVideoAnalyzer.exe` pour lancer l'application.  
   *(Pas besoin d’installer Python)*

---

## Modifier le code source (développeur)

### Prérequis

- Python 3.8+ installé : [https://www.python.org/downloads/](https://www.python.org/downloads/)
- pip installé (inclus avec Python)

### Installation des dépendances

1. Ouvrez un terminal (CMD ou PowerShell).
2. Installez les bibliothèques nécessaires :

```bash
pip install -r requirements.txt
```

### Lancer le programme en mode développement

Depuis la racine du projet :

```bash
python src/main.py
```

---

## Générer un exécutable (.exe)

Une fois vos modifications faites, vous pouvez recréer l'application utilisable sans Python.

### Étapes (Windows) :

1. Lancez le script `build_exe.bat` (double-clic ou via terminal) :

```bash
build_exe.bat
```

Cela va créer un exécutable dans le dossier `dist/`

### Optionnel : créer une version compressée (ZIP)

Vous pouvez zipper le contenu de `dist/` pour le partager facilement :

```bash
cd dist
Compress-Archive -Path * -DestinationPath ../BubbleVideoAnalyzer.zip
```

Ou clic droit > "Envoyer vers > Dossier compressé".

---

## Arborescence du projet

```
BubbleVideoAnalyzer/
│
├── src/                    # Code source Python
│   ├── main.py
│   └── ...
│
├── build_exe.bat           # Script de création d'exécutable (Windows)
├── build_exe.sh            # Script Linux/macOS (optionnel)
├── requirements.txt        # Dépendances Python
├── README.md
├── dist/                   # Exécutable généré (.exe + dépendances)
└── .gitignore
└── ...
```

---

## Git et collaboration (facultatif)

Si vous souhaitez contribuer :

```bash
git https://github.com/lbouvier-inrae/DFA100.git
```

Créez une branche, apportez vos changements, et proposez une *pull request*.

---

## Contact

- Développeur Principal : Maxime Gosselin
[maximeg391@gmail.com](mailto:maximeg391@gmail.com)
- Contact Secondaire: Laurent Bouvier
[laurent.bouvier@inrae.fr](mailto:laurent.bouvier@inrae.fr)

---

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus d'informations.
