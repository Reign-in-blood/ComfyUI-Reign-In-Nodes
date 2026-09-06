from .Architecture import icons

import torch
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "comfy"))

import comfy.model_management

MAX_RESOLUTION=16384

class FLUXSizeLoader:
   
   def __init__(self):
      self.device = comfy.model_management.intermediate_device()

   @classmethod
   def INPUT_TYPES(s):
      return {"required": {
         "resolution": ([
            "320x320   [1:1] S",
            "768x768   [1:1] M",
            "1024x1024 [1:1] L",
            "1280x1280 [1:1] XL",
            "1408x1408 [1:1] UHD",
            "384x256   [3:2] S",
            "1152x768  [3:2] M",
            "1216x832  [3:2] L",
            "1728x1152 [3:2] XL",
            "448x320   [4:3] S",
            "1024x768  [4:3] M",
            "1152x896  [4:3] L",
            "1664x1216 [4:3] XL",
            "256x384   [2:3] S",
            "768x1152  [2:3] M",
            "832x1216  [2:3] L",
            "1152x1728 [2:3] XL",
            "320x448   [3:4] S",
            "768x1024  [3:4] M",
            "896x1152  [3:4] L",
            "1216x1664 [3:4] XL",
            "448x256   [16:9] S",
            "1344x768  [16:9] M",
            "1920x1088 [16:9] L",
            "576x256   [21:9] S",
            "1536x640  [21:9] M",
            "2176x960  [21:9] L",
            "256x448   [9:16] S",
            "768x1344  [9:16] M",
            "1088x1920 [9:16] L",
            "1152x2560 [9:16] XL",
            "256x576   [9:21] S",
            "640x1536  [9:21] M",
            "960x2176  [9:21] L",
         ],
            {"default": "832x1216  [2:3] L"}),
         "batch_size": ("INT", {"default": 1, "min": 1, "max": 4096})
      }}

   RETURN_TYPES = ("LATENT","INT","INT")
   RETURN_NAMES = ("Latent", "width", "height")
   FUNCTION = "MON_size_latent_loader"
   CATEGORY = icons.get("MyNodes/Utils")
   
   def MON_size_latent_loader(self, resolution, batch_size=1):
      width, height = resolution.split(" ")[0].split("x")
      width = int(width)
      height = int(height)
      latent = torch.zeros([batch_size, 4, height // 8, width // 8], device=self.device)
      return ({"samples":latent}, width, height,)

#Prompt outputs failed validation:
#FLUX Size Loader:
#- Value not in list: resolution: '832x1216 (0.68)' not in (list of length 34)