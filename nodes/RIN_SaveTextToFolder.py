#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

import os
import re
import logging
import folder_paths
from ..Architecture import icons

#------------------------------------------------#


def extract_scalar(value, default=None):
    """
    ComfyUI peut envoyer certains champs sous forme de liste
    si INPUT_IS_LIST = True.
    Cette fonction récupère proprement la valeur principale.
    """
    if isinstance(value, (list, tuple)):
        if len(value) == 0:
            return default
        return value[0]
    return value


def ensure_list(value):
    """
    Convertit une entrée texte simple ou multiple en liste.
    """
    if value is None:
        return []

    if isinstance(value, (list, tuple)):
        return list(value)

    return [value]


def sanitize_folder_name(folder_name):
    """
    Nettoie le nom du dossier tout en autorisant les sous-dossiers.
    Exemple :
    dataset/anima -> output/dataset/anima
    """
    folder_name = str(folder_name or "dataset").strip()
    folder_name = folder_name.replace("\\", "/").strip("/")

    parts = []

    for part in folder_name.split("/"):
        part = part.strip()

        if part in ("", ".", ".."):
            continue

        part = re.sub(r'[<>:"|?*]', "_", part)
        parts.append(part)

    if not parts:
        return "dataset"

    return os.path.join(*parts)


def sanitize_filename_prefix(filename_prefix):
    """
    Nettoie le préfixe du fichier texte.
    """
    filename_prefix = str(filename_prefix or "caption").strip()

    if not filename_prefix:
        filename_prefix = "caption"

    filename_prefix = re.sub(r'[\\/:*?"<>|]', "_", filename_prefix)

    return filename_prefix


def make_numbered_filename(filename_prefix, index):
    """
    Crée un nom de fichier selon le style Image Saver.

    Index 0  -> caption.txt
    Index 1  -> caption_1.txt
    Index 2  -> caption_2.txt
    Index 10 -> caption_10.txt
    """
    if index == 0:
        return f"{filename_prefix}.txt"

    return f"{filename_prefix}_{index}.txt"


def get_next_file_index(output_dir, filename_prefix):
    """
    Trouve le prochain index disponible.

    Si aucun fichier n'existe :
        caption.txt

    Si caption.txt existe déjà :
        caption_1.txt

    Si caption_1.txt existe déjà :
        caption_2.txt
    """
    if not os.path.isdir(output_dir):
        return 0

    max_index = -1

    base_filename = f"{filename_prefix}.txt"
    base_path = os.path.join(output_dir, base_filename)

    if os.path.isfile(base_path):
        max_index = max(max_index, 0)

    pattern = re.compile(
        rf"^{re.escape(filename_prefix)}_(\d+)\.txt$"
    )

    for filename in os.listdir(output_dir):
        match = pattern.match(filename)

        if match:
            try:
                index = int(match.group(1))
                max_index = max(max_index, index)
            except ValueError:
                pass

    return max_index + 1


def save_texts_to_folder(texts, output_dir, filename_prefix):
    """
    Sauvegarde une ou plusieurs captions en fichiers .txt.
    Incrémente automatiquement sans jamais écraser.
    """
    os.makedirs(output_dir, exist_ok=True)

    saved_files = []
    current_index = get_next_file_index(output_dir, filename_prefix)

    for text in texts:
        filename = make_numbered_filename(filename_prefix, current_index)
        file_path = os.path.join(output_dir, filename)

        while os.path.exists(file_path):
            current_index += 1
            filename = make_numbered_filename(filename_prefix, current_index)
            file_path = os.path.join(output_dir, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(str(text))

        saved_files.append(file_path)
        current_index += 1

    return saved_files


class RIN_SaveTextToFolder:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "texts": ("STRING", {
                    "multiline": True,
                    "forceInput": True,
                    "default": "",
                    "tooltip": "Texte ou liste de textes à sauvegarder en fichiers .txt."
                }),

                "folder_name": ("STRING", {
                    "default": "dataset",
                    "tooltip": "Nom du dossier dans ComfyUI/output/. Exemple : dataset ou dataset/anima"
                }),

                "filename_prefix": ("STRING", {
                    "default": "caption",
                    "tooltip": "Préfixe des fichiers texte sauvegardés."
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("texts",)

    OUTPUT_NODE = True
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (True,)

    FUNCTION = "SaveTextToFolder"
    CATEGORY = icons.get("MyNodes/Utils")

    def SaveTextToFolder(self, texts, folder_name, filename_prefix):
        folder_name = extract_scalar(folder_name, "dataset")
        filename_prefix = extract_scalar(filename_prefix, "caption")

        folder_name = sanitize_folder_name(folder_name)
        filename_prefix = sanitize_filename_prefix(filename_prefix)

        output_dir = os.path.join(
            folder_paths.get_output_directory(),
            folder_name
        )

        text_list = ensure_list(texts)

        saved_files = save_texts_to_folder(
            texts=text_list,
            output_dir=output_dir,
            filename_prefix=filename_prefix
        )

        logging.info(f"Saved {len(saved_files)} text file(s) to {output_dir}")

        return (text_list,)