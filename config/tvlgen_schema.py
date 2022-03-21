from utils.log import LogInit
from utils.schema import Schema
from utils.singleton import Singleton
from utils.yaml import YamlDataType


class TVLExtensionSchema(Schema, metaclass=Singleton):
    @LogInit()
    def __init__(self, schema_dict: YamlDataType) -> None:
        super().__init__(schema_dict)


class TVLPrimitiveSchema(Schema, metaclass=Singleton):
    @LogInit()
    def __init__(self, schema_dict: YamlDataType) -> None:
        super().__init__(schema_dict)


class TVLPrimitiveClassSchema(Schema, metaclass=Singleton):
    @LogInit()
    def __init__(self, schema_dict: YamlDataType) -> None:
        super().__init__(schema_dict)
