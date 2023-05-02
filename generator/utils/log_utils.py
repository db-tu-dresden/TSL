import functools
import inspect
import logging
import types
from typing import Union

class TSLLogAdapter(logging.LoggerAdapter):
    def __init__(self, logger):
        super().__init__(logger, {})

    def process(self, msg, kwargs):
        return '%s (%s)' % (msg, f"{kwargs['extra']['decorated_filename']}::{kwargs['extra']['decorated_funcName']}"), kwargs

def get_logging_instance_from_self(*args) -> Union[logging.Logger, None]:
    first_args = next(iter(args), None)  # capture first arg to check for `self`
    if first_args is None:
        return None
    if hasattr(first_args, "__dict__"):
        if "decorated_logger" in first_args.__dict__:
            return first_args.__dict__["decorated_logger"]
    elif hasattr(first_args, "decorated_logger"):
        return getattr(first_args, "decorated_logger")
    else:
        return None
    return None

def get_args_without_self(*args):
    iterator = iter(args)
    first_args = next(iterator, None)  # capture first arg to check for `self`
    if first_args is None:
        return ()
    if hasattr(first_args, "__dict__"):
        return tuple(iterator)
    return args

def get_logger(*args, **kwargs):
    logger_params = [  # does kwargs have any logger
                        x
                        for x in kwargs.values()
                        if isinstance(x, logging.Logger)
                    ] + [  # # does args have any logger
                        x
                        for x in args
                        if isinstance(x, logging.Logger)
                    ]
    if logger_params:
        return next(iter(logger_params))
    logger = get_logging_instance_from_self(*args)
    if logger is None:
        return TSLLogAdapter(logging.getLogger(f"{inspect.stack()[1].function}"))
        # raise Exception("No logger defined.")
    return logger

def abbrev_str(msg: str) -> str:
    # if len(msg) > 50:
    #     return f"{msg[:50]}[...]"
    return msg


def get_params_str_without_logger_and_self(*args, **kwargs) -> str:
    args_repr = [abbrev_str(repr(a)) for a in get_args_without_self(*args) if not isinstance(a, logging.Logger)]
    kwargs_repr = [f"{k}={abbrev_str(repr(v))}" for k, v in kwargs.items()]
    return ", ".join(args_repr + kwargs_repr)


def logmsg_decorator_fn(self, loglevel, msg: str) -> None:
    self.decorated_logger.log(
        loglevel,
        msg,
        extra={
            "decorated_filename": inspect.getfile(self.__class__),
            "decorated_funcName": inspect.stack()[1].function
        }
    )

class LogInit:
    def __call__(self,f):
        def wrap(init_self,*args,**kwargs):
            try:
                init_self.decorated_logger = TSLLogAdapter(logging.getLogger(f"{init_self.__class__.__name__}"))
                init_self.log = types.MethodType(logmsg_decorator_fn, init_self)
                signature = get_params_str_without_logger_and_self(*args, **kwargs)
                f(init_self,*args,**kwargs)
                init_self.decorated_logger.debug(
                    f"Created instance of {init_self.__class__.__name__}({signature})",
                    extra={
                        "decorated_filename":inspect.getfile(f),
                        "decorated_funcName": "__init__"
                    }
                )
            except Exception as e:
                TSLLogAdapter(logging.getLogger(f"{init_self.__class__.__name__}")).exception(
                    f"Exception during creation of {init_self.__class__.__name__}. exception: {str(e)}",
                    extra={
                        "decorated_filename": inspect.getfile(f),
                        "decorated_funcName": "__init__"
                    }
                )
                raise e
        return wrap


def log(_func=None, successLevel=logging.DEBUG):
    def decorator_log(func):
        @functools.wraps(func)
        def logging_wrapper(*args, **kwargs):
            logger = get_logger(*args, **kwargs)
            signature = get_params_str_without_logger_and_self(*args, **kwargs)
            logger.debug(
                f"Called {func.__name__}({signature}).",
                extra={
                    "decorated_filename":inspect.getfile(func),
                    "decorated_funcName": func.__name__
                }
            )
            try:

                result = func(*args, **kwargs)
                logger.log(
                    successLevel,
                    f"Returning {type(result)} ({abbrev_str(repr(result))}) from {func.__name__}.",
                    extra={
                        "decorated_filename":inspect.getfile(func),
                        "decorated_funcName": func.__name__
                    }
                )
                return result
            except Exception as e:
                # a = inspect.
                logger.exception(
                    f"Exception raised in {func.__name__}. exception: {str(e)}",
                    extra={
                        "decorated_filename":inspect.getfile(func),
                        "decorated_funcName": func.__name__
                    }
                )
                raise e
        return logging_wrapper

    if _func is None:
        return decorator_log
    else:
        return decorator_log(_func)
