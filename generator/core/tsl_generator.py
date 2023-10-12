import re
import logging
from pathlib import Path
from typing import List

from generator.core.ctrl.tsl_libfile_generator import TSLFileGenerator
from generator.expansions.tsl_cmake import TSLCMakeGenerator
from generator.core.ctrl.tsl_lib import TSLLib
from generator.core.ctrl.tsl_slicer import TSLSlicer
from generator.core.model.tsl_extension import TSLExtensionSet
from generator.core.model.tsl_primitive import TSLPrimitiveClass, TSLPrimitiveClassSet
from generator.core.tsl_config import config
from generator.core.ctrl.tsl_dependencies import TSLDependencyGraph
from generator.expansions.tsl_readme_md import create_readme
from generator.expansions.tsl_translation_unit import TSLTranslationUnitContainer
from generator.expansions.tsl_unit_test import TSLTestGenerator
from generator.utils.log_utils import LogInit
from generator.utils.requirement import requirement
from generator.utils.yaml_utils import yaml_load, yaml_load_all, yaml_store


class TSLGenerator:
    @LogInit()
    def __init__(self) -> None:
        self.__tsl_extension_set: TSLExtensionSet = TSLExtensionSet()
        self.__tsl_primitiveclass_set: TSLPrimitiveClassSet = TSLPrimitiveClassSet()
        self.update()

    @requirement(extension_file="NotNone")
    def __add_extension(self, extension_file: Path) -> None:
        extension_data_dict = None
        try:
            extension_data_dict = config.get_schema("extension").validate(yaml_load(extension_file, **config.yaml_loader_params()))
        except Exception as e:
            self.log(logging.ERROR,
                     f"Error while validating extension {extension_file}. Exception: {str(e)}")
        if extension_data_dict is not None:
            self.__tsl_extension_set.add_extension_from_data_dict(extension_file, extension_data_dict)

    def __add_primitive_class(self, primitive_class_file: Path) -> None:
        class_schema = config.get_schema("primitive_class")
        primitive_schema = config.get_schema("primitive")

        primitive_class: TSLPrimitiveClass = None
        for yaml_document in yaml_load_all(primitive_class_file, **(config.yaml_loader_params())):
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
                    primitive_class = TSLPrimitiveClass.create_from_dict(primitive_class_file, class_dict)
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
        self.__tsl_primitiveclass_set.add_primitive_class(primitive_class)

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

    def generate(self, relevant_hardware_flags: List[str] = None, relevant_primitives: List[str] = None):
        if relevant_primitives is None:
            relevant_primitives = config.get_config_entry("relevant_primitives")

        self.update()
        slicer = TSLSlicer(relevant_hardware_flags, config.relevant_types)

        relevant_extensions_set: TSLExtensionSet = slicer.slice_extensions(self.__tsl_extension_set)
        if relevant_hardware_flags is not None:
            for extension in relevant_extensions_set:
                if extension.has_synonyms:
                    synonym_dict: dict = extension.synonym_flags()
                    for synonym in synonym_dict:
                        if synonym in relevant_hardware_flags:
                            relevant_hardware_flags = list(map(lambda x: x.replace(synonym, synonym_dict[synonym]), relevant_hardware_flags))
        slicer.update_relevant_flags( relevant_hardware_flags )

        if config.emit_tsl_extensions_to_file:
            tsl_extension_name = "{% import 'core/extension_helper.template' as xht %}{{ xht.TSLCPPExtensionName(data_type, extension_name, register_size) }}"
            template = config.create_template(tsl_extension_name)
            extensions_list = []
            for extension in relevant_extensions_set:
                for dtype in config.relevant_types:
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
        relevant_primitives_class_set: TSLPrimitiveClassSet = slicer.slice_primitives(self.__tsl_primitiveclass_set)
        
        """ Only filter if any relevant primitves are set. Also take care that no empty strings are passed """
        filter_by_primitive = list(filter( lambda x: len(x) > 0, relevant_primitives ))
        if filter_by_primitive:
            selective_primitive_list = filter_by_primitive + config.get_config_entry("always_required_primitives")
            selected_relevant_primitives_class_set = TSLPrimitiveClassSet()

            # Filter
            implregex_list = []
            for pClass in relevant_primitives_class_set:
                for primitive in pClass:
                    implregex_list.append( primitive.declaration.functor_name )

            implregex_string = f'(?<!_)({"|".join(implregex_list)})(?!([a-zA-Z]|_|\[|\.))'

            implregex = re.compile(implregex_string, re.IGNORECASE)

            primitive_dependency_dict = dict()
            """ Find all dependencies for primitives """
            for pClass in relevant_primitives_class_set:
                for primitive in pClass:
                    curr_dependencies = []
                    for definition in primitive.definitions:
                        matches = implregex.findall(definition.data["implementation"])
                        for m in matches:
                            if m[0] != primitive.declaration.functor_name:
                                if m[0] not in curr_dependencies:
                                    curr_dependencies.append( m[0] )
                    
                    for test in primitive.tests:
                        matches = implregex.findall(test['implementation'])
                        for m in matches:
                            if m[0] != primitive.declaration.functor_name:
                                if m[0] not in curr_dependencies:
                                    curr_dependencies.append( m[0] )
                                    

                    if curr_dependencies:
                        primitive_dependency_dict[primitive.declaration.functor_name] = curr_dependencies

            """ Explore all currently selected primitves and subsequently their dependencies, recursively """
            frontier = list(primitive_dependency_dict.keys())
            while (frontier):
                key = frontier[0]
                frontier.remove(key)
                if key in selective_primitive_list:
                    for dep in primitive_dependency_dict[key]:
                        if dep not in selective_primitive_list:
                            selective_primitive_list.append(dep)
                            if dep in primitive_dependency_dict:
                                frontier.append( dep )

            for pClass in relevant_primitives_class_set:
                dummyclass = TSLPrimitiveClass( pClass.file_name, pClass.data )
                for primitive in pClass:
                    if primitive.declaration.functor_name in selective_primitive_list:
                        dummyclass.add_primitive( primitive )
                if not dummyclass.is_empty():
                    selected_relevant_primitives_class_set.add_primitive_class( dummyclass )
            relevant_primitives_class_set = selected_relevant_primitives_class_set

        lib: TSLLib = TSLLib(relevant_extensions_set, relevant_primitives_class_set)

        dep_graph = TSLDependencyGraph(lib)
        if not dep_graph.is_well_defined():
            dep_graph.log_errors()
            raise ValueError("Dependency graph is not well defined. Could not generate TSL.")
        if dep_graph.has_warnings():
            dep_graph.log_warnings()
        print("DONE WITH ANAYLSIS")
        #uncomment the next line to start jaal server
        #dep_graph.to_jaal()

        file_generator: TSLFileGenerator = TSLFileGenerator(lib, dep_graph)
        if not config.print_output_only:
            for path in file_generator.out_pathes:
                self.log(logging.INFO, f"Creating directory {path}")
                path.mkdir(parents=True, exist_ok=True)
            for tsl_file in file_generator.library_files:
                self.log(logging.INFO, f"Creating file {tsl_file.file_name}")
                tsl_file.render_to_file()

            lib.copy_relevant_supplementary_files()

            cmake_config = config.get_expansion_config("cmake")

            tsl_translation_units: TSLTranslationUnitContainer = TSLTranslationUnitContainer()

            try:
                for path, tu in TSLTestGenerator.generate(lib, dep_graph):
                    tsl_translation_units.add_tu(path, tu)
            except Exception as e:
                self.log(logging.ERROR, f"Error while generating test files. Exception: {str(e)}")
                raise e

            if cmake_config["enabled"]:
                TSLCMakeGenerator.generate_lib(lib, file_generator, tsl_translation_units, cmake_config)

            if cmake_config["enabled"]:
                TSLCMakeGenerator.generate_source_file(tsl_translation_units, cmake_config)
        else:
            print(";".join(f"{tsl_file.file_name}" for tsl_file in file_generator.library_files))

        create_readme()