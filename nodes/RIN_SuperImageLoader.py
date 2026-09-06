#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

from ..Architecture import icons

from io import BytesIO
from PIL import Image, ImageOps, ImageSequence

import os
import torch
import hashlib
import numpy as np
import folder_paths
import node_helpers

#------------------------------------------------#

class RIN_SuperImageLoader:

    @classmethod
    def INPUT_TYPES(cls):
        
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        files = folder_paths.filter_files_content_types(files, ["image"])  # ne montre que les images

        return {
            "required": {
                # Annotated filepath + support d'upload (comme LoadImage)
                "image": (sorted(files), {"image_upload": True}),
            },
            "optional": {
                # Si fourni, on encode l'image en latent en sortie
                "vae": ("VAE",),
            },
        }


    RETURN_TYPES = ("IMAGE", "INT", "INT", "MASK", "LATENT")
    RETURN_NAMES = ("image", "width", "height", "mask", "latent")
    CATEGORY = icons.get("MyNodes/Images")
    FUNCTION = "load_image"

    def _open_image_any(self, annotated_or_upload):
        
        if isinstance(annotated_or_upload, str):
            image_path = folder_paths.get_annotated_filepath(annotated_or_upload)
            img = node_helpers.pillow(Image.open, image_path)
            return img

        # Upload: ComfyUI peut fournir un dict {"image": <PIL.Image | bytes | file-like>, "filename": "..."}
        if isinstance(annotated_or_upload, dict) and "image" in annotated_or_upload:
            payload = annotated_or_upload["image"]
            if isinstance(payload, Image.Image):
                return payload
            if isinstance(payload, (bytes, bytearray)):
                return Image.open(BytesIO(payload))
            # file-like
            return Image.open(payload)

        raise ValueError("Format d’entrée 'image' non reconnu (ni chemin annoté, ni upload).")

    def load_image(self, image, vae=None):
        img = self._open_image_any(image)

        output_images = []
        output_masks = []
        w, h = None, None

        excluded_formats = ['MPO']  # comme l'origine

        # Itération frames (GIF/WEBP animés, etc.)
        for frame in ImageSequence.Iterator(img):
            frame = node_helpers.pillow(ImageOps.exif_transpose, frame)

            # Gestion du mode 'I' (comme l'origine)
            if frame.mode == 'I':
                frame = frame.point(lambda i: i * (1 / 255))

            rgb = frame.convert("RGB")

            # Fixe la taille de référence sur le premier frame accepté
            if len(output_images) == 0:
                w, h = rgb.size

            # Ignore les frames de taille différente
            if rgb.size != (w, h):
                continue

            # IMAGE -> [1, H, W, 3], float32, 0..1
            arr = np.array(rgb).astype(np.float32) / 255.0
            tensor_img = torch.from_numpy(arr)[None, ...]  # [1, H, W, 3]

            # MASK (même logique que le loader natif: 1 - alpha)
            if 'A' in frame.getbands():
                mask_np = np.array(frame.getchannel('A')).astype(np.float32) / 255.0
                mask = 1.0 - torch.from_numpy(mask_np)
            elif frame.mode == 'P' and 'transparency' in frame.info:
                mask_np = np.array(frame.convert('RGBA').getchannel('A')).astype(np.float32) / 255.0
                mask = 1.0 - torch.from_numpy(mask_np)
            else:
                # masque vide par défaut (comme l'origine) -> 64x64 sur CPU
                mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")

            output_images.append(tensor_img)         # [1, H, W, 3]
            output_masks.append(mask.unsqueeze(0))   # [1, H, W]

        # Empilement batch (comme l'origine)
        if len(output_images) > 1 and (img.format not in excluded_formats):
            output_image = torch.cat(output_images, dim=0)  # [B, H, W, 3]
            output_mask = torch.cat(output_masks, dim=0)    # [B, 1, H, W]
        else:
            output_image = output_images[0]                 # [1, H, W, 3]
            output_mask = output_masks[0]                   # [1, H, W]

        # Encodage VAE -> LATENT (si fourni)
        if vae is not None:
            # vae.encode attend [B, H, W, 3] en 0..1 (conforme à ce qu'on a)
            latent_samples = vae.encode(output_image)  # [B, C, h//8, w//8]
            latent = {"samples": latent_samples}
        else:
            # Dictionnaire LATENT vide compatible (permet de brancher optionnellement)
            latent = {"samples": torch.empty(0)}

        # width/height : dimensions du premier frame retenu
        width = int(w)
        height = int(h)

        return (output_image, width, height, output_mask, latent)

    @classmethod
    def IS_CHANGED(cls, image, vae=None):
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, 'rb') as f:
            m.update(f.read())
        # Inclure l'ID du VAE dans le hash permet de relancer si le VAE change (optionnel)
        if vae is not None:
            m.update(str(id(vae)).encode('utf-8'))
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(cls, image, vae=None):
        if not folder_paths.exists_annotated_filepath(image):
            return "Invalid image file: {}".format(image)
        return True