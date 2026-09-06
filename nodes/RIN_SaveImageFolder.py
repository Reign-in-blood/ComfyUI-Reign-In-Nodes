#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

from ..Architecture import icons
import re
import os
import numpy as np
import folder_paths
from PIL import Image, PngImagePlugin

#------------------------------------------------#

class RIN_SaveImageFolder:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "folder_name": ("STRING", {"default": "my_folder"}),
                "image_name": ("STRING", {"default": "portrait"}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()

    OUTPUT_NODE = True
    CATEGORY = icons.get("MyNodes/Images")
    DESCRIPTION = "A simple image in folder saver"
    FUNCTION = "RIN_SaveImageFolder"

    def _next_index(self, save_dir, image_name):
        pattern = re.compile(
            rf"^{re.escape(image_name)}_(\d+)\.png$", re.IGNORECASE
        )
        max_index = 0

        for filename in os.listdir(save_dir):
            match = pattern.match(filename)
            if match:
                idx = int(match.group(1))
                max_index = max(max_index, idx)

        return max_index + 1

    def RIN_SaveImageFolder(self, images, folder_name, image_name, prompt=None, extra_pnginfo=None):
        output_dir = folder_paths.get_output_directory()
        save_dir = os.path.join(output_dir, folder_name)
        os.makedirs(save_dir, exist_ok=True)

        if images is None:
            return {"ui": {"images": []}}

        start_index = self._next_index(save_dir, image_name)
        ui_images = []

        for offset, img in enumerate(images):
            index = start_index + offset

            img_np = (img.cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)
            pil_img = Image.fromarray(img_np)

            filename = f"{image_name}_{index}.png"
            filepath = os.path.join(save_dir, filename)

            pnginfo = PngImagePlugin.PngInfo()
            if prompt is not None:
                pnginfo.add_text("prompt", str(prompt))
            if extra_pnginfo is not None:
                for k, v in extra_pnginfo.items():
                    pnginfo.add_text(str(k), str(v))

            pil_img.save(filepath, pnginfo=pnginfo)

            ui_images.append({
                "filename": filename,
                "subfolder": folder_name,
                "type": "output"
            })

        return {"ui": {"images": ui_images}}