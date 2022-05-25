from core.tvlgen_file import TVLYamlFileTree
from utils.log import LogInit
from utils.singleton import Singleton


class TVLPrimitiveContainer:
    pass


class TVLPrimitiveGenerator(metaclass=Singleton):
    @LogInit()
    def __init__(self, yaml_file_tree: TVLYamlFileTree:
