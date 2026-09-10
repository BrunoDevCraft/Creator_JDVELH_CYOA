# -*- coding: utf-8 -*-
"""
cyoa_creator.py
================
Éditeur d'histoires "dont vous êtes le héros" (CYOA) pour débutants.

Ce programme reprend l'architecture du projet "Luna et la Vallée aux
Murmures" (un dictionnaire de passages, chacun avec un texte, une image
optionnelle et des choix menant vers d'autres passages), mais y ajoute une
interface graphique permettant de CONSTRUIRE cette structure sans écrire
une seule ligne de code.

Parcours de l'application :
    Écran de démarrage (3 secondes)
        -> "Que voulez-vous faire ?"
              - Voir un exemple      : ouvre une histoire de démonstration
              - Créer son histoire   : ouvre un projet vierge
              - Tutoriel             : guide pas à pas dans l'application
              - Paramètres           : choix du thème visuel de l'éditeur

Ce que permet l'éditeur lui-même :
  - Autant de passages que voulu, reliés comme on veut (pas de limite de
    profondeur : on peut créer 4, 40 ou 400 passages).
  - Chaque passage peut avoir 0 choix (= fin de l'histoire), 1, 2, 3... :
    aucune limite au nombre de choix.
  - Chaque passage peut avoir une image (import depuis un fichier, ou
    réutilisation d'une image déjà importée dans le projet).
  - Un bouton "Tester" permet de jouer sa création directement dans
    l'éditeur, sans rien exporter.
  - Un bouton "Exporter" génère un dossier de jeu autonome, au même format
    que le projet "Luna et la Vallée aux Murmures" (story.py + images/),
    accompagné d'un lecteur graphique prêt à l'emploi (lecteur_cyoa.py).

Aucune dépendance obligatoire : tkinter (fourni avec Python) suffit.
Si Pillow (PIL) est installé, les aperçus d'images sont plus nets et mieux
redimensionnés, mais ce n'est pas indispensable.

Lancement :
    python3 cyoa_creator.py
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ---------------------------------------------------------------------------
#  Constantes générales
# ---------------------------------------------------------------------------
APP_TITLE = "Créateur de CYOA — écris ta propre histoire à choix multiples"
APP_SPLASH_TITLE = "Maître du jeu, à vos crayons !"
SPLASH_DURATION_MS = 3000

THUMB_SIZE = (200, 200)
NEW_PASSAGE_OPTION = "➕ Créer un nouveau passage…"
NO_TARGET_OPTION = "(choisir un passage…)"

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cyoa_settings.json")


# ---------------------------------------------------------------------------
#  Copie de secours de lecteur_cyoa.py (utilisée si le fichier externe est
#  introuvable, par ex. si cyoa_creator.py a été copie/deplace seul, sans
#  le reste du dossier du projet). Garantit que "Rendu" et "Exporter"
#  fonctionnent toujours, meme dans ce cas.
# ---------------------------------------------------------------------------
EMBEDDED_LECTEUR_CYOA_SOURCE = r'''
# -*- coding: utf-8 -*-
"""
lecteur_cyoa.py
-----------------
Lecteur générique pour les histoires générées par cyoa_creator.py (ou pour
tout module story.py au même format que le projet "Luna et la Vallée aux
Murmures" : un dictionnaire `story`, et les fonctions get_story_part /
get_next_part, avec en option une variable TITLE).

Placer ce fichier dans le même dossier que story.py (et son dossier
images/), puis le lancer avec Python pour jouer à l'histoire :

    python3 lecteur_cyoa.py

Aucune dépendance obligatoire : tkinter suffit. Si Pillow (PIL) est
installé, les illustrations sont mieux redimensionnées.
"""

import os
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, ttk

from story import get_story_part, get_next_part

try:
    from story import TITLE
except ImportError:
    TITLE = "Une histoire dont vous êtes le héros"

try:
    from story import THEME
except ImportError:
    THEME = "grimoire"

try:
    from PIL import Image, ImageTk
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

IMAGE_SIZE = (255, 257)

# Les 3 thèmes proposés dans l'éditeur (cyoa_creator.py). Le thème choisi
# au moment de l'export est inscrit dans story.py (variable THEME) afin
# que le jeu final affiche la même apparence que dans l'éditeur.
THEMES = {
    "grimoire": {
        "bg":             "#1c140d",
        "panel":          "#241b13",
        "panel_border":   "#c9a227",
        "parchment":      "#ede0c3",
        "parchment_edge": "#8a7550",
        "ink":            "#3a2c18",
        "gold":           "#d9b04c",
        "gold_soft":      "#b3924e",
        "button":         "#3a2c1c",
        "button_hover":   "#5c4527",
        "button_text":    "#ecdcb8",
        "danger":         "#5c2323",
        "danger_hover":   "#7a2e2e",
    },
    "parchemin_clair": {
        "bg":             "#f4ead2",
        "panel":          "#fffaf5",
        "panel_border":   "#8a6d1f",
        "parchment":      "#fffdf5",
        "parchment_edge": "#c9a227",
        "ink":            "#3a2c18",
        "gold":           "#8a6d1f",
        "gold_soft":      "#b3924e",
        "button":         "#8a6d1f",
        "button_hover":   "#6b5417",
        "button_text":    "#fffaf0",
        "danger":         "#a4423f",
        "danger_hover":   "#7a2e2e",
    },
    "contraste": {
        "bg":             "#000000",
        "panel":          "#0d0d0d",
        "panel_border":   "#ffd60a",
        "parchment":      "#000000",
        "parchment_edge": "#ffd60a",
        "ink":            "#ffffff",
        "gold":           "#ffd60a",
        "gold_soft":      "#ffd60a",
        "button":         "#1a1a1a",
        "button_hover":   "#333333",
        "button_text":    "#ffffff",
        "danger":         "#ff453a",
        "danger_hover":   "#c92c22",
    },
}

PALETTE = dict(THEMES.get(THEME, THEMES["grimoire"]))

TITLE_FONTS = ["Cinzel Decorative", "Cinzel", "Papyrus", "Georgia", "Times New Roman"]
BODY_FONTS = ["Cormorant Garamond", "EB Garamond", "Garamond", "Georgia", "Times New Roman"]
CIRCLED_DIGITS = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩"]


def _pick_font(candidates, fallback="Times New Roman"):
    try:
        available = set(tkfont.families())
    except Exception:
        return fallback
    for name in candidates:
        if name in available:
            return name
    return fallback


def _load_display_image(path, size=IMAGE_SIZE):
    if _PIL_AVAILABLE:
        with Image.open(path) as im:
            im = im.convert("RGBA")
            if im.size != size:
                im = im.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(im)
    return tk.PhotoImage(file=path)


class CyoaPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{TITLE} — Vous êtes le Héros")
        self.root.geometry("780x760")
        self.root.minsize(620, 620)
        self.root.configure(bg=PALETTE["bg"])

        self.current_part_id = 1
        self.history = [1]

        title_family = _pick_font(TITLE_FONTS)
        body_family = _pick_font(BODY_FONTS)
        self.fonts = {
            "chapter": tkfont.Font(family=body_family, size=11, weight="bold"),
            "subtitle": tkfont.Font(family=body_family, size=14, slant="italic"),
            "body": tkfont.Font(family=body_family, size=14),
            "button": tkfont.Font(family=body_family, size=13, weight="bold"),
        }

        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "Story.Vertical.TScrollbar", gripcount=0,
            background=PALETTE["gold_soft"], troughcolor=PALETTE["panel"],
            bordercolor=PALETTE["panel"], arrowcolor=PALETTE["parchment"],
            relief="flat", arrowsize=22, width=22,
        )
        style.map("Story.Vertical.TScrollbar",
                  background=[("active", PALETTE["gold"]), ("pressed", PALETTE["gold"])])

        self.panel = tk.Frame(
            self.root, bg=PALETTE["panel"],
            highlightbackground=PALETTE["panel_border"],
            highlightcolor=PALETTE["panel_border"], highlightthickness=2,
        )
        self.panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.94, relheight=0.94)

        self.image_ref = None
        self.text_label = None
        self.display_story(1)

    def _make_button(self, parent, text, command, width=None, danger=False):
        bg = PALETTE["danger"] if danger else PALETTE["button"]
        hover = PALETTE["danger_hover"] if danger else PALETTE["button_hover"]
        btn = tk.Button(
            parent, text=text, command=command, font=self.fonts["button"],
            bg=bg, fg=PALETTE["button_text"], activebackground=hover,
            activeforeground=PALETTE["gold"], relief="flat", bd=0,
            padx=16, pady=10, cursor="hand2",
            highlightbackground=PALETTE["gold_soft"], highlightthickness=1,
            justify="left", anchor="w" if width else "center",
        )
        if width:
            btn.configure(width=width)

        def on_enter(_e):
            btn.configure(bg=hover, fg=PALETTE["gold"])

        def on_leave(_e):
            btn.configure(bg=bg, fg=PALETTE["button_text"])

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def _separator(self, parent, symbol="✦"):
        tk.Label(parent, text=f"{symbol} {symbol} {symbol}", bg=PALETTE["panel"],
                 fg=PALETTE["gold_soft"], font=self.fonts["subtitle"]).pack(pady=(4, 10))

    def clear_screen(self):
        for widget in self.panel.winfo_children():
            widget.destroy()
        self.text_label = None

    def display_story(self, part_id):
        text, choices, image_path = get_story_part(part_id)
        if text is None or choices is None:
            messagebox.showerror("Erreur", "Partie d'histoire non valide.")
            return

        self.clear_screen()
        self.current_part_id = part_id

        header = tk.Frame(self.panel, bg=PALETTE["panel"])
        header.pack(fill="x", padx=24, pady=(18, 6))
        tk.Label(header, text=f"§ Passage n° {part_id}", bg=PALETTE["panel"],
                 fg=PALETTE["gold_soft"], font=self.fonts["chapter"]).pack(side="left")
        tk.Label(header, text=TITLE, bg=PALETTE["panel"],
                 fg=PALETTE["gold_soft"], font=self.fonts["chapter"]).pack(side="right")

        body = tk.Frame(self.panel, bg=PALETTE["panel"])
        body.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        if image_path and os.path.exists(image_path):
            try:
                image = _load_display_image(image_path)
                self.image_ref = image
                frame_img = tk.Frame(body, bg=PALETTE["gold_soft"], padx=3, pady=3)
                frame_img.pack(pady=(4, 14))
                inner = tk.Frame(frame_img, bg="black", padx=2, pady=2)
                inner.pack()
                tk.Label(inner, image=image, bg="black").pack()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger l'image : {e}")

        choices_frame = tk.Frame(body, bg=PALETTE["panel"])
        choices_frame.pack(side="bottom", fill="x")

        parch_outer = tk.Frame(body, bg=PALETTE["parchment_edge"])
        parch_outer.pack(fill="both", expand=True, pady=(0, 18))
        parch_inner = tk.Frame(parch_outer, bg=PALETTE["parchment"])
        parch_inner.pack(fill="both", expand=True, padx=2, pady=2)

        text_wrapper = tk.Frame(parch_inner, bg=PALETTE["parchment"])
        text_wrapper.pack(fill="both", expand=True)

        self.text_label = tk.Text(
            text_wrapper, font=self.fonts["body"], height=5, width=1,
            bg=PALETTE["parchment"], fg=PALETTE["ink"], wrap="word",
            relief="flat", bd=0, padx=18, pady=16,
            highlightthickness=0, cursor="arrow",
        )
        text_scroll = ttk.Scrollbar(
            text_wrapper, orient="vertical", command=self.text_label.yview,
            style="Story.Vertical.TScrollbar",
        )
        self.text_label.configure(yscrollcommand=text_scroll.set)
        self.text_label.pack(side="left", fill="both", expand=True)
        text_scroll.pack(side="right", fill="y", padx=(6, 0))
        self.text_label.insert("1.0", text)
        self.text_label.configure(state="disabled")

        def _on_mousewheel(event):
            if event.num == 4:
                delta = -1
            elif event.num == 5:
                delta = 1
            else:
                delta = -1 if event.delta > 0 else 1
            self.text_label.yview_scroll(delta, "units")
            return "break"

        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.text_label.bind(seq, _on_mousewheel)

        if choices:
            for i, (key, value) in enumerate(choices.items()):
                marker = CIRCLED_DIGITS[i] if i < len(CIRCLED_DIGITS) else f"({i + 1})"
                label = f"{marker}  {value['text']}"
                btn = self._make_button(choices_frame, label,
                                         lambda k=key: self.make_choice(k), width=52)
                btn.pack(fill="x", pady=5)
        else:
            self._separator(choices_frame, "❖")
            tk.Label(choices_frame, text="F I N   D E   C E   C H E M I N",
                     bg=PALETTE["panel"], fg=PALETTE["gold"], font=self.fonts["subtitle"]).pack(pady=(0, 14))
            self._make_button(choices_frame, "Recommencer l'aventure depuis le début",
                               self.restart_story, width=40).pack(pady=5)
            self._make_button(choices_frame, "Fermer le grimoire", self.root.quit,
                               width=40, danger=True).pack(pady=5)

    def make_choice(self, choice_key):
        next_part_id = get_next_part(self.current_part_id, choice_key)
        if next_part_id is not None:
            self.history.append(next_part_id)
            self.display_story(next_part_id)
        else:
            messagebox.showerror("Erreur", "Ce choix ne mène nulle part (histoire incomplète).")

    def restart_story(self):
        self.history = [1]
        self.display_story(1)


if __name__ == "__main__":
    root = tk.Tk()
    player = CyoaPlayer(root)
    root.mainloop()
'''


# ---------------------------------------------------------------------------
#  Thèmes visuels de l'éditeur (choisis depuis l'écran "Paramètres")
# ---------------------------------------------------------------------------
THEMES = {
    "grimoire": {
        "label":  "Grimoire ancien (sombre)",
        "bg":     "#1c140d",
        "panel":  "#241b13",
        "parchment": "#ede0c3",
        "ink":    "#2c2213",
        "gold":   "#d9b04c",
        "danger": "#8a3a3a",
    },
    "parchemin_clair": {
        "label":  "Parchemin clair",
        "bg":     "#f4ead2",
        "panel":  "#fffaf0",
        "parchment": "#fffdf5",
        "ink":    "#3a2c18",
        "gold":   "#8a6d1f",
        "danger": "#a4423f",
    },
    "contraste": {
        "label":  "Contraste élevé (accessibilité)",
        "bg":     "#000000",
        "panel":  "#0d0d0d",
        "parchment": "#000000",
        "ink":    "#ffffff",
        "gold":   "#ffd60a",
        "danger": "#ff453a",
    },
}
DEFAULT_THEME = "grimoire"

# PALETTE est un dictionnaire mutable : on met à jour son CONTENU (et non
# la variable elle-même) quand on change de thème, pour que tous les
# endroits du code qui font PALETTE["xxx"] voient la nouvelle couleur sans
# avoir besoin de se réimporter.
PALETTE = dict(THEMES[DEFAULT_THEME])


def apply_theme(name):
    theme = THEMES.get(name, THEMES[DEFAULT_THEME])
    for key, value in theme.items():
        PALETTE[key] = value


def find_reader_script():
    """Cherche lecteur_cyoa.py à plusieurs emplacements plausibles (à côté de
    ce fichier, dans le dossier courant, à côté de l'exécutable lancé), afin
    de fonctionner même si cyoa_creator.py a été copié/déplacé seul. Renvoie
    le chemin trouvé, ou None si vraiment introuvable (dans ce cas, la copie
    embarquée EMBEDDED_LECTEUR_CYOA_SOURCE sert de filet de sécurité)."""
    candidates = []
    try:
        candidates.append(os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        pass
    candidates.append(os.getcwd())
    try:
        candidates.append(os.path.dirname(os.path.abspath(sys.argv[0])))
    except Exception:
        pass
    seen = set()
    for d in candidates:
        if not d or d in seen:
            continue
        seen.add(d)
        path = os.path.join(d, "lecteur_cyoa.py")
        if os.path.isfile(path):
            return path
    return None


def write_reader_script(output_dir):
    """Place un fichier lecteur_cyoa.py utilisable dans output_dir : copie le
    fichier externe s'il est trouvé, sinon écrit la copie embarquée dans le
    code (voir EMBEDDED_LECTEUR_CYOA_SOURCE ci-dessus). Ainsi cette étape ne
    peut jamais échouer silencieusement."""
    dest = os.path.join(output_dir, "lecteur_cyoa.py")
    reader_src = find_reader_script()
    if reader_src and os.path.abspath(reader_src) != os.path.abspath(dest):
        shutil.copyfile(reader_src, dest)
    else:
        with open(dest, "w", encoding="utf-8") as f:
            f.write(EMBEDDED_LECTEUR_CYOA_SOURCE)
    return dest


def load_settings():
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_settings(data):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ---------------------------------------------------------------------------
#  Contenu du tutoriel intégré (écran "Tutoriel")
# ---------------------------------------------------------------------------
TUTORIAL_STEPS = [
    (
        "Bienvenue !",
        "Un CYOA (« Choisis ta propre aventure ») est une histoire où le joueur lit un texte, "
        "puis choisit parmi plusieurs options : son choix détermine ce qu'il va lire ensuite. "
        "C'est exactement ce que tu vas construire ici, passage par passage, sans écrire une "
        "seule ligne de code.",
    ),
    (
        "1. Le passage n°1",
        "Chaque histoire commence par le passage n°1 : c'est le tout premier texte que lira le "
        "joueur. Clique dessus dans la liste de gauche pour l'ouvrir, puis écris-le dans la "
        "grande zone de texte à droite. Tout ce que tu tapes est enregistré automatiquement "
        "dans le projet au fur et à mesure — il te suffira d'enregistrer le fichier plus tard.",
    ),
    (
        "2. Ajouter une image (facultatif)",
        "Sous la zone de texte, le bouton « Choisir une image sur mon ordinateur… » permet "
        "d'illustrer le passage. L'image est copiée automatiquement dans le projet : tu n'as "
        "rien d'autre à faire. Le bouton « Réutiliser une image déjà importée… » évite de "
        "réimporter deux fois la même image dans deux passages différents.",
    ),
    (
        "3. Ajouter des choix",
        "Clique sur « + Ajouter un choix » autant de fois que tu veux : il n'y a pas de "
        "limite. Pour chaque choix, écris le texte du bouton que verra le joueur, puis choisis "
        "sa destination dans la liste déroulante — soit un passage déjà écrit, soit "
        "« ➕ Créer un nouveau passage… », qui t'emmène directement écrire la suite.",
    ),
    (
        "4. Construire une histoire longue",
        "C'est en enchaînant « + Ajouter un choix » puis « Créer un nouveau passage… », encore "
        "et encore, que ton histoire grandit. Rien ne t'oblige à t'arrêter après quatre ou cinq "
        "passages : certaines branches peuvent être longues, d'autres courtes, et plusieurs "
        "choix peuvent même se rejoindre sur le même passage plus loin dans l'histoire.",
    ),
    (
        "5. Terminer un chemin",
        "Un passage sans aucun choix est automatiquement une fin de l'histoire. Le joueur "
        "verra alors « FIN DE CE CHEMIN » avec un bouton pour recommencer. Une bonne histoire "
        "à choix multiples a souvent plusieurs fins différentes selon les décisions prises.",
    ),
    (
        "6. Tester en cours d'écriture",
        "Le bouton « ▶ Tester l'histoire depuis ce passage » (ou « ▶ Tester depuis le début » "
        "en haut de l'écran) ouvre une fenêtre de jeu, pour essayer ta création sans rien "
        "exporter. Le bouton « Vérifier l'histoire » repère de son côté les choix qui ne "
        "mènent encore nulle part, ou les passages qu'on ne peut jamais atteindre en jouant.",
    ),
    (
        "7. Enregistrer et exporter",
        "Menu Fichier > Enregistrer : sauvegarde ton projet, modifiable à tout moment plus "
        "tard. Menu Fichier > Exporter le jeu terminé… : génère un dossier autonome avec "
        "story.py, les images, et un lecteur prêt à l'emploi (lecteur_cyoa.py) que n'importe "
        "qui peut lancer pour jouer, sans avoir besoin de cet éditeur.\n\n"
        "Tu es prêt à commencer !",
    ),
]


# ---------------------------------------------------------------------------
#  Histoire de démonstration (écran "Voir un exemple")
# ---------------------------------------------------------------------------
def build_example_project():
    proj = CyoaProject()
    proj.title = "Exemple : Le Phare Oublié"
    proj.passages = {
        1: {
            "text": (
                "Ceci est un exemple d'histoire pour te montrer comment fonctionne l'outil. "
                "Tu es gardien d'un phare abandonné, sur une île balayée par la tempête. Un "
                "bruit sourd résonne depuis la cave.\n\n"
                "(Remarque : cet exemple n'a pas d'image, mais tu peux en ajouter une à "
                "n'importe quel passage avec le bouton « Choisir une image sur mon "
                "ordinateur… ».)"
            ),
            "image": None,
            "choices": {
                "1": {"text": "Descendre voir ce qui fait ce bruit", "next_part": 2},
                "2": {"text": "Rester en haut et attendre le matin", "next_part": 3},
                "3": {"text": "Sortir affronter la tempête dehors", "next_part": 4},
            },
        },
        2: {
            "text": (
                "Tu descends les marches humides. Une vieille caisse s'est renversée : ce "
                "n'était qu'un chat errant, réfugié de l'orage."
            ),
            "image": None,
            "choices": {
                "1": {"text": "Adopter le chat pour la nuit", "next_part": 5},
                "2": {"text": "Le laisser tranquille et remonter", "next_part": 6},
            },
        },
        3: {
            "text": (
                "Tu remontes te coucher, bercé par le vent. Au matin, la tempête est passée, "
                "et le mystère du bruit reste entier.\n\n✦ Fin de ce chemin ✦"
            ),
            "image": None,
            "choices": {},
        },
        4: {
            "text": (
                "Le vent te plaque contre la porte du phare. Tu comprends vite qu'il vaut "
                "mieux ne pas s'attarder dehors et tu rentres en hâte."
            ),
            "image": None,
            "choices": {
                "1": {"text": "Retourner enquêter sur le bruit", "next_part": 2},
            },
        },
        5: {
            "text": (
                "Le chat ronronne à tes pieds toute la nuit. Tu passes une nuit plus paisible "
                "que prévu, malgré la tempête.\n\n✦ Fin de ce chemin ✦"
            ),
            "image": None,
            "choices": {},
        },
        6: {
            "text": (
                "Tu remontes, laissant le chat à son sort. Le lendemain, il a disparu, et tu "
                "te demandes s'il n'était pas venu te prévenir de quelque chose.\n\n"
                "✦ Fin de ce chemin ✦"
            ),
            "image": None,
            "choices": {},
        },
    }
    return proj


def load_thumbnail(path, size=THUMB_SIZE):
    """Charge une image pour l'aperçu, redimensionnée si Pillow est là."""
    if not path or not os.path.exists(path):
        return None
    try:
        if PIL_AVAILABLE:
            with Image.open(path) as im:
                im = im.convert("RGBA")
                im.thumbnail(size, Image.LANCZOS)
                return ImageTk.PhotoImage(im)
        return tk.PhotoImage(file=path)
    except Exception:
        return None


def safe_filename(name):
    """Nettoie un nom de fichier pour éviter les caractères problématiques."""
    name = os.path.basename(name)
    name = re.sub(r"[^A-Za-z0-9_.\-]", "_", name)
    return name or "image.png"


# ---------------------------------------------------------------------------
#  Modèle de données : le projet CYOA
# ---------------------------------------------------------------------------
class CyoaProject:
    """
    Représente une histoire en cours d'écriture.

    self.passages est un dictionnaire :
        { id_passage (int): {
              "text": str,
              "image": str ou None,   # nom de fichier dans images_dir
              "choices": {
                  "1": {"text": str, "next_part": int ou None},
                  "2": {...},
                  ...
              }
          }, ... }

    Le passage n°1 est toujours le point de départ de l'histoire.
    """

    def __init__(self):
        self.title = "Mon histoire"
        self.passages = {1: {"text": "", "image": None, "choices": {}}}
        self.project_file = None      # chemin du fichier .cyoa.json
        self.images_dir = None        # dossier où sont stockées les images importées
        self.dirty = False

    # -- gestion des passages -------------------------------------------------
    def next_free_id(self):
        return (max(self.passages.keys()) + 1) if self.passages else 1

    def new_passage(self, text="", image=None):
        pid = self.next_free_id()
        self.passages[pid] = {"text": text, "image": image, "choices": {}}
        self.dirty = True
        return pid

    def delete_passage(self, pid):
        if pid == 1:
            raise ValueError("Le passage n°1 est le point de départ : il ne peut pas être supprimé.")
        self.passages.pop(pid, None)
        for p in self.passages.values():
            for choice in p["choices"].values():
                if choice.get("next_part") == pid:
                    choice["next_part"] = None
        self.dirty = True

    def duplicate_passage(self, pid):
        if pid not in self.passages:
            return None
        source = self.passages[pid]
        new_id = self.next_free_id()
        self.passages[new_id] = {
            "text": source["text"],
            "image": source["image"],
            "choices": {k: dict(v) for k, v in source["choices"].items()},
        }
        self.dirty = True
        return new_id

    def add_choice(self, pid):
        p = self.passages[pid]
        existing_keys = [int(k) for k in p["choices"].keys() if k.isdigit()]
        new_key = str((max(existing_keys) + 1) if existing_keys else 1)
        p["choices"][new_key] = {"text": "", "next_part": None}
        self.dirty = True
        return new_key

    # -- import d'images --------------------------------------------------
    def import_image(self, source_path):
        """Copie une image externe dans le dossier images/ du projet et
        renvoie son nom de fichier (à stocker dans passage['image'])."""
        if not self.images_dir:
            raise RuntimeError("Enregistre d'abord le projet avant d'ajouter des images.")
        os.makedirs(self.images_dir, exist_ok=True)
        filename = safe_filename(os.path.basename(source_path))
        dest = os.path.join(self.images_dir, filename)
        base, ext = os.path.splitext(filename)
        i = 1
        while os.path.exists(dest) and os.path.abspath(dest) != os.path.abspath(source_path):
            filename = f"{base}_{i}{ext}"
            dest = os.path.join(self.images_dir, filename)
            i += 1
        if os.path.abspath(dest) != os.path.abspath(source_path):
            shutil.copyfile(source_path, dest)
        return filename

    def list_project_images(self):
        if not self.images_dir or not os.path.isdir(self.images_dir):
            return []
        return sorted(
            f for f in os.listdir(self.images_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
        )

    def image_path(self, filename):
        if not filename or not self.images_dir:
            return None
        return os.path.join(self.images_dir, filename)

    # -- validation ---------------------------------------------------------
    def validate(self):
        """Renvoie une liste de messages sur l'état de l'histoire, pour
        aider à repérer les choix oubliés ou les passages inaccessibles."""
        issues = []
        reachable = {1}
        for pid, p in self.passages.items():
            for choice in p["choices"].values():
                target = choice.get("next_part")
                if target is None:
                    issues.append(
                        f"⚠ Passage {pid} : le choix « {choice['text'] or '(sans texte)'} » ne mène nulle part."
                    )
                elif target not in self.passages:
                    issues.append(
                        f"⛔ Passage {pid} : le choix « {choice['text']} » pointe vers un passage inexistant ({target})."
                    )
                else:
                    reachable.add(target)
            if not p["text"].strip():
                issues.append(f"⚠ Passage {pid} : le texte est vide.")
        orphans = set(self.passages.keys()) - reachable
        for pid in sorted(orphans):
            issues.append(f"⚠ Passage {pid} : inaccessible (aucun choix, ailleurs, ne mène jusqu'ici).")
        return issues

    # -- sauvegarde / chargement (format de travail JSON) --------------------
    def save(self, path):
        self.project_file = path
        self.images_dir = os.path.join(os.path.dirname(os.path.abspath(path)), "images")
        os.makedirs(self.images_dir, exist_ok=True)
        data = {
            "title": self.title,
            "passages": {str(pid): p for pid, p in self.passages.items()},
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.dirty = False

    @classmethod
    def load(cls, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        proj = cls()
        proj.title = data.get("title", "Mon histoire")
        proj.passages = {int(pid): p for pid, p in data.get("passages", {}).items()}
        if not proj.passages:
            proj.passages = {1: {"text": "", "image": None, "choices": {}}}
        proj.project_file = path
        proj.images_dir = os.path.join(os.path.dirname(os.path.abspath(path)), "images")
        proj.dirty = False
        return proj

    # -- export du jeu jouable ----------------------------------------------
    def export_game(self, output_dir, theme_name=DEFAULT_THEME):
        """Génère un dossier de jeu autonome : story.py + images/ +
        lecteur_cyoa.py, au même format que le projet
        "Luna et la Vallée aux Murmures". Le thème choisi dans l'éditeur
        (theme_name) est inscrit dans story.py afin que lecteur_cyoa.py
        affiche le jeu avec la même apparence."""
        os.makedirs(output_dir, exist_ok=True)
        out_images = os.path.join(output_dir, "images")
        os.makedirs(out_images, exist_ok=True)

        for p in self.passages.values():
            if p.get("image"):
                src = self.image_path(p["image"])
                if src and os.path.exists(src):
                    shutil.copyfile(src, os.path.join(out_images, p["image"]))

        lines = []
        lines.append("# -*- coding: utf-8 -*-")
        lines.append('"""Histoire générée avec cyoa_creator.py."""')
        lines.append("import os")
        lines.append("")
        lines.append(f"TITLE = {json.dumps(self.title, ensure_ascii=False)}")
        lines.append(f"THEME = {json.dumps(theme_name, ensure_ascii=False)}")
        lines.append("")
        lines.append("current_dir = os.path.dirname(__file__)")
        lines.append("")
        lines.append("story = {")
        for pid in sorted(self.passages.keys()):
            p = self.passages[pid]
            lines.append(f"    {pid}: {{")
            lines.append(f"        \"text\": {json.dumps(p['text'], ensure_ascii=False)},")
            if p.get("image"):
                lines.append(
                    "        \"image\": os.path.join(current_dir, \"images\", "
                    f"{json.dumps(p['image'], ensure_ascii=False)}),"
                )
            else:
                lines.append("        \"image\": None,")
            lines.append("        \"choices\": {")
            for key, choice in p["choices"].items():
                next_part_repr = choice["next_part"] if choice["next_part"] is not None else "None"
                lines.append(
                    f"            {json.dumps(key)}: {{\"text\": "
                    f"{json.dumps(choice['text'], ensure_ascii=False)}, "
                    f"\"next_part\": {next_part_repr}}},"
                )
            lines.append("        },")
            lines.append("    },")
        lines.append("}")
        lines.append("")
        lines.append("")
        lines.append("def get_story_part(part_id):")
        lines.append('    """Retourne le texte, les choix et l\'image du passage demandé."""')
        lines.append("    part = story.get(part_id)")
        lines.append("    if part:")
        lines.append('        return part["text"], part["choices"], part.get("image")')
        lines.append("    return None, None, None")
        lines.append("")
        lines.append("")
        lines.append("def get_next_part(current_part_id, choice_key):")
        lines.append('    """Retourne l\'identifiant du passage suivant selon le choix fait."""')
        lines.append("    part = story.get(current_part_id)")
        lines.append('    if part and choice_key in part["choices"]:')
        lines.append('        return part["choices"][choice_key]["next_part"]')
        lines.append("    return None")
        lines.append("")

        with open(os.path.join(output_dir, "story.py"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        write_reader_script(output_dir)


# ---------------------------------------------------------------------------
#  Une ligne de l'éditeur de choix : texte du choix + passage cible + suppr.
# ---------------------------------------------------------------------------
class ChoiceRow:
    def __init__(self, parent, app, pid, key, choice):
        self.app = app
        self.pid = pid
        self.key = key

        self.frame = tk.Frame(parent, bg=PALETTE["panel"])
        self.frame.pack(fill="x", pady=3)

        self.text_var = tk.StringVar(value=choice.get("text", ""))
        entry = tk.Entry(self.frame, textvariable=self.text_var, width=36)
        entry.pack(side="left", padx=(0, 6))
        entry.bind("<KeyRelease>", self._on_text_change)

        self.target_var = tk.StringVar()
        self.combo = ttk.Combobox(self.frame, textvariable=self.target_var, state="readonly", width=34)
        self.combo.pack(side="left", padx=(0, 6))
        self.combo.bind("<<ComboboxSelected>>", self._on_target_selected)
        self._refresh_targets(choice.get("next_part"))

        del_btn = tk.Button(self.frame, text="Supprimer", command=self._on_delete,
                             bg=PALETTE["danger"], fg="white", relief="flat")
        del_btn.pack(side="left")

    def _refresh_targets(self, current_target):
        options = [NO_TARGET_OPTION]
        mapping = {NO_TARGET_OPTION: None}
        for pid in sorted(self.app.project.passages.keys()):
            preview = self.app.project.passages[pid]["text"].strip().replace("\n", " ")[:40]
            label = f"{pid} — {preview}" if preview else f"{pid} — (vide)"
            options.append(label)
            mapping[label] = pid
        options.append(NEW_PASSAGE_OPTION)
        mapping[NEW_PASSAGE_OPTION] = "NEW"
        self.combo["values"] = options
        self._mapping = mapping
        current_label = NO_TARGET_OPTION
        for label, pid in mapping.items():
            if pid == current_target:
                current_label = label
                break
        self.target_var.set(current_label)

    def _on_text_change(self, event=None):
        self.app.project.passages[self.pid]["choices"][self.key]["text"] = self.text_var.get()
        self.app.mark_dirty()
        self.app.refresh_passage_list()

    def _on_target_selected(self, event=None):
        selected = self._mapping.get(self.target_var.get())
        if selected == "NEW":
            new_id = self.app.project.new_passage()
            self.app.project.passages[self.pid]["choices"][self.key]["next_part"] = new_id
            self.app.mark_dirty()
            self.app.refresh_passage_list()
            self.app.select_passage(new_id)
        else:
            self.app.project.passages[self.pid]["choices"][self.key]["next_part"] = selected
            self.app.mark_dirty()
            self.app.refresh_passage_list()

    def _on_delete(self):
        del self.app.project.passages[self.pid]["choices"][self.key]
        self.app.mark_dirty()
        self.app.open_passage_editor(self.pid)
        self.app.refresh_passage_list()


# ---------------------------------------------------------------------------
#  Fenêtre de test : joue l'histoire telle qu'elle est en cours d'écriture
# ---------------------------------------------------------------------------
class PlayTestWindow(tk.Toplevel):
    def __init__(self, master, project, start_pid):
        super().__init__(master)
        self.project = project
        self.title(f"Test — {project.title}")
        self.geometry("640x680")
        self.configure(bg=PALETTE["bg"])
        self.image_ref = None
        self.history = [start_pid]
        self._render(start_pid)

    def _render(self, pid):
        for w in self.winfo_children():
            w.destroy()
        p = self.project.passages.get(pid)
        if not p:
            tk.Label(self, text="Passage introuvable.", fg="red", bg=PALETTE["bg"]).pack(pady=20)
            return

        tk.Label(self, text=f"§ Passage {pid}", bg=PALETTE["bg"], fg=PALETTE["gold"],
                 font=("Georgia", 11, "bold")).pack(anchor="w", padx=16, pady=(12, 0))

        if p.get("image"):
            thumb = load_thumbnail(self.project.image_path(p["image"]), size=(255, 257))
            if thumb:
                self.image_ref = thumb
                tk.Label(self, image=thumb, bg="black").pack(pady=10)

        text_widget = tk.Text(self, wrap="word", height=9, bg=PALETTE["parchment"], fg=PALETTE["ink"])
        text_widget.pack(fill="both", expand=True, padx=16)
        text_widget.insert("1.0", p["text"])
        text_widget.configure(state="disabled")

        btns = tk.Frame(self, bg=PALETTE["bg"])
        btns.pack(fill="x", padx=16, pady=14)
        if p["choices"]:
            for choice in p["choices"].values():
                target = choice.get("next_part")
                label = choice["text"] or "(choix sans texte)"
                valid = target in self.project.passages
                if not valid:
                    label += "  ⚠ (ne mène nulle part)"
                tk.Button(btns, text=label, anchor="w",
                          command=lambda t=target: self._go(t)).pack(fill="x", pady=3)
        else:
            tk.Label(btns, text="— FIN DE CE CHEMIN —", bg=PALETTE["bg"], fg=PALETTE["gold"],
                     font=("Georgia", 12, "italic")).pack(pady=8)
            tk.Button(btns, text="Recommencer depuis le début",
                      command=lambda: self._go(self.history[0])).pack(fill="x", pady=3)

        nav = tk.Frame(self, bg=PALETTE["bg"])
        nav.pack(fill="x", padx=16, pady=(0, 12))
        tk.Button(nav, text="⬅ Passage précédent", command=self._back,
                  state="normal" if len(self.history) > 1 else "disabled").pack(side="left")
        tk.Button(nav, text="Fermer le test", command=self.destroy).pack(side="right")

    def _go(self, target):
        if target is None or target not in self.project.passages:
            messagebox.showwarning("Test", "Ce choix ne mène vers aucun passage pour le moment.")
            return
        self.history.append(target)
        self._render(target)

    def _back(self):
        if len(self.history) > 1:
            self.history.pop()
            self._render(self.history[-1])


# ---------------------------------------------------------------------------
#  Application principale
# ---------------------------------------------------------------------------
class CyoaCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1150x720")
        self.root.minsize(900, 600)

        settings = load_settings()
        self.theme_name = settings.get("theme", DEFAULT_THEME)
        apply_theme(self.theme_name)
        self.root.configure(bg=PALETTE["bg"])

        self.project = CyoaProject()
        self.current_pid = 1
        self.choice_rows = []
        self.image_thumb_ref = None
        self.tutorial_index = 0

        self.container = tk.Frame(self.root, bg=PALETTE["bg"])
        self.container.pack(fill="both", expand=True)

        self.show_splash()

    # =========================================================
    #  Navigation entre écrans
    # =========================================================
    def _clear_container(self):
        for w in self.container.winfo_children():
            w.destroy()

    def _hide_menu(self):
        self.root.config(menu=tk.Menu(self.root))

    # ---------------- écran 1 : démarrage ----------------
    def show_splash(self):
        self._clear_container()
        self._hide_menu()
        self.root.configure(bg=PALETTE["bg"])
        frame = tk.Frame(self.container, bg=PALETTE["bg"])
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text=APP_SPLASH_TITLE, bg=PALETTE["bg"], fg=PALETTE["gold"],
                 font=("Georgia", 28, "bold"), wraplength=900,
                 justify="center").place(relx=0.5, rely=0.45, anchor="center")
        tk.Label(frame, text="Chargement de l'atelier d'écriture…", bg=PALETTE["bg"],
                 fg=PALETTE["parchment"], font=("Georgia", 12, "italic")
                 ).place(relx=0.5, rely=0.58, anchor="center")

        self.root.after(SPLASH_DURATION_MS, self.show_home)

    # ---------------- écran 2 : accueil ----------------
    def show_home(self):
        self._clear_container()
        self._hide_menu()
        self.root.configure(bg=PALETTE["bg"])
        frame = tk.Frame(self.container, bg=PALETTE["bg"])
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text=APP_SPLASH_TITLE, bg=PALETTE["bg"], fg=PALETTE["gold"],
                 font=("Georgia", 20, "bold")).pack(pady=(50, 6))
        tk.Label(frame, text="Que voulez-vous faire ?", bg=PALETTE["bg"], fg=PALETTE["parchment"],
                 font=("Georgia", 16, "italic")).pack(pady=(0, 40))

        menu_frame = tk.Frame(frame, bg=PALETTE["bg"])
        menu_frame.pack()

        options = [
            ("👁  Voir un exemple", self.start_example),
            ("✏  Créer son histoire", self.start_new_project),
            ("📖  Tutoriel", self.show_tutorial),
            ("⚙  Paramètres", self.show_settings),
        ]
        for label, cmd in options:
            btn = tk.Button(
                menu_frame, text=label, command=cmd, font=("Georgia", 14),
                bg=PALETTE["panel"], fg=PALETTE["parchment"],
                activebackground=PALETTE["gold"], activeforeground=PALETTE["ink"],
                relief="flat", width=28, pady=14, cursor="hand2",
                highlightbackground=PALETTE["gold"], highlightthickness=1,
            )
            btn.pack(pady=8)

        tk.Label(frame, text="Tu pourras toujours ouvrir un projet déjà enregistré "
                              "depuis Fichier > Ouvrir…, une fois dans l'éditeur.",
                 bg=PALETTE["bg"], fg=PALETTE["parchment"], font=("Georgia", 9)
                 ).pack(side="bottom", pady=16)

    def start_example(self):
        self.project = build_example_project()
        self.show_editor()

    def start_new_project(self):
        self.project = CyoaProject()
        self.show_editor()

    # ---------------- écran : tutoriel ----------------
    def show_tutorial(self):
        self.tutorial_index = 0
        self._render_tutorial()

    def _render_tutorial(self):
        self._clear_container()
        self._hide_menu()
        self.root.configure(bg=PALETTE["bg"])
        frame = tk.Frame(self.container, bg=PALETTE["bg"])
        frame.pack(fill="both", expand=True)

        top = tk.Frame(frame, bg=PALETTE["bg"])
        top.pack(fill="x", padx=24, pady=(18, 0))
        tk.Button(top, text="🏠 Accueil", command=self.show_home).pack(side="left")
        tk.Label(top, text=f"Tutoriel — étape {self.tutorial_index + 1}/{len(TUTORIAL_STEPS)}",
                 bg=PALETTE["bg"], fg=PALETTE["gold"], font=("Georgia", 11, "italic")).pack(side="right")

        title, body = TUTORIAL_STEPS[self.tutorial_index]
        card = tk.Frame(frame, bg=PALETTE["panel"], highlightbackground=PALETTE["gold"],
                         highlightthickness=1)
        card.pack(fill="both", expand=True, padx=60, pady=24)

        tk.Label(card, text=title, bg=PALETTE["panel"], fg=PALETTE["gold"],
                 font=("Georgia", 18, "bold"), wraplength=760, justify="left"
                 ).pack(anchor="w", padx=30, pady=(30, 14))
        tk.Label(card, text=body, bg=PALETTE["panel"], fg=PALETTE["parchment"],
                 font=("Georgia", 13), wraplength=760, justify="left").pack(anchor="w", padx=30)

        nav = tk.Frame(frame, bg=PALETTE["bg"])
        nav.pack(fill="x", padx=60, pady=(0, 24))
        prev_state = "normal" if self.tutorial_index > 0 else "disabled"
        tk.Button(nav, text="◀ Précédent", command=self._tutorial_prev, state=prev_state).pack(side="left")
        if self.tutorial_index < len(TUTORIAL_STEPS) - 1:
            tk.Button(nav, text="Suivant ▶", command=self._tutorial_next).pack(side="right")
        else:
            tk.Button(nav, text="✏ Commencer à créer mon histoire",
                      command=self.start_new_project).pack(side="right")

    def _tutorial_next(self):
        self.tutorial_index += 1
        self._render_tutorial()

    def _tutorial_prev(self):
        self.tutorial_index -= 1
        self._render_tutorial()

    # ---------------- écran : paramètres ----------------
    def show_settings(self):
        self._clear_container()
        self._hide_menu()
        self.root.configure(bg=PALETTE["bg"])
        frame = tk.Frame(self.container, bg=PALETTE["bg"])
        frame.pack(fill="both", expand=True)

        top = tk.Frame(frame, bg=PALETTE["bg"])
        top.pack(fill="x", padx=24, pady=(18, 0))
        tk.Button(top, text="🏠 Accueil", command=self.show_home).pack(side="left")

        tk.Label(frame, text="Paramètres", bg=PALETTE["bg"], fg=PALETTE["gold"],
                 font=("Georgia", 22, "bold")).pack(pady=(26, 10))
        tk.Label(frame, text="Apparence de l'éditeur (rendu de l'interface) :",
                 bg=PALETTE["bg"], fg=PALETTE["parchment"], font=("Georgia", 13)
                 ).pack(pady=(10, 14))

        self.theme_choice_var = tk.StringVar(value=self.theme_name)
        for key, theme in THEMES.items():
            row = tk.Frame(frame, bg=PALETTE["bg"])
            row.pack(pady=5)
            tk.Radiobutton(
                row, text=theme["label"], variable=self.theme_choice_var, value=key,
                bg=PALETTE["bg"], fg=PALETTE["parchment"], selectcolor=PALETTE["panel"],
                activebackground=PALETTE["bg"], activeforeground=PALETTE["gold"],
                font=("Georgia", 12),
            ).pack(side="left")
            tk.Frame(row, bg=theme["gold"], width=20, height=20,
                     highlightbackground=theme["ink"], highlightthickness=1).pack(side="left", padx=(10, 4))
            tk.Frame(row, bg=theme["bg"], width=20, height=20,
                     highlightbackground=theme["ink"], highlightthickness=1).pack(side="left")

        tk.Button(frame, text="Appliquer", command=self._apply_theme_choice,
                  font=("Georgia", 13, "bold"), bg=PALETTE["panel"], fg=PALETTE["parchment"],
                  activebackground=PALETTE["gold"]).pack(pady=26)

    def _apply_theme_choice(self):
        self.theme_name = self.theme_choice_var.get()
        apply_theme(self.theme_name)
        save_settings({"theme": self.theme_name})
        self.show_settings()  # redessine l'écran avec les nouvelles couleurs appliquées

    # =========================================================
    #  Écran principal : éditeur de passages
    # =========================================================
    def show_editor(self):
        self._clear_container()
        self.root.configure(bg=PALETTE["bg"])
        self._build_menu()
        self._build_layout(self.container)
        self.current_pid = 1 if 1 in self.project.passages else next(iter(self.project.passages))
        self.refresh_passage_list()
        self.open_passage_editor(self.current_pid)

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Nouveau projet", command=self.new_project)
        filemenu.add_command(label="Ouvrir…", command=self.open_project)
        filemenu.add_command(label="Enregistrer", command=self.save_project)
        filemenu.add_command(label="Enregistrer sous…", command=self.save_project_as)
        filemenu.add_separator()
        filemenu.add_command(label="Exporter le jeu terminé…", command=self.export_game)
        filemenu.add_separator()
        filemenu.add_command(label="Retour à l'accueil", command=self.show_home)
        filemenu.add_command(label="Quitter", command=self.root.quit)
        menubar.add_cascade(label="Fichier", menu=filemenu)
        self.root.config(menu=menubar)

    def _build_layout(self, parent):
        top = tk.Frame(parent, bg=PALETTE["bg"])
        top.pack(fill="x", padx=10, pady=(10, 4))
        tk.Button(top, text="🏠 Accueil", command=self.show_home).pack(side="left", padx=(0, 12))
        tk.Label(top, text="Titre de l'histoire :", bg=PALETTE["bg"], fg=PALETTE["gold"]).pack(side="left")
        self.title_var = tk.StringVar(value=self.project.title)
        title_entry = tk.Entry(top, textvariable=self.title_var, width=44)
        title_entry.pack(side="left", padx=8)
        title_entry.bind("<KeyRelease>", lambda e: self._on_title_change())

        tk.Button(top, text="Vérifier l'histoire", command=self.show_validation).pack(side="right", padx=4)
        tk.Button(top, text="🎬 Rendu", command=self.render_preview).pack(side="right", padx=4)
        tk.Button(top, text="▶ Tester depuis le début", command=lambda: self.play_test(1)).pack(side="right", padx=4)

        # Barre d'actions sur le fichier du projet : toujours visible, en plus
        # du menu "Fichier" en haut de la fenêtre (certains systèmes/gestionnaires
        # de fenêtres affichent mal les menus, donc ces actions sont dupliquées
        # ici sous forme de boutons pour être sûr qu'elles soient visibles).
        file_bar = tk.Frame(parent, bg=PALETTE["panel"])
        file_bar.pack(fill="x", padx=10, pady=(0, 10))
        tk.Label(file_bar, text="Projet :", bg=PALETTE["panel"], fg=PALETTE["parchment"]).pack(side="left", padx=(8, 6))
        tk.Button(file_bar, text="📄 Nouveau", command=self.new_project).pack(side="left", padx=3, pady=6)
        tk.Button(file_bar, text="📂 Ouvrir…", command=self.open_project).pack(side="left", padx=3, pady=6)
        tk.Button(file_bar, text="💾 Enregistrer", command=self.save_project,
                  bg=PALETTE["gold"], fg=PALETTE["ink"], activebackground=PALETTE["gold"]).pack(side="left", padx=3, pady=6)
        tk.Button(file_bar, text="Enregistrer sous…", command=self.save_project_as).pack(side="left", padx=3, pady=6)
        tk.Button(file_bar, text="⬆ Exporter le jeu terminé…", command=self.export_game).pack(side="left", padx=3, pady=6)

        self.save_status_label = tk.Label(file_bar, text="", bg=PALETTE["panel"], fg=PALETTE["gold"],
                                           font=("Georgia", 9, "italic"))
        self.save_status_label.pack(side="right", padx=10)

        paned = tk.PanedWindow(parent, orient="horizontal", sashwidth=6, bg=PALETTE["bg"])
        paned.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # ---- panneau gauche : liste des passages ----
        left = tk.Frame(paned, bg=PALETTE["panel"])
        paned.add(left, width=340)

        tk.Label(left, text="Passages de l'histoire", bg=PALETTE["panel"], fg=PALETTE["gold"],
                 font=("Georgia", 12, "bold")).pack(pady=(8, 4))

        self.tree = ttk.Treeview(left, columns=("id", "apercu", "statut"), show="headings", height=20)
        self.tree.heading("id", text="N°")
        self.tree.heading("apercu", text="Aperçu")
        self.tree.heading("statut", text="Statut")
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("apercu", width=180)
        self.tree.column("statut", width=70, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=8)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        btns = tk.Frame(left, bg=PALETTE["panel"])
        btns.pack(fill="x", pady=8, padx=8)
        tk.Button(btns, text="+ Nouveau passage", command=self.create_passage).pack(fill="x", pady=2)
        tk.Button(btns, text="Dupliquer", command=self.duplicate_current).pack(fill="x", pady=2)
        tk.Button(btns, text="Supprimer", command=self.delete_current).pack(fill="x", pady=2)

        # ---- panneau droit : édition du passage sélectionné ----
        right = tk.Frame(paned, bg=PALETTE["panel"])
        paned.add(right)
        self.editor_frame = tk.Frame(right, bg=PALETTE["panel"])
        self.editor_frame.pack(fill="both", expand=True, padx=12, pady=8)

    def _on_title_change(self):
        self.project.title = self.title_var.get()
        self.mark_dirty()

    def mark_dirty(self):
        self.project.dirty = True

    # ---------------- liste des passages ----------------
    def refresh_passage_list(self):
        selected = self.current_pid
        self.tree.delete(*self.tree.get_children())
        for pid in sorted(self.project.passages.keys()):
            p = self.project.passages[pid]
            preview = p["text"].strip().replace("\n", " ")[:36] or "(vide)"
            statut = "Fin" if not p["choices"] else f"{len(p['choices'])} choix"
            self.tree.insert("", "end", iid=str(pid), values=(pid, preview, statut))
        if str(selected) in self.tree.get_children():
            self.tree.selection_set(str(selected))

    def _on_tree_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        pid = int(sel[0])
        # Le rafraîchissement de la liste (à chaque frappe dans le texte,
        # par exemple) resélectionne le passage courant, ce qui redéclenche
        # cet événement. Si le passage n'a pas réellement changé, on ne
        # reconstruit pas l'éditeur : sinon la zone de texte serait détruite
        # et recréée à chaque lettre tapée, coupant la saisie en cours.
        if pid != self.current_pid:
            self.open_passage_editor(pid)

    # ---------------- actions sur les passages ----------------
    def create_passage(self):
        pid = self.project.new_passage()
        self.refresh_passage_list()
        self.select_passage(pid)

    def duplicate_current(self):
        new_id = self.project.duplicate_passage(self.current_pid)
        if new_id:
            self.refresh_passage_list()
            self.select_passage(new_id)

    def delete_current(self):
        if self.current_pid == 1:
            messagebox.showwarning("Impossible",
                                    "Le passage n°1 est le point de départ de l'histoire : il ne peut pas être supprimé.")
            return
        if messagebox.askyesno("Confirmer",
                                f"Supprimer le passage n°{self.current_pid} ?\n"
                                "Les choix qui y menaient seront à réattribuer."):
            self.project.delete_passage(self.current_pid)
            self.refresh_passage_list()
            self.select_passage(1)

    def select_passage(self, pid):
        self.current_pid = pid
        self.tree.selection_set(str(pid))
        self.tree.see(str(pid))
        self.open_passage_editor(pid)

    # ---------------- édition d'un passage ----------------
    def open_passage_editor(self, pid):
        self.current_pid = pid
        for w in self.editor_frame.winfo_children():
            w.destroy()
        self.choice_rows = []
        p = self.project.passages[pid]

        header_text = f"Passage n° {pid}" + ("  (point de départ)" if pid == 1 else "")
        tk.Label(self.editor_frame, text=header_text, bg=PALETTE["panel"], fg=PALETTE["gold"],
                 font=("Georgia", 14, "bold")).pack(anchor="w")

        tk.Label(self.editor_frame, text="Texte lu par le joueur à ce moment de l'histoire :",
                 bg=PALETTE["panel"], fg=PALETTE["parchment"]).pack(anchor="w", pady=(10, 2))

        text_frame = tk.Frame(self.editor_frame)
        text_frame.pack(fill="x")
        self.text_widget = tk.Text(text_frame, height=8, wrap="word", bg=PALETTE["parchment"], fg=PALETTE["ink"])
        self.text_widget.pack(side="left", fill="both", expand=True)
        scroll = tk.Scrollbar(text_frame, command=self.text_widget.yview)
        scroll.pack(side="right", fill="y")
        self.text_widget.configure(yscrollcommand=scroll.set)
        self.text_widget.insert("1.0", p["text"])
        self.text_widget.bind("<KeyRelease>", self._on_text_change)

        # -- image --
        img_frame = tk.Frame(self.editor_frame, bg=PALETTE["panel"])
        img_frame.pack(fill="x", pady=(12, 4))
        tk.Label(img_frame, text="Image du passage (facultative) :",
                 bg=PALETTE["panel"], fg=PALETTE["parchment"]).pack(anchor="w")

        preview_row = tk.Frame(img_frame, bg=PALETTE["panel"])
        preview_row.pack(anchor="w", pady=4)
        self.image_label = tk.Label(preview_row, bg="black", width=25, height=10)
        self.image_label.pack(side="left", padx=(0, 10))
        self._refresh_image_preview(p.get("image"))

        img_btns = tk.Frame(preview_row, bg=PALETTE["panel"])
        img_btns.pack(side="left")
        tk.Button(img_btns, text="Choisir une image sur mon ordinateur…", command=self.choose_image).pack(fill="x", pady=2)
        tk.Button(img_btns, text="Réutiliser une image déjà importée…", command=self.reuse_image).pack(fill="x", pady=2)
        tk.Button(img_btns, text="Retirer l'image", command=self.remove_image).pack(fill="x", pady=2)

        # -- choix --
        tk.Label(self.editor_frame, text="Choix proposés au joueur (aucun choix = fin de l'histoire) :",
                 bg=PALETTE["panel"], fg=PALETTE["parchment"]).pack(anchor="w", pady=(14, 2))

        self.choices_container = tk.Frame(self.editor_frame, bg=PALETTE["panel"])
        self.choices_container.pack(fill="x")
        for key, choice in p["choices"].items():
            self._add_choice_row(key, choice)

        tk.Button(self.editor_frame, text="+ Ajouter un choix", command=self.add_choice).pack(anchor="w", pady=(6, 4))
        tk.Button(self.editor_frame, text="▶ Tester l'histoire depuis ce passage",
                  command=lambda: self.play_test(pid)).pack(anchor="w", pady=(12, 0))

    def _add_choice_row(self, key, choice):
        row = ChoiceRow(self.choices_container, self, self.current_pid, key, choice)
        self.choice_rows.append(row)

    def add_choice(self):
        self.project.add_choice(self.current_pid)
        self.open_passage_editor(self.current_pid)
        self.refresh_passage_list()

    def _on_text_change(self, event=None):
        self.project.passages[self.current_pid]["text"] = self.text_widget.get("1.0", "end-1c")
        self.mark_dirty()
        self.refresh_passage_list()

    # ---------------- images ----------------
    def choose_image(self):
        path = filedialog.askopenfilename(
            title="Choisir une image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.webp"), ("Tous les fichiers", "*.*")],
        )
        if not path:
            return
        if not self.project.project_file:
            messagebox.showinfo(
                "Enregistre d'abord ton projet",
                "Enregistre le projet (menu Fichier > Enregistrer) avant d'ajouter des images :\n"
                "cela crée le dossier où elles seront rangées.",
            )
            return
        filename = self.project.import_image(path)
        self.project.passages[self.current_pid]["image"] = filename
        self.mark_dirty()
        self._refresh_image_preview(filename)

    def reuse_image(self):
        images = self.project.list_project_images()
        if not images:
            messagebox.showinfo("Aucune image", "Aucune image n'a encore été importée dans ce projet.")
            return
        choice = simpledialog.askstring(
            "Réutiliser une image",
            "Images déjà importées :\n" + "\n".join(images) + "\n\nTape le nom exact du fichier à utiliser :",
        )
        if choice and choice in images:
            self.project.passages[self.current_pid]["image"] = choice
            self.mark_dirty()
            self._refresh_image_preview(choice)

    def remove_image(self):
        self.project.passages[self.current_pid]["image"] = None
        self.mark_dirty()
        self._refresh_image_preview(None)

    def _refresh_image_preview(self, filename):
        path = self.project.image_path(filename) if filename else None
        thumb = load_thumbnail(path)
        self.image_thumb_ref = thumb
        if thumb:
            self.image_label.configure(image=thumb, text="")
        else:
            self.image_label.configure(image="", text="(aucune image)", fg="white")

    # ---------------- validation ----------------
    def show_validation(self):
        issues = self.project.validate()
        win = tk.Toplevel(self.root)
        win.title("Vérification de l'histoire")
        win.geometry("560x400")
        text = tk.Text(win, wrap="word")
        text.pack(fill="both", expand=True, padx=10, pady=10)
        if issues:
            text.insert("1.0", "\n".join(issues))
        else:
            text.insert("1.0", "✅ Aucun souci détecté : tous les choix mènent vers un passage existant, "
                                "et tous les passages sont accessibles depuis le début.")
        text.configure(state="disabled")

    # ---------------- projet : nouveau / ouvrir / enregistrer ----------------
    def new_project(self):
        if messagebox.askyesno("Nouveau projet",
                                "Créer une nouvelle histoire ?\nLes modifications non enregistrées seront perdues."):
            self.project = CyoaProject()
            self.title_var.set(self.project.title)
            self.refresh_passage_list()
            self.select_passage(1)

    def open_project(self):
        path = filedialog.askopenfilename(
            title="Ouvrir un projet CYOA",
            filetypes=[("Projet CYOA", "*.cyoa.json"), ("Tous les fichiers", "*.*")],
        )
        if not path:
            return
        self.project = CyoaProject.load(path)
        self.title_var.set(self.project.title)
        self.refresh_passage_list()
        self.select_passage(1)

    def save_project(self):
        if not self.project.project_file:
            self.save_project_as()
            return
        self.project.save(self.project.project_file)
        if hasattr(self, "save_status_label"):
            self.save_status_label.configure(text="✓ Enregistré")
            self.root.after(2500, lambda: self.save_status_label.configure(text=""))
        else:
            messagebox.showinfo("Enregistré", "Le projet a été enregistré.")

    def save_project_as(self):
        path = filedialog.asksaveasfilename(
            title="Enregistrer le projet sous…", defaultextension=".cyoa.json",
            filetypes=[("Projet CYOA", "*.cyoa.json")],
        )
        if not path:
            return
        self.project.save(path)
        messagebox.showinfo("Enregistré", f"Projet enregistré :\n{path}")

    def export_game(self):
        issues = self.project.validate()
        blocking = [i for i in issues if i.startswith("⛔") or "ne mène nulle part" in i]
        if blocking:
            proceed = messagebox.askyesno(
                "Histoire incomplète",
                "Des choix ne mènent nulle part ou pointent vers un passage inexistant :\n\n"
                + "\n".join(blocking[:8])
                + "\n\nExporter quand même ?",
            )
            if not proceed:
                return
        out_dir = filedialog.askdirectory(title="Choisir le dossier où créer le jeu terminé")
        if not out_dir:
            return
        self.project.export_game(out_dir, theme_name=self.theme_name)
        messagebox.showinfo("Jeu exporté",
                             f"Le jeu a été généré dans :\n{out_dir}\n\n"
                             f"Thème appliqué : {THEMES[self.theme_name]['label']}.\n"
                             "Lance lecteur_cyoa.py dans ce dossier pour y jouer.")

    # ---------------- mode test ----------------
    def play_test(self, start_pid):
        PlayTestWindow(self.root, self.project, start_pid)

    # ---------------- rendu réel (lecteur_cyoa.py) ----------------
    def render_preview(self):
        """Exporte l'histoire en cours (même non enregistrée, même
        incomplète) dans un dossier temporaire, puis lance lecteur_cyoa.py
        dans ce dossier comme un vrai jeu exporté : c'est un aperçu fidèle
        au rendu final, indépendant de la fenêtre de l'éditeur."""
        try:
            tmp_dir = tempfile.mkdtemp(prefix="cyoa_rendu_")
            self.project.export_game(tmp_dir, theme_name=self.theme_name)
            # export_game() écrit toujours lecteur_cyoa.py dans tmp_dir (en
            # copiant le fichier externe s'il le trouve, sinon en utilisant
            # la copie embarquée dans cyoa_creator.py) : ce chemin existe
            # donc forcément à ce stade.
            reader_path = os.path.join(tmp_dir, "lecteur_cyoa.py")
            subprocess.Popen([sys.executable, reader_path], cwd=tmp_dir)
        except Exception as e:
            messagebox.showerror("Rendu impossible", f"Impossible de lancer le rendu :\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CyoaCreatorApp(root)
    root.mainloop()
