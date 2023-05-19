from typing import List, Set, Dict, Tuple, Generator
from pathlib import Path
import logging
import shutil


from generator.core.tsl_config import config
from generator.core.model.tsl_extension import TSLExtensionSet, TSLExtension
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

    @property
    def relevant_supplementary_libraries(self) -> List[Dict[str, str]]:
        libnames: Set[str] = set()
        result: List[Dict[str, str]] = list()
        supplementary_root_path = Path(config.get_configuration_files_entry("supplementary")["root_path"])
        for primitive_definition in self.primitive_class_set.definitions():
            extension: TSLExtension = self.extension_set.get_extension_by_name(
                primitive_definition.target_extension)
            if "required_supplementary_libraries" in extension.data:
                for entry_dict in extension.data["required_supplementary_libraries"]:
                    if entry_dict["name"] not in libnames:
                        libnames.add(entry_dict["name"])
                        result.append({
                            "name": entry_dict["name"],
                            "cmakelists_path": f"{supplementary_root_path.joinpath(entry_dict['cmakelists_path'])}",
                            "library_create_function": entry_dict["library_create_function"]
                        })
                    else:
                        self.log(logging.WARNING, f"Supplementary library {entry_dict['name']} already added. Ignoring.")
        return result

    def copy_relevant_supplementary_files(self) -> None:
        supplementary_root_path = Path(config.generation_out_path)
        for libData in self.relevant_supplementary_libraries:
            shutil.rmtree(supplementary_root_path.joinpath(libData['cmakelists_path']).resolve(), ignore_errors=True)
            shutil.copytree(Path(libData['cmakelists_path']).resolve(), supplementary_root_path.joinpath(libData['cmakelists_path']).resolve())


    @LogInit()
    def __init__(self, extension_set: TSLExtensionSet, primitive_class_set: TSLPrimitiveClassSet) -> None:
        self.__extension_set = extension_set
        self.__primitive_class_set = primitive_class_set
