import datetime
from pathlib import Path

from utils.log import LogInit, log
from utils.singleton import Singleton
from utils.template import TVLTemplate, TVLTemplateFactory
from utils.yaml import YamlDataType


class TVLDocumentationTemplate(metaclass=Singleton):
    @LogInit()
    def __init__(self, template_root_path: Path) -> None:
        self.__file_template: TVLTemplate = TVLTemplateFactory().create_from_file(
            template_root_path.joinpath("tvl_doxygen_file.template"))
        self.__function_template: TVLTemplate = TVLTemplateFactory().create_from_file(
            template_root_path.joinpath("tvl_doxygen_function.template"))

    @log
    def render_file_documentation(self, data: YamlDataType) -> str:
        return self.__file_template.render(data)

    @log
    def render_function_documentation(self, data: YamlDataType) -> str:
        return self.__function_template.render(data)


class TVLLicenseTemplate(metaclass=Singleton):
    @LogInit()
    def __init__(self, template_root_path: Path) -> None:
        self.__license_template: TVLTemplate = TVLTemplateFactory().create_from_file(
            template_root_path.joinpath("tvl_license.template"))

    @log
    def render(self) -> str:
        return self.__license_template.render({"year": datetime.date.today().year})


class TVLExtensionTemplate(metaclass=Singleton):
    @LogInit()
    def __init__(self, template_root_path) -> None:
        self.__extension_template: TVLTemplate = TVLTemplateFactory().create_from_file(
            template_root_path.joinpath("tvl_extension.template"))

    @log
    def render(self, data: YamlDataType) -> str:
        return self.__extension_template.render(data)


class TVLPrimitiveDeclarationTemplate(metaclass=Singleton):
    @LogInit()
    def __init__(self, template_root_path) -> None:
        self.__declaration_template: TVLTemplate = TVLTemplateFactory().create_from_file(
            template_root_path.joinpath("tvl_primitive_declaration.template"))

    @log
    def render(self, data: YamlDataType) -> str:
        return self.__declaration_template.render(data)


class TVLPrimitiveDefinitionTemplate(metaclass=Singleton):
    @LogInit()
    def __init__(self, template_root_path) -> None:
        self.__definition_template: TVLTemplate = TVLTemplateFactory().create_from_file(
            template_root_path.joinpath("tvl_primitive_definition.template"))

    @log
    def render(self, data: YamlDataType) -> str:
        return self.__definition_template.render(data)


class TVLHeaderFileTemplate(metaclass=Singleton):
    @LogInit()
    def __init__(self, template_root_path) -> None:
        self.__header_template: TVLTemplate = TVLTemplateFactory().create_from_file(
            template_root_path.joinpath("tvl_header_file.template"))

    @log
    def render(self, data: YamlDataType) -> str:
        return self.__header_template.render(data)



