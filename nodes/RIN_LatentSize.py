#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

from ..Architecture import icons

#------------------------------------------------#
# Node                                           #
#------------------------------------------------#

class RIN_LatentSize:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "samples": ("LATENT", {"tooltip": "The latent to be decoded."}),
                "vae": ("VAE", {"tooltip": "The VAE model used for decoding the latent."}),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("image", "width", "height")
    FUNCTION = "LatentSize"
    CATEGORY = icons.get("MyNodes/Images")

    def LatentSize(self, vae, samples):
        if samples is None:
            raise ValueError("RIN_LatentSize: input 'samples' is None. Please connect a LATENT input.")

        if vae is None:
            raise ValueError("RIN_LatentSize: input 'vae' is None. Please connect a VAE input.")

        latent = samples["samples"]

        if latent.is_nested:
            latent = latent.unbind()[0]

        images = vae.decode(latent)

        if len(images.shape) == 5:
            images = images.reshape(
                -1,
                images.shape[-3],
                images.shape[-2],
                images.shape[-1]
            )

        height = int(images.shape[1])
        width = int(images.shape[2])

        return (images, width, height)