# Creator_JDVELH_CYOA
Programme basique pour réaliser des jeux dont vous êtes le Héros

# Guide de démarrage

Cet outil permet d'écrire une histoire « dont vous êtes le héros » (texte +
images + choix multiples) **sans écrire une seule ligne de code**, puis de
générer un jeu jouable dans le même style que *Luna et la Vallée aux
Murmures*.

## 1. Ce dont tu as besoin

- **Python 3** installé sur ton ordinateur (il l'est déjà si tu as pu lancer
  les fichiers `.py` du projet Luna). Aucune autre dépendance obligatoire :
  l'interface utilise `tkinter`, fourni avec Python.
- **Optionnel mais recommandé** : la bibliothèque **Pillow**, pour des
  aperçus d'images plus nets et un meilleur redimensionnement :
  ```
  pip install Pillow
  ```
  Sans Pillow, l'outil fonctionne quand même, mais les images doivent être
  assez proches du format carré pour bien s'afficher.

## 2. Lancer l'éditeur

Dans le dossier contenant `cyoa_creator.py` et `lecteur_cyoa.py` :

```
python3 cyoa_creator.py
```

Une page de démarrage s'affiche 3 secondes, puis l'écran d'accueil
**« Que voulez-vous faire ? »** te propose quatre choix :

- **Voir un exemple** — ouvre une petite histoire de démonstration déjà
  écrite (*Le Phare Oublié*), pour voir concrètement à quoi ressemble un
  projet une fois rempli, avant de te lancer.
- **Créer son histoire** — ouvre un projet vierge, prêt à écrire.
- **Tutoriel** — un guide en 8 écrans (un écran de bienvenue + 7 étapes),
  directement dans l'application, qui explique tout ce qu'il y a à savoir
  (voir sections 3 à 7 ci-dessous).
- **Paramètres** — pour changer l'apparence de l'éditeur (voir section 9).

En choisissant « Voir un exemple » ou « Créer son histoire », tu arrives
dans l'éditeur proprement dit :
- à **gauche**, la liste de tous les passages de ton histoire (un passage
  = un moment de l'histoire, avec son texte, son image et ses choix) ;
- à **droite**, l'édition du passage sélectionné ;
- en haut, la barre d'outils : **📄 Nouveau**, **💾 Enregistrer**,
  **Enregistrer sous…**, **⬆ Exporter le jeu terminé…**, **Vérifier
  l'histoire** et **▶ Tester depuis le début** ;
- le bouton **🏠 Accueil** en haut à gauche ramène à tout moment à l'écran
  « Que voulez-vous faire ? ».

Le passage n°1 est toujours le point de départ de l'histoire.

## 3. Écrire un passage

1. Clique sur un passage dans la liste de gauche (ou **+ Nouveau
   passage**). Tu peux aussi **dupliquer** un passage existant ou le
   supprimer depuis la liste.
2. Écris le texte que le joueur va lire, dans la grande zone de texte.
   Tout ce que tu tapes est retenu dans le projet au fur et à mesure ; seul
   l'enregistrement sur disque se fait quand tu le demandes (section 5).
3. Ajoute une image si tu veux — deux possibilités :
   - **« Choisir une image sur mon ordinateur… »** : l'image est copiée et
     rangée automatiquement dans le projet, tu n'as rien d'autre à faire ;
   - **« Réutiliser une image déjà importée… »** : reprend une image déjà
     présente dans le projet sans la réimporter (pratique quand deux
     passages montrent le même lieu ou le même personnage).
   Le bouton **« Retirer l'image »** permet de revenir à un passage sans
   illustration.
4. Ajoute des choix avec **+ Ajouter un choix** : autant que tu veux, il
   n'y a **aucune limite**. Pour chaque choix, écris le texte du bouton,
   puis choisis vers quel passage il mène :
   - un passage déjà existant, dans la liste déroulante ;
   - ou **« ➕ Créer un nouveau passage… »**, qui crée un nouveau passage
     vide relié à ce choix et t'y emmène directement pour l'écrire.

C'est ce mécanisme — créer un nouveau passage directement depuis un choix —
qui permet de construire une histoire aussi longue et ramifiée que tu veux :
4 passages, 40, ou plus, avec des chemins qui se croisent ou pas,
simplement en enchaînant « + Ajouter un choix » → « Créer un nouveau
passage… ».

**Un passage sans aucun choix est automatiquement une fin de l'histoire.**
Le lecteur affichera alors « FIN DE CE CHEMIN » avec un bouton pour
recommencer.

## 4. Naviguer dans l'éditeur

- La **liste de gauche** numérote tous tes passages et te permet de sauter
  de l'un à l'autre en un clic.
- Les boutons associés à la liste permettent de créer, **dupliquer** ou
  supprimer un passage.
- Tu peux revenir à l'accueil à tout moment avec **🏠 Accueil**, puis
  continuer ton projet : menu **Fichier > Ouvrir…** recharge ton fichier
  `.cyoa.json` exactement comme tu l'as laissé.

## 5. Enregistrer ton travail

Menu **Fichier > Enregistrer** (ou **« Enregistrer sous… »** la première
fois, ou le bouton 💾 de la barre d'outils). Cela crée :
- un fichier **`.cyoa.json`** : ton projet, à ouvrir et modifier à
  volonté ;
- un dossier **`images/`** à côté, où sont rangées toutes les images
  importées.

Enregistre régulièrement ! Rien n'est écrit sur le disque tant que tu ne
cliques pas sur « Enregistrer » : si tu fermes l'application sans
enregistrer, le travail non sauvegardé est perdu.

## 6. Tester ton histoire

À tout moment, clique sur **« ▶ Tester l'histoire depuis ce passage »**
(ou **« ▶ Tester depuis le début »** en haut de la fenêtre) pour jouer
directement dans l'éditeur, sans rien exporter. Une fenêtre de jeu
s'ouvre, avec un bouton **« Passage précédent »** pour revenir en arrière.

Le bouton **« Vérifier l'histoire »** (en haut) passe en revue tout ton
projet et signale :
- les choix qui ne mènent encore nulle part (tu as créé le bouton mais pas
  encore choisi sa destination) ;
- les choix qui pointent vers un passage inexistant (par exemple supprimé
  entre-temps) ;
- les passages dont le texte est vide ;
- les passages qu'on ne peut jamais atteindre en jouant (aucun choix, où
  que ce soit dans l'histoire, n'y mène).

C'est utile pour repérer les oublis avant d'exporter, surtout sur une
histoire avec beaucoup de branches.

## 7. Exporter le jeu terminé

Menu **Fichier > Exporter le jeu terminé…** (ou le bouton ⬆ de la barre
d'outils), puis choisis un dossier de destination (par exemple `mon_jeu/`).
L'outil y place :

- **`story.py`** — ton histoire, dans le même format exact que le projet
  *Luna et la Vallée aux Murmures* ;
- **`images/`** — toutes les images utilisées ;
- **`lecteur_cyoa.py`** — l'interface de jeu, avec le même habillage
  « grimoire ancien » (parchemin, filets dorés) que Luna.

Pour jouer au résultat final, il suffit d'aller dans ce dossier et de
lancer :

```
python3 lecteur_cyoa.py
```

Le titre de ton histoire (celui que tu as tapé en haut de l'éditeur)
s'affiche automatiquement dans la fenêtre de jeu.

## 8. Ouvrir un projet existant

Menu **Fichier > Ouvrir…** et sélectionne ton fichier `.cyoa.json` :
l'éditeur recharge le titre, tous les passages, les images et les choix
exactement comme tu les avais laissés. Pense à garder le dossier `images/`
à côté du fichier `.cyoa.json`, puisque c'est lui qui contient les images
du projet.

## 9. Changer l'apparence (Paramètres)

Depuis l'écran d'accueil, **Paramètres** propose trois rendus visuels pour
l'éditeur :

- **Grimoire ancien (sombre)** — le thème par défaut, parchemin et filets
  dorés sur fond sombre, dans l'esprit du projet Luna.
- **Parchemin clair** — les mêmes teintes chaudes, mais sur fond clair.
- **Contraste élevé (accessibilité)** — noir et blanc avec des accents
  jaune vif, pour une meilleure lisibilité.

Le choix est mémorisé (dans un petit fichier `cyoa_settings.json` créé à
côté de `cyoa_creator.py`) et réappliqué automatiquement au prochain
lancement. **Ce thème est aussi celui du jeu final** : au moment de
l'export (Fichier > Exporter le jeu terminé…), le thème actif est inscrit
dans `story.py` (variable `THEME`), et `lecteur_cyoa.py` le lit pour
afficher le jeu terminé avec exactement la même apparence que dans
l'éditeur — pas besoin de le régler une seconde fois.

## 10. Idées pour aller plus loin

- Ce format reste un CYOA « pur » (texte → choix → texte suivant), sans
  variables ni statistiques, volontairement, pour rester simple à utiliser
  sans coder. Si un jour tu veux ajouter des variables (objets collectés,
  relations entre personnages, etc.), ce sera une évolution du code de
  `cyoa_creator.py` et de `lecteur_cyoa.py` — n'hésite pas à demander de
  l'aide pour ça le moment venu.
- Le fichier `story.py` généré est du Python normal et lisible : tu peux
  toujours l'ouvrir dans un éditeur de texte et le modifier à la main si
  tu es à l'aise avec ça, puis relancer `lecteur_cyoa.py`.

---

**Fichiers du projet**

| Fichier | Rôle |
|---|---|
| `cyoa_creator.py` | L'éditeur (à lancer pour créer ou modifier une histoire) |
| `lecteur_cyoa.py` | Le lecteur de jeu, exporté avec chaque histoire |
| `cyoa_settings.json` | Mémorise le thème choisi (créé automatiquement) |
| `*.cyoa.json` | Un projet d'histoire (ex. : `le phare.cyoa.json`) |
| `images/` | Images du projet, rangées automatiquement |

