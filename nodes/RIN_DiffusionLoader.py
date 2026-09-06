#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

import torch
import folder_paths
import comfy.sd

from ..Architecture import icons

#------------------------------------------------#
# Helpers                                        #
#------------------------------------------------#

def get_full_diffusion_model_path(model_name):

    if hasattr(folder_paths, "get_full_path_or_raise"):
        return folder_paths.get_full_path_or_raise("diffusion_models", model_name)

    path = folder_paths.get_full_path("diffusion_models", model_name)
    if path is None:
        raise FileNotFoundError(f"Diffusion model introuvable : {model_name}")
    return path


def format_model_name(model_name):

    return str(model_name).strip().replace("/", "\\")

#------------------------------------------------#
# Node                                           #
#------------------------------------------------#

class RIN_LoadDiffusionModel:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "unet_name": (
                    folder_paths.get_filename_list("diffusion_models"),
                ),
                "weight_dtype": (
                    [
                        "default",
                        "fp8_e4m3fn",
                        "fp8_e4m3fn_fast",
                        "fp8_e5m2",
                    ],
                    {
                        "advanced": True,
                    },
                ),
            },
        }

    RETURN_TYPES = (
        "MODEL",
        "STRING",
    )

    RETURN_NAMES = (
        "MODEL",
        "MODEL_NAME",
    )

    FUNCTION = "LoadDiffusionModel"
    CATEGORY = icons.get("MyNodes/Utils")
    DESCRIPTION = "Load a diffusion model and output its model name."

    def LoadDiffusionModel(
        self,
        unet_name,
        weight_dtype,
    ):
        model_options = {}

        if weight_dtype == "fp8_e4m3fn":
            model_options["dtype"] = torch.float8_e4m3fn

        elif weight_dtype == "fp8_e4m3fn_fast":
            model_options["dtype"] = torch.float8_e4m3fn
            model_options["fp8_optimizations"] = True

        elif weight_dtype == "fp8_e5m2":
            model_options["dtype"] = torch.float8_e5m2

        unet_path = get_full_diffusion_model_path(unet_name)

        model = comfy.sd.load_diffusion_model(
            unet_path,
            model_options=model_options,
        )

        model_name = format_model_name(unet_name)

        return (
            model,
            model_name,
        )