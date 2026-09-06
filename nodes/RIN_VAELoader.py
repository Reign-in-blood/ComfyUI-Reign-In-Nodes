#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

import folder_paths
import comfy.utils
import comfy.sd

from ..Architecture import icons

#------------------------------------------------#
# Helpers                                        #
#------------------------------------------------#

def get_vae_list():

    vaes = folder_paths.get_filename_list("vae")

    if not vaes:
        return ["No VAE Founded"]

    return vaes


def get_full_vae_path(vae_name):

    if hasattr(folder_paths, "get_full_path_or_raise"):
        return folder_paths.get_full_path_or_raise("vae", vae_name)

    vae_path = folder_paths.get_full_path("vae", vae_name)

    if vae_path is None:
        raise FileNotFoundError(f"VAE introuvable : {vae_name}")

    return vae_path

#------------------------------------------------#
# Node                                           #
#------------------------------------------------#

class RIN_VAELoader:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "vae_name": (get_vae_list(),),
            }
        }

    RETURN_TYPES = ("VAE", "STRING")
    RETURN_NAMES = ("VAE", "VAE_Name")

    FUNCTION = "load_vae"
    CATEGORY = icons.get("MyNodes/Utils")

    def load_vae(self, vae_name):
        if vae_name == "No VAE Founded":
            raise FileNotFoundError(
                "No VAE founded in folder ComfyUI/models/vae/"
            )

        vae_path = get_full_vae_path(vae_name)

        sd, metadata = comfy.utils.load_torch_file(
            vae_path,
            return_metadata=True
        )

        vae = comfy.sd.VAE(
            sd=sd,
            metadata=metadata
        )

        vae.throw_exception_if_invalid()

        if hasattr(comfy.sd, "load_vae_patcher"):
            vae.patcher.cached_patcher_init = (
                comfy.sd.load_vae_patcher,
                (vae_path, metadata, None)
            )

        return (vae, vae_name)