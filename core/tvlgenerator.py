import copy
import os.path
from pathlib import Path
from typing import List, Dict

from core.tvl_config import TVLGeneratorConfig
from core.tvlgen_file import TVLYamlFileTree, TVLFile
from core.model.tvl_primitive import TVLPrimitiveClass, TVLPrimitiveClassSet
from utils.log import LogInit, log
from utils.singleton import Singleton
from utils.yaml import YamlLoader, YamlDataType


class TVLGenerator(metaclass=Singleton):
    @LogInit()
    def __init__(self,
                 generation_out_path: Path,
                 template_root_path: Path,
                 schema_file: Path,
                 tvl_data_path: Path,
                 static_files_base_path: Path
                 ):
        self.__config = TVLGeneratorConfig(generation_out_path, template_root_path, schema_file)
        self.__tvl_data_path: Path = tvl_data_path
        self.__primitive_classes_file: Path = tvl_data_path.joinpath("primitive_classes.yaml")
        self.__yaml_file_tree = TVLYamlFileTree(tvl_data_path)
        self.__primitive_classes: TVLPrimitiveClassSet = TVLPrimitiveClassSet()
        self.__static_files_base_path: Path = static_files_base_path
        # self.__extension_files: List[Path] = []


    @log
    def import_data(self) -> None:
        for primitive_class_dict in YamlLoader().load(self.__yaml_file_tree.primitive_classes_file):
            tmp: TVLPrimitiveClass = TVLPrimitiveClass(primitive_class_dict)
            # if tmp not in self.__primitive_classes:
            self.__primitive_classes.add(tmp)
        for primitive_file in self.__yaml_file_tree.relevant_primitive_files():
            primitive_class_obj = self.__primitive_classes.get_by_file(primitive_file)
            primitive_class_obj.reset()
            for primitive_data_dict in YamlLoader().load_all(primitive_file):
                primitive_class_obj.add_primitive_dict(primitive_data_dict)

        # self.__extension_files = [extension_file for extension_file in self.__yaml_file_tree.relevant_extension_files()]

    @log
    def create_generated_files(self, relevant_lscpu_flags: List[str] = None) -> None:

        for primitive_class in self.__primitive_classes.get_classes():
            declaration_file: TVLFile = TVLFile(Path(f"./generated/declarations/"), Path(f"{primitive_class.name}"),
                                                primitive_class.description_data)
            definition_files: Dict[str, TVLFile] = dict()

            for primitive in primitive_class.get_primitives():
                declaration_file.add_code(primitive.render_declaration())
                declaration_file.add_includes(primitive.get_declaration_includes())

                for definition in primitive.get_definitions(relevant_lscpu_flags):
                    if definition.target_extension not in definition_files:
                        definition_files[definition.target_extension] = TVLFile(
                            Path(f"./generated/definitions/{primitive_class.name}/"),
                            Path(f"{primitive_class.name}_{definition.target_extension}"),
                            primitive_class.get_updated_description_data(
                                f"Implementation for {definition.target_extension}"
                            )
                        )
                        # upon first creation we add the declaration header
                        rel_path_to_decl: Path = Path(
                                os.path.relpath(
                                    str(declaration_file.file.parent),
                                    str(definition_files[definition.target_extension].file.parent)
                                )
                            ).joinpath(declaration_file.file.name)
                        definition_files[definition.target_extension].add_include(
                            f"\"{str(rel_path_to_decl)}\""
                        )
                    definition_files[definition.target_extension].add_code(definition.render(extension_dicts[definition.target_extension]))
                    definition_files[definition.target_extension].add_includes(definition.includes)
            declaration_file.generate()
            for definition_file_key in definition_files:
                definition_files[definition_file_key].generate()
                headers_to_be_included_by_tvl_generated_hpp.append(definition_files[definition_file_key].file)
            del declaration_file
            del definition_files
        generated_include_file: TVLFile = TVLFile(Path(f"./generated"), Path(f"tvl_generated"),
                                                  { "brief_description": "yolo"})
        for primitive_definition_header in headers_to_be_included_by_tvl_generated_hpp:
            rel_path_to_def: Path = Path(
                    os.path.relpath(primitive_definition_header.parent, generated_include_file.file.parent)
                ).joinpath(primitive_definition_header.name)
            generated_include_file.add_include(f"\"{str(rel_path_to_def)}\"")


        generated_include_file.generate()

    @log
    def create_static_files(self) -> None:
        for file in self.__static_files_base_path.rglob("*.yaml"):
            data_dict : YamlDataType = YamlLoader().load(file)
            target_path: Path = file.parent.relative_to(self.__static_files_base_path)
            target_file: Path = Path(file.stem)
            tvlFile: TVLFile = TVLFile(target_path, target_file, data_dict)
            if "includes" in data_dict:
                tvlFile.add_includes((include for include in data_dict["includes"]))

            if "implementations" in data_dict:
                for implementation in data_dict["implementations"]:
                    tvlFile.add_code(implementation)
            tvlFile.generate()
