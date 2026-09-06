from ..Architecture import icons


class RIN_TokenCounter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
                "clip": ("CLIP",),
            }
        }

    CATEGORY = icons.get("MyNodes/Prompt")
    OUTPUT_NODE = True
    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("COUNT", "COUNT_AS_STRING")
    FUNCTION = "RIN_TokenCounter"

    def RIN_TokenCounter(self, text, clip):
        tokenization = clip.tokenize(text)
        tokenizer = getattr(clip.tokenizer, "clip_g", clip.tokenizer.clip_l)

        count = sum(
            1
            for batches in tokenization.values()
            for batch in batches
            for token in batch
            if token[0] not in (tokenizer.start_token, tokenizer.end_token, tokenizer.pad_token)
        )

        max_length = tokenizer.max_length
        total_max = max_length * max(1, (count + max_length - 1) // max_length)
        count_as_string = f"{count} / {total_max}"

        return {
            "ui": {"text": (count_as_string,)},
            "result": (count, count_as_string),
        }