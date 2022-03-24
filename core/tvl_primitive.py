from __future__ import annotations
import copy
import logging
from pathlib import Path
from typing import List, Generator, Set, Tuple, Dict, Union

from jinja2 import Template

from core.tvl_config import TVLGeneratorConfig
from utils.log import LogInit, log
from utils.yaml import YamlDataType


class TVLPrimitiveDefinition:
    @LogInit()
    def __init__(self, data_dict: YamlDataType) -> None:
        self.__data: YamlDataType = copy.deepcopy(data_dict)
        self.__target_extension : str = self.__data["target_extension"]
        self.__ctype : str = self.__data["ctype"]
        self.__lscpu_flags : List[str] = self.__data["lscpu_flags"]
        self.__data["tvl_function_doxygen"] = TVLGeneratorConfig().documentation_template.render_function_documentation(
            self.__data)
        implementation_template = Template(self.__data["implementation"])
        if "_mm512_add_epi" in self.__data["implementation"]:
            print("NOW")
        self.__data["implementation"] = implementation_template.render(self.__data)

    @property
    def data(self) -> YamlDataType:
        return self.__data

    @staticmethod
    def schema_identifier() -> str:
        return "definitions"

    @property
    def target_extension(self) -> str:
        return self.__target_extension

    @property
    def ctype(self) -> str:
        return self.__ctype

    @property
    def includes(self) -> Generator[str, None, None]:
        return (include for include in self.__data["includes"])

    @log
    def render(self) -> str:
        return TVLGeneratorConfig().definition_template.render(self.data)

    def __hash__(self):
        t: Tuple[str, str] = (self.__target_extension, self.__ctype)
        return t.__hash__()

    def __eq__(self, other: TVLPrimitiveDefinition) -> bool:
        if not isinstance(other, TVLPrimitiveDefinition):
            return False
        return self.__data == other.data

    def __ne__(self, other: TVLPrimitiveDefinition) -> bool:
        return not self == other

    def __repr__(self):
        return f"{self.__target_extension}::{self.__ctype}->{self.__data['implementation']}"

    def similar_to(self, other: TVLPrimitiveDefinition) -> bool:
        return (self.__ctype==other.ctype) and (self.__target_extension==other.target_extension)

    def is_relevant(self, relevant_lscpu_flags: List[str] = None) -> bool:
        if relevant_lscpu_flags is None:
            return True
        relevant_lscpu_flags_set: Set[str] = set(relevant_lscpu_flags)
        own_lscpu_flags_set: Set[str] = set(self.__lscpu_flags)
        return own_lscpu_flags_set <= relevant_lscpu_flags_set

    def get_prio_score(self, relevant_lscpu_flags: List[str]):
        relevant_lscpu_flags_set: Set[str] = set(relevant_lscpu_flags)
        own_lscpu_flags_set: Set[str] = set(self.__lscpu_flags)
        # we assume, that self is relevant
        # if multiple definitions / specializations exists for different lscpu flags, we choose the definition with the most overlap in relevant_lscpu_flags
        return len(own_lscpu_flags_set.intersection(relevant_lscpu_flags))


class TVLPrimitiveDefinitionContainer:
    @LogInit()
    def __init__(self):
        self.__definitions: Dict[object, List[TVLPrimitiveDefinition]] = dict()

    @log
    def add_definition(self, definition: TVLPrimitiveDefinition) -> None:
        hash_value = hash(definition)
        if hash_value in self.__definitions:
            if not definition.similar_to(self.__definitions[hash_value][0]):
                raise Exception(f"Definition {repr(definition)} maps to the same hash as {repr(self.__definitions[hash_value][0])} but they are not similar.")
            self.__definitions[hash_value].append(definition)
        else:
            self.__definitions[hash_value] = [definition]

    @log
    def get_relevant_definitions(self, relevant_lscpu_flags: List[str] = None) -> Generator[
        TVLPrimitiveDefinition, None, None]:
        for key in self.__definitions:
            definitions: List[TVLPrimitiveDefinition] = self.__definitions[key]
            max_scored_definition = None
            max_score = 0
            for definition in definitions:
                if relevant_lscpu_flags is None:
                    yield definition #this will produce compile time errors if multiple definitions are in the list
                else:
                    if definition.is_relevant(relevant_lscpu_flags):
                        tmp_score = definition.get_prio_score(relevant_lscpu_flags)
                        if tmp_score > max_score:
                            max_scored_definition = definition
                            max_score = tmp_score
            if relevant_lscpu_flags is not None and max_scored_definition is not None:
                yield max_scored_definition



class TVLPrimitiveDeclaration:
    @LogInit()
    def __init__(self, data_dict: YamlDataType) -> None:
        self.__data: YamlDataType = copy.deepcopy(data_dict)
        self.__data["tvl_function_doxygen"] = TVLGeneratorConfig().documentation_template.render_function_documentation(self.__data)

    @property
    def data(self) -> YamlDataType:
        return self.__data

    def __repr__(self):
        params = ", ".join([param['ctype'] for param in self.__data['parameters']])
        return f"{self.__data['returns']['ctype']} {self.__data['primitive_name']}({params})"


class TVLPrimitive:
    @LogInit()
    def __init__(self, data_dict: YamlDataType) -> None:
        data_dict = TVLGeneratorConfig().primitive_schema.validate(data_dict)
        to_exclude_from_declaration: List[str] = [TVLPrimitiveDefinition.schema_identifier()]

        declaration_dict: YamlDataType = {key: data_dict[key] for key in data_dict if
                                          key not in to_exclude_from_declaration}
        self.__declaration: TVLPrimitiveDeclaration = TVLPrimitiveDeclaration(
            declaration_dict
        )
        self.__definitions: TVLPrimitiveDefinitionContainer = TVLPrimitiveDefinitionContainer()
        if "definitions" in data_dict:
            for definition in data_dict["definitions"]:
                types = copy.deepcopy(definition["ctype"])
                for ctype in types:
                    definition["ctype"] = ctype
                    self.__definitions.add_definition(
                        TVLPrimitiveDefinition(
                            {**declaration_dict, **definition}
                        )
                    )

        del data_dict

    @log
    def get_declaration_data(self) -> YamlDataType:
        return self.__declaration.data

    @log
    def get_declaration_includes(self) -> Generator[str, None, None]:
        yield from self.__declaration.data["includes"]

    @log
    def get_definitions_data(self) -> Generator[YamlDataType, None, None]:
        for definition in self.__definitions:
            yield definition.data

    @log
    def render_declaration(self) -> str:

        self.log(logging.INFO, f"Adding declaration {repr(self.__declaration)}")
        return TVLGeneratorConfig().declaration_template.render(self.get_declaration_data())

    # @log
    # def _get_relevant_definitions(self, relevant_lscpu_flags: List[str] = None) -> Generator[
    #     TVLPrimitiveDefinition, None, None]:
    #     yield from self.__definitions.get_relevant_definitions(relevant_lscpu_flags)
        # if relevant_lscpu_flags is not None:
        #     relevant_lscpu_flags_set: Set[str] = set(relevant_lscpu_flags)
        # else:
        #     relevant_lscpu_flags_set: Set[str] = set()
        # for definition in self.__definitions:
        #     if not relevant_lscpu_flags_set or relevant_lscpu_flags_set < set(definition.data["lscpu_flags"]):
        #         yield definition

    # @log
    # def render_definitions(self, relevant_lscpu_flags: List[str] = None) -> Generator[str, None, None]:
    #     for definition in self._get_relevant_definitions(relevant_lscpu_flags):
    #         self.log(logging.INFO, f"Adding definition {repr(definition)}")
    #         yield TVLGeneratorConfig().definition_template.render(definition.data)

    @log
    def get_definitions(self, relevant_lscpu_flags: List[str] = None) -> Generator[TVLPrimitiveDefinition, None, None]:
        yield from self.__definitions.get_relevant_definitions(relevant_lscpu_flags)


    # @log
    # def get_definitions_includes(self, relevant_lscpu_flags: List[str] = None) -> Generator[List[str], None, None]:
    #     for definition in self.__definitions.get_relevant_definitions(relevant_lscpu_flags):
    #         yield definition.data["includes"]


class TVLPrimitiveClass:
    @LogInit()
    def __init__(self, data_dict: YamlDataType) -> None:
        self.__name: str = data_dict["name"]
        self.__description: str = data_dict["description"]
        self.__primitives: List[TVLPrimitive] = []

    @log
    def add_primitive_dict(self, data_dict: YamlDataType) -> None:
        self.__primitives.append(TVLPrimitive(data_dict))

    @log
    def reset(self) -> None:
        self.__primitives = []

    @property
    def name(self) -> str:
        return self.__name

    @property
    def description_data(self)-> YamlDataType:
        return {"file_description": self.__description}

    def get_updated_description_data(self, msg: str) -> YamlDataType:
        return {"file_description": f"{self.__description} {msg}"}

    def get_primitives(self) -> Generator[TVLPrimitive, None, None]:
        yield from self.__primitives

    def __eq__(self, other: TVLPrimitiveClass) -> bool:
        if isinstance(other, TVLPrimitiveClass):
            return other.name == self.__name
        return False

    def __ne__(self, other: TVLPrimitiveClass) -> bool:
        return not self == other

    def __hash__(self):
        return hash(self.__name)

    def __repr__(self):
        return f"TVLPrimitiveClass < Name: {self.__name}. Description: {self.__description} >."


class TVLPrimitiveClassSet:
    @LogInit()
    def __init__(self):
        self.__primitive_class_set: Set[TVLPrimitiveClass] = set()

    @log
    def add_class(self, data_dict: YamlDataType) -> None:
        tmp: TVLPrimitiveClass = TVLPrimitiveClass(data_dict)
        if tmp not in self.__primitive_class_set:
            self.__primitive_class_set.add(tmp)
        else:
            self.log(logging.INFO, f"Did not added already present Primitive class {repr(tmp)}")

    @log
    def add(self, c: TVLPrimitiveClass) -> None:
        if c not in self.__primitive_class_set:
            self.__primitive_class_set.add(c)
        else:
            self.log(logging.INFO, f"Did not added already present Primitive class {repr(c)}")

    @log
    def get_by_name(self, name: str) -> TVLPrimitiveClass:
        tmp: TVLPrimitiveClass = TVLPrimitiveClass({"name": name, "description": ""})
        if tmp not in self.__primitive_class_set:
            raise ValueError(f"Could not get Primitive Class {name} by name.")
        for c in self.__primitive_class_set:
            if c.name == name:
                return c

    @log
    def get_by_file(self, file: Path) -> TVLPrimitiveClass:
        name = file.stem
        tmp: TVLPrimitiveClass = TVLPrimitiveClass({"name": name, "description": ""})
        if tmp not in self.__primitive_class_set:
            raise ValueError(f"Could not get Primitive Class {name} by name.")
        for c in self.__primitive_class_set:
            if c.name == name:
                return c

    def get_classes(self) -> Generator[TVLPrimitiveClass, None, None]:
        yield from self.__primitive_class_set
