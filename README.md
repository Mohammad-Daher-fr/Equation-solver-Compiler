# Projet : Equation Solver Compiler

Un compilateur Python qui **parse**, **formate** et **résout** des systèmes d'équations linéaires depuis un fichier texte ou une URL.

## Contenu du dépôt

- **Equation_Solver.py**  
  Le cœur du compilateur :
  - Définition des nœuds AST (`Term`, `Equation`, `System`)
  - Lexer et parser PLY pour analyser la syntaxe des équations
  - Visiteurs : imprimeur “pretty printer” et solveur (avec résolution directe ou pseudo-inverse)

- **main.py**  
  Interface en ligne de commande :
  - Accepte un chemin local ou une URL HTTP(S)
  - Lit le contenu, crée un fichier temporaire et lance la compilation

- **parsetab.py**  
  Table générée automatiquement par PLY (ne pas modifier)

- **parser.out**  
  Fichier de debug PLY (optionnel)

- **equations.txt**  
  Exemple de fichier d’entrée contenant un système d'équations

- **tests/**  
  Dossier des tests unitaires Python:
  - `__init__.py` : marque le dossier comme module
  - `test_solver.py` : cas de tests pour valider le solveur

- **test.bat**  
  Script Windows pour lancer automatiquement tous les tests

## Prérequis

- Python 3.7+  
- Bibliothèques : `ply`, `numpy`  

Installer via :
```bash
pip install ply numpy
```

## Utilisation

1. Ouvrir un terminal dans le dossier du projet
2. Lancer le solveur :
   ```bash
   python main.py chemin/vers/equations.txt
   # ou
   python main.py https://.../equations.txt
   ```
3. Le programme affiche :
   - Le système formaté (Pretty Printer)
   - Les solutions (variables = valeurs)

## Exécution des tests

Sous Windows, dans le répertoire du projet :
```bat
.
> test.bat
```
Ou avec Python directement :
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

