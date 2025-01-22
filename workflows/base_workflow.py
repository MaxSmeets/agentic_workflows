import uuid

class Workflow:
    def __init__(self) -> None:
        self.id = uuid.uuid1()
    
    def get_id(self):
        return self.id
    
    def execute(self):
        """Main workflow execution logic"""
        print(f"Executing workflow {self.id}")
        return self.id