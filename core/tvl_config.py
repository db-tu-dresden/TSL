import argparse
import copy
import logging.config
import pathlib
import re
from pathlib import Path
from typing import Dict, Any, Generator, List

from jinja2 import Template, Environment, FileSystemLoader

from utils.file_template import load_template_from_file
from utils.file_utils import StaticFileTree
from utils.git_utils import GitUtils
from utils.requirement import requirement
from utils.yaml_schema import Schema
from utils.yaml_utils import yaml_load


class TVLGeneratorConfig:
    class JinjaConfig:
        def __init__(self, root_path: Path):
            self.__env = Environment(trim_blocks=True, lstrip_blocks=True, loader=FileSystemLoader(root_path))

        @property
        def env(self) -> Environment:
            return self.__env

    def __init__(self) -> None:
        self.include_guard_regex = re.compile(r"[/\.\\: ]")
        self.path_seperator: str = pathlib.os.sep
        self.__valid = False
        self.__logger = None
        self.__jinja_templates: Dict[str, str] = dict()
        self.__schemes: Dict[str, Schema] = dict()
        self.__general_configuration_dict: Dict[str, Any] = None
        self.__extensions_file_tree: StaticFileTree = None
        self.__primitives_file_tree: StaticFileTree = None
        self.__configuration_files_dict: Dict[str, Any] = None
        self.__jinja_config = None

    def __setup(self, config_dict: dict) -> None:
        self.__general_configuration_dict = copy.deepcopy(config_dict["configuration"])
        self.__configuration_files_dict = copy.deepcopy(config_dict["configuration_files"])

        def configure_logger():
            """
            Configure Logger
            """
            logging.config.dictConfig(yaml_load(Path(self.__configuration_files_dict["log_config_file"]).resolve()))
            self.__logger = logging.getLogger(f"{self.__class__.__name__}")
            self.__logger.info(f"Started TVL Generator. Loaded Logging Context.",
                               extra={"decorated_funcName": "setup", "decorated_filename": "tvl_config.py"})

        def load_schemes():
            """
            Load Schema
            """
            schema = yaml_load(Path(self.__configuration_files_dict["schema_file"]).resolve())
            self.__schemes["extension"] = Schema(copy.deepcopy(schema["extension"]))
            self.__logger.info(f"Loaded schema for extension.",
                               extra={"decorated_funcName": "setup", "decorated_filename": "tvl_config.py"})
            self.__schemes["primitive"] = Schema(copy.deepcopy(schema["primitive"]))
            self.__logger.info(f"Loaded schema for primitive.",
                               extra={"decorated_funcName": "setup", "decorated_filename": "tvl_config.py"})
            self.__schemes["primitive_class"] = Schema(copy.deepcopy(schema["primitive_class"]))
            self.__logger.info(f"Loaded schema for primitive class.",
                               extra={"decorated_funcName": "setup", "decorated_filename": "tvl_config.py"})
            del schema

        def load_jinja_templates():
            """
            Load Templates.
            Iterates through the jinja_templates basepath. All files with *.template-extension are gathered and inserted
            into the self.__jinja_templates dict. The key results from the relative path, where all path seperators are
            substituted by '::'.
            """
            template_root_path: Path = Path(self.__configuration_files_dict["jinja_templates"]["root_path"]).resolve()
            for template_file in StaticFileTree(template_root_path, "*.template").get_files():
                template_name = re.sub(rf"{self.path_seperator}", "::", str(template_file.relative_to(template_root_path)))[
                                : -len(''.join(template_file.suffix))]
                self.__jinja_templates[template_name] = load_template_from_file(template_file)
                self.__logger.info(f"Loaded template {template_name} (from file {template_file}).",
                                   extra={"decorated_funcName": "setup", "decorated_filename": "tvl_config.py"})
            self.__jinja_config = TVLGeneratorConfig.JinjaConfig(template_root_path)

        def create_file_tress_for_primitive_data():
            """
            Create File Tree for primitive data
            """
            primitive_data_root_path: Path = Path(self.__configuration_files_dict["primitive_data"]["root_path"])
            primitives_root_path: Path = Path(self.__configuration_files_dict["primitive_data"]["primitives_path"])
            self.__primitives_file_tree = StaticFileTree(primitive_data_root_path.joinpath(primitives_root_path), "*.yaml")
            extensions_root_path: Path = Path(self.__configuration_files_dict["primitive_data"]["extensions_path"])
            self.__extensions_file_tree = StaticFileTree(primitive_data_root_path.joinpath(extensions_root_path), "*.yaml")

        def load_library_configs():
            """
            Set Path to static files
            """

        configure_logger()
        load_schemes()
        load_jinja_templates()
        create_file_tress_for_primitive_data()
        load_library_configs()

    def setup(self, config_dict: dict) -> None:
        """
        Setup function for global configuration class. If the configuration class is already setup, nothing happens.
        :param config_dict: Dictionary containing all relevant configurations.
        :return:
        """
        if not self.__valid:
            self.__setup(config_dict)

    @requirement(entry_name="NonEmptyString")
    def get_template(self, template_name: str) -> Template:
        """
        Retrieves a specific Jinja2 template.
        :param template_name: Name of the template (e.g., 'license', 'extension',...).
        :return:  Copy of the requested Jinja2 Template object.
        """
        if template_name not in self.__jinja_templates:
            """
            If the provided template_name is not fully qualified (without prefix), we apply a pattern search
            """
            regex = re.compile(rf".*{template_name}.*")
            result_keys = [key for key in self.__jinja_templates.keys() if regex.match(key)]
            if len(result_keys) == 0:
                self.__logger.critical(f"Template {template_name} not found.",
                                       extra={"decorated_funcName": "get_template",
                                              "decorated_filename": "tvl_config.py"})
                raise ValueError
            if len(result_keys) > 1:
                self.__logger.critical(f"Template {template_name} is ambiguous. "
                                       f"Found following templates {result_keys}.",
                                       extra={"decorated_funcName": "get_template",
                                              "decorated_filename": "tvl_config.py"})
                raise ValueError
            return self.__jinja_config.env.from_string(self.__jinja_templates[result_keys[0]])
        return self.__jinja_config.env.from_string(self.__jinja_templates[template_name])

    @requirement(entry_name="NonEmptyString")
    def get_schema(self, schema_entry_name: str) -> Schema:
        """
        Retrieves a specific schema used for Jinja2 templates.
        :param schema_entry_name: Name of the schema (e.g., 'extension', 'primitive').
        :return: Copy of the requested schema object.
        """
        if schema_entry_name not in self.__schemes:
            self.__logger.critical(f"Schema {schema_entry_name} not found.",
                                   extra={"decorated_funcName": "get_schema", "decorated_filename": "tvl_config.py"})
            raise ValueError
        return copy.deepcopy(self.__schemes[schema_entry_name])

    @requirement(entry_name="NonEmptyString")
    def get_config_entry(self, entry_name: str) -> Any:
        """
        Retrieves a specific configuration value.
        :param entry_name: Name of an entry (e.g., 'lib_generation_out_path').
        :return: Copy of the requested configuration object.
        """
        if entry_name not in self.__general_configuration_dict:
            self.__logger.critical(f"Entry {entry_name} not found.",
                                   extra={"decorated_funcName": "get_schema", "decorated_filename": "tvl_config.py"})
            raise ValueError
        return copy.deepcopy(self.__general_configuration_dict[entry_name])

    @requirement(entry_name="NonEmptyString")
    def get_config_entry_silent(self, entry_name: str) -> bool:
        """
        Retrieves a specific configuration value.
        :param entry_name: Name of an entry (e.g., 'lib_generation_out_path').
        :return: Copy of the requested configuration object.
        """
        if entry_name not in self.__general_configuration_dict:
            raise ValueError
        return copy.deepcopy(self.__general_configuration_dict[entry_name])

    @requirement(entry_name="NonEmptyString")
    def get_library_config_entry(self, entry_name: str) -> Any:
        """
        Retrieves a specific configuration value.
        :param entry_name: Name of an entry (e.g., 'lib_generation_out_path').
        :return: Copy of the requested configuration object.
        """
        if entry_name not in self.__general_configuration_dict["library"]:
            self.__logger.critical(f"Entry {entry_name} not found.",
                                   extra={"decorated_funcName": "get_schema", "decorated_filename": "tvl_config.py"})
            raise ValueError
        return copy.deepcopy(self.__general_configuration_dict["library"][entry_name])

    @requirement(entry_name="NonEmptyString")
    def get_configuration_files_entry(self, entry_name: str) -> Any:
        """
        Retrieves a specific configuration value.
        :param entry_name: Name of an entry (e.g., 'lib_generation_out_path').
        :return: Copy of the requested configuration object.
        """
        if entry_name not in self.__configuration_files_dict:
            self.__logger.critical(f"Entry {entry_name} not found.",
                                   extra={"decorated_funcName": "get_schema", "decorated_filename": "tvl_config.py"})
            raise ValueError
        return copy.deepcopy(self.__configuration_files_dict[entry_name])

    @property
    def lib_namespace(self) -> str:
        return self.get_config_entry("namespace")

    @property
    def lib_header_file_extension(self) -> str:
        return self.get_config_entry("header_file_extension")

    @property
    def lib_source_file_extension(self) -> str:
        return self.get_config_entry("source_file_extension")

    @property
    def generation_out_path_unresolved(self) -> Path:
        return Path(self.get_config_entry("root_path"))

    @property
    def generation_out_path(self) -> Path:
        return self.generation_out_path_unresolved.resolve()

    @property
    def lib_root_path(self) -> Path:
        return self.generation_out_path.joinpath(self.get_library_config_entry("root_path"))

    @property
    def lib_root_header(self) -> Path:
        return self.lib_root_path.joinpath(
            self.get_library_config_entry("top_level_header_fname")).with_suffix(
            self.lib_header_file_extension)

    @property
    def lib_generated_files_root_path(self) -> Path:
        return self.lib_root_path.joinpath(self.get_library_config_entry("hardware_specific_files")["root_path"])

    @property
    def lib_static_files_root_path(self) -> Path:
        return self.lib_root_path.joinpath(self.get_library_config_entry("static_files")["root_path"])

    @property
    def lib_generated_files_root_header(self) -> Path:
        confs = self.get_library_config_entry("hardware_specific_files")
        return self.lib_root_path.joinpath(confs["root_path"]).joinpath(confs["top_level_header_fname"]).with_suffix(
            self.lib_header_file_extension)

    @property
    def compiler_architecture_prefix(self) -> str:
        return self.get_config_entry("compiler_architecture_prefix")

    @property
    def default_types(self) -> List[str]:
        return self.get_config_entry("default_types")

    @property
    def use_concepts(self) -> bool:
        return self.get_config_entry("use_concepts")

    @property
    def emit_workaround_warnings(self) -> bool:
        return self.get_config_entry("emit_workaround_warnings")

    @property
    def silent_warnings(self) -> List[str]:
        return self.get_config_entry("silent_warnings")
    @property
    def static_files_root_path(self) -> Path:
        return Path(self.get_configuration_files_entry("static_files")["root_path"])

    @property
    def static_lib_files_root_path(self) -> Path:
        return self.static_files_root_path.joinpath(self.get_configuration_files_entry("static_files")["lib"])

    def static_lib_files(self) -> Generator[Path, None, None]:
        for file in self.static_lib_files_root_path.rglob("*.yaml"):
            yield file

    def primitive_files(self) -> Generator[Path, None, None]:
        yield from self.__primitives_file_tree.get_files()

    def extension_files(self) -> Generator[Path, None, None]:
        yield from self.__extensions_file_tree.get_files()

    def modified_primitive_files(self) -> Generator[Path, None, None]:
        yield from self.__primitives_file_tree.get_recently_updated_files()

    def modified_extension_files(self) -> Generator[Path, None, None]:
        yield from self.__extensions_file_tree.get_recently_updated_files()

    def get_primitive_files_path(self, entry_name: str) -> Path:
        return Path(self.__configuration_files_dict["primitive_data"]["root_path"]).joinpath(
            self.__configuration_files_dict["primitive_data"][entry_name])

    @requirement(part="NonEmptyString")
    def get_generation_path(self, part: str) -> Path:
        paths = self.get_library_config_entry("hardware_specific_files")
        return self.lib_generated_files_root_path.joinpath(paths[part])

    @requirement(expansion_name="NonEmptyString")
    def get_expansion_config(self, expansion_name: str) -> dict:
        expansions = self.get_config_entry("expansions")
        if expansion_name in expansions:
            return expansions[expansion_name]
        raise ValueError(f"Unknown expansion {expansion_name}")

    @requirement(expansion_name="NonEmptyString")
    def expansion_enabled(self, expansion_name: str) -> bool:
        conf = self.get_expansion_config(expansion_name)
        if "enabled" in conf:
            return conf["enabled"]
        return False

    @requirement(expansion_name="NonEmptyString")
    def static_expansion_files(self, expansion_name: str) -> Generator[Path, None, None]:
        expansion_config = self.get_expansion_config(expansion_name)
        if "static_files" in expansion_config:
            for file in Path(expansion_config["static_files"]["root_path"]).rglob("*.yaml"):
                yield file

    @property
    def git_config_as_list(self) -> List[str]:
        return GitUtils.get_git_data().create_indented_list()

    @property
    def get_version_str(self) -> str:
        return GitUtils.get_git_data().create_version_str()

    @property
    def print_output_only(self) -> bool:
        try:
            result = self.get_config_entry_silent("print_output_only")
            return result
        except ValueError:
            return False

    @property
    def emit_tsl_extensions_to_file(self) -> bool:
        try:
            result = self.get_config_entry_silent("emit_tsl_extensions_to")
            return True
        except ValueError:
            return False

    @property
    def tsl_extensions_yaml_output_path(self) -> Path:
        return Path(self.get_config_entry("emit_tsl_extensions_to"))


config = TVLGeneratorConfig()


def add_bool_arg(parser, name, dest, help_true_prefix="", help_false_prefix="", default=True, **kwargs):
    true_args = copy.deepcopy(kwargs)
    false_args = kwargs
    if "help" in kwargs:
        if default:
            true_args["help"] = f"{help_true_prefix}{true_args['help']} (Default)"
            false_args["help"] = f"{help_false_prefix}{true_args['help']}"
        else:
            true_args["help"] = f"{help_true_prefix}{true_args['help']}"
            false_args["help"] = f"{help_false_prefix}{true_args['help']} (Default)"
    else:
        if default:
            true_args["help"] = f"(Default)"
            false_args["help"] = f""
        else:
            true_args["help"] = f""
            false_args["help"] = f"(Default)"
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--' + name, dest=dest, action='store_true', **true_args)
    group.add_argument('--no-' + name, dest=dest, action='store_false', **false_args)
    parser.set_defaults(**{dest:default})



def parse_args() -> dict:
    parser = argparse.ArgumentParser(description="TVL Generator", epilog="To apply fine-tuned changes to the generator please change the config files (config/default_conf.yaml and config/log_conf.yaml).")
    parser.add_argument('-o', '--out', type=pathlib.Path, help="Generation output path.", required=False,
                                  dest='configuration:root_path', metavar="OutPath")
    parser.add_argument('-i', '--in', type=pathlib.Path,
                        help='Path where TVL primitive and extension files are located (relative to the script location or absolut).',
                        dest='configuration_files:primitive_data:root_path', metavar="InPath")
    parser.add_argument('--targets', default=None, nargs='*',
                        help='List of target flags which match the lscpu_flags from the extension/primitive files.',
                        dest='targets')

    parser.add_argument('--print-outputs-only', dest='configuration:print_output_only', action="store_true",
                        help="Print only the files which would be generated as list (separator by semicolon)")
    parser.add_argument('--emit-tsl-extensions-to', type=pathlib.Path, dest='configuration:emit_tsl_extensions_to', required=False,
                        help="", metavar="ExOutPath")

    add_bool_arg(parser, 'workaround-warnings', 'configuration:emit_workaround_warnings', "Enable ", "Disable ", True, help='workaround warnings', required=False)
    add_bool_arg(parser, 'concepts', 'configuration:use_concepts', "Enable ", "Disable ", True, help='C++20 concepts.', required=False)
    add_bool_arg(parser, 'draw-test-dependencies', 'configuration:expansions:unit_tests:draw_dependency_graph', "Enable ", "Disable ", False, help="draw dependency graph for test generation", required=False)
    add_bool_arg(parser, 'cmake', 'configuration:expansions:cmake:enabled', "Activate ", "Deactivate ", True,
                 help="CMake generation", required=False)
    add_bool_arg(parser, 'testing', 'configuration:expansions:unit_tests:enabled', "Activate ", "Deactivate ", True,
                 help="Unit test generation", required=False)
    regex = re.compile(r"([^:]+):{0,1}")
    args = parser.parse_args()
    args_dict = dict()
    for key, value in vars(args).items():
        if value is not None:
            current_dict = args_dict
            matches = regex.findall(key)
            for match in matches[:-1]:
                if match not in current_dict:
                    current_dict[match] = dict()
                current_dict = current_dict[match]
            current_dict[matches[-1]] = value

    if "targets" not in args_dict:
        args_dict["targets"] = None
    return args_dict

