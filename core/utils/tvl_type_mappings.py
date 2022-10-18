import os
from typing import List, Generator, Tuple, Dict

from tools.tvlgen.core.utils.tvl_misc import get_random_value_str


def map_types_cartesian(alist: List[str], blist: List[str]) -> Generator[Tuple[str, str], None, None]:
   for a in alist:
      for b in blist:
         yield (a,b)


def map_types_one2m(alist: List[str], blist: List[str]) -> Generator[Tuple[str, str], None, None]:
   if len(alist) > 1:
      raise ValueError("map_types_one2m: First parameter must have length of 1.")
   for b in blist:
      yield (alist[0], b)


def map_types_m2one(alist: List[str], blist: List[str]) -> Generator[Tuple[str, str], None, None]:
   if len(blist) > 1:
      raise ValueError("map_types_m2one: Second parameter must have length of 1.")
   for a in alist:
      yield (a, blist[0])


def map_types_one2one(alist: List[str], blist: List[str]) -> Generator[Tuple[str, str], None, None]:
   if len(alist) != len(blist):
      raise ValueError("map_types_one2one: Both parameters must have same length.")
   for i in range(len(alist)):
      yield (alist[i], blist[i])


def map_types_from_dict(alist: List[str], bdict: Dict[str, List[str]]) -> Generator[Tuple[str, str], None, None]:
   for i in alist:
      if i not in bdict:
         raise ValueError("map_types_from_dict: value from left parameter not in right one.")
      for j in bdict[i]:
         yield (i, j)
