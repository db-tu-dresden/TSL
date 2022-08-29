import logging
from pathlib import Path
from typing import List

from core.ctrl.tvl_libfile_generator import TVLFileGenerator
from core.model.tvl_file import TVLSourceFile
from expansions.tvl_cmake import TVLCMakeGenerator
from core.ctrl.tvl_lib import TVLLib
from core.ctrl.tvl_slicer import TVLSlicer
from core.model.tvl_extension import TVLExtensionSet
from core.model.tvl_primitive import TVLPrimitiveClass, TVLPrimitiveClassSet
from core.tvl_config import config
from expansions.tvl_translation_unit import TVLTranslationUnitContainer
from expansions.tvl_unit_test import TVLTestSuite, TVLTestDependencyGraph, TVLTestGenerator
from utils.log_utils import LogInit
from utils.requirement import requirement
from utils.yaml_utils import yaml_load, yaml_load_all, yaml_store


class TVLGenerator:
    @LogInit()
    def __init__(self) -> None:
        self.__tvl_extension_set: TVLExtensionSet = TVLExtensionSet()
        self.__tvl_primitiveclass_set: TVLPrimitiveClassSet = TVLPrimitiveClassSet()
        self.update()

    @requirement(extension_file="NotNone")
    def __add_extension(self, extension_file: Path) -> None:
        extension_data_dict = None
        try:
            extension_data_dict = config.get_schema("extension").validate(yaml_load(extension_file))
        except Exception as e:
            self.log(logging.ERROR,
                     f"Error while validating extension {extension_file}. Exception: {str(e)}")
        if extension_data_dict is not None:
            self.__tvl_extension_set.add_extension_from_data_dict(extension_file, extension_data_dict)

    def __add_primitive_class(self, primitive_class_file: Path) -> None:
        class_schema = config.get_schema("primitive_class")
        primitive_schema = config.get_schema("primitive")

        primitive_class: TVLPrimitiveClass = None
        for yaml_document in yaml_load_all(primitive_class_file):
            if primitive_class is None:
                class_dict = None
                try:
                    class_dict = class_schema.validate(yaml_document)
                except Exception as e:
                    self.log(logging.ERROR,
                             f"Error while validating Primitive class in file {primitive_class_file}. "
                             f"Exception: {str(e)}.")
                    return
                if class_dict is not None:
                    primitive_class = TVLPrimitiveClass.create_from_dict(primitive_class_file, class_dict)
            else:
                primitive_dict = None
                try:
                    primitive_dict = primitive_schema.validate(yaml_document)
                except Exception as e:
                    self.log(logging.ERROR,
                             f"Error while validating Primitive class in file {primitive_class_file} with "
                             f"primitive data ({yaml_document}). "
                             f"Exception: {str(e)}.")
                if primitive_dict is not None:
                    primitive_class.add_primitive_from_dict(primitive_dict)
        self.__tvl_primitiveclass_set.add_primitive_class(primitive_class)

    def update(self) -> None:
        updated_extensions_count = 0
        updated_primitives_count = 0
        for extension_file in config.modified_extension_files():
            self.__add_extension(extension_file)
            updated_extensions_count += 1
        for primitive_file in config.modified_primitive_files():
            self.__add_primitive_class(primitive_file)
            updated_primitives_count += 1
        msg = ""
        if updated_extensions_count > 0:
            msg += f"Updated {updated_extensions_count} extensions. "
        else:
            msg += f"No changes to extensions detected. "
        if updated_primitives_count > 0:
            msg += f"Updated {updated_primitives_count} primitives."
        else:
            msg += f"No changes to primitives detected."
        self.log(logging.INFO, msg)

    def generate(self, relevant_hardware_flags: List[str] = None):
        self.update()
        slicer = TVLSlicer(relevant_hardware_flags)

        relevant_extensions_set: TVLExtensionSet = slicer.slice_extensions(self.__tvl_extension_set)
        if config.emit_tsl_extensions_to_file:
            tsl_extension_name = "{% import 'core/extension_helper.template' as xht %}{{ xht.TSLCPPExtensionName(data_type, extension_name, register_size) }}"
            template = config.create_template(tsl_extension_name)
            extensions_list = []
            for extension in relevant_extensions_set:
                for dtype in config.default_types:
                    extensions_list.append(
                        {
                            "tsl_extension_name": template.render({
                                "data_type": dtype,
                                "extension_name": extension.name,
                                "register_size": 0
                            }).strip(),
                            "register_size": extension.data["simdT_default_size_in_bits"]
                        }
                    )


            extensions_dict = {"generated_extensions": extensions_list}
            yaml_store(config.tsl_extensions_yaml_output_path, extensions_dict)
        relevant_primitives_class_set: TVLPrimitiveClassSet = slicer.slice_primitives(self.__tvl_primitiveclass_set)

        lib: TVLLib = TVLLib(relevant_extensions_set, relevant_primitives_class_set)
        file_generator: TVLFileGenerator = TVLFileGenerator(lib)
        if not config.print_output_only:
            for path in file_generator.out_pathes:
                self.log(logging.INFO, f"Creating directory {path}")
                path.mkdir(parents=True, exist_ok=True)
            for tvl_file in file_generator.library_files:
                self.log(logging.INFO, f"Creating file {tvl_file.file_name}")
                tvl_file.render_to_file()

            cmake_config = config.get_expansion_config("cmake")


            tvl_translation_units: TVLTranslationUnitContainer = TVLTranslationUnitContainer()
            for path, tu in TVLTestGenerator.generate(lib):
                tvl_translation_units.add_tu(path, tu)

            if cmake_config["enabled"]:
                TVLCMakeGenerator.generate_lib(lib, file_generator, tvl_translation_units, cmake_config)

            if cmake_config["enabled"]:
                TVLCMakeGenerator.generate_source_file(tvl_translation_units, cmake_config)
        else:
            print(";".join(f"{tvl_file.file_name}" for tvl_file in file_generator.library_files))


