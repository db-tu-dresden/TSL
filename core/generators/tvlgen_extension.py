import copy
from pathlib import Path
from typing import List, Set, Dict, Generator

from core.tvl_config import TVLGeneratorConfig
from core.tvlgen_file import TVLYamlFileTree, TVLFile
from utils.log import LogInit
from utils.singleton import Singleton
from utils.yaml import YamlLoader


class TVLExtensionsContainer:
    def __init__(self, config: TVLGeneratorConfig):
        self.__extension_header_files: Set[Path] = set()
        self.__extensions_to_data_dict: Dict[str, dict] = dict()
        self.__extensions_to_files_dict: Dict[str, TVLFile] = dict()
        self.__config = config

    def __of_interest(self, data_dict: dict, relevant_lscpu_flags: List[str]) -> bool:
        if relevant_lscpu_flags is not None:
            if len(data_dict["lscpu_flags"]) > 0:
                if not (set(relevant_lscpu_flags) & set(data_dict["lscpu_flags"])):
                    return False
        return True

    def get_relevant_extensions(self, relevant_lscpu_flags: List[str] = None) -> Generator[str, None, None]:
        for extension_name in self.__extensions_to_data_dict:
            if self.__of_interest(self.__extensions_to_data_dict[extension_name], relevant_lscpu_flags):
                yield extension_name

    def get_extension_dict(self, extension_name: str) -> dict:
        return self.__extensions_to_data_dict[extension_name]

    def get_extension_file(self, extension_name: str) -> TVLFile:
        return self.__extensions_to_files_dict[extension_name]

    def add_extension(self, file_name: Path, rel_path: Path, data_dict: dict):
        extension_name = data_dict["extension_name"]
        self.__extensions_to_data_dict[extension_name] = copy.deepcopy(data_dict)
        extension_file: TVLFile = TVLFile(
            Path(f"./generated/extensions/").joinpath(rel_path),
            Path(f"{file_name.stem}"),
            data_dict
        )
        extension_file.add_code(self.__config.extension_template.render(data_dict))
        if "includes" in data_dict:
            extension_file.add_includes((include for include in data_dict["includes"]))
        self.__extension_header_files.add(extension_file.file)
        self.__extensions_to_files_dict[extension_name] = extension_file


class TVLExtensionsGenerator(metaclass=Singleton):
    @LogInit()
    def __init__(self, config: TVLGeneratorConfig, yaml_file_tree: TVLYamlFileTree):
        self.__config = config
        self.__file_tree = yaml_file_tree
        self.__extensions: TVLExtensionsContainer = TVLExtensionsContainer(config)

    def load(self):
        for extension_file in self.__file_tree.relevant_extension_files():
            data_dict = self.__config.extension_schema.validate(YamlLoader().load(extension_file))
            self.__extensions.add_extension(extension_file, self.__file_tree.get_extension_rel_path(extension_file), data_dict)

    # def import_data(self, relevant_lscpu_flags: List[str] = None) -> None:
    #     for relevant_extension in self.__extensions.get_relevant_extensions(relevant_lscpu_flags):
            # self.__extensions

            # extension_file.generate()
            # headers_to_be_included_by_tvl_generated_hpp.append(extension_file.file)
