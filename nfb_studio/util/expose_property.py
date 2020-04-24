def expose_property(cls, attr_container, attr_to_expose):
    def fget(self):
        return getattr(getattr(self, attr_container), attr_to_expose)
    
    def fset(self, value, /):
        setattr(getattr(self, attr_container), attr_to_expose, value)

    prop = property(fget=fget, fset=fset)
    setattr(cls, attr_to_expose, prop)
