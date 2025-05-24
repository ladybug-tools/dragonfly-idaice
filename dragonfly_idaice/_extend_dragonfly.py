# coding=utf-8
from dragonfly.properties import ModelProperties
from .properties.model import ModelIdaiceProperties


# set a hidden idaice attribute on each core geometry Property class to None
# define methods to produce idaice property instances on each Property instance
ModelProperties._idaice = None


def model_idaice_properties(self):
    if self._idaice is None:
        self._idaice = ModelIdaiceProperties(self.host)
    return self._idaice


# add idaice property methods to the Properties classes
ModelProperties.idaice = property(model_idaice_properties)
