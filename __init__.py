from .CFG_Steps import *
from .nodes.BusCan import *
from .nodes.ImageTune import *
from .nodes.RIN_Slider import *
from .nodes.RIN_Bridge import *
from .SamplerScheduler import *
from .ConcatTexte import *
from .MyTextReplace import MyTextReplace
from .SDXLSizeLoader import SDXLSizeLoader
from .FLUXSizeLoader import FLUXSizeLoader
from .Noise_generator import MON_PlasmaNoise
from .Noise_generator import MON_Random_Noise
from .ImageChecker import ImagePresenceChecker
from .SimpleStringNode import SimpleStringNode
from .VAEDecodePreview import *
from .PromptTextOutput import *
from .Reign_Imagereroute import Reign_Imagereroute
from .nodes.NearestSDXLResolution import *
from .NearestFLUXResolution import NearestFLUXResolution
from .nodes.RIN_FluxPromptGuidance import *
from .nodes.RIN_ImageSizePicker import *
from .nodes.RIN_SuperImageLoader import *
from .nodes.RIN_AnySwitch2 import *
from .nodes.RIN_RotateImage import *
from .nodes.RIN_TextAppend import *
from .nodes.RIN_RandomEyes import *
from .nodes.RIN_RandomHair import *
from .nodes.RIN_RandomAnimalFeatures import *
from .nodes.RIN_RandomBreasts import *
from .nodes.RIN_RandomClothes import *
from .nodes.RIN_RandomBackground import *
from .nodes.RIN_RandomCFG import *
from .nodes.RIN_RandomCharacter import *
from .nodes.RIN_SetCondAreaSelector import *
from .nodes.RIN_AreaGen import *
from .nodes.RIN_SaveImageFolder import *
from .nodes.RIN_TokenCounter import *
from .nodes.RIN_LoraNameConverter import *
from .nodes.RIN_LatentSize import *
from .nodes.RIN_SaveTextToFolder import *
from .nodes.RIN_ImagePromptSaver import *
from .nodes.RIN_NodeInputValue import *
from .nodes.RIN_AnyConverter import *
from .nodes.RIN_LoraLoaderModel import *
from .nodes.RIN_DiffusionLoader import *
from .nodes.RIN_VAELoader import *


WEB_DIRECTORY = "./js"
__all__ = [
   "NODE_CLASS_MAPPINGS",
   "NODE_DISPLAY_NAME_MAPPINGS",
   "WEB_DIRECTORY",
]

NODE_CLASS_MAPPINGS = {
   "Image Tuner": ImageTune,
   "Save Images": RIN_SaveBridge,
   "Concat Text": RIN_ConcatText,
   "CFG Steps": RIN_CFGSteps,
   "Slider 1": RIN_Slider_1,
   "Slider 10": RIN_Slider_10,
   "Slider 100": RIN_Slider_100,
   "BusCan Basic": RIN_BusCan_Basic,
   "BusCan Basic +": RIN_BusCan_Plus,
   "BusCan Any 4": RIN_BusCanAny_4,
   "BusCan Any 6": RIN_BusCanAny_6,
   "BusCan Any 8": RIN_BusCanAny_8,
   "BusCan Any 12": RIN_BusCanAny_12,
   "Preview Images": RIN_PreviewBridge,
   "FLUX Size Loader": FLUXSizeLoader,
   "SDXL Size Loader": SDXLSizeLoader,
   "replace Prompt Text": MyTextReplace,
   "sampler scheduler": RIN_SamplerScheduler,
   "Simple String Node": SimpleStringNode,
   "Image Size Picker": RIN_ImageSizePicker,
   "Reign_Imagereroute": Reign_Imagereroute,
   "Plasma Noise Generator": MON_PlasmaNoise,
   "Random Noise Generator": MON_Random_Noise,
   "Super Image Loader": RIN_SuperImageLoader,
   "Prompt Text Output Pos": PromptTextOutputPos,
   "Latent Image Preview": RIN_LatentImagePreview,
   "Image Presence Checker": ImagePresenceChecker,
   "Prompt Text Output Neg": PromptTextOutputNeg,
   "Nearest SDXL Resolution": NearestSDXLResolution,
   "Nearest FLUX Resolution": NearestFLUXResolution,
   "Flux positiv Prompt Guidance": RIN_FluxGuidancePrompt,
   "Any Switch 2": RIN_AnySwitch2,
   "Rotate Image": RIN_RotateImage,
   "Text Append": RIN_TextAppend,
   "Random Eyes": RIN_RandomEyes,
   "Random Hair": RIN_RandomHair,
   "Random Animal Features": RIN_RandomAnimalFeatures,
   "Random Breasts": RIN_RandomBreasts,
   "Random Clothes": RIN_RandomClothes,
   "Random Background": RIN_RandomBackground,
   "Random CFG": RIN_RandomCFG,
   "RIN_RandomCharacter": RIN_RandomCharacter,
   "Cond Area Selector": RIN_SetCondAreaSelector,
   "Float Splitter": RIN_FloatSplitter,
   "Area Generator": RIN_AreaGen,
   "Save image Folder": RIN_SaveImageFolder,
   "Token Counter": RIN_TokenCounter,
   "Lora Name Converteur": RIN_LoraNameConverter,
   "Latent Size": RIN_LatentSize,
   "Prompt Parts Conditioning": RIN_PromptPartsConditioning,
   "Save Text To Folder": RIN_SaveTextToFolder,
   "Image & Prompt Saver": RIN_ImagePromptSaver,
   "Model Name Loader": RIN_ModelName,
   #"VAE Name Loader": RIN_VAEName,
   "Node Input Value": RIN_NodeInputValue,
   "Any Converter": RIN_AnyConverter,
   "Lora Loader Model": RIN_LoraLoaderModel,
   "Diffusion Loader Model": RIN_LoadDiffusionModel,
   "VAE Loader": RIN_VAELoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
   "CFG Steps": "🦁 | CFG Steps",
   "Slider 1": "🦁 | Slider 1",
   "Slider 10": "🦁 | Slider 10",
   "Slider 100": "🦁 | Slider 100",
   "Concat Text": "🦁 | Text Concat", 
   "Save Images": "🦁 | save images",
   "Image Tuner": "🦁 | Image Tuner",
   "BusCan Basic": "🦁 | BusCan Basic",
   "BusCan Basic +": "🦁 | BusCan Basic +",
   "BusCan Any 4": "🦁 | BusCan Any 4",
   "BusCan Any 6": "🦁 | BusCan Any 6",
   "BusCan Any 8": "🦁 | BusCan Any 8",
   "BusCan Any 12": "🦁 | BusCan Any 12",
   "Preview Images": "🦁 | Preview Images",
   "Image Size Picker": "🦁 | Image Size Picker",
   "Reign_Imagereroute": "🦁 | IMage Reroute",
   "replace Prompt Text": "🦁 | Replace Text",
   "FLUX Size Loader": "🦁 | FLUX Size Loader",
   "SDXL Size Loader": "🦁 | SDXL Size Loader",
   "sampler scheduler": "🦁 | Sampler Scheduler",
   "Simple String Node": "🦁 | Simple String Node",
   "Super Image Loader": "🦁 | Super Image Loader",
   "Prompt Text Output Neg": "🦁 | Negative Prompt",
   "Prompt Text Output Pos": "🦁 | Positive Prompt",
   "Latent Image Preview": "🦁 | Latent Image Preview",
   "Image Presence Checker": "🦁 | Image Presence Checker",
   "Plasma Noise Generator": "🦁 | Plasma Noise Generator",
   "Random Noise Generator": "🦁 | Random Noise Generator",
   "Nearest SDXL Resolution": "🦁 | Nearest SDXL Resolution",
   "Nearest FLUX Resolution": "🦁 | Nearest FLUX Resolution",
   "Flux positiv Prompt Guidance": "🦁 | Flux positiv Prompt Guidance",
   "Any Switch 2": "🦁 | Any Switch 2",
   "Rotate Image": "🦁 | Rotate Image",
   "Text Append": "🦁 | Text Append",
   "Random Eyes": "🦁 | Random Eyes",
   "Random Hair": "🦁 | Random Hair",
   "Random Animal Features": "🦁 | Random Animal Features",
   "Random Breasts": "🦁 | Random Breasts",
   "Random Clothes": "🦁 | Random Clothes",
   "Random Background": "🦁 | Random Background",
   "Random CFG": "🦁 | Random CFG",
   "RIN_RandomCharacter": "🦁 | Random Character",
   "Cond Area Selector": "🦁 | Cond Area Selector",
   "Float Splitter": "🦁 | Float Splitter",
   "Area Generator": "🦁 | Area Generator",
   "Save image Folder": "🦁 | Save image Folder",
   "Token Counter": "🦁 | Token Counter",
   "Lora Name Converteur": "🦁 | Lora Name Converteur",
   "Latent Size": "🦁 | Latent Size",
   "Prompt Parts Conditioning": "🦁 | Prompt Parts Conditioning",
   "Save Text To Folder": "🦁 | Save Text To Folder",
   "Image & Prompt Saver": "🦁 | Image & Prompt Saver",   
   "Model Name Loader": "🦁 | Model Name Loader",
   #"VAE Name Loader": "🦁 | VAE Name Loader",
   "Node Input Value": "🦁 | Node Input Value",
   "Any Converter": "🦁 | Any Converter",
   "Lora Loader Model": "🦁 | Lora Loader Model",
   "Diffusion Loader Model": "🦁 | Diffusion Loader Model",
   "VAE Loader": "🦁 | VAE Loader"
}

print("\033[91m------------------------------------------\033[0m")   
print("\033[95mReign-In-Nodes: \033[92mLoaded\033[0m")
print("\033[91m------------------------------------------\033[0m")