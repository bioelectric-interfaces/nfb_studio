class DataType:
    def __init__(self, title=None, data_id=None):
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


Invalid = DataType()
"""Data type that results from default-constructing a DataType object."""
Unknown = DataType("Unknown data", 1)
