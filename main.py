import logging

from core.tvl_config import config

from pathlib import Path

from core.tvl_generator import TVLGenerator
from utils.file_utils import strip_common_path_prefix
from utils.log_utils import log, LogInit
from utils.yaml_utils import yaml_load, yaml_load_all


def tvl_setup(config_path: Path, additional_config=None) -> None:
    if additional_config is None:
        additional_config = dict()
    config_file_cfg = yaml_load(config_path)
    # overwrite / extend config file entries with additional config dict entries
    config.setup({**config_file_cfg, **additional_config})



class TVLExtension:
    def __init__(self, data_dict: dict) -> None:
        self.data = data_dict
    def __eq__(self, other):
        if isinstance(other, TVLExtension):
            return self.data["test"] == other.data["test"]
        return False
    def __ne__(self, other):
        return not self == other
    def __hash__(self):
        return hash(self.data["test"])
    @staticmethod
    def create_from_dict(data_dict: dict):
        return TVLExtension(data_dict)
    def __str__(self):
        return str(self.data)
    def __repr__(self):
        return str(self)


import random
from typing import List
import networkx as nx
import matplotlib.pyplot as plt

def qsort(xs: list, fst, lst):
    if fst >= lst:
        return
    i, j = fst, lst
    pivot = xs[random.randint(fst, lst)]
    while i <= j:
        while xs[i] < pivot:
            i += 1
        while xs[j] > pivot:
            j -= 1
        if i <= j:
            xs[i], xs[j] = xs[j], xs[i]
            i, j = i + 1, j - 1
    qsort(xs, fst, j)
    qsort(xs, i, lst)



class TestCase:
    def __init__(self, primitive_name: str, test_case_name: str, class_name: str, depends_on: List[str] = []):
        self.class_name = class_name
        self.primitive_name = primitive_name
        self.test_name = test_case_name
        self.depends_on = depends_on

    def __str__(self):
        return f"{self.class_name}::{self.primitive_name}"

    def __repr__(self):
        return str(self)

    def __check_type(self, other):
        if not isinstance(other, TestCase):
            raise ValueError

    def __eq__(self, other):
        self.__check_type(other)
        return (self.primitive_name == other.primitive_name) and (self.test_name == other.test_name) and (
                    self.class_name == other.class_name) and (self.depends_on == other.depends_on)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((self.primitive_name, self.test_name))


class TestCaseGraph:
    def __init__(self) -> None:
        self.graph: nx.DiGraph = nx.DiGraph()
        self.tmp = []

    def add_test_case(self, test_case: TestCase) -> None:
        # if test_case was added to the graph through a prior dependency, we "fill" it with the data now
        # self.graph.add_node(test_case)
        self.tmp.append(test_case)

    def finalize(self) -> None:
        self.tmp.sort(key=lambda x: (x.class_name, x.primitive_name))
        for n in self.tmp:
            self.graph.add_node(n)
        # iterate over all nodes
        for node in self.graph.nodes:
            # iterate over all dependencies of every node
            for dependency in node.depends_on:
                #e.g., add
                #get all test-cases of the very primitive (default and corner cases)
                for dep in [dep for dep in self.graph.nodes if dep.primitive_name == dependency]:
                    # add edge for dependency resolution
                    self.graph.add_edge(dep, node)





# if __name__ == '__main__':

    # graph = TestCaseGraph()
    # graph.add_test_case(TestCase("add", "", "calc", ["load", "set1", "hadd"]))
    # graph.add_test_case(TestCase("loadu", "", "ls" ))
    # graph.add_test_case(TestCase("load", "", "ls"))
    # graph.add_test_case(TestCase("set1", "", "ls"))
    # graph.add_test_case(TestCase("hadd", "", "calc", ["set1"]))
    # graph.add_test_case(TestCase("gather", "", "ls"))
    # graph.add_test_case(TestCase("set", "", "ls"))
    #
    # graph.finalize()
    # g = graph.graph
    # pos = nx.planar_layout(g)
    # nx.draw(g,with_labels=True, pos=pos)
    # plt.savefig("graph.png")
    # topo_order = nx.topological_sort(g)
    # for x in topo_order:
    #     print(x)
#
#
#

if __name__ == '__main__':
    tvl_setup(Path("config/default_conf.yaml"))
    gen = TVLGenerator()
    gen.generate(["sse", "sse2", "sse3", "ssse3", "sse4_1", "sse4_2", "avx", "avx2"])