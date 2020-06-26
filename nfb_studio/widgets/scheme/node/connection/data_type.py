class DataType:
    def __init__(self, data_id=None, *, convertible_from=(), convertible_to=()):
        """Constructs a DataType from two parameters.
        
        The parameters are:  
        - data_id - the ID of the data type. Types compare equal when their IDs are the same;
        - convertible_from - an iterable of DataType instances or ids that this type can be converted from;
        - convertible_to - an iterable of DataType instances or ids that this type can be converted to;
        """
        self.data_id = data_id or 0
        """Data type's data id.  
        Data id is the defining attribute of a data type. Data types with the same id compare equal.
        """

        self.convertible_from = convertible_from
        self.convertible_to = convertible_to

    def serialize(self) -> dict:
        return {
            "data_id": self.data_id,
            "convertible_from": self.convertible_from,
            "convertible_to": self.convertible_to,
        }

    def deserialize(self, data: dict):
        self.data_id = data["data_id"]
        self.convertible_from = data["convertible_from"]
        self.convertible_to = data["convertible_to"]

    def __repr__(self):
        return "DataType({})".format(self.data_id)

    def __eq__(self, other):
        return self.data_id == other.data_id

    @property
    def convertible_from(self):
        return self._convertible_from
    
    @convertible_from.setter
    def convertible_from(self, val):
        self._convertible_from = []

        # If the item is a datatype object, take its id. Otherwise assume the id is already the item
        for item in val:
            if isinstance(item, type(self)):
                self._convertible_from.append(item.data_id)
            else:
                self._convertible_from.append(item)

    @property
    def convertible_to(self):
        return self._convertible_to
    
    @convertible_to.setter
    def convertible_to(self, val):
        self._convertible_to = []

        # If the item is a datatype object, take its id. Otherwise assume the id is already the item
        for item in val:
            if isinstance(item, type(self)):
                self._convertible_to.append(item.data_id)
            else:
                self._convertible_to.append(item)

DataType.Invalid = DataType()
"""Data type that results from default-constructing a DataType object."""

DataType.Unknown = DataType(1)
"""Data type that is assigned to default-constructed node connections."""


def convertible(datatype_from: DataType, datatype_to: DataType):
    """Return True if an edge can be created between an output with type datatype_from and input datatype_to."""
    return (
        datatype_from == datatype_to
        or datatype_from.data_id in datatype_to.convertible_from
        or datatype_to.data_id in datatype_from.convertible_to
    )
