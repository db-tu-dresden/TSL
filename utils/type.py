def is_iterable(obj: object) -> bool:
    try:
        tmp = iter(obj)
    except:
        return False
    return True

def is_evaluatable_type(type_str: str) -> bool:
    try:
        x = eval(type_str)
        return True
    except:
        return False