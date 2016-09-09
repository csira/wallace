import functools

from wallace.errors import WallaceError


# def should_throw(wallace_err, code):
#     def wrapper(f):
#         @functools.wraps(f)
#         def wraps(*a, **kw):
#             try:
#                 f(*a, **kw)

#             except wallace_err as e:
#                 if e.code != code:
#                     _throw(wallace_err, code, e)
#                 else:
#                     return

#             except Exception as e:
#                 _throw(wallace_err, code, e)

#             raise ValueError('did not raise exception')
#         return wraps
#     return wrapper


def should_throw(error_class, code=None):
    def wrapper(f):
        @functools.wraps(f)
        def wraps(*a, **kw):
            # print error_class, code
            try:
                f(*a, **kw)

            except error_class as err:
                if hasattr(err, 'code') and err.code != code:
                    raise

                return

            # except Exception as err:
            #     raise

            raise ValueError('did not raise exception')
        return wraps
    return wrapper


# def _throw(expected_error, expected_code, actual_error):
#     str1 = _get_error_info(expected_error, expected_code)
#     str2 = _get_error_info(actual_error)
#     msg = 'should throw {}, threw {} instead'.format(str1, str2)
#     raise ValueError(msg)


# def _get_error_info(err, expected_code=None):
#     '''Get error code and class name.'''

#     if isinstance(err, WallaceError):
#         name, code = err.__class__.__name__, err.code
#     elif issubclass(err, WallaceError):
#         name, code = err.__name__, err.code
#     elif isinstance(err, Exception):
#         name, code = err.__class__.__name__, None
#     else:
#         name, code = err.__name__, None

#     if expected_code:
#         code = expected_code

#     if code:
#         return '{} ({})'.format(name, code)
#     else:
#         return name
