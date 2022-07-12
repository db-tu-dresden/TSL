import functools
import inspect

global_requirements = dict()


def create_requirement(name: str, requirement) -> None:
    global_requirements[name] = requirement


def requirement(_func=None, **requirement_kwargs):
    def verify_requirement(arg, _requirement, arg_name):
        for con in str(_requirement).split(";"):
            if con in global_requirements:
                con = global_requirements[con]
            if callable(con):
                if not con(arg):
                    raise ValueError(f"Argument {arg_name} does not fulfills the requirement {con}.")
            else:
                isType = True
                try:
                    eval(f"{con}")
                except:
                    isType = False
                if isType:
                    if inspect.isclass(eval(f"{con}")):
                        if not eval(f"isinstance({arg}, {con})"):
                            raise ValueError(f"Argument {arg_name} does not fulfills the requirement {con}. "
                                             f"Must be of type: {con}, but is: of type {type(arg)}")
                else:
                    if not eval(f"{arg} {con}"):
                        raise ValueError(f"Argument {arg_name} does not fulfills the requirement {con}. "
                                         f"!({arg} {con})")
    def decorator_requirement(func):
        @functools.wraps(func)
        def requirement_wrapper(*args, **kwargs):
            positional_args = inspect.getfullargspec(func).args
            for argidx in range(len(positional_args)):
                if positional_args[argidx] in requirement_kwargs:
                    verify_requirement(args[argidx], requirement_kwargs[positional_args[argidx]], positional_args[argidx])
                    # print(f"{positional_args[argidx]}: {args[argidx]}")
            for kwarg in kwargs.keys():
                if kwarg in requirement_kwargs:
                    verify_requirement(kwargs[kwarg], requirement_kwargs[kwarg])
            return func(*args, **kwargs)
        return requirement_wrapper
    if _func is None:
        return decorator_requirement
    else:
        return decorator_requirement(_func)


create_requirement("NotNone", lambda arg: arg is not None)
create_requirement("NonEmptyString", lambda arg: arg is not None and isinstance(arg, str) and len(arg) > 0)
