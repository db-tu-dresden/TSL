from __future__ import annotations
from generator.core.tsl_config import config
from generator.core.ctrl.tsl_lib import TSLLib

from typing import Generator, Dict, Iterator, Set, List, Tuple, NewType, Union
import re
import networkx as nx
from dataclasses import dataclass
import pandas as pd


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
  
  NodeType = Union[PrimitiveClassNode, PrimitiveNode, PrimitiveTestNode]
    
  @property
  def graph(self) -> nx.DiGraph:
    return self.__dependency_graph

  def __init__(self, tsl_lib: TSLLib) -> None:
    self.__tsl_lib = tsl_lib
    self.__dependency_graph: nx.DiGraph = nx.DiGraph()
    for primitive_class in self.__tsl_lib.primitive_class_set:
      self.__dependency_graph.add_node(self.PrimitiveClassNode(primitive_class.name))
    for class_name, primitive in self.__tsl_lib.known_primitives:
      self.__dependency_graph.add_node(TSLDependencyGraph.PrimitiveNode(primitive.declaration.functor_name))
      self.__dependency_graph.add_edge(TSLDependencyGraph.PrimitiveNode(primitive.declaration.functor_name), self.PrimitiveClassNode(class_name), label="part of")

    self.__primitive_regex_str: str = rf'(?<!([a-zA-Z]|_))({"|".join(map(lambda x: x.name, filter(lambda y: isinstance(y, TSLDependencyGraph.PrimitiveNode), self.__dependency_graph)))})(?!([a-zA-Z]|_|\[|\.|\())'
    self.__primitive_regex = re.compile(self.__primitive_regex_str)
    
    for class_name, primitive in self.__tsl_lib.known_primitives:
      for implementation_str in primitive.get_implementations(False):
        for match in self.__primitive_regex.finditer(implementation_str):          
          required_primitive = match.group(2)
          if required_primitive != primitive.declaration.functor_name:
            self.__dependency_graph.add_edge(TSLDependencyGraph.PrimitiveNode(required_primitive), TSLDependencyGraph.PrimitiveNode(primitive.declaration.functor_name), label="requires")

  def inspect_tests(self) -> None:
    for _, primitive in self.__tsl_lib.known_primitives:
      for test_name, implementation_str in primitive.get_tests_implementations(False):
        fq_test_name = f"{primitive.declaration.functor_name}::{test_name}"
        self.__dependency_graph.add_node(self.PrimitiveTestNode(fq_test_name))
        self.__dependency_graph.add_edge(self.PrimitiveTestNode(fq_test_name), TSLDependencyGraph.PrimitiveNode(primitive.declaration.functor_name), label="test of")
        for match in self.__primitive_regex.finditer(implementation_str):          
          required_primitive = match.group(2)
          if required_primitive != primitive.declaration.functor_name:
            self.__dependency_graph.add_edge(TSLDependencyGraph.PrimitiveNode(required_primitive), self.PrimitiveTestNode(fq_test_name), label="depends on")
  
  def find(self, name: str) -> NodeType|None:
    for node_type in TSLDependencyGraph.NodeType.__args__:
      node = node_type(name)
      if node in self.__dependency_graph:
        return node
    return None
  
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

  def nodes_by_type(self, node_types_of_interest: list) -> Generator[NodeType, None, None]:
    yield from filter(lambda node: any(isinstance(node, node_type) for node_type in node_types_of_interest), self.__dependency_graph.nodes)

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

