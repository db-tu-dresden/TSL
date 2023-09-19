from __future__ import annotations
from generator.core.tsl_config import config
from generator.core.ctrl.tsl_lib import TSLLib

from typing import Generator, Dict, Iterator, Set, List, Tuple
import re
import networkx as nx
from dataclasses import dataclass
import pandas as pd

class TSLPrimitiveRegex:
  def __init__(self):
    self.tsl_primitive_regex_parts = {
    "namespace": rf'\s+({config.lib_namespace}::)?',
    "functor_namespace": rf'\s+({config.lib_namespace}::)?({config.implementation_namespace}::)?',
    "template": r'<[^;]*>',
    "parameters": r'\(([^)]*)\)?',
  }
  
  def primitive_name_to_regex(self, primitive_name: str) -> str:
    return rf'({self.tsl_primitive_regex_parts["namespace"]}({primitive_name})\s*{self.tsl_primitive_regex_parts["template"]}\s*{self.tsl_primitive_regex_parts["parameters"]})'
  
  def functor_name_to_regex(self, primitive_name: str) -> str:
    return rf'({self.tsl_primitive_regex_parts["functor_namespace"]}({primitive_name})\s*{self.tsl_primitive_regex_parts["template"]}\s*{self.tsl_primitive_regex_parts["parameters"]})'
  
  def primitives_to_regex(self, primitives: Generator[Tuple[str, str], None, None]) -> str:
    primitives_regex_list = []
    for primitive_name, functor_name in primitives:
      primitives_regex_list.append(self.primitive_name_to_regex(primitive_name))
      if functor_name is not None and functor_name != "" and functor_name != primitive_name:
        primitives_regex_list.append(self.functor_name_to_regex(functor_name))
    for x in primitives_regex_list:
      print(x)
    return rf'({"|".join(primitives_regex_list)})'

  def get_primitive_name_from_match(self, match, group_count: int) -> str:
    found_count = 0
    for i in range(group_count, 0, -1):
      if match.group(i) is not None:
        found_count += 1
      if found_count == 2:
        return match.group(i)
      
class TSLDependencyGraphDeprecated:  
  def __init__(self, tsl_lib: TSLLib):
    self.__tsl_lib = tsl_lib
    self.__primitive_regex_helper = TSLPrimitiveRegex()
    self.__primitive_regex = re.compile(self.__primitive_regex_helper.primitives_to_regex(tsl_lib.known_primitives_names_and_functor))
    print(f"REGEX: {self.__primitive_regex_helper.primitives_to_regex(tsl_lib.known_primitives_names_and_functor)}")
    self.__primitive_to_class_dict: Dict[str, str] = {}
    for class_name, primitive in tsl_lib.known_primitives:
      self.__primitive_to_class_dict[primitive.declaration.name] = class_name
      if primitive.declaration.functor_name is not None and primitive.declaration.functor_name != "" and primitive.declaration.functor_name != primitive.declaration.name:
        self.__primitive_to_class_dict[primitive.declaration.functor_name] = class_name
    

  def get_dependencies(self, implementation_str: str) -> List[str]:
    dependencies: Set[str] = set()
    for match in self.__primitive_regex.finditer(implementation_str):
      required_primitive = self.__primitive_regex_helper.get_primitive_name_from_match(match, self.__primitive_regex.groups)
      required_class = self.__primitive_to_class_dict[required_primitive]
      dependencies.add(required_class)
    return list(dependencies)
    
  def sort_tsl_classes(self, primitive_generator_implementation_fun_name: str):
    class_set: Set[str] = {c.name for c in self.__tsl_lib.primitive_class_set}
    dependency_graph: nx.DiGraph = nx.DiGraph()
    for class_name, primitive in self.__tsl_lib.known_primitives:
      fun = getattr(primitive, primitive_generator_implementation_fun_name)
      for implementation_str in fun(False):
        for match in self.__primitive_regex.finditer(implementation_str):
          required_primitive = self.__primitive_regex_helper.get_primitive_name_from_match(match, self.__primitive_regex.groups)
          print(f"primitive: {primitive.declaration.name} - required_primitive: {required_primitive}")

          required_class = self.__primitive_to_class_dict[required_primitive]
          if (required_class != class_name) and (required_primitive != primitive.declaration.name):
            dependency_graph.add_nodes_from([class_name, required_class])
            dependency_graph.add_edge(required_class, class_name)
            class_set.discard(class_name)
            class_set.discard(required_class)
            print(f"{class_name}::{primitive.declaration.name} requires {required_class}::{required_primitive}")
    try:
      order = nx.topological_sort(dependency_graph)
    except nx.NetworkXUnfeasible:
      print("Cyclic dependency detected. Please fix this first.")
      exit(1)
    for class_name in class_set:
      yield class_name
    for primitive_class in order:
        yield primitive_class


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
    
  @property
  def graph(self) -> nx.DiGraph:
    return self.__dependency_graph

  def __init__(self, tsl_lib: TSLLib) -> None:
    self.__tsl_lib = tsl_lib
    self.__dependency_graph: nx.DiGraph = nx.DiGraph()
    for primitive_class in self.__tsl_lib.primitive_class_set:
      self.__dependency_graph.add_node(self.PrimitiveClassNode(primitive_class.name))
    for class_name, primitive in self.__tsl_lib.known_primitives:
      self.__dependency_graph.add_node(self.PrimitiveNode(primitive.declaration.functor_name))
      self.__dependency_graph.add_edge(self.PrimitiveNode(primitive.declaration.functor_name), self.PrimitiveClassNode(class_name), label="part of")

    self.__primitive_regex_str: str = rf'(?<!([a-zA-Z]|_))({"|".join(map(lambda x: x.name, filter(lambda y: isinstance(y, self.PrimitiveNode), self.__dependency_graph)))})(?!([a-zA-Z]|_|\[|\.|\())'
    self.__primitive_regex = re.compile(self.__primitive_regex_str)
    
    for class_name, primitive in self.__tsl_lib.known_primitives:
      for implementation_str in primitive.get_implementations(False):
        for match in self.__primitive_regex.finditer(implementation_str):          
          required_primitive = match.group(2)
          self.__dependency_graph.add_edge(self.PrimitiveNode(required_primitive), self.PrimitiveNode(primitive.declaration.functor_name), label="requires")

  def inspect_tests(self) -> None:
    for _, primitive in self.__tsl_lib.known_primitives:
      for test_name, implementation_str in primitive.get_tests_implementations(False):
        fq_test_name = f"{primitive.declaration.functor_name}::{test_name}"
        self.__dependency_graph.add_node(self.PrimitiveTestNode(fq_test_name))
        self.__dependency_graph.add_edge(self.PrimitiveTestNode(fq_test_name), self.PrimitiveNode(primitive.declaration.functor_name), label="test of")
        for match in self.__primitive_regex.finditer(implementation_str):          
          required_primitive = match.group(2)
          if required_primitive != primitive.declaration.functor_name:
            self.__dependency_graph.add_edge(self.PrimitiveNode(required_primitive), self.PrimitiveTestNode(fq_test_name), label="depends on")

  def __has_primitive(self, primitive_name: str) -> bool:
    return self.PrimitiveNode(primitive_name) in self.__dependency_graph
  
  def __traverse_from_primitives(self, primitives_names: List[str], node_types_of_interest: list, reversed: bool, self_contained: bool = False) -> Set[str]:
    unknown_primitives = list(filter(lambda primitive_name: not self.__has_primitive(primitive_name), primitives_names))
    if len(unknown_primitives) > 0:
      raise Exception(f"Primitives {', '.join(map(str, unknown_primitives))} not found in dependency graph.")
    else:
      self_set = set(primitives_names) if self_contained else set()
      #edge[0]: source, edge[1]: target
      return {*(primitive_name for current_primitive_name in primitives_names for primitive_name in
        map(
          lambda edge: edge[1].name, 
          filter(
            lambda edge: any(isinstance(edge[1], node_type) for node_type in node_types_of_interest), 
            nx.bfs_edges(self.__dependency_graph, self.PrimitiveNode(current_primitive_name), reverse=reversed)))
      ), *self_set}
  
  def is_acyclic(self) -> bool:
    return nx.is_directed_acyclic_graph(self.__dependency_graph)

  def get_cycles_as_str(self) -> List[str]:
    return list(map(lambda list_of_nodes: " -> ".join(map(lambda node: node.name, list_of_nodes)), nx.simple_cycles(self.__dependency_graph)))

  def get_direct_predecessor_names(self, node, node_types_of_interest: list) -> List[str]:
    return list(map(lambda edge: edge[0].name, filter(lambda edge: any(isinstance(edge[0], node_type) for node_type in node_types_of_interest), self.__dependency_graph.in_edges(node))))

  def get_primitive_nodes(self) -> List[TSLDependencyGraph.PrimitiveNode]:
    return list(filter(lambda node: isinstance(node, self.PrimitiveNode), self.__dependency_graph.nodes))
  
  def get_primitives_count(self) -> int:
    return sum(1 for _ in filter(lambda node: isinstance(node, self.PrimitiveNode), self.__dependency_graph.nodes))
  
  def get_class_nodes(self) -> List[TSLDependencyGraph.PrimitiveClassNode]:
    return list(filter(lambda node: isinstance(node, self.PrimitiveClassNode), self.__dependency_graph.nodes))
  
  def class_nodes(self) -> Iterator[TSLDependencyGraph.PrimitiveClassNode]:
    return filter(lambda node: isinstance(node, self.PrimitiveClassNode), self.__dependency_graph.nodes)
  
  def get_classes_count(self) -> int:
    return sum(1 for _ in filter(lambda node: isinstance(node, self.PrimitiveClassNode), self.__dependency_graph.nodes))
  
  def get_test_nodes(self) -> List[TSLDependencyGraph.PrimitiveTestNode]:
    return list(filter(lambda node: isinstance(node, self.PrimitiveTestNode), self.__dependency_graph.nodes))
  
  def get_tests_count(self) -> int:
    return sum(1 for _ in filter(lambda node: isinstance(node, self.PrimitiveTestNode), self.__dependency_graph.nodes))
  
  def get_required_primitives(self, primitive_names: str|List[str], self_contained: bool = False) -> List[str]:
    if isinstance(primitive_names, str):
      primitive_names = primitive_names.split(" ")
    return list(self.__traverse_from_primitives(primitive_names, [self.PrimitiveNode], True, self_contained))
    
  def get_dependent_primitives(self, primitive_names: str|List[str], self_contained: bool = False) -> List[str]:
    if isinstance(primitive_names, str):
      primitive_names = primitive_names.split(" ")
    return list(self.__traverse_from_primitives(primitive_names, [self.PrimitiveNode], False, self_contained))
  
  def get_associated_class(self, primitive_name) -> str:
    if not self.__has_primitive(primitive_name):
      raise Exception(f"Primitive {primitive_name} not found in dependency graph.")
    else:
      for successor in self.__dependency_graph.successors(self.PrimitiveNode(primitive_name)):
        if isinstance(successor, self.PrimitiveClassNode):
          return successor.name
      raise Exception(f"Primitive {primitive_name} has no associated class.")

  def get_required_classes(self, primitive_names: str|List[str]) -> List[str]:
    required_primitives = self.get_required_primitives(primitive_names, True)
    return list({
      self.get_associated_class(required_primitive) for required_primitive in required_primitives
    })
  
  def get_dependent_classes(self, primitive_names: str|List[str]) -> List[str]:
    dependent_primitives = self.get_dependent_primitives(primitive_names, True)
    return list({
      self.get_associated_class(dependent_primitive) for dependent_primitive in dependent_primitives
    })  

  def sorted_classes(self) -> Generator[str, None, None]:
    class_graph = nx.DiGraph()
    for cls in self.class_nodes():
      class_graph.add_node(cls.name)
      for predecessor in self.get_required_classes(self.get_direct_predecessor_names(cls, [self.PrimitiveNode])):
        if predecessor != cls.name:
          if False:
            if predecessor == "calc" and cls.name == "convert":
              for x in self.get_direct_predecessor_names(cls, [self.PrimitiveNode]):
                for requc in self.get_required_classes([x]):
                  print(f"{x} ---> {requc}")
          class_graph.add_edge(predecessor, cls.name)
    try:
      ordered_class_graph = nx.topological_sort(class_graph)
    except nx.NetworkXUnfeasible:
      print("Unable to sort class graph.")
      exit(1)
    for cls in ordered_class_graph:
        yield cls

  def get_required_tests(self, primitive_names: str|List[str]) -> List[str]:
    if isinstance(primitive_names, str):
      primitive_names = primitive_names.split(" ")
    return list(self.__traverse_from_primitives(primitive_names, [self.PrimitiveTestNode], True))
  
  def get_dependent_tests(self, primitive_names: str|List[str]) -> List[str]:
    if isinstance(primitive_names, str):
      primitive_names = primitive_names.split(" ")
    return list(self.__traverse_from_primitives(primitive_names, [self.PrimitiveTestNode], False))
    
  def tested_primitive_count(self) -> int:
    nodes = self.get_primitive_nodes()
    result = 0
    for primitive_node in nodes:
      test_cases = self.get_direct_predecessor_names(primitive_node, [self.PrimitiveTestNode])
      if len(test_cases) > 0:
        result += 1
    return result
  
  def missing_tests(self) -> Generator[str, None, None]:
    nodes = self.get_primitive_nodes()
    for primitive_node in nodes:
      test_cases = self.get_direct_predecessor_names(primitive_node, [self.PrimitiveTestNode])
      if len(test_cases) == 0:
        yield primitive_node.name

  def as_str(self, include_tests: bool = False) -> str:
    class_count = self.get_classes_count()
    primitives_count = self.get_primitives_count()
    result = f"""TSL - Summary:
  - # Primitive Classes:  {class_count}
  - # Primitives:         {primitives_count}"""
    if include_tests:
      tests_count = self.get_tests_count()
      tested_primitive_count = self.tested_primitive_count()
      test_coverage = tested_primitive_count / primitives_count
      average_tests_per_primitive = (tests_count / primitives_count)
      result = f"""{result}
  - # Tests:              {tests_count}
  - Primitives w/ Tests:  {tested_primitive_count}
  - Primitives w/o Tests: {primitives_count - tested_primitive_count}
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
