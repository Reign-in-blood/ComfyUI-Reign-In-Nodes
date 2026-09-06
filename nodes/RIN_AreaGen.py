#------------------------------------------------#
# Imports                                        #
#------------------------------------------------#

from ..Architecture import icons

import numpy as np
import torch
from PIL import Image

#------------------------------------------------#
# Utility functions                              #
#------------------------------------------------#

def tensor2pil(image: torch.Tensor) -> Image.Image:
   
    array = image.detach().cpu().numpy()
    array = np.squeeze(array)
    array = np.clip(255.0 * array, 0, 255).astype(np.uint8)
    return Image.fromarray(array)

def pil2tensor(image: Image.Image) -> torch.Tensor:
  
    arr = np.array(image).astype(np.float32) / 255.0
    return torch.from_numpy(arr).unsqueeze(0)

#------------------------------------------------#
# RIN_AreaGen Node                               #
#------------------------------------------------#

class RIN_AreaGen:

    @classmethod
    def INPUT_TYPES(s):
        """
        Define the input fields for the node.
        """
        return {
            "required": {
                "width": (
                    "INT",
                    {
                        "default": 512,
                        "min": 64,
                        "max": 4096,
                    },
                ),
                "height": (
                    "INT",
                    {
                        "default": 512,
                        "min": 64,
                        "max": 4096,
                    },
                ),
                "mode": (
                    "INT",
                    {
                        "default": 2,
                        "min": 1,
                        "max": 4,
                    },
                ),
                "orientation": (
                    ["vertical", "horizontal", "diagonal", "alt_diagonal"],
                ),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "MASK", "MASK", "MASK")
    RETURN_NAMES = (
        "Image",
        "Region 1 mask",
        "Region 2 mask",
        "Region 3 mask",
        "Region 4 mask",
    )
    CATEGORY = icons.get("MyNodes/Utils")
    FUNCTION = "AreaGen"

    def AreaGen(self, width: int, height: int, mode: int, orientation: str):

        # Clamp number of zones to valid range
        num_zones = int(mode)
        num_zones = max(1, min(4, num_zones))

        # Preview colors for each zone (max 4 zones)
        region_colors = [
            (255, 0, 0),      # Region 1 -> Red
            (0, 255, 0),      # Region 2 -> Green
            (0, 0, 255),      # Region 3 -> Blue
            (255, 255, 255),  # Region 4 -> White
        ]

        # RGB canvas used for visual preview: shape (H, W, 3)
        canvas = np.zeros((height, width, 3), dtype=np.uint8)

        # 4 masks corresponding to 4 possible regions
        # (zones beyond the selected mode remain empty)
        masks = [
            np.zeros((height, width), dtype=np.float32),
            np.zeros((height, width), dtype=np.float32),
            np.zeros((height, width), dtype=np.float32),
            np.zeros((height, width), dtype=np.float32),
        ]

        # Create coordinate grids for pixel-wise region indexing
        # y_idx: row indices [0..H-1], x_idx: column indices [0..W-1]
        y_idx, x_idx = np.meshgrid(
            np.arange(height), np.arange(width), indexing="ij"
        )

        # Compute region index (0 → num_zones-1) depending on orientation
        if orientation == "vertical":
            # Vertical: equal-width bands from left to right
            region_idx = np.floor(x_idx * num_zones / width).astype(int)

        elif orientation == "horizontal":
            # Horizontal: equal-height bands from top to bottom
            region_idx = np.floor(y_idx * num_zones / height).astype(int)

        elif orientation == "diagonal":
            # Diagonal: top-left to bottom-right
            # Use normalized (x + y) to create evenly distributed diagonal strips
            diag_norm = (x_idx + y_idx) / max(1, (width + height - 2))
            region_idx = np.floor(diag_norm * num_zones).astype(int)

        elif orientation == "alt_diagonal":
            # Reverse diagonal: top-right to bottom-left
            # Same method but mirroring the X axis
            diag_norm = ((width - 1 - x_idx) + y_idx) / max(
                1, (width + height - 2)
            )
            region_idx = np.floor(diag_norm * num_zones).astype(int)

        else:
            # Fallback to vertical orientation if something unexpected is passed
            region_idx = np.floor(x_idx * num_zones / width).astype(int)

        # Ensure region indices stay within valid bounds
        region_idx = np.clip(region_idx, 0, num_zones - 1)

        # Apply color to preview canvas and fill region masks
        for idx in range(num_zones):
            mask_zone = (region_idx == idx)

            # Apply color to the preview image for this region
            color = region_colors[idx]
            canvas[mask_zone] = color

            # Fill corresponding region mask
            masks[idx][mask_zone] = 1.0

        # Convert preview canvas to ComfyUI tensor format (B, H, W, C)
        image_out = pil2tensor(Image.fromarray(canvas))

        # Convert masks to tensors [1, H, W]
        mask_tensors = [torch.from_numpy(m).unsqueeze(0) for m in masks]

        return (image_out, *mask_tensors)