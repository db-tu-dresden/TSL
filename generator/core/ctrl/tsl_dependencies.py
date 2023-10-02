from __future__ import annotations
from generator.core.tsl_config import config
from generator.core.ctrl.tsl_lib import TSLLib

from typing import Generator, Dict, Iterator, Set, List, Tuple, NewType, Union
import re
import networkx as nx
from dataclasses import dataclass
import pandas as pd
from enum import Enum


class TSLInspectionLevelOfDetail(Enum):
  # only care about classes and there structure
  CLASS = 1
  # care about primitives and there implementation on an abstract level (no deep inpection of instantiations)
  PRIMITIVE_IMPLEMENTATION = 2
  # care about extensions + ctypes
  PRIMITIVE_INSTANTIATION = 3
  TEST_IMPLEMENTATION = 4
  TEST_INSTANTIATION = 5

class TSLDependencyGraphLevelOfDetail(Enum):
  CLASS = 1
  PRIMITIVE = 2
  PRIMITIVE_IMPLEMENTATION = 3
  TEST = 4
  TEST_IMPLEMENTATION = 5

class TSLDependencyGraph:
  
  @dataclass(order=True, unsafe_hash=True, frozen=True)
  class PrimitiveClassNode:
    name: str
    type: str = "class"
    size: int = 10
    def __str__(self):
      return f"{self.name}"
    def __repr__(self):
      return str(self)
    def id(self):
      return self.name
    def attributes(self):
      return {"name": self.name, "type": self.type, "size": self.size}
  @dataclass(order=True, unsafe_hash=True, frozen=True)
  class PrimitiveNode:
    name: str
    type: str = "primitive"
    size: int = 5
    def __str__(self):
      return f"{self.name}"
    def __repr__(self):
      return str(self)
    def id(self):
      return self.name
    def attributes(self):
      return {"name": self.name, "type": self.type, "size": self.size}
  @dataclass(order=True, unsafe_hash=True, frozen=True)
  class PrimitiveImplementationNode:
    name: str
    type: str = "primitive_implementation"
    size: int = 3
    def __str__(self):
      return f"{self.name}"
    def __repr__(self):
      return str(self)
    def id(self):
      return str(self)
    def attributes(self):
      return {"name": self.name, "type": self.type, "size": self.size}
    @staticmethod
    def create_full_qualified_name(primitive_name: str, extension: str, ctype: str) -> str:
      return f"{primitive_name}<{ctype}, {extension}>"
  @dataclass(order=True, unsafe_hash=True, frozen=True)
  class PrimitiveTestNode:
    name: str
    type: str = "test"
    size: int = 3
    def __str__(self):
      return f"{self.name}"
    def __repr__(self):
      return str(self)
    def id(self):
      return self.name
    def attributes(self):
      return {"name": self.name, "type": self.type, "size": self.size}
    @staticmethod
    def create_full_qualified_name(primitive_name: str, test_name: str) -> str:
      return f"{primitive_name}::{test_name}"  
  @dataclass(order=True, unsafe_hash=True, frozen=True)
  class PrimitiveTestImplementationNode:
    name: str
    type: str = "test_implementation"
    size: int = 3
    def __str__(self):
      return f"{self.name}"
    def __repr__(self):
      return str(self)
    def id(self):
      return str(self)
    def attributes(self):
      return {"name": self.name, "extension": self.extension, "ctype": self.ctype, "type": self.type, "size": self.size}
    @staticmethod
    def create_full_qualified_name(primitive_name: str, test_name: str, extension: str, ctype: str) -> str:
      return f"{TSLDependencyGraph.PrimitiveTestNode.create_full_qualified_name(primitive_name, test_name)}<{ctype}, {extension}>"
  
  NodeType = Union[PrimitiveClassNode, PrimitiveNode, PrimitiveTestNode]
    
  @property
  def graph(self) -> nx.DiGraph:
    return self.__dependency_graph

  def __init__(self, tsl_lib: TSLLib, level_of_detail: TSLInspectionLevelOfDetail = TSLInspectionLevelOfDetail.TEST_INSTANTIATION ) -> None:
    self.__tsl_lib = tsl_lib
    self.__dependency_graph: nx.DiGraph = nx.DiGraph()
    self.__level_of_detail = level_of_detail

    ### Step 1: Add all primitive-classes to the dependency graph
    for primitive_class in self.__tsl_lib.primitive_class_set:
      # add all primitive classes to the graph
      self.__dependency_graph.add_node(self.PrimitiveClassNode(primitive_class.name))
    
    primitive_names: List[str] = []
    for class_name, primitive in self.__tsl_lib.known_primitives:
      primitive_name = primitive.declaration.functor_name
      ### Step 2: Add all primitives to the dependency graph and connect the primitives with their associated primitive-classes
      primitive_names.append(primitive_name)
      primitive_node = TSLDependencyGraph.PrimitiveNode(primitive_name)
      self.__dependency_graph.add_node(primitive_node)
      self.__dependency_graph.add_edge(primitive_node, self.PrimitiveClassNode(class_name), label="part of")

      if level_of_detail.value >= TSLInspectionLevelOfDetail.TEST_IMPLEMENTATION:
        ### Step 3: For every primitive-test, add the primitive-test to the dependency graph and connect the test with the associated primitive node
        for test_name, implementation_str in primitive.get_tests_implementations(False):
          test_node = TSLDependencyGraph.PrimitiveTestNode(TSLDependencyGraph.PrimitiveTestNode.create_full_qualified_name(primitive_name, test_name))
          self.__dependency_graph.add_node(test_node)
          self.__dependency_graph.add_edge(test_node, primitive_node, label="test of")

      if level_of_detail.value >= TSLInspectionLevelOfDetail.PRIMITIVE_INSTANTIATION.value:
        ### Step 4: Iterate over all specializations of a primitive (combination of target_extension and ctype) and add a node of the primitive-instantiation to the dependency graph.
        ###         Connect the instantiation with the associated primitive
        for target_extension, ctype_list in primitive.specialization_dict().items():
          for ctype in ctype_list:
            implementation_node = TSLDependencyGraph.PrimitiveImplementationNode(TSLDependencyGraph.PrimitiveImplementationNode.create_full_qualified_name(primitive_name, target_extension, ctype))
            self.__dependency_graph.add_node(implementation_node)
            self.__dependency_graph.add_edge(implementation_node, primitive_node, label="implementation of")
            if level_of_detail.value >= TSLInspectionLevelOfDetail.TEST_INSTANTIATION.value:
              ### Step 5: Add test-intantiation nodes to the dependency graph and connect them to the associated test node
              ###         Connect the test-instatiation node with the concrete primitive-implementation node
              for test_name, implementation_str in primitive.get_tests_implementations(False):
                test_node = TSLDependencyGraph.PrimitiveTestNode(TSLDependencyGraph.PrimitiveTestNode.create_full_qualified_name(primitive_name, test_name))
                test_implementation_node = TSLDependencyGraph.PrimitiveTestImplementationNode(TSLDependencyGraph.PrimitiveTestImplementationNode.create_full_qualified_name(primitive_name, test_name, target_extension, ctype))
                self.__dependency_graph.add_node(test_implementation_node)
                self.__dependency_graph.add_edge(test_implementation_node, test_node, label="implementation of")
                self.__dependency_graph.add_edge(test_implementation_node, implementation_node, label="concrete test of")

        # regex str for all known primitives, e.g., (?P<primitive>add|sub|mul|div)
        known_primitives_regex = rf'(?P<primitive>{"|".join(primitive_names)})'
        # regex str ensuring that the primitive name is not part of a longer word, e.g., (?<!([a-zA-Z]|_))add(?!([a-zA-Z]|_|\[|\.|\())
        primitive_regex = rf'(?<!([a-zA-Z]|_))({known_primitives_regex})(?!([a-zA-Z]|_|\[|\.|\())'
        
        if level_of_detail.value >= TSLInspectionLevelOfDetail.PRIMITIVE_INSTANTIATION.value:
          # regex str for all known extensions, e.g., (?P<extension>sse|avx2|avx512)
          extension_regex = rf'(?P<extension>{"|".join(map(lambda extension: extension.name, tsl_lib.extension_set))})'
          # regex str for all known ctypes, e.g., (?P<ctype>float|double|uint8_t)
          ctype_regex = rf'(?P<ctype>{"|".join(tsl_lib.primitive_class_set.known_ctypes)})'
          # regex str to capture all simd types (with arbitrary number of whitespaces in between), the trailing ? is meant to indicate, that it is possible, that we don't find it. In such a case we assume that the dependent simd type equals the current simd type
          simd_regex = rf'(?P<simd_type>simd\s*<\s*{ctype_regex}\s*,\s*{extension_regex})?'
          # combined regex str 
          tsl_primitive_regex = rf'{primitive_regex}\s*<\s*{simd_regex}'
        else:
          tsl_primitive_regex = rf'{primitive_regex}'
        
        # compile regex
        self.__primitive_regex = re.compile(tsl_primitive_regex)

        for class_name, primitive in self.__tsl_lib.known_primitives:
          primitive_node = TSLDependencyGraph.PrimitiveNode(primitive.declaration.functor_name)
          for definition in primitive.definitions:
            implementation_str = definition.data["implementation"]
            # analyze all dependencies of a given primitive definition
            # find requirements within the given implemenation string
            for match in self.__primitive_regex.finditer(implementation_str):
              # check if an actual primitive was found, if not raise an error since something went horribly wrong
              if "primitive" not in match.groupdict():
                raise ValueError(f"Could not find primitive name in match group. {match}")
              required_primitive_name = match.group("primitive")
              # self dependencies (which occur in tests) are ommitted
              if required_primitive_name != primitive.declaration.functor_name:
                required_primitive_node = TSLDependencyGraph.PrimitiveNode(required_primitive_name)
                if required_primitive_node not in self.__dependency_graph:
                  raise ValueError(f"Unknown primitive {required_primitive_name} (required by {primitive.declaration.functor_name}")
                self.__dependency_graph.add_edge(required_primitive_node, primitive_node, label="requirement of")
                # if the level of detail should include the actual instantiation (with target_extension and ctype) we check for the presence of those parts
                if level_of_detail.value >= TSLInspectionLevelOfDetail.PRIMITIVE_INSTANTIATION:
                  if "simd_type" in match.groupdict():
                    if "ctype" in match.group_dict() and "extension" in match.group_dict():
                      required_primitive_instantiation_node = TSLDependencyGraph.PrimitiveImplementationNode(TSLDependencyGraph.PrimitiveImplementationNode.create_full_qualified_name(required_primitive_name, match.group("extension"), match.group("ctype")))
                      if required_primitive_instantiation_node not in self.__dependency_graph:
                        raise ValueError("Could not find primitive ({required_primitive_instantiation_node}) required by {primitive_node}")
                      for ctype in definition.ctypes:
                        self.__dependency_graph.add_edge(
                          required_primitive_instantiation_node, 
                          TSLDependencyGraph.PrimitiveImplementationNode(TSLDependencyGraph.PrimitiveImplementationNode.create_full_qualified_name(primitive.declaration.functor_name, definition.target_extension, ctype)), label="concrete requirement of")
                    else:
                      raise ValueError("Found simd_type but no ctype AND extension")
                  else:
                    for ctype in definition.ctypes:
                      self.__dependency_graph.add_edge(
                        TSLDependencyGraph.PrimitiveImplementationNode(TSLDependencyGraph.PrimitiveImplementationNode.create_full_qualified_name(required_primitive_name, definition.target_extension, ctype)), 
                        TSLDependencyGraph.PrimitiveImplementationNode(TSLDependencyGraph.PrimitiveImplementationNode.create_full_qualified_name(primitive.declaration.functor_name, definition.target_extension, ctype)), 
                        label="concrete requirement of")

          if level_of_detail >= TSLInspectionLevelOfDetail.TEST_IMPLEMENTATION:
            for test_name, implementation_str in primitive.get_tests_implementations(False):
              test_node = TSLDependencyGraph.PrimitiveTestNode(TSLDependencyGraph.PrimitiveTestNode.create_full_qualified_name(primitive.declaration.functor_name, test_name))
              # analyze all dependencies of a given primitive definition
              # find requirements within the given test implemenation string
              for match in self.__primitive_regex.finditer(implementation_str):
                # check if an actual primitive was found, if not raise an error since something went horribly wrong
                if "primitive" not in match.groupdict():
                  raise ValueError(f"Could not find primitive name in match group. {match}")
                required_primitive_name = match.group("primitive")
                # self dependencies (which occur in tests) are ommitted
                if required_primitive_name != primitive.declaration.functor_name:
                  required_primitive_node = TSLDependencyGraph.PrimitiveNode(required_primitive_name)
                  if required_primitive_node not in self.__dependency_graph:
                    raise ValueError(f"Unknown primitive {required_primitive_name} (required by {test_node}")
                  self.__dependency_graph.add_edge(required_primitive_node, test_node, label="requirement of")
                  # if the level of detail should include the actual instantiation (with target_extension and ctype) we check for the presence of those parts
                  if level_of_detail.value >= TSLInspectionLevelOfDetail.TEST_INSTANTIATION:
                    if "simd_type" in match.groupdict():

                    else:
                      for definition in primitive.definitions:
                        extension = definition.target_extension
                        for ctype in definition.ctypes:
                          self.__dependency_graph.add_edge(
                            TSLDependencyGraph.PrimitiveTestImplementationNode(TSLDependencyGraph.PrimitiveTestImplementationNode.create_full_qualified_name(required_primitive_name, )),
                            TSLDependencyGraph.PrimitiveTestImplementationNode(TSLDependencyGraph.PrimitiveTestImplementationNode.create_full_qualified_name(primitive.declaration.functor_name, test_name, extension, ctype)), 
                            label="concrete requirement of"
                          )
                      for ctype in definition.
                
          if level_of_detail >= TSLInspectionLevelOfDetail.TEST_IMPLEMENTATION:
            for test_name, implementation_str in primitive.get_tests_implementations(False):
              test_node = TSLDependencyGraph.PrimitiveTestNode(TSLDependencyGraph.PrimitiveTestNode.create_full_qualified_name(primitive.declaration.functor_name, test_name))
              # analyze all dependencies of a given primitive test
              analyze_implementation(implementation_str, test_node, TSLDependencyGraph.PrimitiveTestNode, [primitive.declaration.functor_name, test_name], TSLDependencyGraph.PrimitiveTestImplementationNode, TSLInspectionLevelOfDetail.TEST_INSTANTIATION, "depends on")
  
  def nodes_by_type(self, node_types_of_interest: list) -> Generator[NodeType, None, None]:
    yield from filter(lambda node: any(isinstance(node, node_type) for node_type in node_types_of_interest), self.__dependency_graph.nodes)

  def subgraph(self, level_of_detail: TSLDependencyGraphLevelOfDetail) -> nx.DiGraph:
    if level_of_detail == TSLDependencyGraphLevelOfDetail.CLASS:
      return self.__dependency_graph.subgraph([node for node in self.nodes_by_type([TSLDependencyGraph.PrimitiveClassNode])])
    if self.__level_of_detail.value > TSLInspectionLevelOfDetail.CLASS.value:
      if level_of_detail == TSLDependencyGraphLevelOfDetail.PRIMITIVE:
        return self.__dependency_graph.subgraph([node for node in self.nodes_by_type([TSLDependencyGraph.PrimitiveClassNode, TSLDependencyGraph.PrimitiveNode])])
      if level_of_detail == TSLDependencyGraphLevelOfDetail.PRIMITIVE_IMPLEMENTATION:
        return self.__dependency_graph.subgraph([node for node in self.nodes_by_type([TSLDependencyGraph.PrimitiveClassNode, TSLDependencyGraph.PrimitiveNode, TSLDependencyGraph.PrimitiveImplementationNode])])
      if self.__level_of_detail > TSLInspectionLevelOfDetail.PRIMITIVE_INSTANTIATION.value:
        if level_of_detail == TSLDependencyGraphLevelOfDetail.TEST:
          return self.__dependency_graph.subgraph([node for node in self.nodes_by_type([TSLDependencyGraph.PrimitiveClassNode, TSLDependencyGraph.PrimitiveNode, TSLDependencyGraph.PrimitiveImplementationNode, TSLDependencyGraph.PrimitiveTestNode])])
        else:
          return self.__dependency_graph.subgraph([node for node in self.nodes_by_type([TSLDependencyGraph.PrimitiveClassNode, TSLDependencyGraph.PrimitiveNode, TSLDependencyGraph.PrimitiveImplementationNode, TSLDependencyGraph.PrimitiveTestNode, TSLDependencyGraph.PrimitiveTestImplementationNode])])
    raise ValueError("Inspection level lower than subgraph level")

  def traverse_by_type(self, nodes: List[NodeType], node_types_of_interest: list, reversed:bool, self_contained: bool = False) -> Generator[NodeType, None, None]:
    for current_node in nodes:
      if self_contained:
        yield current_node
      for edge in filter(lambda edge: any(isinstance(edge[1], node_type) for node_type in node_types_of_interest), nx.bfs_edges(self.__dependency_graph, current_node, reverse=reversed)):
        yield edge[1]

  def traverse(self, nodes: List[NodeType], reversed: bool, self_contained: bool = False) -> Generator[NodeType, None, None]:
    for current_node in nodes:
      if self_contained:
        yield current_node
      for edge in nx.bfs_edges(self.__dependency_graph, current_node, reverse=reversed):
        yield edge[1]

  def predecessors_by_type(self, node: NodeType, node_types_of_interest: list) -> Generator[NodeType, None, None]:
    for edge in filter(lambda edge: any(isinstance(edge[0], node_type) for node_type in node_types_of_interest), self.__dependency_graph.in_edges(node)):
      yield edge[0]

  def first_predecessor_by_type(self, node: NodeType, node_types_of_interest: list) -> NodeType|None:
    for edge in filter(lambda edge: any(isinstance(edge[0], node_type) for node_type in node_types_of_interest), self.__dependency_graph.in_edges(node)):
      return edge[0]
    return None

  def successors_by_type(self, node: NodeType, node_types_of_interest: list) -> Generator[NodeType, None, None]:
    for edge in filter(lambda edge: any(isinstance(edge[1], node_type) for node_type in node_types_of_interest), self.__dependency_graph.out_edges(node)):
      yield edge[1]
  
  def first_successor_by_type(self, node: NodeType, node_types_of_interest: list) -> NodeType|None:
    for edge in filter(lambda edge: any(isinstance(edge[1], node_type) for node_type in node_types_of_interest), self.__dependency_graph.out_edges(node)):
      return edge[1]
    return None

  def is_acyclic(self) -> bool:
    return nx.is_directed_acyclic_graph(self.__dependency_graph)

  def get_cycles_as_str(self) -> List[str]:
    return list(map(lambda list_of_nodes: " -> ".join(map(lambda node: node.name, list_of_nodes)), nx.simple_cycles(self.__dependency_graph)))
  
  def class_nodes(self) -> Generator[TSLDependencyGraph.PrimitiveClassNode, None, None]:
    for primitive_class in self.__tsl_lib.primitive_class_set:
      yield self.PrimitiveClassNode(primitive_class.name)
  
  def get_required_primitives(self, node: NodeType, self_contained: bool = False) -> Generator[TSLDependencyGraph.PrimitiveNode, None, None]:
    yield from self.traverse_by_type([node], [TSLDependencyGraph.PrimitiveNode], True, self_contained)
    
  def get_dependent_primitives(self, node: NodeType, self_contained: bool = False) -> Generator[TSLDependencyGraph.PrimitiveNode, None, None]:
    yield from self.traverse_by_type([node], [TSLDependencyGraph.PrimitiveNode], False, self_contained)
  
  def get_associated_class(self, node: NodeType) -> TSLDependencyGraph.PrimitiveClassNode:
    if isinstance(node, self.PrimitiveClassNode):
      return node
    elif isinstance(node, TSLDependencyGraph.PrimitiveNode):
      successor = self.first_successor_by_type(node, [self.PrimitiveClassNode])
      if successor is not None:
        return successor
      raise Exception(f"Primitive {node.name} has no associated class.")
    elif isinstance(node, self.PrimitiveTestNode):
      primitive_node = self.first_successor_by_type(node, [TSLDependencyGraph.PrimitiveNode])
      if primitive_node is not None:
        successor = self.first_successor_by_type(primitive_node, [self.PrimitiveClassNode])
        if successor is not None:
          return successor
        raise Exception(f"Primitive {node.name} has no associated class.")
      raise Exception(f"Test {node.name} has no associated primitive.")
        
  def get_required_classes(self, node: NodeType) -> Set[TSLDependencyGraph.PrimitiveClassNode]:
    node_set: Set[TSLDependencyGraph.PrimitiveClassNode] = set()
    if not isinstance(node, TSLDependencyGraph.PrimitiveClassNode):
      node_set.add(self.get_associated_class(node))
    for child_node in self.traverse_by_type([node], [TSLDependencyGraph.PrimitiveNode, TSLDependencyGraph.PrimitiveTestNode], True, False):
      node_set.add(self.get_associated_class(child_node))
    return node_set

  def get_dependent_classes(self, node: NodeType) -> Set[TSLDependencyGraph.PrimitiveClassNode]:
    node_set: Set[TSLDependencyGraph.PrimitiveClassNode] = set()
    if not isinstance(node, TSLDependencyGraph.PrimitiveClassNode):
      node_set.add(self.get_associated_class(node))
    for child_node in self.traverse_by_type([node], [TSLDependencyGraph.PrimitiveNode, TSLDependencyGraph.PrimitiveTestNode], False, False):
      node_set.add(self.get_associated_class(child_node))    
  
  def sorted_classes_as_string(self) -> Generator[str, None, None]:
    class_graph = nx.DiGraph()
    for cls in self.class_nodes():
      class_graph.add_node(cls)
      for required_class in self.get_required_classes(cls):
        if required_class != cls:
          class_graph.add_edge(required_class, cls)
    try:
      ordered_class_graph = nx.topological_sort(class_graph)
    except nx.NetworkXUnfeasible:
      print("Unable to sort class graph.")
      exit(1)
    for cls in ordered_class_graph:
        yield cls.name

  def get_required_tests(self, node: NodeType) -> Set[TSLDependencyGraph.PrimitiveTestNode]:
    node_set: Set[TSLDependencyGraph.PrimitiveTestNode] = set()
    for child_node in self.traverse_by_type([node], [TSLDependencyGraph.PrimitiveTestNode], True, False):
      node_set.add(child_node)
    return node_set
  
  def get_dependent_tests(self, node: NodeType) -> Set[TSLDependencyGraph.PrimitiveTestNode]:
    node_set: Set[TSLDependencyGraph.PrimitiveTestNode] = set()
    for successor_node in self.traverse_by_type([node], [TSLDependencyGraph.PrimitiveTestNode], False, False):
      node_set.add(successor_node)
    return node_set
    
  def tested_primitive_count(self) -> int:
    nodes = self.nodes_by_type([TSLDependencyGraph.PrimitiveNode])
    result = 0
    for primitive_node in nodes:
      if len([test_case for test_case in self.predecessors_by_type(primitive_node, [TSLDependencyGraph.PrimitiveTestNode])]) > 0:
        result += 1
    return result
  
  def missing_tests(self) -> Generator[TSLDependencyGraph.PrimitiveNode, None, None]:
    nodes = self.nodes_by_type([TSLDependencyGraph.PrimitiveNode])
    for primitive_node in nodes:
      if self.first_predecessor_by_type(primitive_node, [TSLDependencyGraph.PrimitiveTestNode]) is None:
        yield primitive_node

  def unsafe_tests_as_str(self) -> Generator[str, None, None]:
    def traverse_dfs(node: TSLDependencyGraph.NodeType, output_str: str) -> Generator[str, None, None]:
      if self.first_successor_by_type(node, [TSLDependencyGraph.PrimitiveTestNode, TSLDependencyGraph.PrimitiveNode]) is None:
        yield output_str
      else:
        if isinstance(node, TSLDependencyGraph.PrimitiveNode):
          for successor_node in self.successors_by_type(node, [TSLDependencyGraph.PrimitiveTestNode]):
            yield from traverse_dfs(successor_node, f"{output_str}")
        elif isinstance(node, TSLDependencyGraph.PrimitiveTestNode):
          test = node.name.split("::")
          for successor_node in self.successors_by_type(node, [TSLDependencyGraph.PrimitiveNode]):
            if len(output_str) == 0:
              yield from traverse_dfs(successor_node, f"{test[0]}::<{test[1]}>")
            else:
              yield from traverse_dfs(successor_node, f"{test[0]}::<{test[1]}> -> {output_str}")

    for unsafe_primitive in self.missing_tests():
      for message in traverse_dfs(unsafe_primitive, f"{unsafe_primitive.name}::<MISSING>"):
        if message != f"{unsafe_primitive.name}::<MISSING>":
          yield f"{message}"


  def as_str(self, include_tests: bool = False) -> str:
    class_count = sum(1 for _ in self.nodes_by_type([TSLDependencyGraph.PrimitiveClassNode]))
    primitives_count = sum(1 for _ in self.nodes_by_type([TSLDependencyGraph.PrimitiveNode]))

    missing_tests = [primitive.name for primitive in self.missing_tests()]
    unsafe_test = [message for message in self.unsafe_tests_as_str()]
    unsafe_set = {test_chain.split(" ")[0] for test_chain in unsafe_test}
    longest_primitive_name = max(len(max(missing_tests, key=len)), len(max(unsafe_test, key=len)))
    output_missing_tests = "\n".join(['                          ' + primitive for primitive in missing_tests])
    output_unsafe_tests  = "\n".join(['                          ' + message for message in unsafe_test])
    result = f"""TSL - Summary:
  - # Primitive Classes:  {class_count}
  - # Primitives:         {primitives_count}"""
    if include_tests:
      tests_count = sum(1 for _ in self.nodes_by_type([TSLDependencyGraph.PrimitiveTestNode]))
      tested_primitive_count = self.tested_primitive_count()
      test_coverage = tested_primitive_count / primitives_count
      average_tests_per_primitive = (tests_count / primitives_count)
      result = f"""{result}
  - # Tests:              {tests_count}
  - Primitives w/ Tests:  {tested_primitive_count}
  - Primitives w/o Tests: 
{output_missing_tests}
                          {'='*longest_primitive_name}
                          {primitives_count - tested_primitive_count}
  - Unsafe Tests:          
{output_unsafe_tests}
                          {'='*longest_primitive_name}
                          {len(unsafe_set)} ({len(unsafe_test)} specific missing dependencies)
  - Test Coverage:        {test_coverage * 100:.2f}%
  - Avg. Tests/Primitive: {average_tests_per_primitive:.2f}"""
    return result

  def draw(self, out_name: str = "dependency_graph"):
    from networkx.drawing.nx_agraph import to_agraph
    g = to_agraph(self.__dependency_graph)
    # pos = nx.nx_agraph.graphviz_layout(self.__graph)
    g.layout()
    config.generation_out_path.joinpath(out_name).with_suffix(".png").parent.mkdir(parents=True, exist_ok=True)
    g.draw(config.generation_out_path.joinpath(out_name).with_suffix(".png"), prog='dot')
    
  def to_pandas(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
    edge_list = []
    node_list = []
    # Iterate over edges and nodes in the dependency graph
    for source, target in self.__dependency_graph.edges():
      source_node = source
      target_node = target
      edge_data = {
        'from': source_node.id(),
        'to': target_node.id(),
        'weight': 1,
        'strength': "medium",
        **self.__dependency_graph.get_edge_data(source, target)
      }
      edge_list.append(edge_data)
    for node in self.__dependency_graph.nodes():
      node_data = {
        'id': node.id(),
        **node.attributes()
      }
      node_list.append(node_data)
    edge_df = pd.DataFrame(edge_list)
    node_df = pd.DataFrame(node_list)
    return edge_df, node_df
  
  def to_json(self, out_name: str = "dependency_graph") -> None:
    edge_df, node_df = self.to_pandas()
    edge_df.to_json(config.generation_out_path.joinpath(out_name).with_suffix(".edges.json"))
    node_df.to_json(config.generation_out_path.joinpath(out_name).with_suffix(".nodes.json"))

  def to_jaal(self) -> None:
    from jaal import Jaal
    edge_df, node_df = self.to_pandas()
    port=8050
    while True:
      try:
        Jaal(edge_df, node_df).plot(directed=True,port=port)
      except:
        port+=1

