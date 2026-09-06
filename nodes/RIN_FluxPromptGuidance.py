from ..Architecture import icons

class RIN_FluxGuidancePrompt:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "clip": ("CLIP", ),
            "fluxprompt": ("STRING", {"multiline": True, "dynamicPrompts": True}),
            "guidance": ("FLOAT", {"default": 3.5, "min": 0.0, "max": 100.0, "step": 0.1}),
            }}
    
    RETURN_TYPES = ("CONDITIONING", "STRING",)
    RETURN_NAME = ("Pos_Prompt", "Texte",)
    FUNCTION = "RIN_FluxGuidancePrompt"
    CATEGORY = icons.get("MyNodes/Prompt")

    def RIN_FluxGuidancePrompt(self, clip, fluxprompt, guidance):
        tokens = clip.tokenize(fluxprompt)
        return (clip.encode_from_tokens_scheduled(tokens, add_dict={"guidance": guidance}), )
