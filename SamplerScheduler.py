from .Architecture import icons
import comfy.samplers

class RIN_SamplerScheduler:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "sampler": (comfy.samplers.KSampler.SAMPLERS, {"default": "euler_ancestral"}),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS + ['AYS SD1', 'AYS SDXL', 'AYS SVD', 'GITS'], {"default": "karras"}),
            }
        }

    RETURN_TYPES = (comfy.samplers.KSampler.SAMPLERS, comfy.samplers.KSampler.SCHEDULERS + ['AYS SD1', 'AYS SDXL', 'AYS SVD', 'GITS'], "STRING", "STRING")
    RETURN_NAMES = ("sampler", "scheduler", "sampler_name", "scheduler_name")
    FUNCTION = "RIN_SamplerScheduler"
    CATEGORY = icons.get("MyNodes/Utils")

    def RIN_SamplerScheduler(self, sampler, scheduler):
        return (sampler, scheduler, sampler, scheduler)
