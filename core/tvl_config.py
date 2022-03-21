import copy
from pathlib import Path

from config.tvlgen_schema import TVLExtensionSchema, TVLPrimitiveSchema, \
    TVLPrimitiveClassSchema
from config.tvlgen_templates import TVLDocumentationTemplate, TVLLicenseTemplate, \
    TVLExtensionTemplate, TVLPrimitiveDeclarationTemplate, TVLPrimitiveDefinitionTemplate, TVLHeaderFileTemplate
from utils.log import LogInit
from utils.singleton import Singleton
from utils.yaml import YamlLoader, YamlDataType


class TVLGeneratorConfig(metaclass=Singleton):
    @LogInit()
    def __init__(self,
                 generation_out_path: Path,
                 template_root_path: Path,
                 schema_file: Path
                 ) -> None:

        # if generation_out_path.is_absolute():
        #     raise Exception(f"Provided path should be relative but is absolut. ({generation_out_path}).")

        generation_out_path.mkdir(parents=True, exist_ok=True)

        self.__generation_out_path: Path = generation_out_path
        #initialize Templates (singletons)
        self.__documentation_template: TVLDocumentationTemplate = TVLDocumentationTemplate(template_root_path)
        self.__license_template: TVLLicenseTemplate = TVLLicenseTemplate(template_root_path)
        self.__extension_template: TVLExtensionTemplate = TVLExtensionTemplate(template_root_path)
        self.__declaration_template: TVLPrimitiveDeclarationTemplate = TVLPrimitiveDeclarationTemplate(template_root_path)
        self.__definition_template: TVLPrimitiveDefinitionTemplate = TVLPrimitiveDefinitionTemplate(template_root_path)
        self.__header_file_template: TVLHeaderFileTemplate = TVLHeaderFileTemplate(template_root_path)
        a = YamlLoader()
        #initialize Schemes (singletons)
        complete_schema: YamlDataType = YamlLoader().load(schema_file)
        self.__extension_schema: TVLExtensionSchema = TVLExtensionSchema(copy.deepcopy(complete_schema["extension"]))
        self.__primitive_schema: TVLPrimitiveSchema = TVLPrimitiveSchema(copy.deepcopy(complete_schema["primitive"]))
        self.__primitive_class_schema: TVLPrimitiveClassSchema = TVLPrimitiveClassSchema(copy.deepcopy(complete_schema["primitive_classes"]))
        del(complete_schema)

    @property
    def generation_out_base_path(self) -> Path:
        return self.__generation_out_path

    @property
    def documentation_template(self) -> TVLDocumentationTemplate:
        return self.__documentation_template

    @property
    def license_template(self) -> TVLLicenseTemplate:
        return self.__license_template

    @property
    def extension_template(self) -> TVLExtensionTemplate:
        return self.__extension_template

    @property
    def declaration_template(self) -> TVLPrimitiveDeclarationTemplate:
        return self.__declaration_template

    @property
    def primitive_schema(self) -> TVLPrimitiveSchema:
        return self.__primitive_schema

    @property
    def definition_template(self) -> TVLPrimitiveDefinitionTemplate:
        return self.__definition_template

    @property
    def header_file_template(self) -> TVLHeaderFileTemplate:
        return self.__header_file_template

    @property
    def tvl_namespace(self) -> str:
        return "tvl"




