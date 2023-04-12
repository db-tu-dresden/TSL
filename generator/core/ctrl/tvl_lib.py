from typing import Generator

from generator.core.model.tvl_extension import TVLExtensionSet
from generator.core.model.tvl_primitive import TVLPrimitiveClassSet
from generator.utils.log_utils import LogInit


class TVLLib:

    @property
    def extension_set(self) -> TVLExtensionSet:
        return self.__extension_set

    @property
    def primitive_class_set(self) -> TVLPrimitiveClassSet:
        return self.__primitive_class_set

    @property
    def primitive_names(self) -> Generator[str, None, None]:
        for primitive_class in self.primitive_class_set:
            for primitive in primitive_class:
                yield primitive.declaration.name

    @LogInit()
    def __init__(self, extension_set: TVLExtensionSet, primitive_class_set: TVLPrimitiveClassSet) -> None:
        self.__extension_set = extension_set
        self.__primitive_class_set = primitive_class_set
