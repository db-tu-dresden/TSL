from __future__ import annotations
import logging
from typing import Generator, Dict, Iterator, Set, List, Tuple, NewType, Union
import re
import networkx as nx
from dataclasses import dataclass
import pandas as pd
from enum import Enum
from natsort import natsort_key


from generator.core.tsl_config import config
from generator.core.ctrl.tsl_lib import TSLLib
from generator.utils.log_utils import LogInit



class TSLInspectionLevelOfDetail(Enum):
  '''
  Inspection level of detail.
  The default adds primitive-classes, primitives and the dependencies between them and between primitives (through their implementations).
  This is necessary to ensure a correct generated library.
  If the level of detail is increased, the dependency graph is extended with the following information:
  (i) PRIMITIVE_INSTANTIATION: Adds all possible instantiations of a primitive (e.g., add<float, sse>) and its dependencies.
  (ii) TEST: Adds all test implementations and their dependencies (to primitives).
  (iii) TEST_INSTANTIATION: Adds all possible instantiations of a test (e.g., add<float, sse>::test1) and its concrete dependencies.
  '''
  DEFAULT = 1
  PRIMITIVE_INSTANTIATION = 2
  TEST = 3
  TEST_INSTANTIATION = 4

class TSLDependencyGraphLevelOfDetail(Enum):
  CLASS = 1
  PRIMITIVE = 2
  PRIMITIVE_IMPLEMENTATION = 3
  TEST = 4
  TEST_IMPLEMENTATION = 5

class TSLDependencyGraph:
  '''
  Dependency graph for the TSL.
  The dependency graph is a directed graph, where the nodes are of type:
  (i) PrimitiveClassNode: Represents a primitive-class
  (ii) PrimitiveNode: Represents a primitive
  (iii) PrimitiveImplementationNode: Represents a concrete primitive implementation (aka. primitive definition, e.g., add<float, sse>)
  (iv) PrimitiveTestNode: Represents a test case for a primitive
  (v) PrimitiveTestImplementationNode: Represents a concrete test implementation (e.g., add<float, sse>::test1)
  The nodes are connected with edges, which are labeled with the following information:
  (i) "part of": PrimitiveNode -> PrimitiveClassNode
  (ii) "overload of": PrimitiveNode -> PrimitiveNode (for function overloading)
  (iii) "concrete instantiation of": PrimitiveImplementationNode -> PrimitiveNode
  (iv) "requirement of": PrimitiveNode -> PrimitiveNode (for primitive dependencies, e.gl, mod depends on cast --> mod requires cast --> cast is requirement of mod)
  (v) "concrete requirement of": PrimitiveImplementationNode -> PrimitiveImplementationNode (if an edge "requirement of" exists between two PrimitiveNodes, all possible instantiations carry the same dependency)
  (vi) "test of": PrimitiveTestNode -> PrimitiveNode
  (vii) "concrete instantiation of": PrimitiveTestImplementationNode -> PrimitiveTestNode
  (viii) "requirement of": PrimitiveNode -> PrimitiveTestNode (for primitive dependencies, e.gl, mod depends on cast --> mod requires cast --> cast is requirement of mod)
  (ix) "concrete requirement of": PrimitiveImplementationNode -> PrimitiveTestImplementationNode (if an edge "requirement of" exists between PrimitiveTestNode and PrimitiveNode, all possible instantiations carry the same dependency)

  Usage:
    > tsl_dependency_graph = TSLDependencyGraph(tsl_lib, TSLInspectionLevelOfDetail.TEST_INSTANTIATION)
    > if not tsl_dependency_graph.is_well_defined():
    >   # log errors
    >   tsl_dependency_graph.log_errors()
    >   raise ValueError("Dependency graph is not well defined. Could not generate TSL.")
    > if tsl_dependecy_graph.has_warnings():
    >   # log warnings
    >   tsl_dependency_graph.log_warnings()
  '''

  @dataclass(order=True, unsafe_hash=True, frozen=True)
  class PrimitiveClassNode:
    _class_name: str
    type: str = "class"
    size: int = 10
    def id(self) -> str:
      return self._class_name
    def __str__(self):
      return self.id()
    def __repr__(self):
      return f"PrimitiveClassNode: {{{str(self)}}}"
    @classmethod
    def create(cls, name: str) -> TSLDependencyGraph.PrimitiveClassNode:
      return cls(name)
    @property
    def class_name(self) -> str:
      return self._class_name    

  class PrimitiveNode:
    type: str = "primitive"
    size: int = 5
    def __init__(self, name: str):
      self._primitive_name: str = name
      self._valid: bool = True
      self._safe: bool = True
      self._invalidation_notes: List[str] = []
      self._warning_notes: List[str] = []
    def id(self) -> str:
      return self._primitive_name
    def __str__(self):
      return f"{self.id()} (valid: {self._valid})"
    def __repr__(self):
      return f"PrimitiveNode: {{{str(self)}}}"
    @classmethod
    def create(cls, name: str) -> TSLDependencyGraph.PrimitiveNode:
      return cls(name)
    def id(self) -> str:
      return self._primitive_name
    @property
    def primitive_name(self) -> str:
      return self._primitive_name
    @property
    def valid(self) -> bool:
      return self._valid
    def invalidate(self, invalidation_note: str) -> None:
      self._valid = False
      if invalidation_note not in self._invalidation_notes:
        self._invalidation_note.append(invalidation_note)
    def invalidation_notes(self) -> Iterator[str]:
      yield from self._invalidation_notes
    @property
    def unsafe(self) -> bool:
      return not self._safe
    @property
    def safe(self) -> bool:
      return self._safe
    def mark_unsafe(self, unsafe_note: str) -> None:
      self._safe = False
      if unsafe_note not in self._warning_notes:
        self._warning_notes.append(unsafe_note)
    def warning_notes(self) -> Iterator[str]:
      yield from self._warning_notes
    def __lt__(self, other: TSLDependencyGraph.PrimitiveNode) -> bool:
      # Sort by name using natural sorting
      if isinstance(other, TSLDependencyGraph.PrimitiveNode):
        return natsort_key(self.id()) < natsort_key(other.id())
      else:
        return NotImplemented
    def __le__(self, other: TSLDependencyGraph.PrimitiveNode) -> bool:
      if isinstance(other, TSLDependencyGraph.PrimitiveNode):
        return natsort_key(self.id()) <= natsort_key(other.id())
      else:
        return NotImplemented
    def __gt__(self, other: TSLDependencyGraph.PrimitiveNode) -> bool:
      return not self.__le__(other)
    def __ge__(self, other: TSLDependencyGraph.PrimitiveNode) -> bool:
      return not self.__lt__(other)
    def __eq__(self, other: TSLDependencyGraph.PrimitiveNode) -> bool:
      if isinstance(other, TSLDependencyGraph.PrimitiveNode):
        return self.id() == other.id()
      else:
        return NotImplemented
    def __ne__(self, other: TSLDependencyGraph.PrimitiveNode) -> bool:
      return not self.__eq__(other)
    def __hash__(self) -> int:
      return hash(self._primitive_name)

  class PrimitiveImplementationNode:
    type: str = "primitive_implementation"
    size: int = 3
    implementation_regex_str = re.compile(rf'(?P<primitive_name>[^<]+)\s*<\s*(?P<ctype>[^,]+)\s*,\s*(?P<extension>[^>]+)\s*>')
    def __init__(self, primitive_name: str, extension: str, ctype: str) -> None:
      self._primitive_name: str = primitive_name
      self._extension: str = extension
      self._ctype: str = ctype
      self._valid: bool = True
      self._invalidation_notes: List[str] = []
    def id(self) -> str:
      return f"{self._primitive_name}<{self._ctype}, {self._extension}>"
    def __str__(self):
      return f"{self.id()} (valid: {self._valid})"
    def __repr__(self):
      return f"PrimitiveImplementationNode: {{{str(self)}}}"
    @classmethod
    def create(cls, name: str, extension: str = None, ctype: str = None) -> TSLDependencyGraph.PrimitiveImplementationNode:
      if extension is not None:
        if ctype is not None:
          return cls(name, extension, ctype)
        else:
          raise ValueError("ctype must be specified if extension is specified")
      match = cls.implementation_regex_str.match(name)
      if match is None:
        raise ValueError(f"Invalid implementation name: {name}")
      else:
        return cls(match.group("primitive_name").strip(), match.group("extension").strip(), match.group("ctype").strip())    
    @property
    def primitive_name(self) -> str:
      return self._primitive_name
    @property
    def extension(self) -> str:
      return self._extension
    @property
    def ctype(self) -> str:
      return self._ctype
    @property
    def valid(self) -> bool:
      return self._valid
    def invalidate(self, invalidation_note: str) -> None:
      self._valid = False
      if invalidation_note not in self._invalidation_notes:
        self._invalidation_note.append(invalidation_note)
    def __lt__(self, other: TSLDependencyGraph.PrimitiveImplementationNode) -> bool:
      # Sort by name using natural sorting
      if isinstance(other, TSLDependencyGraph.PrimitiveImplementationNode):
        return natsort_key(self.id()) < natsort_key(other.id())
      else:
        return NotImplemented
    def __le__(self, other: TSLDependencyGraph.PrimitiveImplementationNode) -> bool:
      if isinstance(other, TSLDependencyGraph.PrimitiveImplementationNode):
        return natsort_key(self.id()) <= natsort_key(other.id())
      else:
        return NotImplemented
    def __gt__(self, other: TSLDependencyGraph.PrimitiveImplementationNode) -> bool:
      return not self.__le__(other)
    def __ge__(self, other: TSLDependencyGraph.PrimitiveImplementationNode) -> bool:
      return not self.__lt__(other)
    def __eq__(self, other: TSLDependencyGraph.PrimitiveImplementationNode) -> bool:
      if isinstance(other, TSLDependencyGraph.PrimitiveImplementationNode):
        return self.id() == other.id()
      else:
        return NotImplemented
    def __ne__(self, other: TSLDependencyGraph.PrimitiveImplementationNode) -> bool:
      return not self.__eq__(other)
    def __hash__(self) -> int:
      return hash((self._primitive_name, self._extension, self._ctype))
    
  class PrimitiveTestNode:
    type: str = "test"
    size: int = 3
    def __init__(self, primitive_name: str, test_name: str, implicit_reliable: bool = False) -> None:
      self._primitive_name: str = primitive_name
      self._test_name: str = test_name
      self._valid: bool = True
      self._invalidation_notes: List[str] = []
      self._safe: bool = True
      self.__implicit_reliable: bool = implicit_reliable
      self._warning_notes: List[str] = []
    def id(self) -> str:
      return f"{self._primitive_name}::{self._test_name}"
    def __str__(self):
      return f"{self.id()} (valid: {self._valid}, safe: {self._safe})"
    def __repr__(self):
      return f"PrimitiveTestNode: {{{str(self)}}}"
    @classmethod
    def create(cls, name: str, test_name: str = None, implicit_reliable: bool = False) -> TSLDependencyGraph.PrimitiveTestNode:
      if test_name is not None:
        return cls(name, test_name, implicit_reliable)
      else:
        return cls(*name.split("::"), implicit_reliable)
    @property
    def primitive_name(self) -> str:
      return self._primitive_name
    @property
    def test_name(self) -> str:
      return self._test_name
    @property
    def valid(self) -> bool:
      return self._valid
    def invalidate(self, invalidation_note: str) -> None:
      self._valid = False
      if invalidation_note not in self._invalidation_notes:
        self._invalidation_note.append(invalidation_note)
    @property
    def unsafe(self) -> bool:
      return not self._safe
    @property
    def safe(self) -> bool:
      return self._safe
    def mark_unsafe(self, unsafe_note: str) -> None:
      if not self.__implicit_reliable:
        self._safe = False
        if unsafe_note not in self._warning_notes:
          self._warning_notes.append(unsafe_note)
    def warning_notes(self) -> Iterator[str]:
      yield from self._warning_notes
    def __lt__(self, other: TSLDependencyGraph.PrimitiveTestNode) -> bool:
      # Sort by name using natural sorting
      if isinstance(other, TSLDependencyGraph.PrimitiveTestNode):
        return natsort_key(self.id()) < natsort_key(other.id())
      else:
        return NotImplemented
    def __le__(self, other: TSLDependencyGraph.PrimitiveTestNode) -> bool:
      if isinstance(other, TSLDependencyGraph.PrimitiveTestNode):
        return natsort_key(self.id()) <= natsort_key(other.id())
      else:
        return NotImplemented
    def __gt__(self, other: TSLDependencyGraph.PrimitiveTestNode) -> bool:
      return not self.__le__(other)
    def __ge__(self, other: TSLDependencyGraph.PrimitiveTestNode) -> bool:
      return not self.__lt__(other)
    def __eq__(self, other: TSLDependencyGraph.PrimitiveTestNode) -> bool:
      if isinstance(other, TSLDependencyGraph.PrimitiveTestNode):
        return self.id() == other.id()
      else:
        return NotImplemented
    def __ne__(self, other: TSLDependencyGraph.PrimitiveTestNode) -> bool:
      return not self.__eq__(other)
    def __hash__(self) -> int:
      return hash((self._primitive_name, self._test_name))
    
  class PrimitiveTestImplementationNode:
    type: str = "test_implementation"
    size: int = 3
    implementation_regex_str = re.compile(rf'(?P<primitive_name>[^:]+)\s*::\s*(?P<test_name>[^<]+)\s*<\s*(?P<ctype>[^,]+)\s*,\s*(?P<extension>[^>]+)\s*>')
    def __init__(self, primitive_name: str, test_name: str, extension: str, ctype: str):
      self._primitive_name: str = primitive_name
      self._test_name: str = test_name
      self._extension: str = extension
      self._ctype: str = ctype
      self._valid: bool = True
      self._invalidation_notes: List[str] = []
      self._safe: bool = True
      self._warning_notes: List[str] = []
    def id(self) -> str:
      return f"{self._primitive_name}::{self._test_name}<{self._ctype}, {self._extension}>"
    def __str__(self):
      return f"{self.id()} (valid: {self._valid}, safe: {self._safe})"
    def __repr__(self):
      return f"PrimitiveTestImplementationNode: {{{str(self)}}}"
    @classmethod
    def create(cls, name: str, test_name: str = None, extension: str = None, ctype: str = None) -> TSLDependencyGraph.PrimitiveTestImplementationNode:
      if test_name is not None:
        if extension is None or ctype is None:
          raise ValueError("If test_name is specified, extension and ctype must be specified as well")
        else:
          return cls(name, test_name, extension, ctype)
      else:
        match = cls.implementation_regex_str.match(name)
        if match is None:
          raise ValueError(f"Invalid implementation name: {name}")
        else:
          return cls(match.group("primitive_name").strip(), match.group("test_name").strip(), match.group("extension").strip(), match.group("ctype").strip())
    @property
    def primitive_name(self) -> str:
      return self._primitive_name
    @property
    def test_name(self) -> str:
      return self._test_name
    @property
    def extension(self) -> str:
      return self._extension
    @property
    def ctype(self) -> str:
      return self._ctype
    @property
    def valid(self) -> bool:
      return self._valid
    def invalidate(self, invalidation_note: str) -> None:
      self._valid = False
      if invalidation_note not in self._invalidation_notes:
        self._invalidation_note.append(invalidation_note)
    @property
    def unsafe(self) -> bool:
      return not self._safe
    @property
    def safe(self) -> bool:
      return self._safe
    def mark_unsafe(self, warning_note: str) -> None:
      self._safe = False
      if warning_note not in self._warning_notes:
        self._warning_notes.append(warning_note)
    def warning_notes(self) -> Iterator[str]:
      yield from self._warning_notes
    def __lt__(self, other: TSLDependencyGraph.PrimitiveTestImplementationNode) -> bool:
      # Sort by name using natural sorting
      if isinstance(other, TSLDependencyGraph.PrimitiveTestImplementationNode):
        return natsort_key(self.id()) < natsort_key(other.id())
      else:
        return NotImplemented
    def __le__(self, other: TSLDependencyGraph.PrimitiveTestImplementationNode) -> bool:
      if isinstance(other, TSLDependencyGraph.PrimitiveTestImplementationNode):
        return natsort_key(self.id()) <= natsort_key(other.id())
      else:
        return NotImplemented
    def __gt__(self, other: TSLDependencyGraph.PrimitiveTestImplementationNode) -> bool:
      return not self.__le__(other)
    def __ge__(self, other: TSLDependencyGraph.PrimitiveTestImplementationNode) -> bool:
      return not self.__lt__(other)
    def __eq__(self, other: TSLDependencyGraph.PrimitiveTestImplementationNode) -> bool:
      if isinstance(other, TSLDependencyGraph.PrimitiveTestImplementationNode):
        return self.id() == other.id()
      else:
        return NotImplemented
    def __ne__(self, other: TSLDependencyGraph.PrimitiveTestImplementationNode) -> bool:
      return not self.__eq__(other)
    def __hash__(self) -> int:
      return hash((self._primitive_name, self._test_name, self._extension, self._ctype))
  
  NodeType = Union[PrimitiveClassNode, PrimitiveNode, PrimitiveImplementationNode, PrimitiveTestNode, PrimitiveTestImplementationNode]
    
  def __add_node(self, node_type, *args) -> NodeType:
    node = node_type.create(*args)
    self.__dependency_graph.add_node(node)
    self.__known_nodes[node.id()] = node
    return node
  
  def __get_node(self, node: NodeType) -> NodeType:
    return self.__known_nodes[node.id()]

  def __get_node_by_args(self, node_type, *args) -> NodeType|None:
    node = node_type.create(*args)
    if node.id() in self.__known_nodes:
      return self._known_nodes[node.id()]
    else:
      return None
  
  @property
  def graph(self) -> nx.DiGraph:
    return self.__dependency_graph

  def is_well_defined(self) -> bool:
    return self.__well_defined
  
  def has_warnings(self) -> bool:
    return self.__has_warnings
  
  def log_errors(self) -> None:
    for primitive_node in self.nodes_by_type([TSLDependencyGraph.PrimitiveNode]):
      if not primitive_node.valid:
        for invalidity_note in primitive_node.invalidation_notes():
          self.log(logging.ERROR, f"{primitive_node}: {invalidity_note}")
    if self.__level_of_detail.value >= TSLDependencyGraphLevelOfDetail.PRIMITIVE_IMPLEMENTATION.value:
      for primitive_implementation_node in self.nodes_by_type([TSLDependencyGraph.PrimitiveImplementationNode]):
        if not primitive_implementation_node.valid:
          for invalidity_note in primitive_implementation_node.invalidation_notes():
            self.log(logging.ERROR, f"{primitive_implementation_node}: {invalidity_note}")
    if self.__level_of_detail.value >= TSLDependencyGraphLevelOfDetail.TEST.value:
      for primitive_test_node in self.nodes_by_type([TSLDependencyGraph.PrimitiveTestNode]):
        if not primitive_test_node.valid:
          for invalidity_note in primitive_test_node.invalidation_notes():
            self.log(logging.ERROR, f"{primitive_test_node}: {invalidity_note}")
    if self.__level_of_detail.value >= TSLDependencyGraphLevelOfDetail.TEST_IMPLEMENTATION.value:
      for primitive_test_implementation_node in self.nodes_by_type([TSLDependencyGraph.PrimitiveTestImplementationNode]):
        if not primitive_test_implementation_node.valid:
          for invalidity_note in primitive_test_implementation_node.invalidation_notes():
            self.log(logging.ERROR, f"{primitive_test_implementation_node}: {invalidity_note}")

  def log_warnings(self) -> None:
    for primitive_node in self.nodes_by_type([TSLDependencyGraph.PrimitiveNode]):
      if not primitive_node.safe:
        for warning_note in primitive_node.warning_notes():
          self.log(logging.WARNING, f"{primitive_node}: {warning_note}")
    if self.__level_of_detail.value >= TSLDependencyGraphLevelOfDetail.TEST.value:
      for primitive_test_node in self.nodes_by_type([TSLDependencyGraph.PrimitiveTestNode]):
        if not primitive_test_node.safe:
          for warning_note in primitive_test_node.warning_notes():
            self.log(logging.WARNING, f"{primitive_test_node}: {warning_note}")
    if self.__level_of_detail.value >= TSLDependencyGraphLevelOfDetail.TEST_IMPLEMENTATION.value:
      for primitive_test_implementation_node in self.nodes_by_type([TSLDependencyGraph.PrimitiveTestImplementationNode]):
        if not primitive_test_implementation_node.safe:
          for warning_note in primitive_test_implementation_node.warning_notes():
            self.log(logging.ERROR, f"{primitive_test_implementation_node}: {warning_note}")
  

  def roots(self, node_types_of_interest: list = None) -> Generator[NodeType, None, None]:
    '''
    Returns all nodes without incoming edges.
    If node_types_of_interest is not empty, only nodes of the given types are returned.
    '''
    if node_types_of_interest is None:
      yield from filter(lambda node: self.__dependency_graph.in_degree(node) == 0, self.__dependency_graph.nodes)
    else:
      yield from filter(lambda node: self.__dependency_graph.in_degree(node) == 0 and any(isinstance(node, node_type) for node_type in node_types_of_interest), self.__dependency_graph.nodes)      
  
  def nodes_by_type(self, node_types_of_interest: list) -> Generator[NodeType, None, None]:
    '''
    Returns all nodes of the given node_types_of_interest.
    '''
    yield from filter(lambda node: any(isinstance(node, node_type) for node_type in node_types_of_interest), self.__dependency_graph.nodes)

  def edges_by_label(self, edge_label: str, type: str, nodes_of_interest: list = []) -> Generator[Tuple[NodeType, NodeType], None, None]:
    '''
    Returns all edges of the given edge_label.
    If nodes_of_interest is not empty, only edges directly connected to the given nodes are returned.
    '''
    if type == "in":
      if len(nodes_of_interest) == 0:
        edges_of_interest = self.__dependency_graph.in_edges()
      else:
        edges_of_interest = self.__dependency_graph.in_edges(nodes_of_interest)
    elif type == "out":
      if len(nodes_of_interest) == 0:
        edges_of_interest = self.__dependency_graph.out_edges()
      else:
        edges_of_interest = self.__dependency_graph.out_edges(nodes_of_interest)
    elif type == "all":
      if len(nodes_of_interest) == 0:
        edges_of_interest = self.__dependency_graph.edges()
      else:
        edges_of_interest = self.__dependency_graph.edges(nodes_of_interest)
    else:
      raise ValueError(f"Unknown edge type {type} (expected 'in', 'out' or 'all')")
    for edge in filter(lambda edge: "label" in self.__dependency_graph.get_edge_data(*edge) and self.__dependency_graph.get_edge_data(*edge)["label"] == edge_label, edges_of_interest):
      yield edge
  
  def traverse_nodes(self, start_nodes: List[NodeType], reversed: bool, self_contained: bool = False) -> Generator[NodeType, None, None]:
    '''
    Traverses (breadth first) the dependency graph starting from the given start_nodes.
    If self_contained is True, the start_nodes are yielded first.
    If reversed is True, the graph is traversed in reverse order.
    '''
    for current_node in start_nodes:
      if self_contained:
        yield current_node
      for edge in nx.bfs_edges(self.__dependency_graph, current_node, reverse=reversed):
        yield edge[1]

  def traverse_by_type(self, start_nodes: List[NodeType], relevant_node_type: list, reversed:bool, self_contained: bool = False) -> Generator[NodeType, None, None]:
    '''
    Traverses (breadth first) the dependency graph starting from the given start_nodes.
    If self_contained is True, the start_nodes are yielded first.
    If reversed is True, the graph is traversed in reverse order.
    Only nodes of the given relevant_node_type are yielded.    
    '''
    for node in self.traverse_nodes(start_nodes, reversed, self_contained):
      if any(isinstance(node, node_type) for node_type in relevant_node_type):
        yield node

  def slice(self, filter_node_type: NodeType, relevant_node_names: list = [], relevant_node_type: list = []) -> nx.DiGraph:
    '''
    Creates a subgraph of the dependency graph, where all nodes of the given filter_node_type are included (with their respective edges).
    All requirements were added too.
    If relevant_node_names is not empty, only nodes with the given names are included.
    If relevant_node_type is not empty, only nodes of the given types are included.
    '''
    if len(relevant_node_type) == 0:
      start_nodes: List[TSLDependencyGraph.NodeType] = [node for node in self.nodes_by_type([filter_node_type])]
    else:
      start_nodes: List[TSLDependencyGraph.NodeType] = [node for node in self.nodes_by_type([filter_node_type]) if node.name in relevant_node_names]
    if len(relevant_node_names) == 0:
      return self.__dependency_graph.subgraph(self.traverse_nodes(start_nodes, reversed=True, self_contained=True))
    else:
      return self.__dependency_graph.subgraph(self.traverse_by_type(start_nodes, relevant_node_type, reversed=True, self_contained=True))

  def sorted_classes(self) -> Generator[PrimitiveClassNode, None, None]:
    '''
    Returns a list of all primitive-classes sorted by their dependencies and lexicographical by their respective name.
    '''
    yield from nx.lexicographical_topological_sort(self.__dependency_graph.subgraph(self.nodes_by_type([TSLDependencyGraph.PrimitiveClassNode])))

  def __add_primitive_classes(self, tsl_lib: TSLLib) -> None:
    '''
    Iterates over all primitive-classes within the tsl_lib.
    Creates PrimitiveClassNode(s) for every primitive-class and add them to the dependency graph.
    '''
    for primitive_class in tsl_lib.primitive_class_set:
      self.__add_node(TSLDependencyGraph.PrimitiveClassNode, primitive_class.name)

  def __add_primitives(self, tsl_lib: TSLLib) -> None:
    '''
    Iterates over all primitives within the tsl_lib.
    Creates PrimitiveNodes for every primitive and add them to the dependency graph.
    Adds Edges between every primitive and its associated primitive-class.
    If the primitive name is not equal to the functor name (function overloading), two nodes are added:
    (i) a primitive-node for the primitive with its associated class
    (ii) a primitive-node for the overload with the functor name
    Additionally, the overload is connected with the primitive node via a named edge (overload of).
    '''
    for class_name, primitive in tsl_lib.known_primitives:
      primitive_class_node = self.__get_node_by_args(TSLDependencyGraph.PrimitiveClassNode, class_name)
      if primitive.declaration.name != primitive.declaration.functor_name:
        primitive_node = self.__add_node(TSLDependencyGraph.PrimitiveNode, primitive.declaration.name)
        primitive_functor_node = self.__ad_node(TSLDependencyGraph.PrimitiveNode, primitive.declaration.functor_name)
        self.__dependency_graph.add_edge(primitive_functor_node, primitive_node, label="overload of")
        self.__dependency_graph.add_edge(primitive_node, primitive_class_node, label="part of")
      else:
        primitive_node = self.__add_node(TSLDependencyGraph.PrimitiveNode, primitive.declaration.name)
        self.__dependency_graph.add_edge(primitive_node, primitive_class_node, label="part of")

  def __add_primitive_instantiations(self, tsl_lib: TSLLib) -> None:
    '''
    Iterates over all primitives within the tsl_lib.
    For every definition, a PrimitiveImplementationNode is added to the dependency graph as well as a named
    edge ("concrete instantiation") betwwen the implementation-node and the primitive-node.    
    '''
    for _, primitive in tsl_lib.known_primitives:
      primitive_name = primitive.declaration.functor_name
      primitive_node = self.__get_node_by_args(TSLDependencyGraph.PrimitiveNode, primitive_name)
      for definition in primitive.definitions:
        extension = definition.target_extension
        for ctype in definition.ctypes:
          primitive_instantiation_node = self.__add_node(TSLDependencyGraph.PrimitiveImplementationNode, primitive_name, extension, ctype)
          self.__dependency_graph.add_edge(primitive_instantiation_node, primitive_node, label="concrete instantiation of")

  def __add_primitive_implementation_dependencies(self, tsl_lib: TSLLib, primitive_pattern: re.Pattern, level_of_detail: TSLInspectionLevelOfDetail) -> None:
    '''
    Default behaviour:
      Iterates over all definitions for every primitive.
      For every definition, the implementation is checked, whether other tsl-primitives are used (=requirement).
      If a requirement is found, an edge (with the label "requirement of") is added to the graph, connecting
      the required primitive node with the dependent one.

      Error Handling: SILENT
        If a required primitive does not exist in the graph, the dependent PrimitiveNode is marked as invalid.

    level_of_details >= PRIMITIVE_INSTANTIATION:
      For the target_extension of the current definition and all specified ctypes a named edge ("concrete requirement of") 
      is added, connecting the dependent PrimitiveImplementationNode with the required PrimitiveImplementationNode.
      The (rare) case of a primitive depending on itself is ignored (no id-edges are added).
      
      Error Handling: SILENT
        If a required PrimitiveImplementationNode is not present in the graph, the dependent 
        PrimitiveImplementationNode is marked as invalid.
      Error Handling: EXCEPTION
        If a required tsl-primitive was found in the implementation but a ctype or extension could not be 
        parsed, a ValueError is raised.
    '''
    for _, primitive in tsl_lib.known_primitives:
      primitive_name = primitive.declaration.functor_name
      primitive_node = self.__get_node_by_args(TSLDependencyGraph.PrimitiveNode, primitive_name)
      for definition in primitive.definitions:
        implementation_str = definition.data["implementation"]
        extension = definition.target_extension
        for match in primitive_pattern.finditer(implementation_str):
          required_primitive_name = match.group("primitive").strip()
          if required_primitive_name != primitive_name:
            required_primitive_node = self.__get_node_by_args(TSLDependencyGraph.PrimitiveNode, required_primitive_name)
            if required_primitive_node is None:
              primitive_node.invalidate(f"{required_primitive_name} missing (Location: {definition.location_of_origin_str}).")
              self.__well_defined = False
              continue
            self.__dependency_graph.add_edge(required_primitive_node, primitive_node, label="requirement of")
            if level_of_detail.value >= TSLInspectionLevelOfDetail.PRIMITIVE_INSTANTIATION.value:              
              # Check, if a specific tsl extension was specified
              if "simd_type" in match.groupdict():
                if "ctype" in match.group_dict() and "extension" in match.group_dict():
                  required_instantiation_node = self.__get_node_by_args(TSLDependencyGraph.PrimitiveImplementationNode, required_primitive_name, match.group("extension").strip(), match.group("ctype").strip())
                  for ctype in definition.ctypes:
                    primitive_instantiation_node = self.__get_node_by_args(TSLDependencyGraph.PrimitiveImplementationNode, primitive_name, extension, ctype)
                    if required_instantiation_node is None:
                      primitive_instantiation_node.invalidate(f"{required_instantiation_node} missing (Location: {definition.location_of_origin_str}).")
                      self.__well_defined = False
                    else:
                      self.__dependency_graph.add_edge(required_instantiation_node, primitive_instantiation_node, label="concrete requirement of")
                else:
                  raise ValueError(f"Found simd_type but no ctype AND extension ({primitive_instantiation_node}. Location: {definition.location_of_origin_str})")
              else:
                # Generic one -> add all possible nodes
                for ctype in definition.ctypes:
                  primitive_instantiation_node = self.__get_node_by_args(TSLDependencyGraph.PrimitiveImplementationNode, primitive_name, extension, ctype)
                  required_instantiation_node = self.__get_node_by_args(TSLDependencyGraph.PrimitiveImplementationNode, required_primitive_name, extension, ctype)
                  if required_instantiation_node is None:
                    primitive_instantiation_node.invalidate(f"{required_instantiation_node} missing (Location: {definition.location_of_origin_str}).")
                    self.__well_defined = False
                  else:
                    self.__dependency_graph.add_edge(required_instantiation_node, primitive_instantiation_node, label="concrete requirement of")

  def __add_tests(self, tsl_lib: TSLLib) -> None:
    '''
    Iterates over all test cases of all primitives.
    Adds a PrimitiveTestNode per test to the dependency graph and connects the test-node with the corresponding primitive node with a named
    edge ("test of").
    If no tests are present, the primitive is marked as unsafe.
    '''
    for _, primitive in tsl_lib.known_primitives:
      primitive_name = primitive.declaration.functor_name
      primitive_node = self.__get_node_by_args(TSLDependencyGraph.PrimitiveNode, primitive_name)
      has_tests: bool = False
      for test_name, _, implicitly_reliable in primitive.get_tests(copy=False):
        has_tests = True
        test_node = self.__add_node(TSLDependencyGraph.PrimitiveTestNode, primitive_name, test_name, implicitly_reliable)
        self.__dependency_graph.add_edge(test_node, primitive_node, label="test of")
      if not has_tests:
        primitive_node.mark_unsafe("No tests specified.")

  def __add_primitive_tests_instantiations(self, tsl_lib: TSLLib) -> None:
    '''
    Iterates over all test cases of all primitives.
    For every test and for every specified target_extension and ctype of the primitive a PrimitiveTestImplementationNode
    is added to the dependency graph as well as a named edge ("concrete instantiation of") betwwen the implementation-node
    and the test-node.
    '''
    for _, primitive in tsl_lib.known_primitives:
      primitive_name = primitive.declaration.functor_name
      for test_name, _, implicitly_reliable, _ in primitive.get_tests(copy=False):
        test_node = self.__get_node_by_args(TSLDependencyGraph.PrimitiveTestNode, primitive_name, test_name, implicitly_reliable)
        for target_extension, ctype_list in primitive.specialization_dict().items():
          for ctype in ctype_list:
            primitive_test_instantiation_node = self.__add_node(TSLDependencyGraph.PrimitiveTestImplementationNode, primitive_name, test_name, target_extension, ctype)
            self.__dependency_graph.add_edge(primitive_test_instantiation_node, test_node, label="concrete instantiation of")

  def __add_primitive_tests_implementation_dependencies(self, tsl_lib: TSLLib, primitive_pattern: re.Pattern, level_of_detail: TSLInspectionLevelOfDetail) -> None:
    '''
    Default behaviour:
      Iterates over all test implementations of all primitives.
      For every test implementation, it is checked whether other tsl-primitives are used (=requirement).
      If a requirement is found, an named edge ("requirement of") is added to the graph, connecting the 
      required primitive node with the dependent test.
      Error Handling: SILENT
        If a required primitive does not exist in the graph, the dependent PrimitiveTestNode is marked as invalid.

    level_of_details >= TEST_INSTANTIATION:
      For all specified target_extensions and ctypes of the primitive a named edge ("concrete requirement of")
      is added, connecting the dependent PrimitiveTestImplementationNode with the required PrimitiveImplementationNode.

      Error Handling: SILENT
        If a required PrimitiveImplementationNode is not present in the graph, the dependent
        PrimitiveTestImplementationNode is marked as invalid.
      Error Handling: EXCEPTION
        If a required tsl-primitive was found in the implementation but a ctype or extension could not be
        parsed, a ValueError is raised.
    '''
    for _, primitive in tsl_lib.known_primitives:
      primitive_name = primitive.declaration.functor_name
      for test_name, test_implementation, implicitly_reliable, location_or_origin_str in primitive.get_tests(copy=False):
        test_node = self.__get_node_by_args(TSLDependencyGraph.PrimitiveTestNode, primitive_name, test_name, implicitly_reliable)          
        for match in primitive_pattern.finditer(test_implementation):
          required_primitive_name = match.group("primitive").strip()
          if required_primitive_name != primitive_name:
            required_primitive_node = self.__get_node_by_args(TSLDependencyGraph.PrimitiveNode, required_primitive_name)
            if required_primitive_node is None:
              test_node.invalidate(f"{required_primitive_node} missing (Location: {location_or_origin_str}).")
              self.__well_defined = False
              continue
            self.__dependency_graph.add_edge(required_primitive_node, test_node, label="requirement of")
            if level_of_detail.value >= TSLInspectionLevelOfDetail.TEST_INSTANTIATION.value:
              # Check, if a specific tsl extension was specified
              if "simd_type" in match.groupdict():
                if "ctype" in match.group_dict() and "extension" in match.group_dict():
                  required_instantiation_node = self.__get_node_by_args(TSLDependencyGraph.PrimitiveImplementationNode, required_primitive_name, match.group("extension").strip(), match.group("ctype").strip())
                  for target_extension, ctype_list in primitive.specialization_dict().items():
                    for ctype in ctype_list:
                      primitive_test_instantiation_node = self.__get_node_by_args(TSLDependencyGraph.PrimitiveTestImplementationNode, primitive_name, test_name, target_extension, ctype)
                      if required_instantiation_node is None:
                        primitive_test_instantiation_node.invalidate(f"{required_instantiation_node} missing (Location: {location_or_origin_str}).")
                        self.__well_defined = False
                      else:
                        self.__dependency_graph.add_edge(required_instantiation_node, primitive_test_instantiation_node, label="concrete requirement of")
                else:
                  raise ValueError("Found simd_type but no ctype AND extension")
              else:
                # Generic one -> add all possible nodes
                for target_extension, ctype_list in primitive.specialization_dict().items():
                  for ctype in ctype_list:
                    required_instantiation_node = self.__get_node_by_args(TSLDependencyGraph.PrimitiveImplementationNode, required_primitive_name, match.group("extension").strip(), match.group("ctype").strip())
                    primitive_test_instantiation_node = self.__get_node_by_args(TSLDependencyGraph.PrimitiveTestImplementationNode, primitive_name, test_name, target_extension, ctype)
                    if required_instantiation_node is None:
                      primitive_test_instantiation_node.invalidate(f"{required_instantiation_node} missing (Location: {location_or_origin_str}).")
                      self.__well_defined = False
                    else:
                      self.__dependency_graph.add_edge(required_instantiation_node, primitive_test_instantiation_node, label="concrete requirement of")

  def __check_validity(self, level_of_detail: TSLInspectionLevelOfDetail) -> None:
    '''
    @todo: This function is heavily unoptimized and redundant and therefore hard to read. It should be refactored.

    Checks the validity of all relevant (those that have dependencies) nodes in the dependency graph.
    A Node is valid, if all its dependencies are valid. Within in the context of TSL, this means that
    all required TSL-primitives for every definition of a primitive are present.

    The validity check performs validity checks based on the level_of_detail.
    
    Default behaviour:
      Iterates over all PrimitiveNodes (and PrimitiveImplementationNodes) that are root nodes (no incoming edges).
      Starting from such a node, the dependency chain is traversed (breadth first) and the validity of all PrimitiveNodes are updated.
      If a PrimitiveNode within the chain is invalid, all following PrimitiveNodes are marked as invalid as well.

      Error Handling: EXCEPTION
        If a cycle of dependencies is detected while traversing the dependency chain, a ValueError is raised.

    level_of_details >= PRIMITIVE_INSTANTIATION:
      Before the default behaviour is executed, the validity of all PrimitiveImplementationNodes is updated.
      Iterates over all PrimitiveImplementationNodes that are root nodes (no incoming edges).
      Starting from such a node, the dependency chain is traversed (breadth first) and the validity of all PrimitiveImplementationNodes are updated.
      If a PrimitiveImplementationNode within the chain is invalid, all following PrimitiveImplementationNodes are marked as invalid as well.
      Finally, all PrimitiveNodes are updated based on the validity of their associated PrimitiveImplementationNodes. If all associated
      PrimitiveImplementationNodes are invalid, the PrimitiveNode is marked as invalid as well.

      Error Handling: EXCEPTION
        If a cycle of dependencies is detected while traversing the dependency chain, a ValueError is raised.

    level_of_details >= TEST:
      Iterates over all PrimitiveTestNodes (and PrimitiveTestImplementationNodes) that are root nodes (no incoming edges).
      Starting from such a node, the dependency chain is traversed (breadth first) and the validity of all PrimitiveTestNodes are updated.
      If a PrimitiveTestNode within the chain is invalid, all following PrimitiveTestNodes are marked as invalid as well.

      Error Handling: EXCEPTION
        If a cycle of dependencies is detected while traversing the dependency chain, a ValueError is raised.

    level_of_details >= TEST_INSTANTIATION:
      Before the behaviour for >= TEST is executed, the validity of all PrimitiveTestImplementationNodes is updated.
      Iterates over all PrimitiveTestImplementationNodes that are root nodes (no incoming edges).
      Starting from such a node, the dependency chain is traversed (breadth first) and the validity of all PrimitiveTestImplementationNodes are updated.
      If a PrimitiveTestImplementationNode within the chain is invalid, all following PrimitiveTestImplementationNodes are marked as invalid as well.
      Finally, all PrimitiveTestNodes are updated based on the validity of their associated PrimitiveTestImplementationNodes. If all associated
      PrimitiveTestImplementationNodes are invalid, the PrimitiveTestNode is marked as invalid as well.

      Error Handling: EXCEPTION
        If a cycle of dependencies is detected while traversing the dependency chain, a ValueError is raised.
    '''
    if level_of_detail.value >= TSLInspectionLevelOfDetail.PRIMITIVE_INSTANTIATION.value:
      #If level of detail > PRIMITIVE_INSTANTIATION -> go through all PrimitiveImplementationNodes that are root nodes and update the validity of the whole dependency chain
      for primitive_instantiation_node in self.roots([TSLDependencyGraph.PrimitiveImplementationNode]):
        visited_nodes = [primitive_instantiation_node]
        chain_valid: bool = primitive_instantiation_node.valid
        if not chain_valid:
          invalidation_notes = [f"{primitive_instantiation_node} invalid"]
        else:
          invalidation_notes = []
        for current_node in self.traverse_by_type([primitive_instantiation_node], [TSLDependencyGraph.PrimitiveImplementationNode], reversed=False, self_contained=False):
          if current_node in visited_nodes:
            raise ValueError(f"Cycle detected: [{' -> '.join(visited_nodes)}]")
          visited_nodes.append(current_node)
          chain_valid = chain_valid and current_node.valid
          if not chain_valid:
            current_node.invalidate(" -> ".join(invalidation_notes))
            invalidation_notes.append(f"{current_node} invalid")
            self.__well_defined = False
      #If all PrimitiveImplementationNodes of a PrimitiveNode are invalid, the PrimitiveNode is invalid as well.
      for primitive_node in self.nodes_by_type([TSLDependencyGraph.PrimitiveNode]):
        if not any(primitive_implementation_node.valid for primitive_implementation_node, _ in self.edges_by_label("concrete instantiation of", "in", [primitive_node])):
          primitive_node.invalidate(f"All template instantiations are invalid.")
          self.__well_defined = False
    #Go through all PrimitiveNodes that are root nodes and update the validity of the whole dependency chain
    #if level of detail < PRIMITIVE_INSTANTIATION, there will be no PrimitiveImplementationNodes as root nodes, however we can "filter" for them anyways.
    for primitive_node in self.roots([TSLDependencyGraph.PrimitiveNode, TSLDependencyGraph.PrimitiveImplementationNode]):
      if isinstance(primitive_node, TSLDependencyGraph.PrimitiveNode):
        visited_nodes = [primitive_node]
        chain_valid: bool = primitive_node.valid
        if not chain_valid:
          invalidation_notes = [f"{primitive_node} invalid"]
      else:
        visited_nodes = []
        chain_valid: bool = True
        invalidation_notes = []
      for current_node in self.traverse_by_type([primitive_node], [TSLDependencyGraph.PrimitiveNode], reversed=False, self_contained=False):
        if current_node in visited_nodes:
          raise ValueError(f"Cycle detected: [{' -> '.join(visited_nodes)}]")
        visited_nodes.append(current_node)
        chain_valid = chain_valid and current_node.valid
        if not chain_valid:
          current_node.invalidate(" -> ".join(invalidation_notes))
          invalidation_notes.append(f"{current_node} invalid")
          self.__well_defined = False
    if level_of_detail.value >= TSLInspectionLevelOfDetail.TEST.value:
      if level_of_detail.value >= TSLInspectionLevelOfDetail.TEST_INSTANTIATION.value:
        for primitive_test_instantation_node in self.roots([TSLDependencyGraph.PrimitiveTestImplementationNode]):
          visited_nodes = [primitive_test_instantation_node]
          chain_valid: bool = primitive_test_instantation_node.valid
          if not chain_valid:
            invalidation_notes = [f"{primitive_test_instantation_node} invalid"]
          else:
            invalidation_notes = []
          for current_node in self.traverse_by_type([primitive_test_instantation_node], [TSLDependencyGraph.PrimitiveTestImplementationNode], reversed=False, self_contained=False):
            if current_node in visited_nodes:
              raise ValueError(f"Cycle detected: [{' -> '.join(visited_nodes)}]")
            visited_nodes.append(current_node)
            chain_valid = chain_valid and current_node.valid
            if not chain_valid:
              current_node.invalidate(" -> ".join(invalidation_notes))
              invalidation_notes.append(f"{current_node} invalid")
              self.__well_defined = False
        for primitive_test_node in self.nodes_by_type([TSLDependencyGraph.PrimitiveTestNode]):
          #If all PrimitiveTestImplementationNodes of a PrimitiveTestNode are invalid, the PrimitiveTestNode is invalid as well.
          if not any(primitive_test_implementation_node.valid for primitive_test_implementation_node, _ in self.edges_by_label("concrete instantiation of", "in", [primitive_test_node])):
            primitive_test_node.invalidate("All template instantiations are invalid.")
      for primitive_test_node in self.roots([TSLDependencyGraph.PrimitiveTestNode, TSLDependencyGraph.PrimitiveTestImplementationNode]):
        if isinstance(primitive_test_node, TSLDependencyGraph.PrimitiveTestNode):
          visited_nodes = [primitive_test_node]
          chain_valid: bool = primitive_test_node.valid
        else:
          visited_nodes = []
          chain_valid: bool = True
        for current_node in self.traverse_by_type([primitive_test_node], [TSLDependencyGraph.PrimitiveTestNode], reversed=False, self_contained=False):
          if current_node in visited_nodes:
            raise ValueError(f"Cycle detected: [{' -> '.join(visited_nodes)}]")
          visited_nodes.append(current_node)
          chain_valid = chain_valid and current_node.valid
          if not chain_valid:
            current_node.invalidate(" -> ".join(invalidation_notes))
            invalidation_notes.append(f"{current_node} invalid")
            self.__well_defined = False


  def __check_safety(self, level_of_detail: TSLInspectionLevelOfDetail) -> None:
    '''
    Checks the test coverage of all primitives.

    Default behaviour:
      First, iterates over all PrimitiveNodes. If a PrimitiveNode has no associated TestCases it was marked as unsafe (through self.__ad_tests).
      Since this function is executed __after__ self.__check_validity, it may be possible, that all TestCases of a Primitive were marked invalid.
      In this case, the PrimitiveNode is marked unsafe as well. (This is just part of the hollistic reasoning. In fact, if a single PrimitiveNode
      is marked as invalid, the TSL will not be generated anyways. However, this behaviour may help debugging.)

    level_of_detail >= TEST_INSTANTIATION:
      Before the default behaviour is executed, the safeness of all PrimitiveTestImplementationNodes is updated.
      Iterates over all PrimitiveTestImplementationNodes that are root nodes (no incoming edges).
      Starting from such a node, the dependency chain is traversed (breadth first) and the safety of all PrimitiveTestImplementationNodes are updated.
      If a PrimitiveTestImplementationNode within the chain is unsafe, all following PrimitiveTestImplementationNodes are marked as unsafe as well.
      Finally, all PrimitiveTestNodes are updated based on the safety of their associated PrimitiveTestImplementationNodes. If __any__ associated
      PrimitiveTestImplementationNodes are unsafe, the PrimitiveTestNode is marked as unsafe as well.

    '''    
    if level_of_detail.value >= TSLInspectionLevelOfDetail.TEST_INSTANTIATION:
      for primitive_test_instantation_node in self.roots([TSLDependencyGraph.PrimitiveTestImplementationNode]):
        visited_nodes = [primitive_test_instantation_node]
        chain_safe: bool = primitive_test_instantation_node.safe
        if not chain_safe:
          invalidation_notes = [f"{primitive_test_instantation_node} unsafe"]
        else:
          invalidation_notes = []
        for current_node in self.traverse_by_type([primitive_test_instantation_node], [TSLDependencyGraph.PrimitiveTestImplementationNode], reversed=False, self_contained=False):
          if current_node in visited_nodes:
            raise ValueError(f"Cycle detected: [{' -> '.join(visited_nodes)}]")
          visited_nodes.append(current_node)
          chain_safe = chain_safe and current_node.safe
          if not chain_safe:
            current_node.mark_unsafe(" -> ".join(invalidation_notes))
            invalidation_notes.append(f"{current_node} unsafe")
            self.__has_warnings = True
      for primitive_test_node in self.nodes_by_type([TSLDependencyGraph.PrimitiveTestNode]):
        if not all(primitive_test_implementation_node.safe for primitive_test_implementation_node, _ in self.edges_by_label("concrete instantiation of", "in", [primitive_test_node])):
          primitive_test_node.mark_unsafe("All template instantiations are unsafe.")
          self.__has_warnings = True
    for primitive_node in self.nodes_by_type([TSLDependencyGraph.PrimitiveNode]):
      if not any(primitive_test_node.safe for primitive_test_node, _ in self.edges_by_label("test of", "in", [primitive_node])):
        primitive_node.mark_unsafe("All specified tests are invalid.")
        self.__has_warnings = True

  def __add_implicit_class_dependencies(self) -> None:
    '''
    Adds implicit class dependencies.
    If a primitive P1 (associated with class C1) depends on another primitive P2 (associated with class C2),
    the dependency between C1 and C2 is added to the graph.
    '''
    for primitive_node in self.nodes_by_type([TSLDependencyGraph.PrimitiveNode]):
      for _, class_node in self.edges_by_label("part of", "out", [primitive_node]):
        if not isinstance(class_node, TSLDependencyGraph.PrimitiveClassNode):
          raise ValueError(f"Expected PrimitiveClassNode but found {class_node}")
        for required_primitive_node, _ in self.edges_by_label("requirement of", "in", [primitive_node]):
          if not isinstance(required_primitive_node, TSLDependencyGraph.PrimitiveNode):
            raise ValueError(f"Expected PrimitiveNode but found {required_primitive_node}")
          for _, required_class_node in self.edges_by_label("part of", "out", [required_primitive_node]):
            if not isinstance(required_class_node, TSLDependencyGraph.PrimitiveClassNode):
              raise ValueError(f"Expected PrimitiveClassNode but found {required_class_node}")
            self.__dependency_graph.add_edge(required_class_node, class_node, label="implicit requirement of")

  @LogInit()
  def __init__(self, tsl_lib: TSLLib, level_of_detail: TSLInspectionLevelOfDetail = TSLInspectionLevelOfDetail.TEST_INSTANTIATION) -> None:
    self.__dependency_graph: nx.DiGraph = nx.DiGraph()
    self.__level_of_detail = level_of_detail
    self.__known_nodes: Dict[str, TSLDependencyGraph.NodeType] = {}
    self.__well_defined: bool = True
    self.__has_warnings: bool = False

    ### Step 1: Add all primitive-classes to the dependency graph
    self.__add_primitive_classes(tsl_lib)
    ### Step 2: Add all primitives to the dependency graph and connect the primitives with their associated primitive-classes
    self.__add_primitives(tsl_lib)
    ### Step 3: Create Regex for parsing implementations
    # regex str for all known primitives, e.g., (?P<primitive>add|sub|mul|div)
    known_primitives_regex = rf'(?P<primitive>{"|".join(tsl_lib.distinct_primitive_names())})'
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
    primitive_pattern = re.compile(tsl_primitive_regex)

    # Step 4: Add all possible primitive instantiations to the dependency graph and connect them with their associated primitive
    if level_of_detail.value >= TSLInspectionLevelOfDetail.PRIMITIVE_INSTANTIATION.value:
      self.__add_primitive_instantiations(tsl_lib)

    # Step 5: Inspect Primitive implementations for dependencies
    self.__add_primitive_implementation_dependencies(tsl_lib, primitive_pattern, level_of_detail)      

    if level_of_detail.value >= TSLInspectionLevelOfDetail.TEST.value:
      # Step 6 (may be omitted): If level of detail is greater or equal TEST, add tests to the dependency graph and connect them with their associated primitive
      self.__add_tests(tsl_lib)
      if level_of_detail.value >= TSLInspectionLevelOfDetail.TEST_INSTANTIATION.value:
        # Step 7 (may be ommitted): If level of detail is greater or equal TEST_INSTANTIATION, add all possible test instantiations to the dependency graph and connect them with their associated test
        self.__add_primitive_tests_instantiations(tsl_lib)
      # Step 8 (may be ommitted): Inspect test implementations for dependencies
      self.__add_primitive_tests_implementation_dependencies(tsl_lib, primitive_pattern, level_of_detail)
    
    # Step 9: Execute a validity check for the dependency graph and return
    self.__check_validity(level_of_detail)

    if level_of_detail.value >= TSLInspectionLevelOfDetail.TEST.value:
      # Step 10 (may be ommitted):
      self.__check_safety(level_of_detail)

    # Step 11: Add implicit class dependencies (derived from the primitive dependencies)
    self.__add_implicit_class_dependencies()

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

