"""Function for importing an enumeration into a class."""

def import_enum(target_class, enum, fmt: str = None):
    """Import an enumeration into a target class.
    
    For every enumeration member in the enum, this function sets it as an attribute of the target class. If `fmt` is not
    specified, the name of the arrtibute will be the same as name in the enumeration. `fmt` can be specified as a format
    string with two keyword parameters: `{name}` and `{cls}`. `{name}` will be replaced with the name of the enum member
    being imported, `{cls}` - with the name of the enum class.

    No existing attributes will be overwritten - instead, an exception will be raised.

    Example
    -------
    ```python
    from enum import Enum

    class Flag(Enum):
        Disabled = 0
        Enabled = 1
    
    class Device1:
        pass

    class Device2:
        pass

    import_enum(Device1, Flags)
    import_enum(Device2, Flags, fmt="{name}{cls}")

    print(Device1.Disabled)  # <Flag.Disabled: 0>
    print(Device1.Enabled)   # <Flag.Enabled: 1>

    print(Device2.DisabledFlag)  # <Flag.Disabled: 0>
    print(Device2.EnabledFlag)   # <Flag.Enabled: 1>
    ```

    Raises
    ------
    ValueError : If an attribute with the same name already exists in the target class.
    """
    fmt = fmt or "{name}"

    for key in enum.__members__:
        attr = fmt.format(name=key, cls=enum.__name__)

        if hasattr(target_class, attr):
            raise ValueError("overriding attribute " + attr + " of target class " + enum.__name__)

        setattr(target_class, attr, enum.__members__[key])
