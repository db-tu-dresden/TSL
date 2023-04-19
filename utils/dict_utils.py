import copy


def dict_update(left: dict, right: dict) -> dict:
    result = dict()
    for left_key, left_value in left.items():
        if left_key not in right:
            result[left_key] = left_value
        else:
            if type(left_value) != type(right[left_key]):
                result[left_key] = right[left_key]
            else:
                if isinstance(left_value, dict):
                    result[left_key] = dict_update(left_value, right[left_key])
                else:
                    result[left_key] = right[left_key]
    for right_key, right_value in right.items():
        if right_key not in result:
            result[right_key] = right_value
    return result

def intersects(left: set, right: set) -> bool:
    """
    relaxed intersection check (empty set intersects with every set)
    """
    if len(left) == 0 or len(right) == 0:
        return True
    return not left.isdisjoint(right)

def remove_from_list(alist: list, to_remove: list, in_place = True):
    if in_place:
        l = alist
    else:
        l = copy.deepcopy(alist)
    for e in to_remove:
        while e in alist:
            alist.remove(e)
    return l

def keep_in_list(alist: list, to_keep: list, in_place = True):
    if in_place:
        l = alist
    else:
        l = copy.deepcopy(alist)
    idx_l = [idx for idx in range(len(l)) if l[idx] not in to_keep]
    idx_l.sort(reverse=True)
    for idx in idx_l:
        l.pop(idx)

    return l
def remove_from_set(aset: set, to_remove: list, in_place = True):
    if in_place:
        s = aset
    else:
        s = copy.deepcopy(aset)
    for e in to_remove:
        if e in s:
            s.remove(e)
    return s

def keep_in_set(aset: set, to_keep: list, in_place = True):
    if in_place:
        s = aset
    else:
        s = copy.deepcopy(aset)
    for e in s:
        if e not in to_keep:
            s.remove(e)
    return s
def deep_remove_from_dict(adict: dict, to_remove: list, in_place = True):
    if in_place:
        d = adict
    else:
        d = copy.deepcopy(adict)
    for element in to_remove:
        if element in d:
            del d[element]

    for k,v in d.items():
        if isinstance(v, list):
            remove_from_list(d[k], to_remove, True)
        elif isinstance(v, set):
            remove_from_set(d[k], to_remove, True)
        elif isinstance(v, dict):
            deep_remove_from_dict(d[k], to_remove, True)
    return d

def deep_update_dict(adict: dict, to_keep: list, in_place = True):
    if len(adict) == 0:
        return adict
    if in_place:
        d = adict
    else:
        d = copy.deepcopy(adict)

    to_del = [k for k in d if k not in to_keep]
    for td in to_del:
        del d[td]

    for k,v in d.items():
        if isinstance(v, list):
            keep_in_list(d[k], to_keep, True)
        elif isinstance(v, set):
            keep_in_set(d[k], to_keep, True)
        elif isinstance(v, dict):
            deep_update_dict(d[k], to_keep, True)

    to_del = [k for k in d if len(d[k]) == 0]
    for td in to_del:
        del d[td]
    return d
