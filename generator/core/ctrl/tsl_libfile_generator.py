from generator.core.ctrl.tsl_lib import TSLLib
from generator.core.tsl_config import config

import copy
import logging
from pathlib import Path
from typing import Generator

from jinja2 import Template

from typing import List, Dict
from generator.core.model.tsl_extension import TSLExtensionSet, TSLExtension
from generator.core.model.tsl_file import TSLHeaderFile
from generator.core.model.tsl_primitive import TSLPrimitiveClassSet
from generator.utils.file_utils import strip_common_path_prefix
from generator.utils.log_utils import LogInit
from generator.utils.yaml_utils import yaml_load, YamlDataType
from generator.core.ctrl.tsl_dependendies import TSLDependencyGraph



class TSLFileGenerator:
    @classmethod
    def generate_extension_file(cls, extension: TSLExtension) -> TSLHeaderFile:
        file_path: Path = config.get_generation_path("extensions").joinpath(extension.file_name).joinpath(
            extension.name).with_suffix(config.get_config_entry("header_file_extension"))
        tsl_file: TSLHeaderFile = TSLHeaderFile.create_from_dict(file_path, extension.data)
        extension_template: Template = config.get_template("core::extension")
        tsl_file.add_code(extension_template.render(extension.data))
        tsl_file.import_includes(extension.data)
        return tsl_file

    @property
    def extension_files(self) -> Generator[TSLHeaderFile, None, None]:
        yield from self.__extension_name_to_file_dict.values()

    @property
    def primitive_declaration_files(self) -> Generator[TSLHeaderFile, None, None]:
        yield from self.__primitive_class_declarations

    @property
    def primitive_definition_files(self) -> Generator[TSLHeaderFile, None, None]:
        yield from self.__primitive_class_definitions

    @property
    def static_files(self) -> Generator[TSLHeaderFile, None, None]:
        yield from self.__static_files

    @property
    def out_pathes(self) -> Generator[Path, None, None]:
        def get_fnames(l):
            return [f.file_name.parent for f in l]

        pathes = set(get_fnames(self.static_files) + get_fnames(self.extension_files) + get_fnames(
            self.primitive_declaration_files) + get_fnames(self.primitive_definition_files))
        for p in sorted(pathes):
            yield p

    @property
    def library_files(self) -> Generator[TSLHeaderFile, None, None]:
        yield from self.static_files
        yield from self.extension_files
        yield from self.primitive_declaration_files
        yield from self.primitive_definition_files

    def __create_extension_header_files(self, extension_set: TSLExtensionSet) -> None:
        self.log(logging.INFO, f"Starting generation of extensions header.")
        for extension in extension_set:
            file_path: Path = config.get_generation_path("extensions").joinpath(extension.file_name).joinpath(
                extension.name).with_suffix(config.get_config_entry("header_file_extension"))
            tsl_file: TSLHeaderFile = TSLHeaderFile.create_from_dict(file_path, extension.data)
            tsl_file.add_code(config.get_template("core::extension").render(extension.data))
            self.log(logging.INFO,
                     f"Created struct for hardware extension {extension.name}.")
            tsl_file.import_includes(extension.data)
            self.__extension_name_to_file_dict[extension.name] = tsl_file

    def __create_primitive_header_files(self, extension_set: TSLExtensionSet,
                                        primitive_class_set: TSLPrimitiveClassSet):
        self.log(logging.INFO, f"Starting generation of primitive header.")
        for primitive_class in primitive_class_set:
            declaration_file_path: Path = config.get_generation_path("primitive_declarations").joinpath(
                primitive_class.file_name).joinpath(primitive_class.name).with_suffix(
                config.get_config_entry("header_file_extension"))
            declaration_file: TSLHeaderFile = TSLHeaderFile.create_from_dict(declaration_file_path,
                                                                             primitive_class.data)

            definition_files_per_extension_dict: Dict[str, TSLHeaderFile] = dict()
            for primitive in primitive_class:
                declaration_data = copy.deepcopy(primitive.declaration.data)
                declaration_data["tsl_function_doxygen"] = config.get_template("core::doxygen_function").render(
                    declaration_data)
                declaration_file.add_code(
                    config.get_template("core::primitive_declaration").render(declaration_data))
                declaration_file.import_includes(declaration_data)

                # print(primitive)

                for definition in primitive.definitions:
                    if definition.target_extension not in definition_files_per_extension_dict:
                        primitive_path: Path = config.get_generation_path("primitive_definitions").joinpath(
                            primitive_class.file_name).joinpath(primitive_class.name).joinpath(
                            f"{primitive_class.name}_{definition.target_extension}").with_suffix(
                            config.get_config_entry("header_file_extension"))
                        definition_files_per_extension_dict[
                            definition.target_extension] = TSLHeaderFile.create_from_dict(primitive_path,
                                                                                          primitive_class.data)
                    definition_file: TSLHeaderFile = definition_files_per_extension_dict[definition.target_extension]

                    # print(definition)

                    definition_copy = copy.deepcopy(definition.data)

                    for ctype, additional_simd_template_base_type in definition.types:
                        definition_copy["ctype"] = ctype
                        definition_copy["additional_simd_template_base_type"] = additional_simd_template_base_type
                        decl_and_def_combined_data = { **extension_set.get_extension_by_name(
                            definition.target_extension).data, **declaration_data, **definition_copy }
                        decl_and_def_combined_data["implementation"] = config.create_template(
                            definition_copy["implementation"]).render(
                            decl_and_def_combined_data)
                        definition_file.add_code(
                            config.get_template("core::primitive_definition").render(decl_and_def_combined_data))
                        self.log(logging.INFO,
                                 f"Created template specialization for {primitive.declaration.name} (details::{primitive.declaration.name}_impl<simd<{ctype}, {definition.target_extension}>>)")

                    definition_file.import_includes(definition.data)
                    definition_file.add_file_include(declaration_file)

            self.__primitive_class_declarations.append(declaration_file)
            self.__primitive_class_definitions.extend(definition_files_per_extension_dict.values())

    def __create_static_header_files(self) -> None:
        self.log(logging.INFO, f"Starting generation of static header.")
        for static_yaml_file_path in config.static_lib_files():
            if static_yaml_file_path.stem == config.lib_root_header.stem:
                file_path = config.lib_root_header
            else:
                static_file_path_without_prefix = strip_common_path_prefix(static_yaml_file_path,
                                                                           config.static_lib_files_root_path)
                static_file_name = static_file_path_without_prefix.name
                static_file_path = static_file_path_without_prefix.parent
                file_path: Path = config.lib_static_files_root_path.joinpath(static_file_path).joinpath(
                    static_file_name).with_suffix(config.get_config_entry("header_file_extension"))

            data_dict: YamlDataType = yaml_load(static_yaml_file_path)
            tsl_file: TSLHeaderFile = TSLHeaderFile.create_from_dict(file_path, data_dict)
            if "implementations" in data_dict:
                for implementation in data_dict["implementations"]:
                    tsl_file.add_code_to_be_rendered(implementation)
            self.__static_files.append(tsl_file)

    def __sort_header_files(self, sorted_keys: List[str], header_files: List[TSLHeaderFile]) -> List[TSLHeaderFile]:
        result: List[TSLHeaderFile] = []
        for key in sorted_keys:
            for header_file in header_files:
                if header_file.file_name.stem.startswith(key):
                    result.append(header_file)
        if len(result) != len(header_files):    
            raise Exception("Could not sort header files.")
        return result

    @LogInit()
    def __init__(self, lib: TSLLib) -> None:
        self.__static_files: List[TSLHeaderFile] = []
        self.__extension_name_to_file_dict: Dict[str, TSLHeaderFile] = {}
        self.__primitive_class_declarations: List[TSLHeaderFile] = []
        self.__primitive_class_definitions: List[TSLHeaderFile] = []

        self.__create_extension_header_files(lib.extension_set)
        self.__create_primitive_header_files(lib.extension_set, lib.primitive_class_set)

        self.__create_static_header_files()
        # dep_graph = TSLDependencyGraph(lib)
        # print("Checking implementation dependencies:")
        # ordered_primitive_classes = list(dep_graph.sort_tsl_classes("get_implementations"))


        generated_files_root: TSLHeaderFile = TSLHeaderFile.create_from_dict(config.lib_generated_files_root_header, {})
        for extension_file in self.extension_files:
            generated_files_root.add_file_include(extension_file)
        # for primitive_declaration in self.__sort_header_files(ordered_primitive_classes, list(self.primitive_declaration_files)):
        for primitive_declaration in self.primitive_declaration_files:
            generated_files_root.add_file_include(primitive_declaration)
        for primitive_definition in self.primitive_definition_files:
            generated_files_root.add_file_include(primitive_definition)
        for runtime_header in lib.relevant_runtime_headers:
            generated_files_root.add_predefined_tsl_file_include(f'"{runtime_header.name}"')
        self.__static_files.append(generated_files_root)
