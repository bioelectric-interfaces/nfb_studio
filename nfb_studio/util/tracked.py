class TrackedMixin:
    """Adds functionality for tracking changes to instance attributes.  
    By inheriting this class, all attributes defined after this class' `__init__` will be "tracked". When an attribute
    is set or replaced (e.g. when `__setattr__` is called) `self.notify` will be called with a single argument:
    attribute name (str). By default, `self.notify` is a noop.  
    Attributes can be manually untracked by calling `self.untrack(attr)` and tracked again using `self.track(attr)`.

    Example
    -------
    ```python
    class Test(TrackedMixin):
        def __init__(self):
            super().__init__()  # TrackedMixin is initialized, after this point every attribute is tracked by default
            
            self.a = 0
            self.b = 0
            self.c = 0
            
            self.untrack("a")
            
            self.notify = lambda attr: print(attr + ": " + str(getattr(self, attr)))
    
    t = Test()
    t.a += 1         # nothing printed
    t.b += 1         # printed "b: 1"
    t.c = 42         # printed "c: 15"
    t.new_attr = 42  # printed "new_attr: 42"

    t.track("a")
    t.a = 42         # printed "a: 42"
    ```

    Note that mutable members such as lists can change their contents without calling `__setattr__`, and because of this
    `notify` function will not be called when you, for example, change an element of a list:
    ```python
    t.my_list[10] = 1  # nothing printed
    ```
    `notify` function only gets called when the member itself is replaced.
    ```python
    t.my_list = [1, 2, 3]  # printed "my_list: [1, 2, 3]"
    ```
    """
    def __init__(self, *args, **kwargs):
        super().__setattr__("tracked_attrs", {})
        super().__setattr__("notify", lambda attr: None)

        super().__init__(*args, **kwargs)

    def __setattr__(self, key, value):
        # If a new attribute is added, track it automatically
        if not hasattr(self, key) and key not in self.tracked_attrs:
            self.tracked_attrs[key] = True
        
        super().__setattr__(key, value)

        # If an attribute is changed, call notify()
        if self.tracked_attrs.get(key, False):
            self.notify(key)
    
    def track(self, attr):
        self.tracked_attrs[attr] = True
    
    def untrack(self, attr):
        self.tracked_attrs[attr] = False


def tracked(cls):
    """Decorator that adds `TrackedMixin` to the end of class' bases."""
    cls.__bases__ = (TrackedMixin,) + cls.__bases__
    return cls
