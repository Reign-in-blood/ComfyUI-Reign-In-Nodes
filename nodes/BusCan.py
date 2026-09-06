from ..Architecture import icons

#------------------------------------------------#
# ANY TYPE  Credit to pythongosssss
#------------------------------------------------#

class RIN_AnyType(str):

    def __ne__(self, __value: object) -> bool:
        return False

any_type = RIN_AnyType("*")

#------------------------------------------------#

class RIN_BusCan_Basic:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":{},
            "optional": {
                "bus" : ("BUS",),
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "vae": ("VAE",),
                "positive": ("CONDITIONING",),
                "negative": ("CONDITIONING",),
            }
        }
    RETURN_TYPES = ("BUS", "MODEL", "CLIP", "VAE", "CONDITIONING", "CONDITIONING",)
    RETURN_NAMES = ("bus", "model", "clip", "vae", "positive",     "negative")
    FUNCTION = "canbusbasic"
    CATEGORY = icons.get("MyNodes/BusCan")

    def canbusbasic(
        self,
        bus=(None,)*5,
        model=None,
        clip=None,
        vae=None,
        positive=None,
        negative=None
    ):

        # Unpack the 5 constituents of the bus from the bus tuple.
        (
            bus_model,
            bus_clip,
            bus_vae,
            bus_positive,
            bus_negative
        ) = bus

        #Overpass
        out_model       = model     or bus_model
        out_clip        = clip      or bus_clip
        out_vae         = vae       or bus_vae
        out_positive    = positive  or bus_positive
        out_negative    = negative  or bus_negative

        out_bus = (out_model, out_clip, out_vae, out_positive, out_negative)

        if not out_model:
            raise ValueError('Either model or bus containing a model should be supplied')
        if not out_clip:
            raise ValueError('Either clip or bus containing a clip should be supplied')
        if not out_vae:
            raise ValueError('Either vae or bus containing a vae should be supplied')

        return (out_bus, out_model, out_clip, out_vae, out_positive, out_negative)
    
#------------------------------------------------#

class RIN_BusCan_Plus:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":{},
            "optional": {
                "bus" : ("BUS",),
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "vae": ("VAE",),
                "positive": ("CONDITIONING",),
                "negative": ("CONDITIONING",),
                "latent": ("LATENT",),
                "sam_model": (any_type,),
            }
        }
    
    RETURN_TYPES = ("BUS", "MODEL", "CLIP", "VAE", "CONDITIONING", "CONDITIONING", "LATENT", any_type,)
    RETURN_NAMES = ("bus", "model", "clip", "vae", "positive", "negative", "latent", "SAM_Model",)
    FUNCTION = "canbusplus"
    CATEGORY = icons.get("MyNodes/BusCan")

    def canbusplus(
        self,
        bus=(None,)*7,
        model=None,
        clip=None,
        vae=None,
        positive=None,
        negative=None,
        latent=None,
        sam_model=None
    ):

        # Unpack the 5 constituents of the bus from the bus tuple.
        (
            bus_model,
            bus_clip,
            bus_vae,
            bus_positive,
            bus_negative,
            bus_latent,
            bus_sam_model
        ) = bus

        #Overpass
        out_model       = model     or bus_model
        out_clip        = clip      or bus_clip
        out_vae         = vae       or bus_vae
        out_positive    = positive  or bus_positive
        out_negative    = negative  or bus_negative
        out_latent      = latent    or bus_latent
        out_sam_model   = sam_model or bus_sam_model

        out_bus = (out_model, out_clip, out_vae, out_positive, out_negative, out_latent, out_sam_model, )

        if not out_model:
            raise ValueError('Either model or bus containing a model should be supplied')
        if not out_clip:
            raise ValueError('Either clip or bus containing a clip should be supplied')
        if not out_vae:
            raise ValueError('Either vae or bus containing a vae should be supplied')

        return (out_bus, out_model, out_clip, out_vae, out_positive, out_negative, out_latent, out_sam_model)
    
#------------------------------------------------#

class RIN_BusCanAny_4:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
            },
            "optional": {
                "bus": ("PIPE_LINE",),
                "any1": (any_type,),
                "any2": (any_type,),
                "any3": (any_type,),
                "any4": (any_type,), 
            }
        }

    RETURN_TYPES = ("PIPE_LINE", any_type, any_type, any_type, any_type,)
    RETURN_NAMES = ("BUS", "any1", "any2", "any3", "any4", )
    FUNCTION = "canbusany4"
    CATEGORY = icons.get("MyNodes/BusCan")

    def canbusany4(self, bus=(None,)*4, any1=None, any2=None, any3=None, any4=None):

        # Unpack the 5 constituents of the bus from the bus tuple.
        new_any1, new_any2, new_any3, new_any4 = None, None, None, None
     
        if bus is not None:
            new_any1, new_any2, new_any3, new_any4 = bus

        #Overpass
        new_any1 = any1 if any1 is not None else new_any1
        new_any2 = any2 if any2 is not None else new_any2
        new_any3 = any3 if any3 is not None else new_any3
        new_any4 = any4 if any4 is not None else new_any4

        new_bus = new_any1, new_any2, new_any3, new_any4

        return (new_bus, new_any1, new_any2, new_any3, new_any4, )
    
#------------------------------------------------#

class RIN_BusCanAny_6:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
            },
            "optional": {
                "bus": ("PIPE_LINE",),
                "any1": (any_type,),
                "any2": (any_type,),
                "any3": (any_type,),
                "any4": (any_type,), 
                "any5": (any_type,), 
                "any6": (any_type,), 
            }
        }

    RETURN_TYPES = ("PIPE_LINE", any_type, any_type, any_type, any_type, any_type, any_type,)
    RETURN_NAMES = ("BUS", "any1", "any2", "any3", "any4", "any5", "any6", )
    FUNCTION = "canbusany6"
    CATEGORY = icons.get("MyNodes/BusCan")

    def canbusany6(self, bus=(None,)*6, any1=None, any2=None, any3=None, any4=None, any5=None, any6=None):

        # Unpack the 56 constituents of the bus from the bus tuple.
        new_any1, new_any2, new_any3, new_any4, new_any5, new_any6 = None, None, None, None, None, None
     
        if bus is not None:
            new_any1, new_any2, new_any3, new_any4, new_any5, new_any6 = bus

        #Overpass
        new_any1 = any1 if any1 is not None else new_any1
        new_any2 = any2 if any2 is not None else new_any2
        new_any3 = any3 if any3 is not None else new_any3
        new_any4 = any4 if any4 is not None else new_any4
        new_any5 = any5 if any5 is not None else new_any5
        new_any6 = any6 if any6 is not None else new_any6

        new_bus = new_any1, new_any2, new_any3, new_any4, new_any5, new_any6

        return (new_bus, new_any1, new_any2, new_any3, new_any4, new_any5, new_any6, )
    
#------------------------------------------------#
class RIN_BusCanAny_8:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
            },
            "optional": {
                "bus": ("PIPE_LINE",),
                "any1": (any_type,),
                "any2": (any_type,),
                "any3": (any_type,),
                "any4": (any_type,), 
                "any5": (any_type,), 
                "any6": (any_type,), 
                "any7": (any_type,), 
                "any8": (any_type,), 
            }
        }

    RETURN_TYPES = ("PIPE_LINE", any_type, any_type, any_type, any_type, any_type, any_type, any_type, any_type,)
    RETURN_NAMES = ("BUS", "any1", "any2", "any3", "any4", "any5", "any6", "any7", "any8", )
    FUNCTION = "canbusany8"
    CATEGORY = icons.get("MyNodes/BusCan")

    def canbusany8(self, bus=(None,)*8, any1=None, any2=None, any3=None, any4=None, any5=None, any6=None, any7=None, any8=None):

        # Unpack the 56 constituents of the bus from the bus tuple.
        new_any1, new_any2, new_any3, new_any4, new_any5, new_any6, new_any7, new_any8 = None, None, None, None, None, None, None, None
     
        if bus is not None:
            new_any1, new_any2, new_any3, new_any4, new_any5, new_any6, new_any7, new_any8 = bus

        #Overpass
        new_any1 = any1 if any1 is not None else new_any1
        new_any2 = any2 if any2 is not None else new_any2
        new_any3 = any3 if any3 is not None else new_any3
        new_any4 = any4 if any4 is not None else new_any4
        new_any5 = any5 if any5 is not None else new_any5
        new_any6 = any6 if any6 is not None else new_any6
        new_any7 = any7 if any7 is not None else new_any7
        new_any8 = any8 if any8 is not None else new_any8

        new_bus = new_any1, new_any2, new_any3, new_any4, new_any5, new_any6, new_any7, new_any8

        return (new_bus, new_any1, new_any2, new_any3, new_any4, new_any5, new_any6, new_any7, new_any8, )
    
    #------------------------------------------------#


class RIN_BusCanAny_12:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
            },
            "optional": {
                "bus": ("PIPE_LINE",),
                "any1": (any_type,),
                "any2": (any_type,),
                "any3": (any_type,),
                "any4": (any_type,), 
                "any5": (any_type,), 
                "any6": (any_type,), 
                "any7": (any_type,), 
                "any8": (any_type,), 
                "any9": (any_type,), 
                "any10": (any_type,), 
                "any11": (any_type,), 
                "any12": (any_type,), 
            }
        }

    RETURN_TYPES = ("PIPE_LINE", any_type, any_type, any_type, any_type, any_type, any_type, any_type, any_type, any_type, any_type, any_type, any_type,)
    RETURN_NAMES = ("BUS", "any1", "any2", "any3", "any4", "any5", "any6", "any7", "any8", "any9", "any10", "any11", "any12", )
    FUNCTION = "canbusany12"
    CATEGORY = icons.get("MyNodes/BusCan")

    def canbusany12(self, bus=(None,)*12, any1=None, any2=None, any3=None, any4=None, any5=None, any6=None, any7=None, any8=None, any9=None, any10=None, any11=None, any12=None):

        # Unpack the 56 constituents of the bus from the bus tuple.
        new_any1, new_any2, new_any3, new_any4, new_any5, new_any6, new_any7, new_any8, new_any9, new_any10, new_any11, new_any12 = None, None, None, None, None, None, None, None, None, None, None, None
     
        if bus is not None:
            new_any1, new_any2, new_any3, new_any4, new_any5, new_any6, new_any7, new_any8, new_any9, new_any10, new_any11, new_any12 = bus

        #Overpass
        new_any1 = any1 if any1 is not None else new_any1
        new_any2 = any2 if any2 is not None else new_any2
        new_any3 = any3 if any3 is not None else new_any3
        new_any4 = any4 if any4 is not None else new_any4
        new_any5 = any5 if any5 is not None else new_any5
        new_any6 = any6 if any6 is not None else new_any6
        new_any7 = any7 if any7 is not None else new_any7
        new_any8 = any8 if any8 is not None else new_any8
        new_any9 = any9 if any9 is not None else new_any9
        new_any10 = any10 if any10 is not None else new_any10
        new_any11 = any11 if any11 is not None else new_any11
        new_any12 = any12 if any12 is not None else new_any12

        new_bus = new_any1, new_any2, new_any3, new_any4, new_any5, new_any6, new_any7, new_any8, new_any9, new_any10, new_any11, new_any12

        return (new_bus, new_any1, new_any2, new_any3, new_any4, new_any5, new_any6, new_any7, new_any8, new_any9, new_any10, new_any11, new_any12, )
    
    #------------------------------------------------#