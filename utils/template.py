import logging
from pathlib import Path

from jinja2 import Template, Environment

from utils.file import BadSuffixError
from utils.log import LogInit, log
from utils.singleton import Singleton
from utils.yaml import YamlDataType


class TVLTemplate:
    @LogInit()
    def __init__(self, env, template: str) -> None:
        self.__template = env.from_string(template)

    @log
    def render(self, data: YamlDataType) -> str:
        return self.__template.render(data)


class TVLTemplateFactory(metaclass=Singleton):
    @LogInit()
    def __init__(self):
        self.__jinja_env = Environment(trim_blocks=True, lstrip_blocks=True)

    @log(successLevel=logging.INFO)
    def create_from_file(self, template_file_path: Path) -> TVLTemplate:
        if template_file_path.is_file():
            if template_file_path.suffix == ".template":
                return TVLTemplate(self.__jinja_env, template_file_path.read_text())
            else:
                raise BadSuffixError(
                    f"File has the wrong format. Only template files are supported.", {"filename": template_file_path})
        else:
            raise FileNotFoundError(f"File does not exist.", {"filename": template_file_path})