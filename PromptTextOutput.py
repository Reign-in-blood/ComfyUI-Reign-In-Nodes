#------------------------------------------------#
# Imports                                        #
#------------------------------------------------#

from .Architecture import icons

#------------------------------------------------#
# Utility functions                              #
#------------------------------------------------#


def encode_prompt_conditioning(clip, prompt_text):
    if clip is None:
        raise RuntimeError(
            "ERROR: clip input is invalid: None\n\n"
            "Le modèle chargé ne contient pas de CLIP/text encoder valide."
        )

    tokens = clip.tokenize(prompt_text)

    if hasattr(clip, "encode_from_tokens_scheduled"):
        conditioning = clip.encode_from_tokens_scheduled(tokens)
        return conditioning

    output = clip.encode_from_tokens(tokens, return_pooled=True, return_dict=True)
    cond = output.pop("cond")
    return [[cond, output]]

#------------------------------------------------#

class PromptTextOutputPos:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip": ("CLIP",),
                "prompt_text": ("STRING", {
                    "multiline": True,
                    "dynamicPrompts": True,
                    "default": ""
                })
            }
        }

    RETURN_TYPES = ("CONDITIONING", "STRING")
    RETURN_NAMES = ("positive", "text")
    FUNCTION = "encode"
    CATEGORY = icons.get("MyNodes/Prompt")

    def encode(self, clip, prompt_text):
        conditioning = encode_prompt_conditioning(clip, prompt_text)
        return (conditioning, prompt_text)


class PromptTextOutputNeg:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip": ("CLIP",),
                "prompt_text": ("STRING", {
                    "multiline": True,
                    "dynamicPrompts": True,
                    "default": ""
                })
            }
        }

    RETURN_TYPES = ("CONDITIONING", "STRING")
    RETURN_NAMES = ("negative", "text")
    FUNCTION = "encode"
    CATEGORY = icons.get("MyNodes/Prompt")

    def encode(self, clip, prompt_text):
        conditioning = encode_prompt_conditioning(clip, prompt_text)
        return (conditioning, prompt_text)
    
#------------------------------------------------#


class RIN_PromptPartsConditioning:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip": ("CLIP",),

                "subject": ("STRING", {
                    "multiline": True,
                    "dynamicPrompts": True,
                    "default": ""
                }),

                "hair": ("STRING", {
                    "multiline": True,
                    "dynamicPrompts": True,
                    "default": ""
                }),

                "eyes": ("STRING", {
                    "multiline": True,
                    "dynamicPrompts": True,
                    "default": ""
                }),

                "face": ("STRING", {
                    "multiline": True,
                    "dynamicPrompts": True,
                    "default": ""
                }),

                "body": ("STRING", {
                    "multiline": True,
                    "dynamicPrompts": True,
                    "default": ""
                }),

                "clothes": ("STRING", {
                    "multiline": True,
                    "dynamicPrompts": True,
                    "default": ""
                }),

                "pose": ("STRING", {
                    "multiline": True,
                    "dynamicPrompts": True,
                    "default": ""
                }),

                "background": ("STRING", {
                    "multiline": True,
                    "dynamicPrompts": True,
                    "default": ""
                }),

                "extra": ("STRING", {
                    "multiline": True,
                    "dynamicPrompts": True,
                    "default": ""
                }),
            }
        }

    RETURN_TYPES = ("CONDITIONING", "STRING")
    RETURN_NAMES = ("conditioning", "text")
    FUNCTION = "build_prompt"
    CATEGORY = icons.get("MyNodes/Prompt")

    def build_prompt(self, clip, subject, hair, eyes, face, body, clothes, pose, background, extra):
        parts = [
            subject.strip(),
            hair.strip(),
            eyes.strip(),
            face.strip(),
            body.strip(),
            clothes.strip(),
            pose.strip(),
            background.strip(),
            extra.strip()
        ]

        # Garde uniquement les champs non vides
        parts = [p for p in parts if p]

        # Concaténation avec " . "
        final_text = " . ".join(parts)

        conditioning = encode_prompt_conditioning(clip, final_text)

        return (conditioning, final_text)