from .RIN_AnyType import any_type
from ..Architecture import icons

import os
import re
import json
import hashlib
from datetime import datetime
from itertools import chain
from pathlib import Path

import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo

try:
    import piexif
    import piexif.helper
except Exception:
    piexif = None

from nodes import MAX_RESOLUTION
from comfy.cli_args import args
import comfy.samplers
import folder_paths


#------------------------------------------------#
# Utilitaires folder_paths                       #
#------------------------------------------------#

SUPPORTED_FORMATS = (".png", ".jpg", ".jpeg", ".webp")


def safe_filename_list(folder_name: str):
    try:
        return folder_paths.get_filename_list(folder_name)
    except Exception:
        return []


def safe_full_path(folder_name: str, file_name: str):
    if not folder_name or not file_name:
        return None

    try:
        full_path = folder_paths.get_full_path(folder_name, file_name)
    except Exception:
        return None

    if full_path and os.path.isfile(full_path):
        return full_path

    return None


def clean_text(value):
    if value is None:
        return ""

    if isinstance(value, (list, tuple)):
        if not value:
            return ""
        return clean_text(value[0])

    return str(value).strip()


def strip_selector_prefix(value: str):
    value = clean_text(value)

    if value.startswith("[checkpoints] "):
        return value.replace("[checkpoints] ", "", 1), "checkpoints"

    if value.startswith("[diffusion_models] "):
        return value.replace("[diffusion_models] ", "", 1), "diffusion_models"

    if value.startswith("[unet] "):
        return value.replace("[unet] ", "", 1), "unet"

    return value, ""


def unique_keep_order(values):
    result = []
    seen = set()

    for value in values:
        value = clean_text(value)

        if not value:
            continue

        key = value.lower()

        if key in seen:
            continue

        seen.add(key)
        result.append(value)

    return result


def model_display_name(model_name: str):
    model_name, _folder = strip_selector_prefix(model_name)
    model_name = clean_text(model_name)

    if not model_name:
        return ""

    return Path(model_name).stem


def resolve_model_full_path(model_name: str):
    model_name, prefixed_folder = strip_selector_prefix(model_name)
    model_name = clean_text(model_name)

    if not model_name:
        return None, "", ""

    folders_to_try = []

    if prefixed_folder:
        folders_to_try.append(prefixed_folder)

    folders_to_try.extend([
        "checkpoints",
        "diffusion_models",
        "unet",
    ])

    folders_to_try = unique_keep_order(folders_to_try)

    for folder_name in folders_to_try:
        full_path = safe_full_path(folder_name, model_name)

        if full_path:
            return full_path, folder_name, model_name

    wanted_path = Path(model_name)
    wanted_file = wanted_path.name
    wanted_stem = wanted_path.stem

    for folder_name in folders_to_try:
        files = safe_filename_list(folder_name)

        for file in files:
            file_path = Path(file)

            if file == model_name:
                full_path = safe_full_path(folder_name, file)

                if full_path:
                    return full_path, folder_name, file

            if file_path.name == wanted_file:
                full_path = safe_full_path(folder_name, file)

                if full_path:
                    return full_path, folder_name, file

            if file_path.stem == wanted_stem:
                full_path = safe_full_path(folder_name, file)

                if full_path:
                    return full_path, folder_name, file

    return None, "", ""


#------------------------------------------------#
# RIN Model Name                                 #
#------------------------------------------------#

class RIN_ModelName:

    @classmethod
    def INPUT_TYPES(cls):
        checkpoints = safe_filename_list("checkpoints")
        diffusion_models = safe_filename_list("diffusion_models")
        unet_models = safe_filename_list("unet")

        choices = []

        for name in checkpoints:
            choices.append(f"[checkpoints] {name}")

        for name in diffusion_models:
            choices.append(f"[diffusion_models] {name}")

        for name in unet_models:
            choices.append(f"[unet] {name}")

        if not choices:
            choices = [""]

        return {
            "required": {
                "model": (choices,),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("model_name",)
    FUNCTION = "set_model_name"
    CATEGORY = "RIN/Utils"

    def set_model_name(self, model):
        return (clean_text(model),)


#------------------------------------------------#
# RIN VAE Name                                   #
#------------------------------------------------#

class RIN_VAEName:

    @classmethod
    def INPUT_TYPES(cls):
        vaes = safe_filename_list("vae")

        if not vaes:
            vaes = [""]

        return {
            "required": {
                "vae_name": (vaes,),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("vae_name",)
    FUNCTION = "set_vae_name"
    CATEGORY = "RIN/Utils"

    def set_vae_name(self, vae_name):
        return (vae_name,)


#------------------------------------------------#
# RIN Image Prompt Saver                         #
#------------------------------------------------#

class RIN_ImagePromptSaver:
    model_hash_dict = {}
    vae_hash_dict = {}
    lora_hash_dict = {}
    ti_hash_dict = {}

    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
            },
            "optional": {
                "filename": (
                    "STRING",
                    {
                        "default": "ComfyUI_%time_%seed_%counter",
                        "multiline": False,
                    },
                ),
                "path": (
                    "STRING",
                    {
                        "default": "%date/",
                        "multiline": False,
                    },
                ),
                "model_name": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                        "forceInput": True,
                    },
                ),
                "vae_name": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                        "forceInput": True,
                    },
                ),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFFFFFFFFFF,
                        "forceInput": True,
                    },
                ),
                "steps": (
                    "INT",
                    {
                        "default": 20,
                        "min": 1,
                        "max": 10000,
                    },
                ),
                "cfg": (
                    "FLOAT",
                    {
                        "default": 8.0,
                        "min": 0.0,
                        "max": 100.0,
                        "step": 0.5,
                        "round": 0.01,
                    },
                ),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                "lora_name": (any_type,),
                "width": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": MAX_RESOLUTION,
                        "step": 1,
                    },
                ),
                "height": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": MAX_RESOLUTION,
                        "step": 1,
                    },
                ),
                "positive": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "forceInput": True,
                    },
                ),
                "negative": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "forceInput": True,
                    },
                ),
                "extension": (["png", "jpg", "jpeg", "webp"],),
                "calculate_hash": ("BOOLEAN", {"default": True}),
                "resource_hash": ("BOOLEAN", {"default": True}),
                "lossless_webp": ("BOOLEAN", {"default": True}),
                "save_metadata_file": ("BOOLEAN", {"default": True}),
                "extra_info": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                    },
                ),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("IMAGE", "METADATA")
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = icons.get("MyNodes/Images")

    def save_images(
        self,
        images,
        filename: str = "ComfyUI_%time_%seed_%counter",
        path: str = "%date/",
        model_name: str = "",
        vae_name: str = "",
        seed: int = 0,
        steps: int = 20,
        cfg: float = 8.0,
        sampler_name: str = "",
        scheduler: str = "",
        lora_name=None,
        width: int = 1,
        height: int = 1,
        positive: str = "",
        negative: str = "",
        extension: str = "png",
        calculate_hash: bool = True,
        resource_hash: bool = True,
        lossless_webp: bool = True,
        save_metadata_file: bool = True,
        extra_info: str = "",
        prompt=None,
        extra_pnginfo=None,
    ):
        extension = self.normalize_extension(extension)

        date_format = "%Y-%m-%d"
        time_format = "%H%M%S"
        jpg_webp_quality = 100

        model_name = clean_text(model_name)
        vae_name = clean_text(vae_name)

        (
            full_output_folder,
            _filename_alt,
            _counter_alt,
            _subfolder_alt,
            _filename_prefix,
        ) = folder_paths.get_save_image_path(
            self.prefix_append,
            self.output_dir,
            images[0].shape[1],
            images[0].shape[0],
        )

        results = []
        comments = []

        for image in images:
            model_stem = model_display_name(model_name)
            vae_stem = model_display_name(vae_name)

            sampler_real = clean_text(sampler_name)
            scheduler_real = clean_text(scheduler)

            sampler_metadata = sampler_real

            scheduler_metadata = (
                f"Scheduler: {scheduler_real}, "
                if scheduler_real
                else ""
            )

            variable_map = {
                "%date": self.get_time(date_format),
                "%time": self.get_time(time_format),
                "%seed": seed,
                "%steps": steps,
                "%cfg": cfg,
                "%width": width,
                "%height": height,
                "%extension": extension,
                "%model": model_stem,
                "%sampler": sampler_real,
                "%scheduler": scheduler_real,
                "%quality": jpg_webp_quality,
            }

            subfolder = self.get_path(path, variable_map)
            output_folder = Path(full_output_folder) / subfolder
            output_folder.mkdir(parents=True, exist_ok=True)

            counter = self.get_counter(output_folder)
            variable_map["%counter"] = f"{counter:05}"

            img_array = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))

            model_hash_str = ""
            vae_hash_str = ""
            vae_str = ""
            lora_hash_str = ""
            ti_hash_str = ""
            hashes = {}

            if calculate_hash:
                if model_name:
                    model_hash = self.calculate_hash(
                        name=model_name,
                        hash_type="model",
                    )

                    if model_hash:
                        model_hash_str = f"Model hash: {model_hash}, "
                        hashes["model"] = model_hash

                if vae_name:
                    vae_hash = self.calculate_hash(
                        name=vae_name,
                        hash_type="vae",
                    )

                    if vae_hash:
                        vae_hash_str = f"VAE hash: {vae_hash}, "
                        hashes["vae"] = vae_hash

                lora_hash_dict = self.get_lora_hashes(lora_name)

                if lora_hash_dict:
                    for lora_stem, lora_hash in lora_hash_dict.items():
                        hashes[f"lora:{lora_stem}"] = lora_hash

                    lora_hash_items = [
                        f"{name}: {value}"
                        for name, value in lora_hash_dict.items()
                    ]
                    lora_hash_str_value = ", ".join(lora_hash_items)
                    lora_hash_str = f'Lora hashes: "{lora_hash_str_value}", '

                ti_hash_dict = self.get_ti_hashes(positive, negative)

                if ti_hash_dict:
                    for ti_stem, ti_hash in ti_hash_dict.items():
                        hashes[f"embed:{ti_stem}"] = ti_hash

                    ti_hash_items = [
                        f"{name}: {value}"
                        for name, value in ti_hash_dict.items()
                    ]
                    ti_hash_str_value = ", ".join(ti_hash_items)
                    ti_hash_str = f'TI hashes: "{ti_hash_str_value}", '

            if vae_stem:
                vae_str = f"VAE: {vae_stem}, "

            hashes_str = (
                f", Hashes: {json.dumps(hashes)}"
                if hashes and resource_hash
                else ""
            )

            extra_info_str = (
                f", Extra info: {extra_info}"
                if extra_info
                else ""
            )

            size_width = img.width if width == 0 else width
            size_height = img.height if height == 0 else height

            model_str = (
                f"Model: {model_stem}, "
                if model_stem
                else ""
            )

            comment = (
                f"{positive}\n"
                f"Negative prompt: {negative}\n"
                f"Steps: {steps}, "
                f"Sampler: {sampler_metadata}, "
                f"{scheduler_metadata}"
                f"CFG scale: {cfg}, "
                f"Seed: {seed}, "
                f"Size: {size_width}x{size_height}, "
                f"{model_hash_str}"
                f"{model_str}"
                f"{vae_hash_str}"
                f"{vae_str}"
                f"{lora_hash_str}"
                f"{ti_hash_str}"
                f"Version: ComfyUI"
                f"{hashes_str}"
                f"{extra_info_str}"
            )

            stem = self.get_path(filename, variable_map)
            file = self.get_unique_filename(stem, extension, output_folder)
            file_path = output_folder / file
            file_path.parent.mkdir(parents=True, exist_ok=True)

            self.save_image_with_metadata(
                img=img,
                file_path=file_path,
                extension=extension,
                comment=comment,
                prompt=prompt,
                extra_pnginfo=extra_pnginfo,
                jpg_webp_quality=jpg_webp_quality,
                lossless_webp=lossless_webp,
            )

            if save_metadata_file:
                with open(file_path.with_suffix(".txt"), "w", encoding="utf-8") as f:
                    f.write(comment)

            results.append(
                {
                    "filename": file.name,
                    "subfolder": str(subfolder),
                    "type": self.type,
                }
            )

            comments.append(comment)

        return {
            "ui": {
                "images": results,
            },
            "result": (
                images,
                self.unpack_singleton(comments),
            ),
        }

    #------------------------------------------------#
    # Sauvegarde image + métadonnées                #
    #------------------------------------------------#

    @staticmethod
    def save_image_with_metadata(
        img: Image.Image,
        file_path: Path,
        extension: str,
        comment: str,
        prompt=None,
        extra_pnginfo=None,
        jpg_webp_quality: int = 100,
        lossless_webp: bool = True,
    ):
        if extension == "png":
            metadata = None

            if not args.disable_metadata:
                metadata = PngInfo()
                metadata.add_text("parameters", comment)

                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))

                if extra_pnginfo is not None:
                    for key, value in extra_pnginfo.items():
                        metadata.add_text(key, json.dumps(value))

            img.save(
                file_path,
                pnginfo=metadata,
                compress_level=4,
            )
            return

        save_kwargs = {
            "quality": jpg_webp_quality,
        }

        if extension == "webp":
            save_kwargs["lossless"] = lossless_webp

        if not args.disable_metadata and piexif is not None:
            try:
                exif_bytes = piexif.dump(
                    {
                        "Exif": {
                            piexif.ExifIFD.UserComment:
                                piexif.helper.UserComment.dump(
                                    comment,
                                    encoding="unicode",
                                )
                        },
                    }
                )

                save_kwargs["exif"] = exif_bytes

            except Exception:
                pass

        img.save(file_path, **save_kwargs)

    #------------------------------------------------#
    # Hash CIVITAI / A1111                          #
    #------------------------------------------------#

    @staticmethod
    def calculate_hash(
        name: str,
        hash_type: str,
    ):
        name = clean_text(name)

        if not name:
            return ""

        if hash_type == "model":
            hash_dict = RIN_ImagePromptSaver.model_hash_dict

            file_name, folder_name, resolved_name = resolve_model_full_path(name)

            if not file_name:
                return ""

        elif hash_type == "vae":
            hash_dict = RIN_ImagePromptSaver.vae_hash_dict
            folder_name = "vae"
            resolved_name = name
            file_name = safe_full_path(folder_name, resolved_name)

        elif hash_type == "lora":
            hash_dict = RIN_ImagePromptSaver.lora_hash_dict
            folder_name = "loras"
            resolved_name = name
            file_name = safe_full_path(folder_name, resolved_name)

        elif hash_type == "ti":
            hash_dict = RIN_ImagePromptSaver.ti_hash_dict
            folder_name = "embeddings"
            resolved_name = name
            file_name = safe_full_path(folder_name, resolved_name)

        else:
            return ""

        if not file_name:
            return ""

        cache_key = f"{folder_name}:{resolved_name}"

        if hash_value := hash_dict.get(cache_key):
            return hash_value

        hash_sha256 = hashlib.sha256()
        block_size = 1024 * 1024

        try:
            with open(file_name, "rb") as f:
                for chunk in iter(lambda: f.read(block_size), b""):
                    hash_sha256.update(chunk)

        except Exception:
            return ""

        hash_value = hash_sha256.hexdigest()[:10]
        hash_dict[cache_key] = hash_value

        return hash_value

    #------------------------------------------------#
    # LoRA                                          #
    #------------------------------------------------#

    @classmethod
    def get_lora_hashes(cls, lora_name):
        lora_hashes = {}

        lora_names = cls.normalize_lora_names(lora_name)

        for name in lora_names:
            resolved_name = cls.resolve_by_stem_or_name(name, "loras")

            if not resolved_name:
                continue

            lora_hash = cls.calculate_hash(
                name=resolved_name,
                hash_type="lora",
            )

            if lora_hash:
                lora_hashes[Path(resolved_name).stem] = lora_hash

        return lora_hashes

    @classmethod
    def normalize_lora_names(cls, value):
        if value is None:
            return []

        if isinstance(value, tuple):
            if len(value) > 0 and isinstance(value[0], str):
                return [value[0]]

            result = []

            for item in value:
                result.extend(cls.normalize_lora_names(item))

            return unique_keep_order(result)

        if isinstance(value, (list, set)):
            result = []

            for item in value:
                result.extend(cls.normalize_lora_names(item))

            return unique_keep_order(result)

        text = clean_text(value)

        if not text:
            return []

        try:
            parsed = json.loads(text)

            if isinstance(parsed, (list, tuple, set)):
                return cls.normalize_lora_names(parsed)

        except Exception:
            pass

        parts = re.split(r"[\n;,]+", text)
        parts = [part.strip() for part in parts if part.strip()]

        return unique_keep_order(parts)

    #------------------------------------------------#
    # Textual inversion / embeddings                #
    #------------------------------------------------#

    @classmethod
    def get_ti_hashes(cls, positive: str, negative: str):
        ti_hashes = {}

        ti_pattern = (
            r"(?:\(|\s|,)?"
            r"embedding:"
            r"([^\s:,()]+)"
            r"(?:\.(?:pt|safetensors))?"
            r"(?::\d+(?:\.\d+)?)?"
            r"(?:\)|,|\s)?"
        )

        ti_names = re.findall(ti_pattern, f"{positive}\n{negative}")

        for name in ti_names:
            resolved_name = cls.resolve_by_stem_or_name(name, "embeddings")

            if not resolved_name:
                continue

            ti_hash = cls.calculate_hash(
                name=resolved_name,
                hash_type="ti",
            )

            if ti_hash:
                ti_hashes[Path(resolved_name).stem] = ti_hash

        return ti_hashes

    #------------------------------------------------#
    # Résolution simple par nom ou stem             #
    #------------------------------------------------#

    @staticmethod
    def resolve_by_stem_or_name(name: str, folder_name: str):
        name = clean_text(name)

        if not name:
            return ""

        files = safe_filename_list(folder_name)

        if name in files:
            return name

        name_path = Path(name)
        name_file = name_path.name
        name_stem = name_path.stem

        for file in files:
            file_path = Path(file)

            if file_path.name == name_file:
                return file

            if file_path.stem == name_stem:
                return file

        return ""

    #------------------------------------------------#
    # Fichiers / chemins                            #
    #------------------------------------------------#

    @staticmethod
    def get_counter(directory: Path):
        img_files = list(
            chain(
                *(
                    directory.rglob(f"*{suffix}")
                    for suffix in SUPPORTED_FORMATS
                )
            )
        )

        return len(img_files) + 1

    @staticmethod
    def get_path(name, variable_map):
        name = clean_text(name)

        for variable, value in variable_map.items():
            name = name.replace(variable, str(value))

        return Path(name)

    @staticmethod
    def get_time(time_format):
        try:
            return datetime.now().strftime(time_format)
        except Exception:
            return ""

    @staticmethod
    def get_unique_filename(stem: Path, extension: str, output_folder: Path):
        extension = clean_text(extension).lower().lstrip(".")
        stem = Path(stem)

        file = stem.with_suffix(f"{stem.suffix}.{extension}")
        index = 0

        while (output_folder / file).exists():
            index += 1
            new_stem = Path(f"{stem}_{index}")
            file = new_stem.with_suffix(f"{new_stem.suffix}.{extension}")

        return file

    @staticmethod
    def normalize_extension(extension: str):
        extension = clean_text(extension).lower().lstrip(".")

        if extension not in ("png", "jpg", "jpeg", "webp"):
            return "png"

        return extension

    @staticmethod
    def unpack_singleton(arr: list):
        return arr[0] if len(arr) == 1 else arr