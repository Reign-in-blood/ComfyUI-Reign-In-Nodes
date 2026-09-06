#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

from typing import Any, Mapping
from ..Architecture import icons

#------------------------------------------------#

SDXL_SUPPORTED_RESOLUTIONS = [
    (1024, 1024, 1.0),
    (1152, 896, 1.2857142857142858),
    (896, 1152, 0.7777777777777778),
    (1216, 832, 1.4615384615384615),
    (832, 1216, 0.6842105263157895),
    (1344, 768, 1.75),
    (768, 1344, 0.5714285714285714),
    (1536, 640, 2.4),
    (640, 1536, 0.4166666666666667),
]

#------------------------------------------------#

class NearestSDXLResolution:
    
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"image": ("IMAGE",)}}

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("IMAGE", "width", "height")
    FUNCTION = "Near_SDXL_Reso"
    CATEGORY = icons.get("MyNodes/Images")

    def Near_SDXL_Reso(self, image):
        # ComfyUI IMAGE: [batch, height, width, channels]
        image_width = image.size()[2]
        image_height = image.size()[1]
        print(f"Input image resolution: {image_width}x{image_height}")

        image_ratio = image_width / image_height

        # Trouver la résolution SDXL dont le ratio est le plus proche
        smallest_diff = None
        best = None
        for w, h, r in self.resolutions():
            diff = abs(image_ratio - r)
            if smallest_diff is None or diff < smallest_diff:
                smallest_diff = diff
                best = (w, h)

        if best is None:
            width, height = 1024, 1024
        else:
            width, height = best

        print(f"Selected resolution: {width}x{height}")
        return (image, width, height)

    @staticmethod
    def resolutions():
        return SDXL_SUPPORTED_RESOLUTIONS