from __future__ import annotations

import colorsys
import copy
import logging
from pathlib import Path
from typing import List, Set, Generator, Dict, Tuple

import networkx as nx

from generator.core.ctrl.tsl_lib import TSLLib

import wget

from generator.core.model.tsl_file import TSLSourceFile, TSLHeaderFile
from generator.core.model.tsl_primitive import TSLPrimitive
from generator.core.tsl_config import config
from generator.expansions.tsl_translation_unit import TSLTranslationUnit
from generator.utils.file_utils import strip_common_path_prefix
from generator.utils.log_utils import LogInit
from generator.utils.yaml_utils import YamlDataType, yaml_load

import os

class TSLPrimitiveTestCaseData:
    def __init__(self, class_name: str, primitive_name: str, data_dict: YamlDataType, lib_definitions: Dict[str, List[str]], conversion_types: Dict[str, Dict[str, Dict[str, List[str]]]], missing_primitive_definitions: Dict[str, Dict[str, List[str]]]):
        self.__class_name: str = class_name
        self.__primitive_name: str = primitive_name
        self.__test_name: str = data_dict["test_name"]
        self.__data_dict: YamlDataType = data_dict
        self.__lib_definitions: Dict[str, List[str]] = lib_definitions
        self.__conversion_types: Dict[str, Dict[str, Dict[str, List[str]]]] = conversion_types
        self.__complete_tests_lib_definitions: Dict[str, List[str]] = lib_definitions
        self.__missing_previous_tests: Dict[str, Dict[str, List[str]]] = dict()
        self.__missing_required_primitive_definitions: Dict[str, Dict[str, List[str]]] = missing_primitive_definitions
        self.__complete = True

    def set_missing_previous_tests(self, missing_tests: Dict[str, Dict[str, List[str]]]) -> None:
        self.__missing_previous_tests = copy.deepcopy(missing_tests)

    @property
    def missing_required_primitive_definitions(self) -> Dict[str, Dict[str, List[str]]]:
        return self.__missing_required_primitive_definitions

    @property
    def missing_previous_tests(self) -> Dict[str, Dict[str, List[str]]]:
        return self.__missing_previous_tests

    def has_dependencies(self) -> bool:
        if self.__data_dict["implicitly_reliable"]:
            return False
        if "requires" in self.__data_dict:
            return len(self.__data_dict["requires"]) > 0
        return False

    @property
    def dependencies(self) -> Generator[str, None, None]:
        for r in self.__data_dict["requires"]:
            yield r

    @property
    def class_name(self) -> str:
        return self.__class_name

    @property
    def primitive_name(self) -> str:
        return self.__primitive_name

    @property
    def test_name(self) -> str:
        return self.__test_name

    @property
    def data(self) -> YamlDataType:
        return self.__data_dict

    @property
    def lib_definitions(self) -> Dict[str, List[str]]:
        return copy.deepcopy(self.__lib_definitions)

    @property
    def conversion_types(self) -> Dict[str, Dict[str, Dict[str, List[str]]]]:
        return copy.deepcopy(self.__conversion_types)

    @property
    def complete_tests_lib_definitions(self):
        return self.__complete_tests_lib_definitions

    @complete_tests_lib_definitions.setter
    def complete_tests_lib_definitions(self, value: Dict[str, List[str]]):
        self.__complete_tests_lib_definitions = copy.deepcopy(value)

    def set_incomplete(self) -> None:
        self.__complete = False

    @property
    def complete(self) -> bool:
        return self.__complete

    def __eq__(self, other):
        if isinstance(other, TSLPrimitiveTestCaseData):
            if (self.test_name == other.test_name) and (self.__primitive_name == other.primitive_name):
                return True
        return False

    def __hash__(self):
        return hash((self.primitive_name, self.test_name))

    def __str__(self):
        return f"{self.primitive_name}_{self.test_name}"

    def __repr__(self):
        return str(self)


class TSLPrimitiveTestCase:
    def __init__(self, case_data: TSLPrimitiveTestCaseData):
        self.__data: YamlDataType = case_data.data
        self.__lib_definitions: Dict[str, List[str]] = case_data.lib_definitions
        self.__conversion_types: Dict[str, Dict[str, Dict[str, List[str]]]] = case_data.conversion_types
        self.__complete_tests_lib_definitions: Dict[str, List[str]] = case_data.complete_tests_lib_definitions
        self.__associated_primitive_class_name = case_data.class_name
        self.__associated_primitive_name = case_data.primitive_name
        self.__test_name = case_data.test_name
        self.__complete = case_data.complete
        self.__missing_previous_tests: Dict[str, Dict[str, List[str]]] = case_data.missing_previous_tests
        self.__missing_required_primitive_definitions: Dict[str, Dict[str, List[str]]] = case_data.missing_required_primitive_definitions

    def as_dict(self) -> dict:
        return { **self.__data, **{
            "lib_definitions": self.__lib_definitions,
            "conversion_types": self.__conversion_types,
            "complete_tests_lib_definitions":  self.__complete_tests_lib_definitions,
            "missing_previous_tests": self.__missing_previous_tests,
            "missing_required_primitive_definitions": self.__missing_required_primitive_definitions if len(self.__missing_required_primitive_definitions) > 0 else None,
            "primitive_class": self.__associated_primitive_class_name,
            "primitive_name": self.__associated_primitive_name
        }}

    @property
    def data_dict(self) -> YamlDataType:
        return self.__data

    @property
    def associated_primitive_name(self) -> str:
        return self.__associated_primitive_name

    @property
    def associated_primitive_class_name(self) -> str:
        return self.__associated_primitive_class_name


class TSLPrimitiveTest:
    def __init__(self, primitive_name: str, declaration: TSLPrimitive.Declaration):
        self.__primitive_name = primitive_name
        self.__test_cases: List[TSLPrimitiveTestCase] = []
        self.__declaration: dict = {key: value for key, value in declaration.data.items() if key not in ["parameters", "returns", "testing"]}
        self.__complete = False

    def add_case(self, case: TSLPrimitiveTestCase) -> None:
        self.__test_cases.append(case)
        self.__complete = True

    @property
    def primitive_name(self) -> str:
        return self.__primitive_name

    @property
    def cases(self) -> Generator[TSLPrimitiveTestCase, None, None]:
        for x in self.__test_cases:
            yield x

    def as_dict(self) -> dict:
        return {**self.__declaration, **{
            "cases": [x.as_dict() for x in self.__test_cases]
        }}

    @property
    def complete(self) -> bool:
        return self.__complete

    def has_tests(self) -> bool:
        return len(self.__test_cases) > 0

    def __eq__(self, other):
        if isinstance(other, TSLPrimitiveTest):
            if self.primitive_name == other.primitive_name:
                return True
        return False

    def __hash__(self):
        return hash(self.primitive_name)

    def __str__(self):
        return self.primitive_name

    def __repr__(self):
        return str(self)


class TSLPrimitiveClassTests:
    def __init__(self, primitive_class_name: str):
        self.__primitive_class_name: str = primitive_class_name
        self.__primitive_tests: List[TSLPrimitiveTest] = []

    def add_primitive_test(self, test: TSLPrimitiveTest):
        self.__primitive_tests.append(test)

    def sort(self) -> None:
        self.__primitive_tests.sort(key=lambda x: x.primitive_name)

    @property
    def primitive_class_name(self) -> str:
        return self.__primitive_class_name

    @property
    def primitive_tests(self) -> Generator[TSLPrimitiveTest, None, None]:
        for x in self.__primitive_tests:
            yield x

    def as_dict(self) -> dict:
        return {
            "class_name": self.__primitive_class_name,
            "primitive_tests": [x.as_dict() for x in self.__primitive_tests]
        }


class TSLTestSuite:
    @LogInit()
    def __init__(self, lib: TSLLib) -> None:
        self.__test_cases: List[TSLPrimitiveTestCaseData] = []
        self.__test_class_names: Set[str] = set()
        self.__primitive_test: Set[Tuple[str, str]] = set()
        known_definitions_names: Set[str] = {x for x in lib.primitive_class_set.definitions_names()}

        for primitive_class in lib.primitive_class_set:
            self.__test_class_names.add(primitive_class.name)
            for primitive in primitive_class:
                test_name_dict: Dict[str, int] = dict()
                self.__primitive_test.add((primitive_class.name, primitive.declaration.functor_name))
                if primitive.has_test():
                    primitive_definition_extension_ctype: Dict[str, List[str]] = primitive.specialization_dict()
                    missing_primitive_definitions: Dict[str, Dict[str, List[str]]] = dict()
                    for test in primitive.tests:
                        if test["test_name"] in test_name_dict:
                            test_name = f"{test['test_name']}_{test_name_dict[test['test_name']]}"
                            test_name_dict[test["test_name"]] += 1
                            test["test_name"] = test_name
                        if ("requires" in test) and (len(test['requires']) > 0):
                            updated_primitive_definition_extension_ctype: Dict[str, List[str]] = dict()
                            for target_extension in primitive_definition_extension_ctype:
                                valid_ctypes: List[str] = []
                                for ctype in primitive_definition_extension_ctype[target_extension]:
                                    non_fullfilled_requirements: List[str] = []
                                    for requirement in test["requires"]:
                                        if TSLPrimitive.human_readable(requirement, ctype,
                                                                       target_extension) not in known_definitions_names:
                                            non_fullfilled_requirements.append(
                                                f"{TSLPrimitive.human_readable(requirement, ctype, target_extension)}")
                                    if len(non_fullfilled_requirements) > 0:
                                        # self.log(logging.WARN,
                                        #          f"Could not create test case \"{test['test_name']}\" for "
                                        #          f"{TSLPrimitive.human_readable(primitive.declaration.name, ctype, target_extension)}. The following requirements were not met: "
                                        #          f"{non_fullfilled_requirements}.")
                                        if target_extension not in missing_primitive_definitions:
                                            missing_primitive_definitions[target_extension] = dict()
                                        if ctype not in missing_primitive_definitions[target_extension]:
                                            missing_primitive_definitions[target_extension][ctype] = list()
                                        missing_primitive_definitions[target_extension][ctype].extend([nfr for nfr in non_fullfilled_requirements if nfr not in missing_primitive_definitions[target_extension][ctype]])
                                    else:
                                        valid_ctypes.append(ctype)
                                if len(valid_ctypes) > 0:
                                    updated_primitive_definition_extension_ctype[target_extension] = valid_ctypes
                                # else:
                                #     self.log(logging.WARN,
                                #              f"Could not create test case \"{test['test_name']}\" for "
                                #              f"{TSLPrimitive.human_readable(primitive.declaration.name, 'typename T', target_extension)}. The following requirements were not met: "
                                #              f"{non_fullfilled_requirements}.")
                                #     self.log(logging.WARN,
                                #              f"Could not create test case for {primitive_class.name}::{primitive.declaration.name}_{test['test_name']}<typename T, {target_extension}>")
                            if len(updated_primitive_definition_extension_ctype) > 0:
                                self.__test_cases.append(
                                    TSLPrimitiveTestCaseData(primitive_class.name, primitive.declaration.functor_name, test, updated_primitive_definition_extension_ctype, primitive.conversion_types(updated_primitive_definition_extension_ctype), missing_primitive_definitions))
                                for ext in missing_primitive_definitions:
                                    for t in missing_primitive_definitions[ext]:
                                        self.log(logging.WARN,
                                                 f"Could not create test case \"{test['test_name']}\" for "
                                                 f"{TSLPrimitive.human_readable(primitive.declaration.functor_name, t, ext)}. The following requirements were not met: "
                                                 f"{missing_primitive_definitions[ext][t]}.")
                                        # self.log(logging.WARN,
                                                 # f"Could not create test case for {primitive_class.name}::{primitive.declaration.name}_{test['test_name']}<{t}, {ext}>: {missing_primitive_definitions[ext][t]}")
                            else:
                                self.log(logging.WARN,
                                         f"Could not create test case \"{test['test_name']}\" for any type and extension.")
                        else:
                            self.__test_cases.append(TSLPrimitiveTestCaseData(primitive_class.name, primitive.declaration.functor_name, test, primitive_definition_extension_ctype, primitive.conversion_types(primitive_definition_extension_ctype), missing_primitive_definitions))
                            for ext in missing_primitive_definitions:
                                for t in missing_primitive_definitions[ext]:
                                    print(f"{ext.center(10)}{t.center(10)}: {missing_primitive_definitions[ext][t]}")
        self.__test_cases.sort(key=lambda x: (x.class_name, x.primitive_name, x.test_name))

    @property
    def test_cases(self) -> Generator[TSLPrimitiveTestCaseData, None, None]:
        for case in self.__test_cases:
            yield case

    @property
    def test_class_names(self) -> List[str]:
        return sorted(list(self.__test_class_names))

    @property
    def primitive_tests(self) -> Generator[Tuple[str, str], None, None]:
        primitives = sorted(list(self.__primitive_test),key=lambda x: (x[0], x[1]))
        for test in primitives:
            yield test


class TSLTestDependencyGraph:

    class TestProxyNode:
        def __init__(self, name: str):
            self.__name = name
            self.__complete = True
        @property
        def name(self) -> str:
            return self.__name

        def set_incomplete(self) -> None:
            self.__complete = False

        @property
        def complete(self) -> bool:
            return self.__complete

        def __eq__(self, other):
            if isinstance(other, TSLTestDependencyGraph.TestProxyNode):
                return self.name == other.name

        def __hash__(self):
            return hash(self.name)

        def __str__(self):
            return f"{self.name}"

        def __repr__(self):
            return str(self)

    @staticmethod
    def create_color_map(keys: List[str]) -> Dict[str, Tuple[str, str]]:
        def hsv_to_rgb(h, s, v) -> Tuple[str, str]:
            (r, g, b) = colorsys.hsv_to_rgb(h, s, v)
            (rComplement, gComplement, bComplement) = (r*0.299), (g*0.587), (b*0.114)
            return "#{red}{green}{blue}".format(
                red='{:02x}'.format(int(255 * r)),
                green='{:02x}'.format(int(255 * g)),
                blue='{:02x}'.format(int(255 * b)),
            ), "#{red}{green}{blue}".format(
                red='{:02x}'.format(int(255 * rComplement)),
                green='{:02x}'.format(int(255 * gComplement)),
                blue='{:02x}'.format(int(255 * bComplement)),
            )

        hue_partition = 1.0 / (len(keys) + 1)
        result: Dict[str, Tuple[str, str]] = dict()
        for pos, key in enumerate(keys):
            result[key] = hsv_to_rgb(hue_partition * pos, 1.0, 1.0)
        return result

    def __init__(self, test_suite: TSLTestSuite) -> None:
        self.__graph: nx.DiGraph = nx.DiGraph()

        color_map = TSLTestDependencyGraph.create_color_map(test_suite.test_class_names)

        for test in test_suite.primitive_tests:
            # print(f"Adding test {test[1]} from class {test[0]}")
            self.__graph.add_node(
                TSLTestDependencyGraph.TestProxyNode(test[1]),
                style="filled",
                fillcolor=color_map[test[0]][0],
                color="#000000",
                shape="folder",
                fontcolor=color_map[test[0]][1]
            )

        for test_case in test_suite.test_cases:
            self.__graph.add_node(
                test_case,
                style="filled",
                fillcolor=color_map[test_case.class_name][0],
                color="#000000",
                shape="note",
                fontcolor=color_map[test_case.class_name][1]
            )
            self.__graph.add_edge(test_case, TSLTestDependencyGraph.TestProxyNode(test_case.primitive_name))

        for case in test_suite.test_cases:
            if case.has_dependencies():
                self.__graph.add_edges_from([(TSLTestDependencyGraph.TestProxyNode(dependency), case) for dependency in case.dependencies])

    def update_completeness(self) -> None:
        invalid_nodes_dict: dict = dict()
        all_paths = []
        for root in (v for v, d in self.__graph.in_degree if d == 0):
            # print(f"{root} -> {type(root)}")
            if isinstance(root, TSLTestDependencyGraph.TestProxyNode):
                #if a testproxynode is a root node, no tests are specified for the proxy node (primitive) -> it is incomplete
                root.set_incomplete()
                invalid_nodes_dict[root] = "filled,dotted"
        for root in (v for v, d in self.__graph.in_degree if d == 0):
            for leaf in (v for v, d in self.__graph.out_degree() if d == 0):
                paths = nx.all_simple_paths(self.__graph, root, leaf)
                all_paths.extend(paths)
        for path in all_paths:
            invalidate: bool = False
            for node in path:
                if invalidate:
                    node.set_incomplete()
                if not node.complete:
                    invalidate = True
                    invalid_nodes_dict[node] = "filled,dotted"
        nx.set_node_attributes(self.__graph, invalid_nodes_dict, "style")

        for path in all_paths:
            start = True
            complete_tests_extension_ctype_dict: Dict[str, List[str]] = None
            missing_tests: Dict[str, Dict[str, List[str]]] = dict()
            for node in path:
                if not node.complete:
                    break
                if isinstance(node, TSLPrimitiveTestCaseData):
                    if start:
                        start = False
                        complete_tests_extension_ctype_dict = node.lib_definitions
                    else:
                        if len(missing_tests) > 0:
                            node.set_missing_previous_tests(missing_tests)
                        for key in complete_tests_extension_ctype_dict.keys():
                            if key not in node.lib_definitions.keys():
                                offenders = {ctype: [f"{str(node)}<{ctype}, {key}>"] for ctype in
                                             complete_tests_extension_ctype_dict[key]}
                            else:
                                offenders = {ctype: [f"{str(node)}<{ctype}, {key}>"] for ctype in
                                             complete_tests_extension_ctype_dict[key] if
                                             ctype not in node.lib_definitions[key]}
                            if len(offenders) > 0:
                                if key not in missing_tests:
                                    missing_tests[key] = offenders
                                else:
                                    for ctype in offenders:
                                        if ctype not in missing_tests[key]:
                                            missing_tests[key][ctype] = offenders[ctype]
                                        else:
                                            missing_tests[key][ctype].extend([offender for offender in offenders[ctype] if offender not in missing_tests[key][ctype]])
                        if len(complete_tests_extension_ctype_dict) > 0:
                            complete_tests_extension_ctype_dict = {
                                key: list(set(complete_tests_extension_ctype_dict[key]) & set(node.lib_definitions[key]))
                                for key in complete_tests_extension_ctype_dict.keys() & node.lib_definitions.keys()}
                        node.complete_tests_lib_definitions = complete_tests_extension_ctype_dict


    @property
    def graph(self) -> nx.DiGraph:
        return self.__graph

    def draw(self, filename: Path) -> None:
        from networkx.drawing.nx_agraph import to_agraph
        A = to_agraph(self.__graph)
        # pos = nx.nx_agraph.graphviz_layout(self.__graph)
        A.layout()
        A.draw(filename, prog='dot')#|'dot'|'twopi'|'circo'|'fdp'|'nop'])
        # nx.draw(self.__graph, pos=pos)
        # plt.savefig(filename)

    def get_case_data_topological_order(self) -> Generator[TSLPrimitiveTestCaseData, None, None]:
        order = nx.topological_sort(self.__graph)
        for case in order:
            if isinstance(case, TSLPrimitiveTestCaseData):
                yield case

class TSLTestGenerator:
    @LogInit()
    def __init__(self):
        pass

    @staticmethod
    def generate(lib: TSLLib) -> Generator[Tuple[Path,TSLTranslationUnit], None, None]:
        if not config.expansion_enabled("unit_tests"):
            return

        unit_test_config: dict = config.get_expansion_config("unit_tests")

        tsltu: TSLTranslationUnit = TSLTranslationUnit(target_name="tsl_test")

        suite: TSLTestSuite = TSLTestSuite(lib)
        dependency_graph: TSLTestDependencyGraph = TSLTestDependencyGraph(suite)
        dependency_graph.update_completeness()
        root_path: Path = config.generation_out_path.joinpath(unit_test_config["root_path"])
        root_path.mkdir(parents=True, exist_ok=True)

        if unit_test_config["draw_dependency_graph"]:
            dependency_graph.draw(root_path.joinpath("test_dependencies.png"))

        # print(f"Downloading ... {unit_test_config['test_header_url']}", end='', flush=True)
        tsltestgenerator = TSLTestGenerator()
        tsltestgenerator.log(logging.DEBUG, f"Starting download of {unit_test_config['test_header_url']}")
        header_name = unit_test_config['test_header_url'].split("/")[-1]
        
        if ( os.path.exists( f"{str(root_path)}/{header_name}") ):
            tsltestgenerator.log(logging.DEBUG, f"File (test header) already present, skipping download")
        else:
            try:
                if config.get_config_entry("silent"):
                    wget.download(unit_test_config["test_header_url"], out=str(root_path), bar=lambda *args: None)
                else:
                    wget.download(unit_test_config["test_header_url"], out=str(root_path))
            except Exception as e:
                tsltestgenerator.log(logging.WARN,
                                    f"Could not download the necessary test header file. Check your network connection. {e}")

        tests: Dict[str,List[TSLPrimitiveClassTests]] = dict()
        primitive_class: TSLPrimitiveClassTests = None
        primitive_test: TSLPrimitiveTest = None
        declaration_dict: Dict[Dict[str, TSLPrimitive.Declaration]] = lib.primitive_class_set.get_declaration_dict()

        test_by_primitive_dict: Dict[str, TSLSourceFile] = dict()
        for pClass in lib.primitive_class_set:
            tests[pClass.name] = []
            test_by_primitive_dict[pClass.name] = TSLSourceFile.create_from_dict(
                root_path.joinpath(f"{pClass.name}_unit_test.cpp"),
                {
                    "description": "Unit test file for TSL Primitives using Catch2",
                    "nested_namespaces": [unit_test_config["namespace"]]
                }
            )
            test_by_primitive_dict[pClass.name].add_include(f"<{strip_common_path_prefix(config.lib_root_header, config.lib_root_path)}>")
        
        for static_yaml_file_path in config.static_expansion_files("unit_tests"):
            # print(static_yaml_file_path)
            # print(unit_test_config["static_files"]["root_path"])
            static_file_path_without_prefix = strip_common_path_prefix(static_yaml_file_path,
                                                                       Path(unit_test_config["static_files"][
                                                                                "root_path"]))
            file_path: Path = root_path.joinpath(static_file_path_without_prefix).with_suffix(
                config.get_config_entry("header_file_extension"))
            data_dict: YamlDataType = yaml_load(static_yaml_file_path)
            tsl_file: TSLHeaderFile = TSLHeaderFile.create_from_dict(file_path, {**data_dict, **{
                "description": "Utility functions for testing.", "nested_namespaces": [unit_test_config["namespace"]]}})
            if "implementations" in data_dict:
                for implementation in data_dict["implementations"]:
                    tsl_file.add_code(implementation)

            tsl_file.render_to_file()

            catch_includer_path = root_path.joinpath("catch_manager.cpp")
            catch2_includer: TSLSourceFile = TSLSourceFile.create_from_dict(catch_includer_path, {"preliminary_defines": [
                "#ifndef CATCH_CONFIG_MAIN\n#define CATCH_CONFIG_MAIN\n#endif"], "includes": ['"catch.hpp"']})
            catch2_includer.render_to_file()
            tsltu.add_header(catch2_includer)

            for prim, tsf in test_by_primitive_dict.items():
                tsf.add_file_include(tsl_file)

        for test_data in dependency_graph.get_case_data_topological_order():
            case: TSLPrimitiveTestCase = TSLPrimitiveTestCase(test_data)
            if primitive_class is None:
                primitive_class = TSLPrimitiveClassTests(case.associated_primitive_class_name)
                primitive_test = TSLPrimitiveTest(case.associated_primitive_name,
                                                  declaration_dict[case.associated_primitive_class_name][
                                                      case.associated_primitive_name])
            else:
                if primitive_class.primitive_class_name != case.associated_primitive_class_name:
                    primitive_class.add_primitive_test(primitive_test)
                    tests[primitive_class.primitive_class_name].append(primitive_class)
                    primitive_class = TSLPrimitiveClassTests(case.associated_primitive_class_name)
                    primitive_test = TSLPrimitiveTest(case.associated_primitive_name,
                                                      declaration_dict[case.associated_primitive_class_name][
                                                          case.associated_primitive_name])
                if primitive_test.primitive_name != case.associated_primitive_name:
                    primitive_class.add_primitive_test(primitive_test)
                    primitive_test = TSLPrimitiveTest(case.associated_primitive_name,
                                                      declaration_dict[case.associated_primitive_class_name][
                                                          case.associated_primitive_name])
            primitive_test.add_case(case)
            test_by_primitive_dict[primitive_class.primitive_class_name].import_includes(case.data_dict)
        if primitive_class is not None:
            primitive_class.add_primitive_test(primitive_test)
            tests[primitive_class.primitive_class_name].append(primitive_class)

        for prim, tsf in test_by_primitive_dict.items():
            if tests[prim]:
                tsf.add_code(
                    config.get_template("expansions::unit_test").render(
                        {
                            "tsl_namespace": config.lib_namespace,
                            "known_extensions": lib.extension_set.known_extensions,
                            "known_ctypes": lib.primitive_class_set.known_ctypes,
                            "tests": [test.as_dict() for test in tests[prim]],
                            "nested_namespaces": [unit_test_config["namespace"]]
                        }
                    )
                )
                tsf.render_to_file()
                tsltu.add_source(tsf)

        yield root_path, tsltu
