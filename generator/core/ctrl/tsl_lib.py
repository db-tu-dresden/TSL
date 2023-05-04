from typing import Generator

from generator.core.model.tsl_extension import TSLExtensionSet
from generator.core.model.tsl_primitive import TSLPrimitiveClassSet
from generator.utils.log_utils import LogInit


class TSLLib:

    @property
    def extension_set(self) -> TSLExtensionSet:
        return self.__extension_set

    @property
    def primitive_class_set(self) -> TSLPrimitiveClassSet:
        return self.__primitive_class_set

    @property
    def primitive_names(self) -> Generator[str, None, None]:
        for primitive_class in self.primitive_class_set:
            for primitive in primitive_class:
                yield primitive.declaration.name

    @LogInit()
    def __init__(self, extension_set: TSLExtensionSet, primitive_class_set: TSLPrimitiveClassSet) -> None:
        self.__extension_set = extension_set
        self.__primitive_class_set = primitive_class_set
