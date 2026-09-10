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
