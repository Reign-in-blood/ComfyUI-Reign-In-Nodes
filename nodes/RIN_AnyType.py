#------------------------------------------------#
# ANY TYPE                                       #
#------------------------------------------------#

"""A special type that can be connected to any other types. Credit to pythongosssss"""

#------------------------------------------------#

class RIN_AnyType(str):
    
    def __ne__(self, __value: object) -> bool:
        return False

any_type = RIN_AnyType("*")

#------------------------------------------------#

""" from .RIN_AnyType import any_type """

#------------------------------------------------#