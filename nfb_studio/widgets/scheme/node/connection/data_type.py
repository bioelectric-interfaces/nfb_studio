class DataType:
    """A special tag class that represents the type of data travelling from an to a node.
    
    Connections that emit/accept data of different types cannot be connected.
    """
    def __init__(self, title=None, data_id=None):
        """Constructs a DataType from two parameters.
        
        The parameters are:  
        - title - the "name" of this data type, such as "Processed data"
        - data_id - the ID of the data type. Types compare equal when their IDs are the same.
        """
        self._title = title or "Invalid data"
        self._data_id = data_id or 0

    def title(self):
        return self._title

    def data_id(self):
        """Data type's data id.

        Data id is the defining attribute of a data type. Data types with the same id compare equal.
        """
        return self._data_id

    def setTitle(self, title):
        self._title = title

    def setDataId(self, data_id):
        self._data_id = data_id

    def serialize(self) -> dict:
        return {
            "data_id": self.data_id(),
            "title": self.title()
        }

    def deserialize(self, data: dict):
        self.setTitle(data["title"])
        self.setDataId(data["data_id"])

    def __str__(self):
        return self.title()

    def __eq__(self, other):
        return self.data_id() == other.data_id()

    def __ne__(self, other):
        return not self == other


DataType.Invalid = DataType()
"""Data type that results from default-constructing a DataType object."""

DataType.Unknown = DataType("Unknown data", 1)
"""Data type that is assigned to default-constructed node connections."""
