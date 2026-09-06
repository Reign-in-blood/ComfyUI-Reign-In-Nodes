from typing import Any, Mapping
from .Architecture import icons
import torch


FLUX_SUPPORTED_RESOLUTIONS = [
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

class NearestFLUXResolution:

    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {"required": {"image": ("IMAGE",)}}

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("IMAGE", "width", "height")
    FUNCTION = "Near_FLUX_Reso"
    CATEGORY = icons.get("MyNodes/Images")

    def Near_FLUX_Reso(self, image) -> tuple[torch.Tensor, int, int]:
        image_width = image.size()[2]
        image_height = image.size()[1]
        print(f"Input image resolution: {image_width}x{image_height}")

        image_ratio = image_width / image_height
        differences = [
            (abs(image_ratio - resolution[2]), resolution)
            for resolution in self.resolutions()
        ]
        smallest = None
        for difference in differences:
            if smallest is None:
                smallest = difference
            else:
                if difference[0] < smallest[0]:
                    smallest = difference
        if smallest is not None:
            width = smallest[1][0]
            height = smallest[1][1]
        else:
            width = 1024
            height = 1024
        print(f"Selected resolution: {width}x{height}")
        return (image, width, height)

    def resolutions(cls):
        return FLUX_SUPPORTED_RESOLUTIONS