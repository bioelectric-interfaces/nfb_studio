class ExampleClass:
    class Nested:
        def __init__(self):
            self.int_var = -5
            self.float_var = 0.69
            self.string_var = "string"
            self.list_var = [1, 2, 3]
            self.tuple_var = (1, 2, 3)
            self.dict_var = {1: 1, 2: 2, 3: 3}
            self.set_var = {1, 2, 3, 3}
            self.bool_var1 = True
            self.bool_var2 = False
            self.none_var = None

        def serialize(self):
            return {
                "int_var": self.int_var,
                "float_var": self.float_var,
                "string_var": self.string_var,
                "list_var": self.list_var,
                "tuple_var": self.tuple_var,
                "dict_var": self.dict_var,
                "set_var": self.set_var,
                "bool_var1": self.bool_var1,
                "bool_var2": self.bool_var2,
                "none_var": self.none_var
            }

        @classmethod
        def deserialize(cls, data):
            obj = cls()
            obj.int_var = data["int_var"]
            obj.float_var = data["float_var"]
            obj.string_var = data["string_var"]
            obj.list_var = data["list_var"]
            obj.tuple_var = tuple(data["tuple_var"])
            obj.dict_var = data["dict_var"]
            obj.set_var = set(data["set_var"])
            obj.bool_var1 = data["bool_var1"]
            obj.bool_var2 = data["bool_var2"]
            obj.none_var = data["none_var"]

            return obj
        
        def __eq__(self, other):
            return (
                self.int_var == other.int_var
                and self.float_var == other.float_var
                and self.string_var == other.string_var
                and self.list_var == other.list_var
                and self.tuple_var == other.tuple_var
                and self.dict_var == other.dict_var
                and self.set_var == other.set_var
                and self.bool_var1 == other.bool_var1
                and self.bool_var2 == other.bool_var2
                and self.none_var == other.none_var
            )


    def __init__(self):
        self.nested = self.Nested()
        self.dict_var = {"nested": self.nested}
        self.list_var = [None, self.nested]

    def serialize(self):
        return {
            "nested": self.nested,
            "dict_var": self.dict_var,
            "list_var": self.list_var,
        }
    
    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.nested = data["nested"]
        obj.dict_var = data["dict_var"]
        obj.list_var = data["list_var"]

        return obj

    def __eq__(self, other):
        return (
            self.nested == other.nested
            and self.dict_var == other.dict_var
            and self.list_var == other.list_var
        )
