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
                        entry = {
                            "name": entry_dict["name"],
                            "cmakelists_path": f"{supplementary_root_path.joinpath(entry_dict['cmakelists_path'])}",
                            "library_create_function": entry_dict["library_create_function"],

                        }
                        if "include_path" in entry_dict:
                            entry["include_path"] = f"{supplementary_root_path.joinpath(entry_dict['include_path'])}"
                        result.append(entry)
                    else:
                        self.log(logging.WARNING, f"Supplementary library {entry_dict['name']} already added. Ignoring.")
        return result

    @property
    def relevant_runtime_headers(self) -> List[Path]:
        result_set: Set[str] = set()
        supplementary_root_path = Path(config.get_configuration_files_entry("supplementary")["root_path"])
        runtime_root_path = supplementary_root_path.joinpath(config.get_configuration_files_entry("supplementary")["runtime"]["root_path"])
        for extension in self.extension_set:
            if "runtime_headers" in extension.data:
                result_set.update([f"{runtime_root_path.joinpath(p)}" for p in extension.data["runtime_headers"]])
        return [Path(p) for p in result_set]
    
    def copy_relevant_supplementary_files(self) -> None:
        supplementary_root_path = Path(config.generation_out_path)
        for libData in self.relevant_supplementary_libraries:
            shutil.rmtree(supplementary_root_path.joinpath(libData['cmakelists_path']).resolve(), ignore_errors=True)
            shutil.copytree(Path(libData['cmakelists_path']).resolve(), supplementary_root_path.joinpath(libData['cmakelists_path']).resolve())
        to_copy = self.relevant_runtime_headers
        #create all directories recursively
        for fpath in to_copy:
            runtime_dir = supplementary_root_path.joinpath(fpath).resolve().parent
            runtime_dir.mkdir(parents=True, exist_ok=True)
        #copy all files from to_copy to supplementary_root_path, ignoring whether they already exist and keeping the directory structure
        for fpath in to_copy:
            shutil.copy(fpath.resolve(), supplementary_root_path.joinpath(fpath).resolve(), follow_symlinks=True)

    @LogInit()
    def __init__(self, extension_set: TSLExtensionSet, primitive_class_set: TSLPrimitiveClassSet) -> None:
        self.__extension_set = extension_set
        self.__primitive_class_set = primitive_class_set
