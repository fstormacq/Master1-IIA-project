# Rapport LaTeX - Canne Adaptative

Ce dossier contient le rapport LaTeX du projet "Canne Adaptative" adapté depuis le format Markdown original.

## Fichiers principaux

- `adaptive-cane-report.tex` - Document principal LaTeX avec le contenu du rapport
- `bibliography.bib` - Fichier de références bibliographiques
- `Makefile` - Script de compilation automatique
- `figures/` - Dossier pour les images et diagrammes
- `template/` - Template original fourni

## Compilation du document

### Méthode 1 : Avec le Makefile (recommandé)
```bash
cd doc/
make all
```

### Méthode 2 : Compilation manuelle
```bash
cd doc/
pdflatex adaptive-cane-report.tex
bibtex adaptive-cane-report
pdflatex adaptive-cane-report.tex
pdflatex adaptive-cane-report.tex
```

### Nettoyage des fichiers temporaires
```bash
make clean      # Supprime les fichiers auxiliaires
make cleanall   # Supprime tous les fichiers générés
make rebuild    # Nettoie et recompile
```

## Sections à compléter

Le document LaTeX contient plusieurs sections marquées comme "à compléter" :

1. **Section Contribution** - Détailler les contributions spécifiques du projet
2. **Section Evaluation** - Ajouter les résultats des tests utilisateurs
3. **Section Conclusion** - Synthèse finale du projet
4. **Figures** - Ajouter l'image `adaptive-cane-system.png` dans le dossier `figures/`

## Structure du document

Le document suit la structure académique standard :
- Titre et auteurs
- Résumé (Abstract)
- Mots-clés et concepts CCS
- Introduction
- État de l'art (Related work)
- Méthodologie
- Contribution
- Évaluation
- Discussion
- Conclusion
- Références

## Notes importantes

- Le template utilise la classe `acmart` pour les publications ACM
- Les auteurs et emails ont été adaptés depuis le rapport markdown
- La date a été mise à jour pour 2024
- Le lien GitHub est déjà inclus dans la section Open Science
- Les concepts CCS incluent l'accessibilité, qui est pertinent pour ce projet

## Prérequis

Pour compiler le document, vous aurez besoin de :
- Une distribution LaTeX (TeX Live, MiKTeX, etc.)
- La classe `acmart` (généralement incluse dans les distributions modernes)
- Les packages utilisés (`xspace`, etc.)

Le template est compatible avec la plupart des distributions LaTeX modernes.