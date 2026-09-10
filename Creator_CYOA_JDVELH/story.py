# -*- coding: utf-8 -*-
"""Histoire générée avec cyoa_creator.py."""
import os

TITLE = "Exemple : Le Phare Oublié"
THEME = "grimoire"

current_dir = os.path.dirname(__file__)

story = {
    1: {
        "text": "Ceci est un exemple d'histoire pour te montrer comment fonctionne l'outil. Tu es gardien d'un phare abandonné, sur une île balayée par la tempête. Un bruit sourd résonne depuis la cave.\n\n(Remarque : cet exemple n'a pas d'image, mais tu peux en ajouter une à n'importe quel passage avec le bouton « Choisir une image sur mon ordinateur… ».)",
        "image": None,
        "choices": {
            "1": {"text": "Descendre voir ce qui fait ce bruit", "next_part": 2},
            "2": {"text": "Rester en haut et attendre le matin", "next_part": 3},
            "3": {"text": "Sortir affronter la tempête dehors", "next_part": 4},
        },
    },
    2: {
        "text": "Tu descends les marches humides. Une vieille caisse s'est renversée : ce n'était qu'un chat errant, réfugié de l'orage.",
        "image": None,
        "choices": {
            "1": {"text": "Adopter le chat pour la nuit", "next_part": 5},
            "2": {"text": "Le laisser tranquille et remonter", "next_part": 6},
        },
    },
    3: {
        "text": "Tu remontes te coucher, bercé par le vent. Au matin, la tempête est passée, et le mystère du bruit reste entier.\n\n✦ Fin de ce chemin ✦",
        "image": None,
        "choices": {
        },
    },
    4: {
        "text": "Le vent te plaque contre la porte du phare. Tu comprends vite qu'il vaut mieux ne pas s'attarder dehors et tu rentres en hâte.",
        "image": None,
        "choices": {
            "1": {"text": "Retourner enquêter sur le bruit", "next_part": 2},
        },
    },
    5: {
        "text": "Le chat ronronne à tes pieds toute la nuit. Tu passes une nuit plus paisible que prévu, malgré la tempête.\n\n✦ Fin de ce chemin ✦",
        "image": None,
        "choices": {
        },
    },
    6: {
        "text": "Tu remontes, laissant le chat à son sort. Le lendemain, il a disparu, et tu te demandes s'il n'était pas venu te prévenir de quelque chose.\n\n✦ Fin de ce chemin ✦",
        "image": None,
        "choices": {
        },
    },
}


def get_story_part(part_id):
    """Retourne le texte, les choix et l'image du passage demandé."""
    part = story.get(part_id)
    if part:
        return part["text"], part["choices"], part.get("image")
    return None, None, None


def get_next_part(current_part_id, choice_key):
    """Retourne l'identifiant du passage suivant selon le choix fait."""
    part = story.get(current_part_id)
    if part and choice_key in part["choices"]:
        return part["choices"][choice_key]["next_part"]
    return None
