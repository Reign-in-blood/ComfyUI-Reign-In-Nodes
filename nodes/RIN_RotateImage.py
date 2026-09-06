# ------------------------------------------------------------------------- #
# Importations                                                              #
# ------------------------------------------------------------------------- #

from ..Architecture import icons

from PIL import Image

import torch
import torchvision.transforms
import torchvision.transforms.functional

# ------------------------------------------------------------------------- #
# Functions                                                                 #
# ------------------------------------------------------------------------- #

def to_binary_mask(image):
    images_sum = image.sum(axis=3)
    return torch.where(images_sum > 0, 1.0, 0.)

def permute_to_image(image):
    image = torchvision.transforms.ToTensor()(image).unsqueeze(0)
    return image.permute([0, 2, 3, 1])[:, :, :, :3]

# ------------------------------------------------------------------------- #

class RIN_RotateImage:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "rotation_angle": ("INT", {
                    "default": 0,
                    "min": -359,
                    "max": 359,
                    "step": 1,
                    "display": "number"})
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    CATEGORY = icons.get("MyNodes/Images")
    FUNCTION = "RIN_RotateImage"


    def RIN_RotateImage(self, image, rotation_angle):
        samples = image.movedim(-1, 1)
        height, width = torchvision.transforms.functional.get_image_size(samples)

        rotation_angle = rotation_angle * -1
        rotated_image = torchvision.transforms.functional.rotate(samples, angle=rotation_angle, expand=True)

        empty_mask = Image.new('RGBA', (height, width), color=(255, 255, 255))
        rotated_mask = torchvision.transforms.functional.rotate(empty_mask, angle=rotation_angle, expand=True)

        img_out = rotated_image.movedim(1, -1)
        mask_out = to_binary_mask(permute_to_image(rotated_mask))

        return (img_out, mask_out)