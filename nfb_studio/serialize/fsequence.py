def _fsequence_iter(iterator):
    """Create and return a single callable that calls arguments in sequence and passes the result to the next callable.
    Calls are performed in order in which they were specified.

    Parameters
    ----------
    callables : iterator
        An iterator to a sequence of callables.
    """
    func = next(iterator)

    try:
        next_func = _fsequence_iter(iterator)
        return lambda *args, **kwargs: next_func(func(*args, **kwargs))
    except StopIteration:
        return func


def fsequence(callables):
    """Create and return a single callable that calls arguments in sequence and passes the result to the next callable.
    Calls are performed in order in which they were specified.

    Parameters
    ----------
    callables : iterable
        A sequence of callables. No checks are performed whether a callable can accepts previous one's output.
    """
    try:
        return _fsequence_iter(iter(callables))
    except StopIteration:
        raise ValueError("no callables to create a sequence from")

