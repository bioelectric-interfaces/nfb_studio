class EdgeDrag:
    def __init__(self):
        self.node_id = None
        self.connection_type = None
        self.connection_index = None
        self.data_type = None
    
    def serialize(self) -> dict:
        return {
            "node_id": self.node_id,
            "connection_type": self.connection_type,
            "connection_index": self.connection_index,
            "data_type": self.data_type
        }
    
    def deserialize(self, data: dict):
        self.node_id = data["node_id"]
        self.connection_type = data["connection_type"]
        self.connection_index = data["connection_index"]
        self.data_type = data["data_type"]