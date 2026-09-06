#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

import json
import folder_paths
import comfy.utils
import comfy.sd

from ..Architecture import icons

#------------------------------------------------#
# Types                                          #
#------------------------------------------------#

RIN_LORA_STACK_TYPE = "RIN_LORA_STACK"

#------------------------------------------------#
# Helpers                                        #
#------------------------------------------------#

def get_full_lora_path(lora_name):
    """
    Compatible avec les versions récentes et moins récentes de ComfyUI.
    """
    if hasattr(folder_paths, "get_full_path_or_raise"):
        return folder_paths.get_full_path_or_raise("loras", lora_name)

    path = folder_paths.get_full_path("loras", lora_name)
    if path is None:
        raise FileNotFoundError(f"LoRA introuvable : {lora_name}")
    return path


def normalize_lora_stack(last_lora):

    if last_lora is None:
        return []

    if isinstance(last_lora, list):
        cleaned = []

        for item in last_lora:
            if isinstance(item, str) and item.strip():
                cleaned.append(item.strip())
            elif isinstance(item, dict) and item.get("name"):
                cleaned.append(str(item["name"]).strip())

        return cleaned

    if isinstance(last_lora, str):
        value = last_lora.strip()

        if not value:
            return []

        try:
            parsed = json.loads(value)
            return normalize_lora_stack(parsed)
        except Exception:
            return [value]

    return []

#------------------------------------------------#
# Node                                           #
#------------------------------------------------#

class RIN_LoraLoaderModel:

    def __init__(self):
        self.loaded_lora = None

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "lora_name": (folder_paths.get_filename_list("loras"),),
                "strength_model": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": -100.0,
                        "max": 100.0,
                        "step": 0.01,
                    },
                ),
            },
            "optional": {
                "last_lora": (
                    RIN_LORA_STACK_TYPE,
                    {
                        "forceInput": True,
                    },
                ),
            },
        }

    RETURN_TYPES = (
        "MODEL",
        RIN_LORA_STACK_TYPE,
    )

    RETURN_NAMES = (
        "MODEL",
        "NEXT_LORA",
    )

    FUNCTION = "LoraLoaderModel"
    CATEGORY = icons.get("MyNodes/Utils")
    DESCRIPTION = "Load a LoRA on MODEL only and stack its name for RIN image & prompt metadata."

    def LoraLoaderModel(
        self,
        model,
        lora_name,
        strength_model,
        last_lora=None,
    ):
        lora_stack = normalize_lora_stack(last_lora)

        if strength_model == 0:
            return (
                model,
                lora_stack,
            )

        lora_path = get_full_lora_path(lora_name)

        lora = None
        lora_metadata = None

        if self.loaded_lora is not None:
            if self.loaded_lora[0] == lora_path:
                lora = self.loaded_lora[1]
                lora_metadata = self.loaded_lora[2]
            else:
                self.loaded_lora = None

        if lora is None:
            try:
                lora, lora_metadata = comfy.utils.load_torch_file(
                    lora_path,
                    safe_load=True,
                    return_metadata=True,
                )
            except TypeError:
                lora = comfy.utils.load_torch_file(
                    lora_path,
                    safe_load=True,
                )
                lora_metadata = None

            self.loaded_lora = (
                lora_path,
                lora,
                lora_metadata,
            )

        try:
            model_lora, _ = comfy.sd.load_lora_for_models(
                model,
                None,
                lora,
                strength_model,
                0,
                lora_metadata=lora_metadata,
            )
        except TypeError:
            model_lora, _ = comfy.sd.load_lora_for_models(
                model,
                None,
                lora,
                strength_model,
                0,
            )

        next_lora = lora_stack + [lora_name]

        return (
            model_lora,
            next_lora,
        )