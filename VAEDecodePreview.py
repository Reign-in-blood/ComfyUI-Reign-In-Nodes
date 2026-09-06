#from .Architecture import icons
#
#class VAEDecodePreview:
#   @classmethod
#   def INPUT_TYPES(s):
#      return {
#         "required": {
#            "samples": ("LATENT", ),
#            "vae": ("VAE", )
#         }
#      }
#
#   RETURN_TYPES = ("IMAGE",)
#   RETURN_NAME = ("image",)
#   FUNCTION = "RIN_vaedecode00000000"
#   CATEGORY = icons.get("MyNodes/VAE")
#
#   def RIN_vaedecode(self, vae, samples):
#      return (vae.decode(samples["samples"]), )

from .Architecture import icons

import numpy as np
from PIL import Image

class RIN_LatentImagePreview:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "latent": ("LATENT",),
                "vae": ("VAE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "RIN_LatentImagePreview"
    OUTPUT_NODE = True
    CATEGORY = icons.get("MyNodes/Images")

    def RIN_LatentImagePreview(self, latent, vae):
        # Décodage normal
        image = vae.decode(latent["samples"])
        
        # Génération de la preview
        preview = self.generate_preview(image)
        
        return {
            "ui": {"images": [preview]},  # Affichage dans l'interface
            "result": (image,),           # Sortie pour le traitement suivant
        }

    def generate_preview(self, image_tensor):
        """Convertit le tensor en image PIL avec ratio original (max 512px)"""
        # Conversion tensor -> numpy
        image_np = 255. * image_tensor.cpu().numpy()
        image_np = np.clip(image_np, 0, 255).astype(np.uint8)
        
        # Formatage BCHW -> BHWC si nécessaire
        if len(image_np.shape) == 4:
            image_np = image_np.transpose(0, 2, 3, 1)
        
        # Sélection de la première image du batch
        if image_np.shape[0] > 1:
            image_np = image_np[0]
        
        # Création de l'image PIL
        img = Image.fromarray(image_np.squeeze())
        
        # Redimensionnement en conservant le ratio (côté le plus long = 512px)
        original_width, original_height = img.size
        max_size = 512
        
        if original_width > original_height:
            new_width = max_size
            new_height = int(max_size * original_height / original_width)
        else:
            new_height = max_size
            new_width = int(max_size * original_width / original_height)
            
        img = img.resize((new_width, new_height), Image.LANCZOS)
        
        return img